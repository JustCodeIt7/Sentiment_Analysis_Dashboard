# Project Structure
# streamlit_app/
# ├── config.py
# ├── state.py
# ├── sidebar.py
# ├── sentiment.py
# ├── scraper.py
# ├── data_fetcher.py
# ├── ui.py
# └── main.py



# state.py
import streamlit as st
import pandas as pd

def initialize_session_state():
    """Initialize the session state variables for the app"""
    defaults = {
        'ticker': "",
        'avg_polarity': 0.0,
        'avg_subjectivity': 0.0,
        'overall_sentiment': "Neutral",
        'news_df': pd.DataFrame(),
        'combined_sentiment': None,
        'analysis_performed': False,
        'num_articles': 5,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# sidebar.py
import streamlit as st
import pandas as pd

def create_sidebar():
    """Create the sidebar with settings and controls"""
    st.sidebar.header("Settings")
    st.sidebar.slider(
        "Number of news articles to analyze",
        min_value=1,
        max_value=10,
        value=st.session_state.num_articles,
        key="num_articles"
    )
    if st.sidebar.button("Clear Saved Results"):
        st.session_state.analysis_performed = False
        st.session_state.ticker = ""
        st.session_state.news_df = pd.DataFrame()
        st.session_state.combined_sentiment = None
        st.experimental_rerun()

# sentiment.py
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

# scraper.py
import requests
from bs4 import BeautifulSoup
import re
import streamlit as st

def extract_article_text(url: str) -> str:
    """Extract main text content from a news article URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return ""
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup(['script', 'style', 'header', 'footer', 'nav']):
            tag.extract()
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text().strip() for p in paragraphs])
        text = re.sub(r'\s+', ' ', text).strip()
        text = text.replace(
            "Oops, something went wrong Unlock stock picks and a broker-level newsfeed that powers Wall", ""
        )
        return text
    except Exception as e:
        st.warning(f"Could not extract text from {url}: {e}")
        return ""

# data_fetcher.py
import time
import pandas as pd
import yfinance as yf
import streamlit as st
from scraper import extract_article_text
from sentiment import analyze_sentiment, calculate_combined_sentiment

def get_stock_news(ticker_symbol: str, num_articles: int = 5) -> list:
    """Fetch recent news articles for a given stock ticker."""
    try:
        news = yf.Search(ticker_symbol, news_count=num_articles).news
        return news[:num_articles] if news else []
    except Exception as e:
        st.error(f"Error fetching news for {ticker_symbol}: {e}")
        return []


def process_article(article: dict, index: int, total: int, status_text) -> dict:
    """Process a single news article to extract and analyze sentiment."""
    status_text.text(f"Processing article {index+1}/{total}...")
    title = article.get('title', '')
    summary = article.get('summary', '')
    url = article.get('link', '')
    headline = f"{title} {summary}"
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
        'published': article.get('providerPublishTime', 'Unknown'),
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

# ui.py
import streamlit as st
from datetime import datetime

def display_combined_sentiment(combined):
    """Display combined sentiment metrics."""
    if not combined:
        return
    st.subheader("Combined Sentiment Analysis")
    st.write("Combines all article texts for holistic sentiment.")
    cols = st.columns(3)
    cols[0].metric("Combined Sentiment", f"{combined['sentiment']} {combined['emoji']}")
    cols[1].metric("Combined Polarity", f"{combined['polarity']:.2f}")
    cols[2].metric("Combined Subjectivity", f"{combined['subjectivity']:.2f}")

def display_article_details(row):
    """Display details for an individual article."""
    pub = row['published']
    if isinstance(pub, int):
        pub = datetime.fromtimestamp(pub).strftime('%Y-%m-%d %H:%M:%S')
    st.write(f"**Publisher:** {row['publisher']} - {pub}")
    st.write("### Sentiment Analysis")
    st.write(f"**Sentiment:** {row['full_text_sentiment']} {row['full_text_emoji']}")
    st.write(f"**Polarity:** {row['full_text_polarity']:.2f}")
    st.write(f"**Subjectivity:** {row['full_text_subjectivity']:.2f}")
    st.write("### Article Preview")
    st.write(row['article_text'])
    st.write(f"**Full Article:** [{row['title']}]({row['link']})")

def display_news_articles(ticker, df):
    """Display news articles in expanders."""
    st.subheader(f"Recent News Articles for {ticker}")
    for _, row in df.iterrows():
        with st.expander(f"{row['title']} {row['full_text_emoji']}"):
            display_article_details(row)

def perform_stock_news_analysis(ticker):
    """Run sentiment analysis and display results."""
    from data_fetcher import analyze_stock_news_sentiment
    state = st.session_state
    if not ticker:
        st.warning("Please enter a ticker.")
        return
    if state.ticker == ticker and state.analysis_performed:
        avg_pol, avg_subj, overall, df, combined = (
            state.avg_polarity, state.avg_subjectivity,
            state.overall_sentiment, state.news_df, state.combined_sentiment
        )
    else:
        with st.spinner(f"Analyzing {ticker} news..."):
            avg_pol, avg_subj, overall, df, combined = analyze_stock_news_sentiment(
                ticker, state.num_articles
            )
        state.ticker = ticker
        state.avg_polarity = avg_pol
        state.avg_subjectivity = avg_subj
        state.overall_sentiment = overall
        state.news_df = df
        state.combined_sentiment = combined
        state.analysis_performed = True

    if df.empty:
        st.warning("No news found.")
        return
    display_combined_sentiment(combined)
    display_news_articles(ticker, df)

# main.py
import streamlit as st
from config import setup_page
from state import initialize_session_state
from sidebar import create_sidebar
from ui import perform_stock_news_analysis

def main():
    """Main function to run the Streamlit app."""
    setup_page()
    initialize_session_state()

    st.title("📈 Stock News Sentiment Analyzer")
    st.write("Enter a stock ticker to get sentiment analysis based on recent news.")
    st.markdown("---")

    create_sidebar()

    st.header("Analyze Stock News Sentiment")
    ticker = st.text_input(
        "Enter Stock Ticker Symbol:",
        value=st.session_state.ticker,
        placeholder="e.g., AAPL, MSFT, GOOGL",
        help="Enter the ticker symbol for the stock you want to analyze"
    ).upper()
    if ticker:
        st.session_state.ticker = ticker

    if st.button("Analyze Stock News 📰"):
        perform_stock_news_analysis(ticker)
    elif st.session_state.analysis_performed:
        perform_stock_news_analysis(st.session_state.ticker)

if __name__ == "__main__":
    main()
