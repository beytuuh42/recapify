from dotenv import load_dotenv

load_dotenv()

import logging
import time
import uuid

from fastapi import FastAPI, HTTPException, Query, Request
from models import EpisodeSummary, SummarizeRequest
from llm_client import LlmClient
from srt_handler import SrtHandler
from summary_workflow import run_summary
from errors import ModelUnavailableError, SubtitleNotFoundError
from logging_config import configure_logging, request_id

configure_logging()
logger = logging.getLogger(__name__)
app = FastAPI()
llm_client = LlmClient(merge_model="gemini-2.5-flash")
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
    result = srt_handler.search_subtitles(title, season, episode, language)
    logger.info("Subtitle search completed resultCount=%s", len(getattr(result, "data", result)))
    return result


@app.post("/api/v1/intent", response_model=SummarizeRequest)
def extract_intent(message: str) -> SummarizeRequest:
    logger.info("Intent extraction requested messageLength=%s", len(message))
    intent = llm_client.extract_intent(message)
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
    try:
        return run_summary(request, llm_client, srt_handler)
    except SubtitleNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "subtitle_not_found",
                "title": e.title,
                "season": e.season,
                "episode": e.episode,
                "language": e.language,
            },
        )
    except ModelUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
