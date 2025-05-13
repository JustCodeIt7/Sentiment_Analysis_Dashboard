"""
Sentiment Analysis Tools
-----------------------
Functions for analyzing text sentiment.
"""

from textblob import TextBlob


def analyze_sentiment(text):
    """
    Analyze text sentiment using TextBlob.

    Parameters:
        text (str): The text to analyze

    Returns:
        tuple: (polarity, subjectivity, sentiment_label, emoji)
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # -1 (negative) to 1 (positive)
    subjectivity = blob.sentiment.subjectivity  # 0 (objective) to 1 (subjective)

    # Classify sentiment based on polarity
    if polarity > 0.1:
        sentiment_label = "Positive"
        emoji = "😊"
    elif polarity < -0.1:
        sentiment_label = "Negative"
        emoji = "😠"
    else:
        sentiment_label = "Neutral"
        emoji = "😐"

    return polarity, subjectivity, sentiment_label, emoji


def calculate_combined_sentiment(article_texts):
    """
    Calculate sentiment from all article texts combined

    Parameters:
        article_texts (list): List of article text strings

    Returns:
        dict or None: Combined sentiment metrics or None if no texts available
    """
    combined_text = " ".join(article_texts)
    if not combined_text:
        return None

    combined_polarity, combined_subjectivity, combined_sentiment_label, combined_emoji = analyze_sentiment(
        combined_text)

    return {
        'polarity': combined_polarity,
        'subjectivity': combined_subjectivity,
        'sentiment': combined_sentiment_label,
        'emoji': combined_emoji
    }
