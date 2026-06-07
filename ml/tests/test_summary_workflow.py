import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))


# --- Mock classes ---

class _FakeChatGoogleGenerativeAI:
    def __init__(self, **kwargs):
        pass

    def with_structured_output(self, schema):
        return self

    def with_retry(self, **kwargs):
        return self

    def __or__(self, other):
        return other


class _FakeLangsmithClient:
    def pull_prompt(self, name):
        fake = MagicMock()
        fake.input_variables = ["text"]
        return fake


# --- Mock modules and variables ---

for mod_name in ["opensubtitlescom", "srt", "dotenv"]:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = types.ModuleType(mod_name)

opensubtitles_mod = sys.modules["opensubtitlescom"]
opensubtitles_mod.OpenSubtitles = object
opensubtitles_mod.responses = types.SimpleNamespace()

lgg_mod = types.ModuleType("langchain_google_genai")
lgg_mod.ChatGoogleGenerativeAI = _FakeChatGoogleGenerativeAI
sys.modules["langchain_google_genai"] = lgg_mod

ls_mod = types.ModuleType("langsmith")
ls_mod.Client = _FakeLangsmithClient
sys.modules["langsmith"] = ls_mod


# --- Imports ---

from models import SummarizeRequest, EpisodeSummary, ChunkSummary, TranscriptChunk
from errors import ModelUnavailableError, SubtitleNotFoundError
from summary_workflow import run_summary


# --- Helper functions ---

def _make_request():
    return SummarizeRequest(title="Breaking Bad", season=1, episode=1, language="en")


def _make_chunk_summaries():
    return [
        ChunkSummary(
            chunk_number=1,
            title="Cold Open",
            summary="Walter White is diagnosed with cancer.",
            key_events=["Walter diagnosed"],
            characters=["Walter White"],
        ),
        ChunkSummary(
            chunk_number=2,
            title="Desperate Decision",
            summary="Walter recruits Jesse to cook meth.",
            key_events=["Jesse recruited"],
            characters=["Walter White", "Jesse Pinkman"],
        ),
    ]


def _make_episode_summary(chunk_summaries=None):
    return EpisodeSummary(
        title="Pilot",
        final_summary="Walter White begins cooking meth.",
        key_events=["Walter diagnosed", "Jesse recruited"],
        characters=["Walter White", "Jesse Pinkman"],
        chunk_summaries=chunk_summaries or _make_chunk_summaries(),
    )


# --- Tests ---

class SummaryWorkflowTest(unittest.TestCase):
    def _make_mocks(self):
        llm_client = MagicMock()
        srt_handler = MagicMock()
        return llm_client, srt_handler

    @patch("summary_workflow.cache")
    def test_cache_hit_returns_cached_summary_without_calling_dependencies(self, mock_cache):
        request = _make_request()
        expected = _make_episode_summary()
        mock_cache.read.return_value = expected.model_dump(mode="json")
        llm_client, srt_handler = self._make_mocks()

        result = run_summary(request, llm_client, srt_handler)

        self.assertEqual(result.title, expected.title)
        self.assertEqual(result.final_summary, expected.final_summary)
        llm_client.extract_intent.assert_not_called()
        llm_client.summarize_chunks.assert_not_called()
        srt_handler.download_subtitle.assert_not_called()

    @patch("summary_workflow.cache")
    def test_full_workflow_passes_data_through_each_stage(self, mock_cache):
        request = _make_request()
        mock_cache.read.return_value = None
        llm_client, srt_handler = self._make_mocks()

        raw_subtitle = "raw srt content"
        chunks = [
            TranscriptChunk(chunk_number=1, text="Walter White is a chemistry teacher.", start_time="00:00:00", end_time="00:08:00"),
            TranscriptChunk(chunk_number=2, text="He gets diagnosed with inoperable lung cancer.", start_time="00:08:00", end_time="00:16:00"),
        ]
        chunk_summaries = _make_chunk_summaries()
        expected = _make_episode_summary(chunk_summaries)

        srt_handler.download_subtitle.return_value = raw_subtitle
        srt_handler.subtitles_to_chunks.return_value = chunks
        llm_client.summarize_chunks.return_value = chunk_summaries
        llm_client.merge_chunk_summaries.return_value = expected

        result = run_summary(request, llm_client, srt_handler)

        srt_handler.subtitles_to_chunks.assert_called_once_with(raw_subtitle)
        llm_client.summarize_chunks.assert_called_once_with(chunks)
        llm_client.merge_chunk_summaries.assert_called_once_with(chunk_summaries)
        self.assertEqual(result.title, expected.title)
        self.assertEqual(result.final_summary, expected.final_summary)
        self.assertEqual(len(result.chunk_summaries), 2)
        mock_cache.write.assert_called_once()

    @patch("summary_workflow.cache")
    def test_cache_miss_runs_full_workflow_and_writes_cache(self, mock_cache):
        request = _make_request()
        expected = _make_episode_summary()
        mock_cache.read.return_value = None
        llm_client, srt_handler = self._make_mocks()
        srt_handler.download_subtitle.return_value = []
        srt_handler.subtitles_to_chunks.return_value = []
        llm_client.summarize_chunks.return_value = expected.chunk_summaries
        llm_client.merge_chunk_summaries.return_value = expected

        result = run_summary(request, llm_client, srt_handler)

        self.assertEqual(result.title, expected.title)
        srt_handler.download_subtitle.assert_called_once_with(
            request.title, request.season, request.episode, request.language
        )
        llm_client.summarize_chunks.assert_called_once()
        llm_client.merge_chunk_summaries.assert_called_once()
        mock_cache.write.assert_called_once()

    @patch("summary_workflow.cache")
    def test_model_unavailable_error_propagates_from_run_summary(self, mock_cache):
        request = _make_request()
        mock_cache.read.return_value = None
        llm_client, srt_handler = self._make_mocks()
        srt_handler.download_subtitle.return_value = []
        srt_handler.subtitles_to_chunks.return_value = []
        llm_client.summarize_chunks.side_effect = ModelUnavailableError(
            code=503, status="UNAVAILABLE", message="Model overloaded"
        )

        with self.assertRaises(ModelUnavailableError):
            run_summary(request, llm_client, srt_handler)

        mock_cache.write.assert_not_called()

    @patch("summary_workflow.cache")
    def test_subtitle_not_found_propagates_from_run_summary(self, mock_cache):
        request = _make_request()
        mock_cache.read.return_value = None
        llm_client, srt_handler = self._make_mocks()
        srt_handler.download_subtitle.side_effect = SubtitleNotFoundError(
            title=request.title,
            season=request.season,
            episode=request.episode,
            language=request.language,
        )

        with self.assertRaises(SubtitleNotFoundError):
            run_summary(request, llm_client, srt_handler)

        llm_client.summarize_chunks.assert_not_called()
        mock_cache.write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
