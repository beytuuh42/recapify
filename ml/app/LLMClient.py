import os

from google.genai.errors import ServerError
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import Client

from models import (
    LLMProvider,
    TranscriptChunk,
    EpisodeSummary,
    ChunkSummary,
    SummarizeRequest,
)
from errors import ModelUnavailableError


class LLMClient:
    def __init__(
        self,
        provider: LLMProvider,
        chunk_model: str = "gemini-3.1-flash-lite",
        merge_model: str = "gemini-3-flash",
        intent_model: str = "gemma-4-31b-it",
    ):
        if provider != LLMProvider.GEMINI:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not configured.")

        self.provider = provider
        self.chunk_model = chunk_model
        self.merge_model = merge_model
        self.intent_model = intent_model

        # TODO: add content class for dynamic model calling

        chunk_model_chain = (
            ChatGoogleGenerativeAI(model=chunk_model, api_key=api_key)
            .with_structured_output(ChunkSummary)
            .with_retry(
                retry_if_exception_type=(ServerError,),
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
        except ServerError as e:
            raise ModelUnavailableError(
                code=e.code,
                status=e.status,
                message=e.message,
            ) from e

    def extract_intent(self, message: str) -> SummarizeRequest:
        [variable] = self._intent_prompt.input_variables
        return self._invoke_structured(self._intent_chain, {variable: message})

    def summarize_chunks(self, chunks: list[TranscriptChunk]) -> list[ChunkSummary]:
        [variable] = self._chunk_prompt.input_variables

        # TODO: verify if these params are needed for the prompt
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
            return self._chunk_chain.batch(inputs)
        except ServerError as e:
            raise ModelUnavailableError(
                code=e.code,
                status=e.status,
                message=e.message,
            ) from e

    def merge_chunk_summaries(
        self, chunk_summaries: list[ChunkSummary]
    ) -> EpisodeSummary:
        [variable] = self._merge_prompt.input_variables

        summaries_json = [
            summary.model_dump(mode="json") for summary in chunk_summaries
        ]

        episode_summary = self._invoke_structured(
            self._merge_chain, {variable: f"CHUNK_SUMMARIES:\n{summaries_json}"}
        )
        episode_summary.chunk_summaries = chunk_summaries

        return episode_summary
