from textblob import TextBlob

def analyze_sentiment(text: str):
    """
    Analyze text sentiment using TextBlob.
    Returns polarity, subjectivity, sentiment label, and emoji.
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    if polarity > 0.1:
        label, emoji = "Positive", "😊"
    elif polarity < -0.1:
        label, emoji = "Negative", "😠"
    else:
        label, emoji = "Neutral", "😐"
    return polarity, subjectivity, label, emoji


def calculate_combined_sentiment(article_texts: list):
    """
    Calculate sentiment from all article texts combined.
    """
    if not article_texts:
        return None
    combined_text = " ".join(article_texts)
    polarity, subjectivity, label, emoji = analyze_sentiment(combined_text)
    return {
        'polarity': polarity,
        'subjectivity': subjectivity,
        'sentiment': label,
        'emoji': emoji
    }