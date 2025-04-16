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
    if 'ticker' not in st.session_state:
        st.session_state.ticker = ""
    if 'avg_polarity' not in st.session_state:
        st.session_state.avg_polarity = 0.0
    if 'avg_subjectivity' not in st.session_state:
        st.session_state.avg_subjectivity = 0.0
    if 'overall_sentiment' not in st.session_state:
        st.session_state.overall_sentiment = "Neutral"
    if 'news_df' not in st.session_state:
        st.session_state.news_df = pd.DataFrame()
    if 'combined_sentiment' not in st.session_state:
        st.session_state.combined_sentiment = None
    if 'analysis_performed' not in st.session_state:
        st.session_state.analysis_performed = False
    if 'num_articles' not in st.session_state:
        st.session_state.num_articles = 5


def create_sidebar():
    """Create the sidebar with information about the app"""
    # Options section
    st.sidebar.header("Settings")

    # Number of articles to fetch for stock news analysis
    st.sidebar.slider(
        "Number of news articles to analyze",
        min_value=1,
        max_value=10,
        value=st.session_state.get('num_articles', 5),
        key="num_articles"
    )

    # Add a button to clear results
    if st.sidebar.button("Clear Saved Results"):
        st.session_state.analysis_performed = False
        st.session_state.ticker = ""
        st.session_state.news_df = pd.DataFrame()
        st.session_state.combined_sentiment = None
        st.rerun()


# -------------- UTILITY FUNCTIONS --------------

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


def extract_article_text(url):
    """
    Extract the main text content from a news article URL

    Parameters:
        url (str): The URL of the news article

    Returns:
        str: The extracted article text or empty string if extraction fails
    """
    try:
        # Add user agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Send request to get the webpage
        response = requests.get(url, headers=headers, timeout=10)

        # Check if request was successful
        if response.status_code != 200:
            return ""

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements that might contain irrelevant text
        for script_or_style in soup(['script', 'style', 'header', 'footer', 'nav']):
            script_or_style.extract()

        # Get all paragraphs which usually contain the main article text
        paragraphs = soup.find_all('p')

        # Join paragraphs to form the complete article text
        article_text = ' '.join([p.get_text().strip() for p in paragraphs])

        # Clean up the text (remove extra whitespace, etc.)
        article_text = re.sub(r'\s+', ' ', article_text).strip()

        # Remove the specific error string that appears in some articles
        article_text = article_text.replace(
            "Oops, something went wrong Unlock stock picks and a broker-level newsfeed that powers Wall", "")

        return article_text

    except Exception as e:
        st.warning(f"Could not extract text from {url}. Error: {str(e)}")
        return ""


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


# -------------- UI FUNCTIONS --------------

def display_combined_sentiment(combined_sentiment):
    """
    Display the combined sentiment analysis results

    Parameters:
        combined_sentiment (dict): The combined sentiment data to display
    """
    if not combined_sentiment:
        return

    st.subheader("Combined Sentiment Analysis")
    st.write("This analysis combines the text of all articles into a single body for sentiment analysis.")

    combined_cols = st.columns(3)
    with combined_cols[0]:
        st.metric(
            label="Combined Sentiment",
            value=f"{combined_sentiment['sentiment']} {combined_sentiment['emoji']}"
        )
    with combined_cols[1]:
        st.metric(
            label="Combined Polarity",
            value=f"{combined_sentiment['polarity']:.2f}"
        )
    with combined_cols[2]:
        st.metric(
            label="Combined Subjectivity",
            value=f"{combined_sentiment['subjectivity']:.2f}"
        )


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

    # Button to trigger analysis
    analyze_button = st.button("Analyze Stock News 📰")

    # Perform analysis when button is pressed or if we have saved results
    if analyze_button:
        perform_stock_news_analysis(ticker)
    elif st.session_state.analysis_performed and st.session_state.ticker:
        # Display saved results
        perform_stock_news_analysis(st.session_state.ticker)


# Run the app
if __name__ == "__main__":
    main()
