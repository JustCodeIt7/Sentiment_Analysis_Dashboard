import time
import pandas as pd
import yfinance as yf
import streamlit as st
from scraper import extract_article_text
from sentiment import analyze_sentiment, calculate_combined_sentiment

def get_stock_news(ticker_symbol: str, num_articles: int = 5) -> list:
    """Fetch recent news articles for a given stock ticker."""
    try:
        news = yf.Ticker(ticker_symbol).news # Changed yf.Search to yf.Ticker based on common yfinance usage
        return news[:num_articles] if news else []
    except Exception as e:
        st.error(f"Error fetching news for {ticker_symbol}: {e}")
        return []


def process_article(article: dict, index: int, total: int, status_text) -> dict:
    """Process a single news article to extract and analyze sentiment."""
    status_text.text(f"Processing article {index+1}/{total}...")
    title = article.get('title', '')
    # summary = article.get('summary', '') # yfinance Ticker.news might not have 'summary'
    url = article.get('link', '')
    headline = f"{title}" # Removed summary as it might not be present
    h_pol, h_subj, h_label, h_emoji = analyze_sentiment(headline)
    full_text = ""
    if url:
        status_text.text(f"Extracting text from article {index+1}...")
        full_text = extract_article_text(url)
        time.sleep(0.5)
    if full_text:
        f_pol, f_subj, f_label, f_emoji = analyze_sentiment(full_text)
    else:
        f_pol, f_subj, f_label, f_emoji = h_pol, h_subj, h_label, h_emoji
        full_text = "Could not extract full article text"
    return {
        'title': title,
        'publisher': article.get('publisher', 'Unknown'),
        'link': url,
        'headline_polarity': h_pol,
        'headline_subjectivity': h_subj,
        'headline_sentiment': h_label,
        'headline_emoji': h_emoji,
        'full_text_polarity': f_pol,
        'full_text_subjectivity': f_subj,
        'full_text_sentiment': f_label,
        'full_text_emoji': f_emoji,
        'article_text': (full_text[:500] + '...') if len(full_text) > 500 else full_text,
        'published': article.get('providerPublishTime', 'Unknown'), # yfinance uses providerPublishTime
        'raw_text': full_text
    }

def analyze_stock_news_sentiment(ticker: str, num_articles: int):
    """Analyze sentiment of stock news articles."""
    articles = get_stock_news(ticker, num_articles)
    if not articles:
        return 0,0,"Neutral",pd.DataFrame(),None
    progress = st.progress(0)
    status = st.empty()
    results = []
    texts = []
    for i, art in enumerate(articles):
        data = process_article(art, i, len(articles), status)
        results.append(data)
        if data['raw_text']:
            texts.append(data['raw_text'])
        progress.progress((i+1)/len(articles))
    progress.empty()
    status.empty()
    df = pd.DataFrame(results).drop(columns=['raw_text'])
    avg_pol = df['full_text_polarity'].mean() if not df.empty else 0
    avg_subj = df['full_text_subjectivity'].mean() if not df.empty else 0
    overall = "Positive" if avg_pol>0.1 else "Negative" if avg_pol<-0.1 else "Neutral"
    combined = calculate_combined_sentiment(texts)
    return avg_pol, avg_subj, overall, df, combined