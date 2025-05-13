"""
Data Collection and Processing
-----------------------------
Functions for fetching and analyzing stock news data.
"""

import time

import pandas as pd
import streamlit as st
import yfinance as yf
from scraper import extract_article_text
from sentiment import analyze_sentiment, calculate_combined_sentiment

def get_stock_news(ticker_symbol, num_articles=5):
    """
        Fetch recent news articles for a given stock ticker

        Parameters:
            ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL')
            num_articles (int): Number of articles to retrieve

        Returns:
            list: List of news dictionaries with 'title', 'link', and 'publisher'
    """
    try:
        # Get news using yf.Search
        news = yf.Search(ticker_symbol, news_count=num_articles).news
        print(news)  # Debugging line to check the news data

        # Limit to specified number of articles
        if news and len(news) > 0:
            return news[:num_articles]
        else:
            return []
    except Exception as e:
        st.error(f"Error fetching news for {ticker_symbol}: {e}")
        return []



def process_article(article, index, total_articles, status_text):
    """
        Process a single news article to extract and analyze its content

        Parameters:
            article (dict): The article to process
            index (int): The index of the article in the list
            total_articles (int): Total number of articles
            status_text (streamlit.delta_generator.DeltaGenerator): For status updates

        Returns:
            dict: Dictionary with article data and sentiment analysis
    """
    status_text.text(f"Processing article {index + 1} of {total_articles}...")

    # Get article URL and basic info
    article_url = article.get('link', '')
    title = article.get('title', '')
    summary = article.get('summary', '')

    # For headline sentiment
    headline_text = f"{title} {summary}"
    headline_polarity, headline_subjectivity, headline_sentiment, headline_emoji = analyze_sentiment(headline_text)

    # Get article full text if URL is available
    article_full_text = ""
    if article_url:
        status_text.text(f"Extracting text from article {index + 1}...")
        article_full_text = extract_article_text(article_url)
        time.sleep(0.5)  # Small delay to avoid overloading servers

    # For full article sentiment (if available)
    if article_full_text:
        full_text_polarity, full_text_subjectivity, full_text_sentiment, full_text_emoji = analyze_sentiment(
            article_full_text)
    else:
        # Use headline sentiment if full text is not available
        full_text_polarity, full_text_subjectivity, full_text_sentiment, full_text_emoji = headline_polarity, headline_subjectivity, headline_sentiment, headline_emoji
        article_full_text = "Could not extract full article text"

    # Create result dictionary
    return {
        'title': title,
        'publisher': article.get('publisher', 'Unknown'),
        'link': article_url,
        'headline_polarity': headline_polarity,
        'headline_subjectivity': headline_subjectivity,
        'headline_sentiment': headline_sentiment,
        'headline_emoji': headline_emoji,
        'full_text_polarity': full_text_polarity,
        'full_text_subjectivity': full_text_subjectivity,
        'full_text_sentiment': full_text_sentiment,
        'full_text_emoji': full_text_emoji,
        'article_text': article_full_text[:500] + "..." if len(article_full_text) > 500 else article_full_text,
        'published': article.get('providerPublishTime', 'Unknown'),
        'raw_text': article_full_text  # Store full text for combined analysis
    }



def analyze_stock_news_sentiment(ticker_symbol, num_articles=5):
    """
        Analyze sentiment of news articles for a stock

        Parameters:
            ticker_symbol (str): The stock ticker symbol
            num_articles (int): Number of articles to analyze

        Returns:
            tuple: (avg_polarity, avg_subjectivity, overall_sentiment, news_df, combined_sentiment)
    """
    news_articles = get_stock_news(ticker_symbol, num_articles)

    if not news_articles:
        return 0.0, 0.0, "Neutral", pd.DataFrame(), None

    # Set up a progress bar for article scraping
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Process each article
    results = []
    all_article_texts = []

    for i, article in enumerate(news_articles):
        article_data = process_article(article, i, len(news_articles), status_text)
        results.append(article_data)

        # Add full text to collection for combined analysis
        if article_data['raw_text']:
            all_article_texts.append(article_data['raw_text'])

        # Update progress bar
        progress_bar.progress((i + 1) / len(news_articles))

    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()

    # Convert to DataFrame and remove raw text column (not needed for display)
    for result in results:
        if 'raw_text' in result:
            del result['raw_text']
    news_df = pd.DataFrame(results)

    # Calculate aggregate sentiment metrics
    if not news_df.empty:
        avg_polarity = news_df['full_text_polarity'].mean()
        avg_subjectivity = news_df['full_text_subjectivity'].mean()

        # Determine overall sentiment based on full text analysis
        if avg_polarity > 0.1:
            overall_sentiment = "Positive"
        elif avg_polarity < -0.1:
            overall_sentiment = "Negative"
        else:
            overall_sentiment = "Neutral"
    else:
        avg_polarity = 0.0
        avg_subjectivity = 0.0
        overall_sentiment = "Neutral"

    # Perform combined sentiment analysis on all articles together
    combined_sentiment = calculate_combined_sentiment(all_article_texts)

    return avg_polarity, avg_subjectivity, overall_sentiment, news_df, combined_sentiment


def perform_stock_news_analysis(ticker):
    """
        Perform sentiment analysis on stock news and save results to session state

        Parameters:
            ticker (str): The stock ticker symbol to analyze

        Returns:
            tuple or None: Analysis results or None if analysis couldn't be performed
    """
    if not ticker:
        st.warning("⚠️ Please enter a stock ticker above before analyzing.")
        return None

    # Check if we already have results for this ticker
    if st.session_state.ticker == ticker and st.session_state.analysis_performed:
        # Use the saved results
        return (
            st.session_state.avg_polarity,
            st.session_state.avg_subjectivity,
            st.session_state.overall_sentiment,
            st.session_state.news_df,
            st.session_state.combined_sentiment
        )
    else:
        # Show analysis in progress
        with st.spinner(f'Fetching and analyzing recent news for {ticker}...'):
            # Get number of articles to analyze
            num_articles = st.session_state.get('num_articles', 3)

            # Perform the analysis
            avg_polarity, avg_subjectivity, overall_sentiment, news_df, combined_sentiment = analyze_stock_news_sentiment(
                ticker, num_articles)

            # Save results to session state
            st.session_state.ticker = ticker
            st.session_state.avg_polarity = avg_polarity
            st.session_state.avg_subjectivity = avg_subjectivity
            st.session_state.overall_sentiment = overall_sentiment
            st.session_state.news_df = news_df
            st.session_state.combined_sentiment = combined_sentiment
            st.session_state.analysis_performed = True

            # Check if we got any news
            if news_df.empty:
                st.warning(f"No news articles found for {ticker}. Please check the ticker symbol and try again.")
                return None

            return avg_polarity, avg_subjectivity, overall_sentiment, news_df, combined_sentiment
