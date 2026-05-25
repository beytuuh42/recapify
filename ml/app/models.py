from enum import Enum
from typing import List, Optional, Literal

from pydantic import BaseModel, Field, PositiveInt


class LLMProvider(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"


class MediaType(str, Enum):
    MOVIE = "movie"
    TV_SHOW = "tv_show"
    ANIME = "anime"
    OTHER = "other"


class Transcript(BaseModel):
    text: str = Field(
        description="Raw transcript text (e.g., subtitle/SRT-derived dialogue or screenplay text)."
    )


class TranscriptChunk(BaseModel):
    chunk_number: int = Field(
        description="Sequential index of the chunk in chronological order (starting from 1)."
    )
    text: str = Field(
        description="Cleaned transcript text for this chunk, typically representing a fixed time window."
    )
    start_time: Optional[str] = Field(
        default=None,
        description="Optional start timestamp of the chunk (e.g., '00:08:00').",
    )
    end_time: Optional[str] = Field(
        default=None,
        description="Optional end timestamp of the chunk (e.g., '00:16:00').",
    )


class ChunkSummary(BaseModel):
    chunk_number: int = Field(description="Sequential index of the summarized chunk.")
    title: str = Field(
        description="Short descriptive title capturing the main focus of this chunk."
    )
    summary: str = Field(
        description="Concise 2-4 sentence summary of the chunk, focusing on key narrative events."
    )
    key_events: List[str] = Field(
        default_factory=list,
        description="List of the most important events occurring in this chunk.",
    )
    characters: List[str] = Field(
        default_factory=list,
        description="Characters clearly involved or mentioned in this chunk (avoid guessing).",
    )


class EpisodeSummary(BaseModel):
    title: str = Field(
        description="Generated title for the episode or summarized content."
    )
    final_summary: str = Field(
        description="Cohesive episode recap (150-300 words), preserving narrative flow and major plot points."
    )
    key_events: List[str] = Field(
        default_factory=list,
        description="Key events across the entire episode, deduplicated and chronologically ordered.",
    )
    characters: List[str] = Field(
        default_factory=list,
        description="Main characters appearing throughout the episode.",
    )
    chunk_summaries: List[ChunkSummary] = Field(
        description="Intermediate summaries generated per transcript chunk."
    )


class SummarizeRequest(BaseModel):
    title: str = Field(..., description="Title of the media")

    media_type: Literal["series", "anime", "movie", "documentary", "other"] | None = (
        None
    )

    season: Optional[PositiveInt] = Field(
        None, description="Season number if specified"
    )

    episode: Optional[PositiveInt] = Field(
        None, description="Episode number if specified"
    )

    language: str = Field("en", description="Target language for the summary")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Breaking Bad",
                "media_type": "series",
                "season": 1,
                "episode": 1,
                "language": "en",
            }
        }
