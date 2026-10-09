import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval import make_terms, split_text


class RetrievalTests(unittest.TestCase):
    def test_make_terms(self):
        terms = make_terms("年假有多少天 python api")

        self.assertIn("年假", terms)
        self.assertIn("python", terms)
        self.assertIn("api", terms)

    def test_split_long_text(self):
        text = "年假规定。" * 100
        chunks = split_text(text, max_chars=100, overlap=20)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= 100 for chunk in chunks))


if __name__ == "__main__":
    unittest.main()