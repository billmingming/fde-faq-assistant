import io
import os
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.llm import ask_deepseek, build_messages


HITS = [
    {
        "source": "handbook.txt",
        "title": "年假",
        "content": "员工每年享有五天年假。",
    }
]


class LlmTests(unittest.TestCase):
    def test_missing_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            answer = ask_deepseek("年假有多少天", HITS)

        self.assertIn("未配置 DEEPSEEK_API_KEY", answer)

    def test_build_messages_contains_source(self):
        messages = build_messages("年假有多少天", HITS)

        self.assertIn("[1]", messages[1]["content"])
        self.assertIn("年假有多少天", messages[1]["content"])
        self.assertIn("handbook.txt", messages[1]["content"])

    def test_http_error(self):
        http_error = HTTPError(
            url="https://api.deepseek.com/chat/completions",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=io.BytesIO(b'{"error":"invalid key"}'),
        )

        with patch.dict(
            os.environ,
            {"DEEPSEEK_API_KEY": "test-key"},
            clear=True,
        ):
            with patch(
                "app.llm.request.urlopen",
                side_effect=http_error,
            ):
                answer = ask_deepseek("年假有多少天", HITS)

        self.assertIn("401", answer)


if __name__ == "__main__":
    unittest.main()