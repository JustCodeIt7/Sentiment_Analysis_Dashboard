"""
User Interface Components
------------------------
Functions to create and render the user interface elements.
"""

import streamlit as st
from datetime import datetime

def create_main_section():
    """Create the main app title and description"""
    st.title("📈 Stock Sentiment Analyzer Final App")
    st.write(
        "Enter a stock ticker to get sentiment analysis based on recent news."
    )
    st.markdown("---")


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


def display_analysis_results(ticker, avg_polarity, avg_subjectivity, overall_sentiment, news_df, combined_sentiment):
    """
    Display the full sentiment analysis results

    Parameters:
        ticker (str): The stock ticker symbol
        avg_polarity (float): Average polarity score
        avg_subjectivity (float): Average subjectivity score
        overall_sentiment (str): Overall sentiment label
        news_df (pandas.DataFrame): DataFrame with news and analysis
        combined_sentiment (dict): Combined sentiment data
    """
    # Display combined sentiment analysis if available
    display_combined_sentiment(combined_sentiment)

    # Display news articles with their sentiment
    display_news_articles(ticker, news_df)
