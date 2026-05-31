from dotenv import load_dotenv

load_dotenv()

from typing import List

from fastapi import FastAPI, HTTPException, Query
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


@app.get("/api/v1/subtitles")
def get_subtitle(
    title: str = Query(..., description="Show title"),
    season: int = Query(1, description="Season number", ge=1),
    episode: int = Query(1, description="Episode number", ge=1),
    language: str = Query("en", description="Subtitle language code"),
):
    srt = srt_handler.find_subtitle(title, season, episode, language)
    return srt


@app.post("/api/v1/intent", response_model=SummarizeRequest)
def extract_intent(message: str) -> SummarizeRequest:
    return llm.extract_intent(message)


@app.post("/api/v1/chat")
def chat_with_llm(message: str):
    resp = model.invoke(message)
    return resp.content[-1]["text"]


@app.post("/api/v1/summarize", response_model=EpisodeSummary)
def create_summary(request: SummarizeRequest) -> EpisodeSummary:
    cached = cache.read(
        request.title, request.season, request.episode, request.language
    )
    if cached:
        print("Sending cached result")
        return EpisodeSummary.model_validate(cached)

    chunks: List[TranscriptChunk] = srt_handler.subtitles_to_chunks(
        srt_handler.fetch_subtitle(
            request.title, request.season, request.episode, request.language
        )
    )

    try:
        chunk_summaries: List[ChunkSummary] = llm.summarize_chunks(chunks)
    except ModelUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

    episode_summary = llm.merge_chunk_summaries(chunk_summaries)
    cache.write(
        request.title,
        request.season,
        request.episode,
        request.language,
        episode_summary.model_dump(mode="json"),
    )
    return episode_summary
