import sys
import unittest
from pathlib import Path

import pandas as pd

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

from xquik_import import normalize_xquik_export


class XquikImportTests(unittest.TestCase):
    def test_normalizes_export_columns_for_stock_dashboard(self):
        frame = pd.DataFrame(
            {
                "full_text": [" Stock outlook improved ", ""],
                "username": ["analyst", "empty"],
                "created_at": ["2026-07-05", "2026-07-06"],
                "tweet_id": ["201", "202"],
            }
        )

        result = normalize_xquik_export(frame)

        self.assertEqual(
            result.to_dict("records"),
            [
                {
                    "text": "Stock outlook improved",
                    "author": "analyst",
                    "published": "2026-07-05",
                    "source_id": "201",
                }
            ],
        )

    def test_unknown_schema_returns_empty_frame(self):
        result = normalize_xquik_export(pd.DataFrame({"score": [1]}))

        self.assertEqual(list(result.columns), ["text", "author", "published", "source_id"])
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
