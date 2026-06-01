from dotenv import load_dotenv

load_dotenv()

import logging
import time
import uuid
from typing import List

from fastapi import FastAPI, HTTPException, Query, Request
from models import (
    LLMProvider,
    EpisodeSummary,
    TranscriptChunk,
    ChunkSummary,
    SummarizeRequest,
)
from LLMClient import LLMClient
from srt_handler import SrtHandler

from errors import ModelUnavailableError
import cache
from logging_config import configure_logging, request_id

configure_logging()
logger = logging.getLogger(__name__)
app = FastAPI()
llm = LLMClient(LLMProvider.GEMINI, merge_model="gemini-2.5-flash")
srt_handler = SrtHandler()

# Raw model kept only for the /api/v1/chat testing endpoint.
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(
    model="gemma-4-31b-it",
    temperature=1.0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    include_thoughts=True,
)


@app.middleware("http")
async def log_api_requests(request: Request, call_next):
    if not request.url.path.startswith("/api/"):
        return await call_next(request)

    current_request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    token = request_id.set(current_request_id)
    started_at = time.perf_counter()

    try:
        logger.info("Incoming request method=%s path=%s", request.method, request.url.path)
        response = await call_next(request)
        response.headers["X-Request-Id"] = current_request_id
        return response
    finally:
        duration_ms = round((time.perf_counter() - started_at) * 1000)
        status_code = locals().get("response").status_code if "response" in locals() else 500
        logger.info(
            "Completed request method=%s path=%s status=%s durationMs=%s",
            request.method,
            request.url.path,
            status_code,
            duration_ms,
        )
        request_id.reset(token)


@app.get("/api/v1/subtitles")
def get_subtitle(
    title: str = Query(..., description="Show title"),
    season: int = Query(1, description="Season number", ge=1),
    episode: int = Query(1, description="Episode number", ge=1),
    language: str = Query("en", description="Subtitle language code"),
):
    logger.info(
        "Subtitle search requested title=%s season=%s episode=%s language=%s",
        title,
        season,
        episode,
        language,
    )
    srt = srt_handler.find_subtitle(title, season, episode, language)
    logger.info("Subtitle search completed resultCount=%s", len(getattr(srt, "data", srt)))
    return srt


@app.post("/api/v1/intent", response_model=SummarizeRequest)
def extract_intent(message: str) -> SummarizeRequest:
    logger.info("Intent extraction requested messageLength=%s", len(message))
    intent = llm.extract_intent(message)
    logger.info(
        "Intent extraction completed title=%s season=%s episode=%s language=%s",
        intent.title,
        intent.season,
        intent.episode,
        intent.language,
    )
    return intent


@app.post("/api/v1/chat")
def chat_with_llm(message: str):
    logger.info("Chat request received messageLength=%s", len(message))
    resp = model.invoke(message)
    logger.info("Chat request completed")
    return resp.content[-1]["text"]


@app.post("/api/v1/summarize", response_model=EpisodeSummary)
def create_summary(request: SummarizeRequest) -> EpisodeSummary:
    started_at = time.perf_counter()
    logger.info(
        "Summary requested title=%s season=%s episode=%s language=%s",
        request.title,
        request.season,
        request.episode,
        request.language,
    )

    cached = cache.read(
        request.title, request.season, request.episode, request.language
    )
    if cached:
        logger.info("Summary cache hit")
        return EpisodeSummary.model_validate(cached)

    logger.info("Summary cache miss")
    chunks: List[TranscriptChunk] = srt_handler.subtitles_to_chunks(
        srt_handler.fetch_subtitle(
            request.title, request.season, request.episode, request.language
        )
    )
    logger.info("Subtitle chunks prepared chunkCount=%s", len(chunks))

    try:
        chunk_summaries: List[ChunkSummary] = llm.summarize_chunks(chunks)
    except ModelUnavailableError as e:
        logger.exception("Chunk summarization failed")
        raise HTTPException(status_code=503, detail=str(e))
    logger.info("Chunk summarization completed chunkSummaryCount=%s", len(chunk_summaries))

    episode_summary = llm.merge_chunk_summaries(chunk_summaries)
    logger.info(
        "Chunk summary merge completed finalSummaryLength=%s",
        len(episode_summary.final_summary),
    )
    cache.write(
        request.title,
        request.season,
        request.episode,
        request.language,
        episode_summary.model_dump(mode="json"),
    )
    duration_ms = round((time.perf_counter() - started_at) * 1000)
    logger.info("Summary completed durationMs=%s", duration_ms)
    return episode_summary
