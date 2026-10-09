import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.storage import Database
from app.workflow import answer_question


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "test.sqlite"
        self.db = Database(str(db_path))
        self.db.add_document(
            "handbook.txt",
            "员工手册",
            ["员工每年享有五天年假。"],
        )

    def tearDown(self):
        self.db.close()
        self.temp_dir.cleanup()

    def test_no_result(self):
        result = answer_question(self.db, "量子计算")

        self.assertEqual(
            result["answer"],
            "资料中没有找到相关内容。",
        )
        self.assertEqual(result["sources"], [])

    def test_answer_with_sources(self):
        with patch(
            "app.workflow.ask_deepseek",
            return_value="员工每年享有五天年假。[1]",
        ):
            result = answer_question(self.db, "年假")

        self.assertIn("五天年假", result["answer"])
        self.assertEqual(len(result["sources"]), 1)


if __name__ == "__main__":
    unittest.main()