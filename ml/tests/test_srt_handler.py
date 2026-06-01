import sys
import types
import unittest
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))


@dataclass
class Subtitle:
    index: int
    start: timedelta
    end: timedelta
    content: str


srt_module = types.ModuleType("srt")
srt_module.Subtitle = Subtitle
sys.modules["srt"] = srt_module

opensubtitles_module = types.ModuleType("opensubtitlescom")
opensubtitles_module.OpenSubtitles = object
opensubtitles_module.responses = types.SimpleNamespace()
sys.modules["opensubtitlescom"] = opensubtitles_module

from srt_handler import SrtHandler


class SrtHandlerTest(unittest.TestCase):
    def setUp(self):
        self.handler = SrtHandler.__new__(SrtHandler)

    def test_clean_subtitle_content_removes_markup_and_collapses_whitespace(self):
        subtitle_content = "  <i>Hello</i>\n   world   "

        cleaned_content = self.handler._clean_subtitle_content(subtitle_content)

        self.assertEqual("Hello world", cleaned_content)

    def test_format_timestamp_returns_hours_minutes_and_seconds(self):
        timestamp = timedelta(hours=1, minutes=2, seconds=3)

        formatted_timestamp = self.handler._format_timestamp(timestamp)

        self.assertEqual("01:02:03", formatted_timestamp)

    def test_subtitles_to_chunks_groups_cleaned_subtitles_into_time_windows(self):
        subtitles = [
            Subtitle(
                index=1,
                start=timedelta(seconds=0),
                end=timedelta(seconds=10),
                content="<i>Cold open</i>",
            ),
            Subtitle(
                index=2,
                start=timedelta(minutes=4),
                end=timedelta(minutes=4, seconds=10),
                content="First\nscene",
            ),
            Subtitle(
                index=3,
                start=timedelta(minutes=8, seconds=1),
                end=timedelta(minutes=8, seconds=20),
                content="Second act",
            ),
        ]

        chunks = self.handler.subtitles_to_chunks(subtitles)

        self.assertEqual(2, len(chunks))
        self.assertEqual(1, chunks[0].chunk_number)
        self.assertEqual("Cold open First scene", chunks[0].text)
        self.assertEqual("00:00:00", chunks[0].start_time)
        self.assertEqual("00:04:10", chunks[0].end_time)
        self.assertEqual(2, chunks[1].chunk_number)
        self.assertEqual("Second act", chunks[1].text)
        self.assertEqual("00:08:01", chunks[1].start_time)
        self.assertEqual("00:08:20", chunks[1].end_time)

    def test_subtitles_to_chunks_skips_empty_cleaned_subtitles(self):
        subtitles = [
            Subtitle(
                index=1,
                start=timedelta(seconds=0),
                end=timedelta(seconds=10),
                content="<i>   </i>",
            ),
            Subtitle(
                index=2,
                start=timedelta(seconds=11),
                end=timedelta(seconds=20),
                content="Visible subtitle",
            ),
        ]

        chunks = self.handler.subtitles_to_chunks(subtitles)

        self.assertEqual(1, len(chunks))
        self.assertEqual("Visible subtitle", chunks[0].text)


if __name__ == "__main__":
    unittest.main()
