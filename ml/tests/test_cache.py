import sys
import tempfile
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

import cache


class CacheTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.original_cache_directory = cache._CACHE_DIR
        cache._CACHE_DIR = Path(self.temporary_directory.name)

    def tearDown(self):
        cache._CACHE_DIR = self.original_cache_directory
        self.temporary_directory.cleanup()

    def test_read_returns_none_for_missing_entry(self):
        title = "Breaking Bad"
        season = 1
        episode = 1
        language = "en"

        cached_summary = cache.read(title, season, episode, language)

        self.assertIsNone(cached_summary)

    def test_write_and_read_round_trips_summary_data(self):
        title = "Breaking Bad"
        season = 1
        episode = 1
        language = "en"
        summary_data = {
            "title": "Pilot",
            "final_summary": "Walter White makes a life-changing decision.",
        }

        cache.write(title, season, episode, language, summary_data)
        cached_summary = cache.read(title, season, episode, language)

        self.assertEqual(summary_data, cached_summary)

    def test_cache_key_is_case_insensitive_for_title_and_language(self):
        title = "Breaking Bad"
        season = 1
        episode = 1
        language = "EN"
        summary_data = {
            "title": "Pilot",
            "final_summary": "Walter White starts cooking meth.",
        }

        cache.write(title, season, episode, language, summary_data)
        cached_summary = cache.read("breaking bad", season, episode, "en")

        self.assertEqual(summary_data, cached_summary)


if __name__ == "__main__":
    unittest.main()
