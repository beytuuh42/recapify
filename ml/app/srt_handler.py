import os
import re

from datetime import timedelta
from typing import List
from models import TranscriptChunk

import srt
from opensubtitlescom import OpenSubtitles, responses


class SrtHandler:
    def __init__(self):
        self.subtitles = OpenSubtitles(
            "recapify v0.1", os.getenv("OPEN_SUBTITLES_API_KEY")
        )
        self.subtitles.login(
            os.getenv("OPEN_SUBTITLES_USER"), os.getenv("OPEN_SUBTITLES_PASSWORD")
        )

    def find_subtitle(
        self, title: str, season_number: int, episode_number: int, languages: str = "en"
    ) -> list:
        response = self.subtitles.search(
            query=title,
            season_number=season_number,
            episode_number=episode_number,
            languages=languages,
            order_by=["download_count"],
        )

        return response

    def fetch_subtitle(
        self, title: str, season_number: int, episode_number: int, languages: str = "en"
    ) -> list:
        response = self.find_subtitle(title, season_number, episode_number, languages)
        srt = self.subtitles.download_and_parse(response.data[0])
        return srt

    def _clean_subtitle_content(self, content: str) -> str:
        content = content.replace("\n", " ")
        content = re.sub(r"<[^>]+>", "", content)  # remove HTML tags like <i>
        content = re.sub(r"\s+", " ", content)
        return content.strip()

    def _format_timestamp(self, value: timedelta) -> str:
        total_seconds = int(value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def subtitles_to_chunks(
        self, subtitles: List[srt.Subtitle]
    ) -> List[TranscriptChunk]:
        chunk_duration = timedelta(minutes=8)
        chunks: List[TranscriptChunk] = []

        current_chunk_number = 1
        current_start = timedelta(seconds=0)
        current_end = timedelta(seconds=0)
        current_parts: list[str] = []

        for sub in subtitles:
            content = self._clean_subtitle_content(sub.content)

            if not content:
                continue

            if sub.start >= current_start + chunk_duration and current_parts:
                chunks.append(
                    TranscriptChunk(
                        chunk_number=current_chunk_number,
                        text=" ".join(current_parts),
                        start_time=self._format_timestamp(current_start),
                        end_time=self._format_timestamp(current_end),
                    )
                )

                current_chunk_number += 1
                current_start = sub.start
                current_parts = []

            current_parts.append(content)
            current_end = sub.end

        if current_parts:
            chunks.append(
                TranscriptChunk(
                    chunk_number=current_chunk_number,
                    text=" ".join(current_parts),
                    start_time=self._format_timestamp(current_start),
                    end_time=self._format_timestamp(current_end),
                )
            )

        return chunks
