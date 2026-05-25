import os
import time
from pathlib import Path
from typing import Optional, Type, TypeVar

from google import genai
from google.genai import types
from google.genai.errors import ServerError
from pydantic import BaseModel
from models import (
    LLMProvider,
    TranscriptChunk,
    EpisodeSummary,
    ChunkSummary,
    SummarizeRequest,
)
from errors import ModelUnavailableError

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    def __init__(
        self,
        provider: LLMProvider,
        chunk_model: str = "gemini-3.1-flash-lite",
        merge_model: str = "gemini-3-flash",
    ):
        self.provider = provider
        self.client: Optional[genai.Client]

        if provider == LLMProvider.GEMINI:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY is not configured.")

            self.chunk_model = chunk_model
            self.merge_model = merge_model
            self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def _generate_cache(self, model: str, prompt: str):
        # TODO: check if LLM result can be cached directly to prevent wasting tokens / api requests
        cache = self.client.caches.create(
            model=model,
            config=types.CreateCachedContentConfig(
                contents=[], system_instruction=prompt
            ),
        )
        return cache

    def _generate_structured(
        self, prompt: str, response_schema: Type[T], model: str
    ) -> T:
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": response_schema.model_json_schema(),
                },
            )

            if not response.text:
                raise ValueError("LLM response was empty.")

            return response_schema.model_validate_json(response.text)
        except ServerError as e:
            err = e.response.json()["error"]

            raise ModelUnavailableError(
                code=err["code"],
                status=err["status"],
                message=err["message"],
            ) from e

    def extract_intent(self, text: str) -> SummarizeRequest:
        prompt = "" + text
        resp: SummarizeRequest = self._generate_structured(
            prompt, SummarizeRequest, self.chunk_model
        )
        return resp

    def summarize_chunks(self, chunk: TranscriptChunk) -> ChunkSummary:
        prompt_template = self._load_prompt("prompt_summarize_chunk.txt")

        # TODO: verify if these params are needed for the prompt
        prompt = (
            f"{prompt_template}\n\n"
            f"CHUNK_NUMBER:\n{chunk.chunk_number}\n\n"
            f"START_TIME:\n{chunk.start_time or 'unknown'}\n\n"
            f"END_TIME:\n{chunk.end_time or 'unknown'}\n\n"
            f"TRANSCRIPT_CHUNK:\n{chunk.text}"
        )

        # TODO: maybe refactor this somewhere else, idk where or how. could use retry_attempt into the method signature?
        MAX_RETRIES = 5

        for attempt in range(MAX_RETRIES):
            try:
                return self._generate_structured(prompt, ChunkSummary, self.chunk_model)
            except ModelUnavailableError:
                if attempt == MAX_RETRIES - 1:
                    raise

                time.sleep(2**attempt)

    def merge_chunk_summaries(
        self, chunk_summaries: list[ChunkSummary]
    ) -> EpisodeSummary:
        prompt_template = self._load_prompt("prompt_merge_episode_summary.txt")

        summaries_json = [
            summary.model_dump(mode="json") for summary in chunk_summaries
        ]

        prompt = f"{prompt_template}\n\n" f"CHUNK_SUMMARIES:\n{summaries_json}"

        episode_summary = self._generate_structured(
            prompt, EpisodeSummary, self.merge_model
        )
        episode_summary.chunk_summaries = chunk_summaries

        return episode_summary

    @staticmethod
    def _load_prompt(filename: str) -> str:
        prompt_path = Path("prompts") / filename

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        return prompt_path.read_text(encoding="UTF-8")
