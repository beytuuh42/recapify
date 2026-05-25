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
from concurrent.futures import ThreadPoolExecutor
import cache

app = FastAPI()
llm = LLMClient(LLMProvider.GEMINI, merge_model="gemini-2.5-flash")
srt_handler = SrtHandler()


from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(
    model="gemma-4-31b-it",
    temperature=1.0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    include_thoughts=True,
)

structured_model = model.bind(include_thoughts=True).with_structured_output(
    SummarizeRequest.model_json_schema(), include_raw=True
)

from langchain_core.messages import HumanMessage, SystemMessage
from pathlib import Path


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
    prompt_path = Path("prompts") / "extract_intent_v1.txt"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    messages = [
        SystemMessage(content=prompt_path.read_text(encoding="UTF-8")),
        HumanMessage(content=message),
    ]
    structured_response = structured_model.invoke(messages)
    return structured_response["parsed"]


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

    chunk_summaries: List[ChunkSummary] = []

    try:
        with ThreadPoolExecutor() as executor:
            chunk_summaries = list(executor.map(llm.summarize_chunks, chunks))
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
