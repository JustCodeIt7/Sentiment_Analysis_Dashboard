# This file is for app configuration.
# You can define constants, API keys (though be careful with version control),
# or page setup functions here.

import streamlit as st

def setup_page():
    """Sets up the Streamlit page configuration."""
    st.set_page_config(
        page_title="Stock News Sentiment Analyzer",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://www.example.com/help', # Replace with your help page
            'Report a bug': "https://www.example.com/bug", # Replace with your bug report page
            'About': """
            ## Stock News Sentiment Analyzer
            This app analyzes the sentiment of recent news articles for a given stock ticker.
            It uses yfinance to fetch news and TextBlob for sentiment analysis.
            """
        }
    )

# Example of a constant you might use:
# DEFAULT_NUM_ARTICLES = 5