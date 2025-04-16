# -------------- SECTION 1: IMPORTS --------------
import streamlit as st
from textblob import TextBlob
import time  # For optional loading effects
import yfinance as yf  # For stock data and news
import pandas as pd
from datetime import datetime, timedelta


# -------------- SECTION 2: PAGE CONFIGURATION --------------
def setup_page():
    """Configure the Streamlit page layout and appearance"""
    st.set_page_config(
        page_title="Stock Sentiment Analysis",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
# -------------- SECTION 5: MAIN APP LAYOUT --------------
def create_main_section():
    """Create the main app title and description"""
    st.title("📈 Stock News Sentiment Analyzer")
    st.write(
        "Enter a stock ticker to get sentiment analysis based on recent news." # Updated description
    )
    st.markdown("---")


# -------------- SECTION 3: SENTIMENT ANALYSIS LOGIC --------------
# This function is still needed for stock news analysis
def analyze_sentiment(text):
    """
    Analyze text sentiment using TextBlob.

    Parameters:
        text (str): The text to analyze

    Returns:
        tuple: (polarity, subjectivity, sentiment_label, emoji)
    """
    # Handle empty input
    if not text:
        return 0.0, 0.0, "Neutral", "😐"

    # Process text with TextBlob
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


# -------------- SECTION 4: STOCK NEWS FUNCTIONS --------------
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


def analyze_stock_news_sentiment(ticker_symbol, num_articles=5):
    """
    Analyze sentiment of news articles for a stock

    Parameters:
        ticker_symbol (str): The stock ticker symbol
        num_articles (int): Number of articles to analyze

    Returns:
        tuple: (avg_polarity, avg_subjectivity, overall_sentiment, news_df)
    """
    news_articles = get_stock_news(ticker_symbol, num_articles)

    if not news_articles:
        return 0.0, 0.0, "Neutral", pd.DataFrame()

    # Create a dataframe to store results
    results = []

    # Analyze each article's title and description
    for article in news_articles:
        # Combine title and description for better sentiment analysis
        full_text = f"{article.get('title', '')} {article.get('summary', '')}"

        # Get sentiment using the shared analyze_sentiment function
        polarity, subjectivity, sentiment, emoji = analyze_sentiment(full_text)

        # Add to results
        results.append({
            'title': article.get('title', 'No title'),
            'publisher': article.get('publisher', 'Unknown'),
            'link': article.get('link', '#'),
            'polarity': polarity,
            'subjectivity': subjectivity,
            'sentiment': sentiment,
            'emoji': emoji,
            'published': article.get('providerPublishTime', 'Unknown')
        })

    # Convert to DataFrame
    news_df = pd.DataFrame(results)

    # Calculate averages
    if not news_df.empty:
        avg_polarity = news_df['polarity'].mean()
        avg_subjectivity = news_df['subjectivity'].mean()

        # Determine overall sentiment
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

    return avg_polarity, avg_subjectivity, overall_sentiment, news_df


# -------------- SECTION 7: ANALYSIS & RESULTS --------------
# Removed perform_text_analysis function as it's no longer needed

def perform_stock_news_analysis(ticker):
    """Perform sentiment analysis on stock news and display results"""
    if not ticker:
        st.warning("⚠️ Please enter a stock ticker above before analyzing.")
        return

    # Show analysis in progress
    with st.spinner(f'Fetching and analyzing recent news for {ticker}...'):
        # Get number of articles to analyze
        num_articles = st.session_state.get('num_articles', 5)

        # Perform the analysis
        avg_polarity, avg_subjectivity, overall_sentiment, news_df = analyze_stock_news_sentiment(ticker, num_articles)

    # Check if we got any news
    if news_df.empty:
        st.warning(f"No news articles found for {ticker}. Please check the ticker symbol and try again.")
        return

    # Display results

    # # Stock info section
    # try:
    #     stock = yf.Ticker(ticker)
    #     info = stock.get_info()  # Use the correct get_info() method

    #     # Create a header row for stock info
    #     st.subheader(f"Stock Information: {info.get('longName', ticker)} ({ticker})")

    #     # Display basic stock info in columns
    #     col1, col2, col3 = st.columns(3)

    #     with col1:
    #         # Current price with change
    #         current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
    #         previous_close = info.get('previousClose', 'N/A')

    #         if current_price != 'N/A' and previous_close != 'N/A':
    #             # Ensure both values are numeric for calculation
    #             if isinstance(current_price, (int, float)) and isinstance(previous_close, (int, float)):
    #                 price_change = current_price - previous_close
    #                 price_change_pct = (price_change / previous_close) * 100 if previous_close != 0 else 0

    #                 delta_color = "normal" # This shows positive changes in green, negative in red

    #                 st.metric(
    #                     label="Current Price",
    #                     value=f"${current_price:,.2f}",
    #                     delta=f"{price_change_pct:+.2f}%",
    #                     delta_color=delta_color
    #                 )
    #             else: # Handle case where one or both prices are not numeric
    #                  st.metric(label="Current Price", value=f"${current_price}" if isinstance(current_price, (int, float)) else current_price)

    #         else:
    #             st.metric(label="Current Price", value="N/A")

    #     with col2:
    #         # 52-Week Range
    #         low_52 = info.get('fiftyTwoWeekLow', 'N/A')
    #         high_52 = info.get('fiftyTwoWeekHigh', 'N/A')
    #         range_val = "N/A"
    #         if isinstance(low_52, (int, float)) and isinstance(high_52, (int, float)):
    #             range_val = f"${low_52:,.2f} - ${high_52:,.2f}"

    #         st.metric(
    #             label="52-Week Range",
    #             value=range_val
    #         )

    #     with col3:
    #         # Market Cap
    #         market_cap = info.get('marketCap', 'N/A')
    #         market_cap_str = "N/A"
    #         if isinstance(market_cap, (int, float)):
    #             if market_cap >= 1_000_000_000_000:
    #                 market_cap_str = f"${market_cap / 1_000_000_000_000:.2f}T"
    #             elif market_cap >= 1_000_000_000:
    #                 market_cap_str = f"${market_cap / 1_000_000_000:.2f}B"
    #             elif market_cap >= 1_000_000:
    #                 market_cap_str = f"${market_cap / 1_000_000:.2f}M"
    #             else:
    #                 market_cap_str = f"${market_cap:,.0f}"
    #         st.metric(label="Market Cap", value=market_cap_str)

    # except Exception as e:
    #     st.warning(f"Could not fetch detailed stock information for {ticker}: {e}")

    # News sentiment results section
    st.subheader("📊 News Sentiment Analysis Results")

    # Overall sentiment from news
    col1, col2 = st.columns(2)

    # Get emoji based on sentiment
    if overall_sentiment == "Positive":
        emoji = "😊"
    elif overall_sentiment == "Negative":
        emoji = "😠"
    else:
        emoji = "😐"

    with col1:
        st.metric(
            label="Average News Sentiment",
            value=f"{overall_sentiment} {emoji}"
        )

    with col2:
        st.metric(
            label="Average Polarity Score",
            value=f"{avg_polarity:.2f}",
            help="Ranges from -1 (very negative) to +1 (very positive). Closer to 0 is more neutral."
        )

    st.metric(
        label="Average Subjectivity Score",
        value=f"{avg_subjectivity:.2f}",
        help="Ranges from 0 (very objective) to 1 (very subjective)."
    )

    # Display news articles with their sentiment
    st.subheader(f"Recent News Articles for {ticker}")

    for i, row in news_df.iterrows():
        with st.expander(f"{row['title']} {row['emoji']}"):
            st.write(f"**Publisher:** {row['publisher']}")

            # Convert Unix timestamp to readable date if available
            pub_time = row['published']
            if isinstance(pub_time, (int, float)):
                try:
                    # Attempt conversion assuming it's a standard Unix timestamp (seconds)
                    pub_date = datetime.fromtimestamp(pub_time)
                    st.write(f"**Published:** {pub_date.strftime('%Y-%m-%d %H:%M')}")
                except (ValueError, OSError):
                    # Handle potential errors like out-of-range timestamps
                    st.write(f"**Published:** Invalid timestamp ({pub_time})")
            elif isinstance(pub_time, str) and pub_time != 'Unknown':
                 st.write(f"**Published:** {pub_time}") # Display if it's already a string
            else:
                 st.write(f"**Published:** Unknown")


            st.write(f"**Sentiment:** {row['sentiment']} {row['emoji']}")
            st.write(f"**Polarity:** {row['polarity']:.2f}")
            st.write(f"**Subjectivity:** {row['subjectivity']:.2f}")
            st.write(f"**Link:** [{row['title']}]({row['link']})")


# -------------- SECTION 8: SIDEBAR INFORMATION --------------
def create_sidebar():
    """Create the sidebar with information about the app"""

    # Options section
    st.sidebar.header("Settings")

    # Number of articles to fetch for stock news analysis
    st.sidebar.slider(
        "Number of news articles to analyze",
        min_value=1,
        max_value=10,
        value=1,
        key="num_articles"
    )

    # How it works
    st.sidebar.header("How It Works")
    st.sidebar.markdown( # Removed Custom Text Analysis section
        """
        ### Stock News Analysis:
        1. Enter a stock ticker symbol (e.g., AAPL)
        2. The app fetches recent news articles
        3. Sentiment is analyzed for each article using TextBlob
        4. Results (average sentiment, polarity, subjectivity) and individual articles are displayed
        """
    )


# -------------- SECTION 9: MAIN FUNCTION --------------
def main():
    """Main function to run the Streamlit app"""
    # Set up the page configuration
    setup_page()

    # Create the main section with title/description
    create_main_section()

    # Create the sidebar
    create_sidebar()

    # Removed tabs - Stock analysis is now the main content
    st.header("Analyze Stock News Sentiment")

    # Input for stock ticker
    ticker = st.text_input(
        "Enter Stock Ticker Symbol:",
        placeholder="e.g., AAPL, MSFT, GOOGL",
        help="Enter the ticker symbol for the stock you want to analyze"
    ).upper()

    # Button to trigger analysis
    if st.button("Analyze Stock News 📰"):
        perform_stock_news_analysis(ticker)

    # Removed the Custom Text Analysis Tab section


# Run the app
if __name__ == "__main__":
    main()