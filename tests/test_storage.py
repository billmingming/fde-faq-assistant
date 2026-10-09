import tempfile
import unittest
from pathlib import Path

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.storage import Database


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "test.sqlite"
        self.db = Database(str(db_path))

    def tearDown(self):
        self.db.close()
        self.temp_dir.cleanup()

    def test_add_document(self):
        self.db.add_document(
            "handbook.txt",
            "员工手册",
            ["员工每年享有五天年假。"],
        )

        self.assertEqual(
            self.db.stats(),
            {"documents": 1, "chunks": 1},
        )

    def test_search_chinese_text(self):
        self.db.add_document(
            "handbook.txt",
            "员工手册",
            ["员工入职满一年后，每年享有五天年假。"],
        )

        results = self.db.search(["年假"])

        self.assertEqual(len(results), 1)
        self.assertIn("五天年假", results[0]["content"])

    def test_search_unknown_term(self):
        self.db.add_document(
            "handbook.txt",
            "员工手册",
            ["员工每年享有五天年假。"],
        )

        self.assertEqual(self.db.search(["量子计算"]), [])


if __name__ == "__main__":
    unittest.main()