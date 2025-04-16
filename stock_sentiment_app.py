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
        layout="centered",
        initial_sidebar_state="expanded"
    )


# -------------- SECTION 3: SENTIMENT ANALYSIS LOGIC --------------
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

        # Get sentiment
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


# -------------- SECTION 5: MAIN APP LAYOUT --------------
def create_main_section():
    """Create the main app title and description"""
    st.title("📈 Stock News Sentiment Analyzer")
    st.write(
        "This app analyzes sentiment from recent news for a specific stock ticker or any text you input. "
        "Enter a stock ticker to get news sentiment analysis, or input your own text for manual analysis."
    )
    st.markdown("---")  # Horizontal divider


# -------------- SECTION 6: TEXT INPUT AREA --------------
def create_text_input():
    """Create and return the text input area"""
    return st.text_area(
        "Type or paste your text here:",
        value="I absolutely love using Streamlit for creating interactive data apps! "
              "It's intuitive, fast, and makes sharing my work with others a breeze. "
              "The community is also incredibly helpful.",
        height=150,
        placeholder="E.g., 'Streamlit makes building web apps so easy and fun!'",
        key="user_input_text"
    )


# -------------- SECTION 7: ANALYSIS & RESULTS --------------
def perform_text_analysis(text):
    """Perform sentiment analysis on user input text and display results"""
    # Only analyze if there's text
    if not text:
        st.warning("⚠️ Please enter some text above before analyzing.")
        return

    # Show analysis in progress
    with st.spinner('Analyzing the text...'):
        # Perform the analysis
        polarity, subjectivity, sentiment, emoji = analyze_sentiment(text)

    # Display results section
    st.subheader("📊 Analysis Results")

    # Create a two-column layout
    col1, col2 = st.columns(2)

    # Column 1: Overall sentiment
    with col1:
        st.metric(
            label="Overall Sentiment",
            value=f"{sentiment} {emoji}"
        )

    # Column 2: Polarity score
    with col2:
        st.metric(
            label="Polarity Score",
            value=f"{polarity:.2f}",
            help="Ranges from -1 (very negative) to +1 (very positive). Closer to 0 is more neutral."
        )

    # Subjectivity score (full width)
    st.metric(
        label="Subjectivity Score",
        value=f"{subjectivity:.2f}",
        help="Ranges from 0 (very objective) to 1 (very subjective)."
    )

    # Add explanation of the metrics
    st.info("""
    * **Sentiment:** The overall feeling expressed (Positive, Negative, or Neutral).
    * **Polarity:** How positive or negative the text is.
    * **Subjectivity:** How much the text expresses personal opinions vs. factual information.
    """)


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

    # Stock info section
    try:
        stock = yf.Ticker(ticker)
        info = stock.get_info()  # Use the correct get_info() method

        # Create a header row for stock info
        st.subheader(f"Stock Information: {info.get('longName', ticker)} ({ticker})")

        # Display basic stock info in columns
        col1, col2, col3 = st.columns(3)

        with col1:
            # Current price with change
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
            previous_close = info.get('previousClose', 'N/A')

            if current_price != 'N/A' and previous_close != 'N/A':
                price_change = current_price - previous_close
                price_change_pct = (price_change / previous_close) * 100

                # Use only the accepted values for delta_color
                # 'normal', 'inverse', or 'off'
                delta_color = "normal"  # This shows positive changes in green, negative in red

                st.metric(
                    label="Current Price",
                    value=f"${current_price:,.2f}" if isinstance(current_price, (int, float)) else current_price,
                    delta=f"{price_change_pct:+.2f}%" if isinstance(price_change_pct, (int, float)) else price_change,
                    delta_color=delta_color
                )
            else:
                st.metric(label="Current Price", value="N/A")

        with col2:
            # 52-Week Range
            st.metric(
                label="52-Week Range",
                value=f"${info.get('fiftyTwoWeekLow', 'N/A'):,.2f} - ${info.get('fiftyTwoWeekHigh', 'N/A'):,.2f}"
                if isinstance(info.get('fiftyTwoWeekLow'), (int, float)) and
                   isinstance(info.get('fiftyTwoWeekHigh'), (int, float))
                else "N/A"
            )

        with col3:
            # Market Cap
            market_cap = info.get('marketCap', 'N/A')
            if isinstance(market_cap, (int, float)):
                if market_cap >= 1_000_000_000_000:
                    market_cap_str = f"${market_cap / 1_000_000_000_000:.2f}T"
                elif market_cap >= 1_000_000_000:
                    market_cap_str = f"${market_cap / 1_000_000_000:.2f}B"
                elif market_cap >= 1_000_000:
                    market_cap_str = f"${market_cap / 1_000_000:.2f}M"
                else:
                    market_cap_str = f"${market_cap:,.0f}"
                st.metric(label="Market Cap", value=market_cap_str)
            else:
                st.metric(label="Market Cap", value="N/A")

        # Additional financial metrics in expandable section
        with st.expander("Company & Financial Details"):
            # Company information
            st.subheader("Company Overview")
            st.write(f"**Sector:** {info.get('sector', 'N/A')}")
            st.write(f"**Industry:** {info.get('industry', 'N/A')}")
            st.write(f"**Website:** [{info.get('website', 'N/A')}]({info.get('website', '#')})")
            st.write(f"**Headquarters:** {info.get('city', '')}, {info.get('state', '')}, {info.get('country', 'N/A')}")

            # Trading info
            st.subheader("Trading Information")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Exchange:** {info.get('fullExchangeName', 'N/A')}")
                st.write(f"**Volume:** {info.get('regularMarketVolume', 'N/A'):,}" if isinstance(
                    info.get('regularMarketVolume'), (int, float)) else "N/A")
                st.write(f"**Avg Volume (10d):** {info.get('averageVolume10days', 'N/A'):,}" if isinstance(
                    info.get('averageVolume10days'), (int, float)) else "N/A")

            with col2:
                st.write(f"**P/E Ratio:** {info.get('trailingPE', 'N/A'):.2f}" if isinstance(info.get('trailingPE'),
                                                                                             (int, float)) else "N/A")

                # Dividend info
                if info.get('dividendYield'):
                    dividend_yield = info.get('dividendYield', 0) * 100  # Convert to percentage
                    st.write(f"**Dividend Yield:** {dividend_yield:.2f}%")
                    st.write(
                        f"**Dividend Rate:** ${info.get('dividendRate', 'N/A')}" if info.get('dividendRate') else "N/A")
                else:
                    st.write("**Dividend:** None")

            # Financial metrics
            st.subheader("Key Financial Metrics")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Return on Equity",
                          f"{info.get('returnOnEquity', 'N/A') * 100:.2f}%" if isinstance(info.get('returnOnEquity'),
                                                                                          (int, float)) else "N/A")

            with col2:
                st.metric("Revenue Growth",
                          f"{info.get('revenueGrowth', 'N/A') * 100:.2f}%" if isinstance(info.get('revenueGrowth'),
                                                                                         (int, float)) else "N/A")

            with col3:
                st.metric("Earnings Growth",
                          f"{info.get('earningsGrowth', 'N/A') * 100:.2f}%" if isinstance(info.get('earningsGrowth'),
                                                                                          (int, float)) else "N/A")

            # Analyst recommendations
            if info.get('recommendationMean'):
                recommendation = info.get('recommendationKey', 'N/A').capitalize()
                st.metric("Analyst Recommendation",
                          f"{recommendation} ({info.get('recommendationMean', 'N/A'):.2f})" if isinstance(
                              info.get('recommendationMean'), (int, float)) else recommendation)
                st.write(f"**Analyst Count:** {info.get('numberOfAnalystOpinions', 'N/A')}")

            # Business summary if available
            if info.get('longBusinessSummary'):
                st.subheader("Business Summary")
                st.write(info.get('longBusinessSummary', 'No summary available.'))

    except Exception as e:
        st.warning(f"Could not fetch detailed stock information for {ticker}: {e}")

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
            if isinstance(row['published'], (int, float)) and row['published'] != 'Unknown':
                pub_date = datetime.fromtimestamp(row['published'])
                st.write(f"**Published:** {pub_date.strftime('%Y-%m-%d %H:%M')}")

            st.write(f"**Sentiment:** {row['sentiment']} {row['emoji']}")
            st.write(f"**Polarity:** {row['polarity']:.2f}")
            st.write(f"**Subjectivity:** {row['subjectivity']:.2f}")
            st.write(f"**Link:** [{row['title']}]({row['link']})")


# -------------- SECTION 8: SIDEBAR INFORMATION --------------
def create_sidebar():
    """Create the sidebar with information about the app"""
    # About section
    st.sidebar.header("About This App")
    st.sidebar.info(
        "This app analyzes sentiment from stock news or custom text using TextBlob. "
        "Enter a stock ticker to get news sentiment or paste your own text for analysis."
    )

    # Options section
    st.sidebar.header("Settings")

    # Number of articles to fetch for stock news analysis
    st.sidebar.slider(
        "Number of news articles to analyze",
        min_value=1,
        max_value=10,
        value=5,
        key="num_articles"
    )

    # How it works
    st.sidebar.header("How It Works")
    st.sidebar.markdown(
        """
        ### Stock News Analysis:
        1. Enter a stock ticker symbol (e.g., AAPL)
        2. The app fetches recent news articles
        3. Sentiment is analyzed for each article
        4. Results and articles are displayed with sentiment scores

        ### Custom Text Analysis:
        1. Enter text in the text area
        2. Click the 'Analyze Text' button
        3. The app uses TextBlob to calculate:
           * **Polarity**: Negative (-1) to Positive (+1)
           * **Subjectivity**: Objective (0) to Subjective (1)
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

    # Create tabs for different analysis modes
    stock_tab, text_tab = st.tabs(["📈 Stock News Analysis", "📝 Custom Text Analysis"])

    # Stock News Analysis Tab
    with stock_tab:
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

    # Custom Text Analysis Tab
    with text_tab:
        st.header("Analyze Custom Text")

        # Display the text input area
        user_text = create_text_input()

        # Add the analysis button
        if st.button("Analyze Text 📝"):
            perform_text_analysis(user_text)


# Run the app
if __name__ == "__main__":
    main()
