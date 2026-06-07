import logging
import time
from typing import List

from models import SummarizeRequest, EpisodeSummary, TranscriptChunk, ChunkSummary
from llm_client import LlmClient
from srt_handler import SrtHandler
import cache

logger = logging.getLogger(__name__)


def run_summary(
    request: SummarizeRequest,
    llm_client: LlmClient,
    srt_handler: SrtHandler,
) -> EpisodeSummary:
    started_at = time.perf_counter()
    logger.info(
        "Summary requested title=%s season=%s episode=%s language=%s",
        request.title,
        request.season,
        request.episode,
        request.language,
    )

    cached = cache.read(request.title, request.season, request.episode, request.language)
    if cached:
        logger.info("Summary cache hit")
        return EpisodeSummary.model_validate(cached)

    logger.info("Summary cache miss")
    chunks: List[TranscriptChunk] = srt_handler.subtitles_to_chunks(
        srt_handler.download_subtitle(
            request.title, request.season, request.episode, request.language
        )
    )
    logger.info("Subtitle chunks prepared chunkCount=%s", len(chunks))

    chunk_summaries: List[ChunkSummary] = llm_client.summarize_chunks(chunks)
    logger.info("Chunk summarization completed chunkSummaryCount=%s", len(chunk_summaries))

    episode_summary = llm_client.merge_chunk_summaries(chunk_summaries)
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
