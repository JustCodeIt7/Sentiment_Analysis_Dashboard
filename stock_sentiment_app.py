from datetime import datetime

import streamlit as st
from textblob import TextBlob
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re


# -------------- App Config --------------
def setup_page():
    """Configure the Streamlit page layout and appearance"""
    st.set_page_config(
        page_title="Stock Sentiment Analysis",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def create_main_section():
    """Create the main app title and description"""
    st.title("📈 Stock News Sentiment Analyzer")
    st.write(
        "Enter a stock ticker to get sentiment analysis based on recent news."
    )
    st.markdown("---")


def initialize_session_state():
    """Initialize the session state variables if they don't exist"""



def create_sidebar():
    """Create the sidebar with information about the app"""
# -------------- UTILITY FUNCTIONS --------------

def analyze_sentiment(text):
    """
    Analyze text sentiment using TextBlob.

    Parameters:
        text (str): The text to analyze

    Returns:
        tuple: (polarity, subjectivity, sentiment_label, emoji)
    """
    


def extract_article_text(url):
    """
    Extract the main text content from a news article URL

    Parameters:
        url (str): The URL of the news article

    Returns:
        str: The extracted article text or empty string if extraction fails
    """





# -------------- DATA FUNCTIONS --------------

def get_stock_news(ticker_symbol, num_articles=5):
    """
    Fetch recent news articles for a given stock ticker

    Parameters:
        ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL')
        num_articles (int): Number of articles to retrieve

    Returns:
        list: List of news dictionaries with 'title', 'link', and 'publisher'
    """

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

def analyze_stock_news_sentiment(ticker_symbol, num_articles=5):
    """
    Analyze sentiment of news articles for a stock

    Parameters:
        ticker_symbol (str): The stock ticker symbol
        num_articles (int): Number of articles to analyze

    Returns:
        tuple: (avg_polarity, avg_subjectivity, overall_sentiment, news_df, combined_sentiment)
    """

def calculate_combined_sentiment(article_texts):
    """
    Calculate sentiment from all article texts combined

    Parameters:
        article_texts (list): List of article text strings

    Returns:
        dict or None: Combined sentiment metrics or None if no texts available
    """



# -------------- UI FUNCTIONS --------------

def display_combined_sentiment(combined_sentiment):
    """
    Display the combined sentiment analysis results

    Parameters:
        combined_sentiment (dict): The combined sentiment data to display
    """



def display_article_details(row):
    """
    Display details for a single news article

    Parameters:
        row (pandas.Series): A row from the news DataFrame
    """
    pub_time = row['published']
    if isinstance(pub_time, int):
        pub_time = datetime.fromtimestamp(pub_time).strftime('%Y-%m-%d %H:%M:%S')

    st.write(f"**Publisher:** {row['publisher']} - {pub_time}")

    # Article sentiment information section
    st.write("### Sentiment Analysis")

    st.write(f"**Sentiment:** {row['full_text_sentiment']} {row['full_text_emoji']}")
    st.write(f"**Polarity:** {row['full_text_polarity']:.2f}")
    st.write(f"**Subjectivity:** {row['full_text_subjectivity']:.2f}")

    # Article text preview and link
    st.write("### Article Preview")
    st.write(row['article_text'])
    st.write(f"**Full Article:** [{row['title']}]({row['link']})")


def display_news_articles(ticker, news_df):
    """
    Display the news articles with their sentiment analysis

    Parameters:
        ticker (str): The stock ticker symbol
        news_df (pandas.DataFrame): DataFrame with news articles data
    """
    st.subheader(f"Recent News Articles for {ticker}")

    for i, row in news_df.iterrows():
        with st.expander(f"{row['title']} {row['full_text_emoji']}"):
            display_article_details(row)


def perform_stock_news_analysis(ticker):
    """
    Perform sentiment analysis on stock news and display results

    Parameters:
        ticker (str): The stock ticker symbol to analyze
    """
    if not ticker:
        st.warning("⚠️ Please enter a stock ticker above before analyzing.")
        return

    # Check if we already have results for this ticker
    if st.session_state.ticker == ticker and st.session_state.analysis_performed:
        # Use the saved results
        avg_polarity = st.session_state.avg_polarity
        avg_subjectivity = st.session_state.avg_subjectivity
        overall_sentiment = st.session_state.overall_sentiment
        news_df = st.session_state.news_df
        combined_sentiment = st.session_state.combined_sentiment
    else:
        # Show analysis in progress
        with st.spinner(f'Fetching and analyzing recent news for {ticker}...'):
            # Get number of articles to analyze
            num_articles = st.session_state.get('num_articles', 5)

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
        return

    # Display combined sentiment analysis if available
    display_combined_sentiment(combined_sentiment)

    # Display news articles with their sentiment
    display_news_articles(ticker, news_df)


# -------------- MAIN FUNCTION --------------

def main():
    """Main function to run the Streamlit app"""
    setup_page()

    # Initialize session state
    initialize_session_state()

    # Create the main section with title/description
    create_main_section()

    create_sidebar()

    # Stock analysis is now the main content
    st.header("Analyze Stock News Sentiment")

    # Input for stock ticker
    ticker = st.text_input(
        "Enter Stock Ticker Symbol:",
        value=st.session_state.get('ticker', ''),
        placeholder="e.g., AAPL, MSFT, GOOGL",
        help="Enter the ticker symbol for the stock you want to analyze"
    ).upper()

    # Update ticker in session state when it changes
    if ticker:
        st.session_state.ticker = ticker

    # Button to trigger analysis with 2 columns
    col1, col2 = st.columns(2)
    
    with col1:
        analyze_button = st.button("Analyze Stock News 📰")
    
    with col2:
        reset_button = st.button("Reset", key="reset_button")
        if reset_button:
            st.session_state.ticker = ""
            st.session_state.analysis_performed = False
            st.experimental_rerun()

    # Perform analysis when button is pressed or if we have saved results
    if analyze_button:
        perform_stock_news_analysis(ticker)
    elif st.session_state.analysis_performed and st.session_state.ticker:
        # Display saved results
        perform_stock_news_analysis(st.session_state.ticker)


# Run the app
if __name__ == "__main__":
    main()
