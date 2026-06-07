import logging
import os
import time

import google.api_core.exceptions
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import Client

from models import (
    TranscriptChunk,
    EpisodeSummary,
    ChunkSummary,
    SummarizeRequest,
)
from errors import ModelUnavailableError

logger = logging.getLogger(__name__)


class LlmClient:
    def __init__(
        self,
        intent_model: str = "gemma-4-31b-it",
        chunk_model: str = "gemini-3.1-flash-lite",
        merge_model: str = "gemini-3-flash",
    ):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not configured.")

        self.chunk_model = chunk_model
        self.merge_model = merge_model
        self.intent_model = intent_model

        chunk_model_chain = (
            ChatGoogleGenerativeAI(model=chunk_model, api_key=api_key)
            .with_structured_output(ChunkSummary)
            .with_retry(
                retry_if_exception_type=(
                    google.api_core.exceptions.ServiceUnavailable,
                    google.api_core.exceptions.InternalServerError,
                    google.api_core.exceptions.ResourceExhausted,
                ),
                stop_after_attempt=5,
            )
        )

        merge_model_chain = ChatGoogleGenerativeAI(
            model=merge_model, api_key=api_key
        ).with_structured_output(EpisodeSummary)

        intent_model_chain = ChatGoogleGenerativeAI(
            model=intent_model,
            api_key=api_key,
            temperature=1.0,
            include_thoughts=True,
        ).with_structured_output(SummarizeRequest)

        self.prompt_client = Client()

        self._intent_prompt = self.prompt_client.pull_prompt("extract_intent")
        self._intent_chain = self._intent_prompt | intent_model_chain

        self._chunk_prompt = self.prompt_client.pull_prompt("summarize_chunk")
        self._chunk_chain = self._chunk_prompt | chunk_model_chain

        self._merge_prompt = self.prompt_client.pull_prompt("merge_episode_summary")
        self._merge_chain = self._merge_prompt | merge_model_chain

    def _invoke_structured(self, chain, prompt):
        try:
            return chain.invoke(prompt)
        except google.api_core.exceptions.GoogleAPICallError as e:
            raise ModelUnavailableError(
                code=getattr(e, "code", 500),
                status=getattr(e, "status", "INTERNAL"),
                message=str(e),
            ) from e

    def extract_intent(self, message: str) -> SummarizeRequest:
        started_at = time.perf_counter()
        [variable] = self._intent_prompt.input_variables
        logger.info("Invoking intent model model=%s messageLength=%s", self.intent_model, len(message))
        intent = self._invoke_structured(self._intent_chain, {variable: message})
        duration_ms = round((time.perf_counter() - started_at) * 1000)
        logger.info("Intent model completed durationMs=%s", duration_ms)
        return intent

    def summarize_chunks(self, chunks: list[TranscriptChunk]) -> list[ChunkSummary]:
        started_at = time.perf_counter()
        [variable] = self._chunk_prompt.input_variables

        inputs = [
            {
                variable: (
                    f"CHUNK_NUMBER:\n{chunk.chunk_number}\n\n"
                    f"START_TIME:\n{chunk.start_time or 'unknown'}\n\n"
                    f"END_TIME:\n{chunk.end_time or 'unknown'}\n\n"
                    f"TRANSCRIPT_CHUNK:\n{chunk.text}"
                )
            }
            for chunk in chunks
        ]

        try:
            logger.info(
                "Invoking chunk model model=%s chunkCount=%s",
                self.chunk_model,
                len(chunks),
            )
            summaries = self._chunk_chain.batch(inputs)
            duration_ms = round((time.perf_counter() - started_at) * 1000)
            logger.info("Chunk model completed chunkCount=%s durationMs=%s", len(summaries), duration_ms)
            return summaries
        except google.api_core.exceptions.GoogleAPICallError as e:
            duration_ms = round((time.perf_counter() - started_at) * 1000)
            logger.exception("Chunk model failed durationMs=%s", duration_ms)
            raise ModelUnavailableError(
                code=getattr(e, "code", 500),
                status=getattr(e, "status", "INTERNAL"),
                message=str(e),
            ) from e

    def merge_chunk_summaries(
        self, chunk_summaries: list[ChunkSummary]
    ) -> EpisodeSummary:
        started_at = time.perf_counter()
        [variable] = self._merge_prompt.input_variables

        summaries_json = [
            summary.model_dump(mode="json") for summary in chunk_summaries
        ]

        logger.info(
            "Invoking merge model model=%s chunkSummaryCount=%s",
            self.merge_model,
            len(chunk_summaries),
        )
        episode_summary = self._invoke_structured(
            self._merge_chain, {variable: f"CHUNK_SUMMARIES:\n{summaries_json}"}
        )
        episode_summary.chunk_summaries = chunk_summaries

        duration_ms = round((time.perf_counter() - started_at) * 1000)
        logger.info("Merge model completed durationMs=%s", duration_ms)
        return episode_summary
