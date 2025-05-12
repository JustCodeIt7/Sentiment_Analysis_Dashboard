# Step 1: Import necessary libraries
# ----------------------------------
import streamlit as st
import pandas as pd
import yfinance as yf
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime

# --- Constants ---
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# ==============================================================================
# Step 2: Core Analysis Logic
# ==============================================================================

def analyze_sentiment(text):
    """
    Analyzes the sentiment of a given text using TextBlob.

    Args:
        text (str): The input text to analyze.

    Returns:
        tuple: Contains polarity (float), subjectivity (float),
               sentiment label (str), and sentiment emoji (str).
    """
    if not isinstance(text, str):
        text = str(text) # Ensure text is a string

    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # Score from -1 (negative) to 1 (positive)
    subjectivity = blob.sentiment.subjectivity  # Score from 0 (objective) to 1 (subjective)

    # Classify sentiment based on polarity score
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

# ==============================================================================
# Step 3: Web Scraping Logic (Can be explained as an advanced/optional step)
# ==============================================================================

def extract_article_text(url):
    """
    Attempts to extract the main text content from a news article URL.
    Uses requests and BeautifulSoup for web scraping.

    NOTE: Web scraping can be unreliable due to website structure changes
          or anti-scraping measures.

    Args:
        url (str): The URL of the news article.

    Returns:
        str: The extracted article text, or an empty string if extraction fails.
    """
    if not url:
        return ""
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove elements that typically don't contain main content
        for element in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
            element.extract()

        # Find all paragraph tags, assuming they contain the main content
        paragraphs = soup.find_all('p')
        article_text = ' '.join([p.get_text().strip() for p in paragraphs])

        # Basic cleaning: remove excessive whitespace
        article_text = re.sub(r'\s+', ' ', article_text).strip()

        # Specific cleaning (example for a known issue)
        article_text = article_text.replace(
            "Oops, something went wrong Unlock stock picks and a broker-level newsfeed that powers Wall", "")

        return article_text

    except requests.exceptions.RequestException as e:
        # Handle network/HTTP errors
        st.warning(f"Could not fetch URL {url}. Error: {e}")
        return ""
    except Exception as e:
        # Handle other potential errors during parsing
        st.warning(f"Could not extract text from {url}. Error: {e}")
        return ""

# ==============================================================================
# Step 4: Data Fetching and Processing Functions
# ==============================================================================

def get_stock_news(ticker_symbol, num_articles=5):
    """
    Fetches recent news articles for a given stock ticker using yfinance.

    Args:
        ticker_symbol (str): The stock ticker (e.g., 'AAPL').
        num_articles (int): The maximum number of articles to retrieve.

    Returns:
        list: A list of news article dictionaries, or an empty list on error.
              Each dictionary contains keys like 'title', 'link', 'publisher', etc.
    """
    try:
        # Use yfinance Ticker object to get news
        stock = yf.Ticker(ticker_symbol)
        news = stock.news
        # Sometimes yfinance returns dicts with UUIDs as keys, sometimes lists. Handle both.
        if isinstance(news, dict):
            news_list = list(news.values())
        elif isinstance(news, list):
            news_list = news
        else:
            news_list = []

        # Ensure keys like 'link' are present, default to empty string if not
        processed_news = []
        for article in news_list:
             if isinstance(article, dict): # Ensure it's a dictionary
                processed_article = {
                    'title': article.get('title', 'No Title'),
                    'link': article.get('link', ''),
                    'publisher': article.get('publisher', 'Unknown'),
                    'providerPublishTime': article.get('providerPublishTime', None),
                    'summary': article.get('summary', '') # Add summary if available
                }
                processed_news.append(processed_article)

        if processed_news:
             # Sort by publish time if available (most recent first)
            processed_news.sort(key=lambda x: x.get('providerPublishTime', 0), reverse=True)
            return processed_news[:num_articles]
        else:
            st.warning(f"No news found for {ticker_symbol} via yfinance.")
            return []

    except Exception as e:
        st.error(f"Error fetching news for {ticker_symbol}: {e}")
        return []


def process_single_article(article, index, total_articles, status_placeholder):
    """
    Processes a single news article: extracts text and analyzes sentiment.

    Args:
        article (dict): Dictionary containing article info ('title', 'link', etc.).
        index (int): Current article index (for progress reporting).
        total_articles (int): Total number of articles being processed.
        status_placeholder (st.empty): Streamlit element to display status updates.

    Returns:
        dict: A dictionary containing processed data including sentiment scores.
    """
    status_placeholder.text(f"Processing article {index + 1}/{total_articles}: {article.get('title', 'No Title')[:50]}...")

    article_url = article.get('link', '')
    title = article.get('title', 'No Title')
    summary = article.get('summary', '') # Get summary if available

    # --- Headline Sentiment ---
    # Analyze sentiment based on title and summary (if available)
    headline_text = f"{title}. {summary}" if summary else title
    headline_polarity, headline_subjectivity, headline_sentiment, headline_emoji = analyze_sentiment(headline_text)

    # --- Full Article Sentiment (Attempt) ---
    article_full_text = ""
    full_text_polarity = headline_polarity # Default to headline sentiment
    full_text_subjectivity = headline_subjectivity
    full_text_sentiment = headline_sentiment
    full_text_emoji = headline_emoji

    if article_url:
        # Show we are trying to scrape
        status_placeholder.text(f"Extracting text from article {index + 1} ({article_url[:50]}...).")
        article_full_text = extract_article_text(article_url)
        time.sleep(0.3) # Small delay to be polite to servers

        if article_full_text:
            # If full text was extracted, analyze its sentiment
            (full_text_polarity, full_text_subjectivity,
             full_text_sentiment, full_text_emoji) = analyze_sentiment(article_full_text)
        else:
            # If scraping failed, explicitly note it
            article_full_text = "Could not extract full article text."
            # Keep headline sentiment as the fallback

    # Format publish time
    publish_time = article.get('providerPublishTime')
    if isinstance(publish_time, (int, float)):
         try:
             publish_time_str = datetime.fromtimestamp(publish_time).strftime('%Y-%m-%d %H:%M')
         except Exception:
             publish_time_str = "Invalid Date"
    elif isinstance(publish_time, str): # Handle if it's already a string
        publish_time_str = publish_time
    else:
        publish_time_str = "Unknown Time"


    # Return a structured dictionary for this article
    return {
        'title': title,
        'publisher': article.get('publisher', 'Unknown'),
        'link': article_url,
        'published': publish_time_str,
        'headline_polarity': headline_polarity,
        'headline_subjectivity': headline_subjectivity,
        'headline_sentiment': f"{headline_sentiment} {headline_emoji}",
        'full_text_polarity': full_text_polarity,
        'full_text_subjectivity': full_text_subjectivity,
        'full_text_sentiment': f"{full_text_sentiment} {full_text_emoji}",
        'article_preview': article_full_text[:300] + "..." if len(article_full_text) > 300 else article_full_text,
        'raw_text': article_full_text # Keep raw text for combined analysis later
    }


def calculate_overall_and_combined_sentiment(results_df):
    """
    Calculates average sentiment scores and combined sentiment from a DataFrame.

    Args:
        results_df (pd.DataFrame): DataFrame containing analysis results for multiple articles.

    Returns:
        tuple: (avg_polarity, avg_subjectivity, overall_sentiment_label, combined_sentiment_dict)
               Returns defaults if DataFrame is empty.
               combined_sentiment_dict contains 'polarity', 'subjectivity', 'sentiment', 'emoji'.
    """
    if results_df.empty:
        return 0.0, 0.0, "Neutral 😐", None

    # --- Average Sentiment (based on full text analysis) ---
    avg_polarity = results_df['full_text_polarity'].mean()
    avg_subjectivity = results_df['full_text_subjectivity'].mean()

    # Determine overall sentiment label based on average polarity
    if avg_polarity > 0.1:
        overall_sentiment_label = "Positive 😊"
    elif avg_polarity < -0.1:
        overall_sentiment_label = "Negative 😠"
    else:
        overall_sentiment_label = "Neutral 😐"

    # --- Combined Sentiment (analyze all text together) ---
    # Concatenate all *successfully extracted* raw texts
    valid_texts = results_df[results_df['raw_text'] != "Could not extract full article text."]['raw_text']
    combined_text = " ".join(valid_texts)

    combined_sentiment_dict = None
    if combined_text:
        (comb_pol, comb_subj, comb_label, comb_emoji) = analyze_sentiment(combined_text)
        combined_sentiment_dict = {
            'polarity': comb_pol,
            'subjectivity': comb_subj,
            'sentiment': comb_label,
            'emoji': comb_emoji
        }

    return avg_polarity, avg_subjectivity, overall_sentiment_label, combined_sentiment_dict

# ==============================================================================
# Step 5: Streamlit UI Setup and Configuration
# ==============================================================================

def setup_page():
    """Configures the Streamlit page settings."""
    st.set_page_config(
        page_title="Stock Sentiment Analyzer",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def create_main_interface():
    """Creates the main title and description."""
    st.title("📈 Stock News Sentiment Analyzer")
    st.write(
        "Enter a stock ticker to fetch recent news and analyze sentiment."
    )
    st.markdown("---")

def create_sidebar():
    """Creates the sidebar with options and info."""
    st.sidebar.header("⚙️ Settings")

    # Slider to control the number of articles
    st.sidebar.slider(
        "Number of news articles to analyze:",
        min_value=1,
        max_value=15, # Increased max slightly
        value=st.session_state.get('num_articles', 5), # Use get for default
        step=1,
        key="num_articles", # Key links slider to session state
        help="Select how many recent news articles to fetch and analyze."
    )

    st.sidebar.markdown("---")
    st.sidebar.header("ℹ️ About")
    st.sidebar.info(
        "This app fetches news using `yfinance`, attempts to scrape article text, "
        "and analyzes sentiment using `TextBlob`. "
        "Web scraping may not always succeed."
    )

    # Button to clear results and reset
    if st.sidebar.button("Clear Results & Reset"):
        # Reset relevant session state keys
        keys_to_reset = ['ticker', 'avg_polarity', 'avg_subjectivity',
                         'overall_sentiment', 'news_df', 'combined_sentiment',
                         'analysis_performed']
        for key in keys_to_reset:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun() # Rerun the script to reflect the cleared state

def initialize_session_state():
    """Initializes session state variables if they don't exist."""
    # Stores the currently entered ticker
    if 'ticker' not in st.session_state:
        st.session_state.ticker = ""
    # Stores the calculated average polarity
    if 'avg_polarity' not in st.session_state:
        st.session_state.avg_polarity = 0.0
    # Stores the calculated average subjectivity
    if 'avg_subjectivity' not in st.session_state:
        st.session_state.avg_subjectivity = 0.0
    # Stores the overall sentiment label (e.g., "Positive 😊")
    if 'overall_sentiment' not in st.session_state:
        st.session_state.overall_sentiment = "Neutral 😐"
    # Stores the DataFrame of processed news articles
    if 'news_df' not in st.session_state:
        st.session_state.news_df = pd.DataFrame()
    # Stores the result of analyzing all article text combined
    if 'combined_sentiment' not in st.session_state:
        st.session_state.combined_sentiment = None
    # Flag to indicate if an analysis has been run and results are stored
    if 'analysis_performed' not in st.session_state:
        st.session_state.analysis_performed = False
    # Stores the number of articles selected by the user
    if 'num_articles' not in st.session_state:
        st.session_state.num_articles = 5 # Default value

# ==============================================================================
# Step 6: UI Functions for Displaying Results
# ==============================================================================

def display_summary_metrics(avg_polarity, avg_subjectivity, overall_sentiment):
    """Displays the overall sentiment summary metrics."""
    st.subheader("Overall Sentiment Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Sentiment", value=overall_sentiment)
    with col2:
        st.metric("Average Polarity", value=f"{avg_polarity:.3f}")
    with col3:
        st.metric("Average Subjectivity", value=f"{avg_subjectivity:.3f}")
    st.caption("Based on the average sentiment analysis of full article texts (or headlines if text extraction failed).")

def display_combined_sentiment(combined_sentiment_data):
    """Displays the combined sentiment analysis results."""
    if not combined_sentiment_data:
        st.info("Combined sentiment analysis could not be performed (no article text extracted).")
        return

    st.subheader("Combined Text Sentiment Analysis")
    st.write("Analyzes the sentiment of *all successfully extracted article texts* concatenated together.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Combined Sentiment",
            value=f"{combined_sentiment_data['sentiment']} {combined_sentiment_data['emoji']}"
        )
    with col2:
        st.metric(label="Combined Polarity", value=f"{combined_sentiment_data['polarity']:.3f}")
    with col3:
        st.metric(label="Combined Subjectivity", value=f"{combined_sentiment_data['subjectivity']:.3f}")

def display_article_details(article_row):
    """Displays the details for a single article within an expander."""
    st.write(f"**Publisher:** {article_row['publisher']}")
    st.write(f"**Published:** {article_row['published']}")
    st.write(f"**Link:** [Read Full Article]({article_row['link']})", unsafe_allow_html=True)

    st.markdown("---")
    st.write("#### Sentiment Analysis (Full Text / Headline)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sentiment", article_row['full_text_sentiment'])
    with col2:
        st.metric("Polarity", f"{article_row['full_text_polarity']:.3f}")
    with col3:
        st.metric("Subjectivity", f"{article_row['full_text_subjectivity']:.3f}")

    if article_row['raw_text'] == "Could not extract full article text.":
         st.caption("Full text could not be extracted; sentiment based on headline/summary.")
         # Optionally show headline sentiment too for comparison
         st.write(f"_(Headline Sentiment:_ {article_row['headline_sentiment']})")


    st.markdown("---")
    st.write("#### Article Preview / Status")
    # Use markdown for better formatting, escape potential markdown chars in text
    st.markdown(f"> {article_row['article_preview'].replace('`', '\\`').replace('*', '\\*')}")


def display_news_results_section(ticker, news_df):
    """Displays the detailed news article results section."""
    if news_df.empty:
        st.warning(f"No news data available to display for {ticker}.")
        return

    st.subheader(f"Analysis of Recent News Articles for {ticker}")
    st.write(f"Showing {len(news_df)} articles.")

    # Display each article in an expander
    for index, row in news_df.iterrows():
        expander_label = f"{row['title']} ({row['full_text_sentiment']})"
        with st.expander(expander_label):
            display_article_details(row)

# ==============================================================================
# Step 7: Main Application Flow and Logic
# ==============================================================================

def run_analysis(ticker_symbol):
    """
    Orchestrates the fetching, processing, and analysis of news for the ticker.
    Updates session state with the results.
    """
    if not ticker_symbol:
        st.warning("⚠️ Please enter a stock ticker symbol.")
        return

    st.session_state.analysis_performed = False # Reset flag before starting
    st.session_state.news_df = pd.DataFrame() # Clear previous results
    num_articles_to_fetch = st.session_state.num_articles # Get from slider

    # Placeholders for progress updates
    progress_bar = st.progress(0)
    status_placeholder = st.empty()

    with st.spinner(f"Analyzing news for {ticker_symbol}..."):
        # 1. Fetch News
        status_placeholder.text("Fetching news links...")
        news_list = get_stock_news(ticker_symbol, num_articles_to_fetch)
        if not news_list:
            st.error(f"Could not fetch news for {ticker_symbol}. Check the ticker or try again later.")
            progress_bar.empty()
            status_placeholder.empty()
            return # Stop analysis if no news

        # 2. Process Each Article (Scraping + Sentiment)
        processed_results = []
        total_articles = len(news_list)
        for i, article in enumerate(news_list):
             result = process_single_article(article, i, total_articles, status_placeholder)
             processed_results.append(result)
             progress_bar.progress((i + 1) / total_articles) # Update progress

        # Clear progress indicators
        progress_bar.empty()
        status_placeholder.empty()

        # 3. Convert results to DataFrame and Calculate Overall/Combined Sentiment
        if processed_results:
            news_df = pd.DataFrame(processed_results)
             # Remove the raw_text column after calculations if you don't need it later
             # raw_texts = news_df['raw_text'].copy() # Keep if needed elsewhere
            (avg_pol, avg_subj, overall_sent, combined_data) = calculate_overall_and_combined_sentiment(news_df)

             # Drop raw text before saving to session state to save memory
            news_df_to_store = news_df.drop(columns=['raw_text'])
        else:
            news_df_to_store = pd.DataFrame()
            avg_pol, avg_subj, overall_sent, combined_data = 0.0, 0.0, "Neutral 😐", None


        # 4. Store results in Session State
        st.session_state.ticker = ticker_symbol # Store the ticker that was analyzed
        st.session_state.avg_polarity = avg_pol
        st.session_state.avg_subjectivity = avg_subj
        st.session_state.overall_sentiment = overall_sent
        st.session_state.news_df = news_df_to_store # Store DF without raw text
        st.session_state.combined_sentiment = combined_data
        st.session_state.analysis_performed = True # Mark analysis as done

    st.success(f"Analysis complete for {ticker_symbol}!")


# ==============================================================================
# Step 8: Main Function to Run the App
# ==============================================================================

def main():
    """Main function to set up and run the Streamlit application."""

    # --- Initial Setup ---
    setup_page()
    initialize_session_state() # Ensure session state exists before accessing
    create_sidebar()
    create_main_interface()

    # --- User Input Area ---
    st.header("📰 Analyze Stock News Sentiment")
    # Use session state to remember the last ticker entered
    ticker_input = st.text_input(
        "Enter Stock Ticker Symbol:",
        value=st.session_state.ticker,
        placeholder="e.g., AAPL, MSFT, GOOGL",
        help="Enter the ticker symbol and click 'Analyze'."
    ).upper().strip() # Convert to uppercase and remove whitespace

    # Update session state if input changes (important for remembering across reruns)
    if ticker_input != st.session_state.ticker:
         st.session_state.ticker = ticker_input
         # Optionally clear previous results when ticker changes
         st.session_state.analysis_performed = False
         st.session_state.news_df = pd.DataFrame()


    # --- Analysis Trigger ---
    analyze_button = st.button(f"Analyze News for {st.session_state.ticker}" if st.session_state.ticker else "Analyze News")

    if analyze_button:
        # Run the full analysis process when the button is clicked
        run_analysis(st.session_state.ticker)

    # --- Display Results Area ---
    # This section displays results if analysis has been performed (either just now or previously)
    if st.session_state.analysis_performed and not st.session_state.news_df.empty:
        st.markdown("---")
        st.header(f"Results for {st.session_state.ticker}")

        # Display Summary Metrics
        display_summary_metrics(
            st.session_state.avg_polarity,
            st.session_state.avg_subjectivity,
            st.session_state.overall_sentiment
        )

        st.markdown("---")
        # Display Combined Sentiment
        display_combined_sentiment(st.session_state.combined_sentiment)

        st.markdown("---")
        # Display Detailed Article Breakdown
        display_news_results_section(
            st.session_state.ticker,
            st.session_state.news_df
        )
    elif st.session_state.analysis_performed and st.session_state.news_df.empty:
        # Handle case where analysis ran but found no articles to show
        st.warning(f"Analysis was performed for {st.session_state.ticker}, but no processable news articles were found.")


# --- Entry Point ---
if __name__ == "__main__":
    main()