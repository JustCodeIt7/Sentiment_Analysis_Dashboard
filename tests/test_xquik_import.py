import sys
import unittest
from importlib import import_module
from pathlib import Path

import pandas as pd

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

xquik_import = import_module("xquik_import")
analyze_xquik_posts = xquik_import.analyze_xquik_posts
normalize_xquik_export = xquik_import.normalize_xquik_export


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

        self.assertEqual(
            list(result.columns), ["text", "author", "published", "source_id"]
        )
        self.assertEqual(len(result), 0)

    def test_normalizes_spaced_header_aliases(self):
        result = normalize_xquik_export(
            pd.DataFrame({"Tweet Text": ["Market update"], "Post ID": ["301"]})
        )

        self.assertEqual(
            result.to_dict("records"),
            [
                {
                    "text": "Market update",
                    "author": "",
                    "published": "",
                    "source_id": "301",
                }
            ],
        )

    def test_text_only_export_keeps_normalized_schema(self):
        result = normalize_xquik_export(pd.DataFrame({"full_text": [" Update "]}))

        self.assertEqual(
            result.to_dict("records"),
            [{"text": "Update", "author": "", "published": "", "source_id": ""}],
        )

    def test_all_empty_text_rows_return_empty_normalized_frame(self):
        result = normalize_xquik_export(pd.DataFrame({"full_text": ["", "  ", None]}))

        self.assertTrue(result.empty)
        self.assertEqual(
            list(result.columns), ["text", "author", "published", "source_id"]
        )

    def test_analysis_result_exposes_named_display_fields(self):
        frame = pd.DataFrame({"text": ["Stock outlook improved"]})

        result = analyze_xquik_posts(frame)

        self.assertTrue(result.has_rows)
        self.assertTrue(result.has_text_column)
        self.assertTrue(result.has_non_empty_text)
        self.assertEqual(result.news_df.iloc[0]["title"], "Stock outlook improved")
        self.assertEqual(
            result.as_display_args()[3].iloc[0]["publisher"], "Xquik export"
        )

    def test_analysis_aggregates_sentiment_and_applies_fallbacks(self):
        result = analyze_xquik_posts(
            pd.DataFrame({"text": ["Strong growth", "Weak outlook"]})
        )

        self.assertIsInstance(result.avg_polarity, float)
        self.assertIsInstance(result.avg_subjectivity, float)
        self.assertIn(result.overall_sentiment, {"Positive", "Neutral", "Negative"})
        self.assertEqual(result.news_df["publisher"].tolist(), ["Xquik export"] * 2)
        self.assertEqual(result.news_df["published"].tolist(), ["Row 1", "Row 2"])
        self.assertEqual(result.news_df["link"].tolist(), ["", ""])
        self.assertIsNotNone(result.combined_sentiment)

    def test_empty_analysis_result_has_no_rows(self):
        result = analyze_xquik_posts(pd.DataFrame({"score": [1]}))

        self.assertFalse(result.has_rows)
        self.assertFalse(result.has_text_column)
        self.assertFalse(result.has_non_empty_text)
        self.assertTrue(result.news_df.empty)

    def test_empty_supported_text_column_is_distinct_from_unknown_schema(self):
        result = analyze_xquik_posts(pd.DataFrame({"text": ["", "  ", None]}))

        self.assertFalse(result.has_rows)
        self.assertTrue(result.has_text_column)
        self.assertFalse(result.has_non_empty_text)
        self.assertEqual(result.overall_sentiment, "Neutral")
        self.assertIsNone(result.combined_sentiment)


if __name__ == "__main__":
    unittest.main()
