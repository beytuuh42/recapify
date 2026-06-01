import logging
import sys
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

from logging_config import RequestIdFilter, request_id


class RequestIdFilterTest(unittest.TestCase):
    def test_adds_default_request_id_to_log_record(self):
        request_filter = RequestIdFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="message",
            args=(),
            exc_info=None,
        )

        was_included = request_filter.filter(log_record)

        self.assertTrue(was_included)
        self.assertEqual("system", log_record.request_id)

    def test_adds_current_request_id_to_log_record(self):
        request_filter = RequestIdFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="message",
            args=(),
            exc_info=None,
        )
        token = request_id.set("request-123")

        try:
            was_included = request_filter.filter(log_record)
        finally:
            request_id.reset(token)

        self.assertTrue(was_included)
        self.assertEqual("request-123", log_record.request_id)


if __name__ == "__main__":
    unittest.main()
