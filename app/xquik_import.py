from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
import re

import pandas as pd

from sentiment import analyze_sentiment, calculate_combined_sentiment


TEXT_COLUMNS = (
    "text",
    "tweet",
    "tweet_text",
    "full_text",
    "content",
    "post_content",
    "body",
    "headline",
    "title",
    "message",
)
AUTHOR_COLUMNS = ("author", "username", "user", "screen_name", "handle", "publisher")
DATE_COLUMNS = ("created_at", "date", "timestamp", "published")
SOURCE_ID_COLUMNS = ("id", "tweet_id", "post_id", "source_id", "link")


@dataclass(frozen=True)
class XquikAnalysisResult:
    avg_polarity: float
    avg_subjectivity: float
    overall_sentiment: str
    news_df: pd.DataFrame
    combined_sentiment: dict[str, object] | None
    has_text_column: bool
    has_non_empty_text: bool

    @property
    def has_rows(self) -> bool:
        return not self.news_df.empty

    def as_display_args(
        self,
    ) -> tuple[float, float, str, pd.DataFrame, dict[str, object] | None]:
        return (
            self.avg_polarity,
            self.avg_subjectivity,
            self.overall_sentiment,
            self.news_df,
            self.combined_sentiment,
        )


def _match_column(columns: Iterable[str], candidates: tuple[str, ...]) -> str | None:
    by_key = {
        re.sub(r"[^a-z0-9]+", "_", column.strip().lower()).strip("_"): column
        for column in columns
    }
    for candidate in candidates:
        if candidate in by_key:
            return by_key[candidate]
    return None


def _clean(frame: pd.DataFrame, column: str | None) -> pd.Series:
    if column is None:
        return pd.Series([""] * len(frame), index=frame.index, dtype="string")
    return frame[column].fillna("").astype(str).str.strip()


def normalize_xquik_export(frame: pd.DataFrame) -> pd.DataFrame:
    text_column = _match_column(frame.columns, TEXT_COLUMNS)
    if text_column is None:
        return pd.DataFrame(columns=["text", "author", "published", "source_id"])

    normalized = pd.DataFrame(index=frame.index)
    normalized["text"] = _clean(frame, text_column)
    normalized["author"] = _clean(frame, _match_column(frame.columns, AUTHOR_COLUMNS))
    normalized["published"] = _clean(frame, _match_column(frame.columns, DATE_COLUMNS))
    normalized["source_id"] = _clean(
        frame, _match_column(frame.columns, SOURCE_ID_COLUMNS)
    )
    normalized = normalized[normalized["text"] != ""]
    return normalized.reset_index(drop=True)


def analyze_xquik_posts(frame: pd.DataFrame) -> XquikAnalysisResult:
    has_text_column = _match_column(frame.columns, TEXT_COLUMNS) is not None
    normalized = normalize_xquik_export(frame)
    if normalized.empty:
        return XquikAnalysisResult(
            0.0,
            0.0,
            "Neutral",
            pd.DataFrame(),
            None,
            has_text_column,
            False,
        )

    rows = []
    for index, row in normalized.iterrows():
        polarity, subjectivity, sentiment, emoji = analyze_sentiment(row["text"])
        rows.append(
            {
                "title": row["text"][:80],
                "publisher": row["author"] or "Xquik export",
                "link": row["source_id"],
                "headline_polarity": polarity,
                "headline_subjectivity": subjectivity,
                "headline_sentiment": sentiment,
                "headline_emoji": emoji,
                "full_text_polarity": polarity,
                "full_text_subjectivity": subjectivity,
                "full_text_sentiment": sentiment,
                "full_text_emoji": emoji,
                "article_text": row["text"],
                "published": row["published"] or f"Row {index + 1}",
            }
        )

    news_df = pd.DataFrame(rows)
    avg_polarity = news_df["full_text_polarity"].mean()
    avg_subjectivity = news_df["full_text_subjectivity"].mean()
    if avg_polarity > 0.1:
        overall_sentiment = "Positive"
    elif avg_polarity < -0.1:
        overall_sentiment = "Negative"
    else:
        overall_sentiment = "Neutral"

    combined_sentiment = calculate_combined_sentiment(normalized["text"].tolist())
    return XquikAnalysisResult(
        avg_polarity,
        avg_subjectivity,
        overall_sentiment,
        news_df,
        combined_sentiment,
        True,
        True,
    )
