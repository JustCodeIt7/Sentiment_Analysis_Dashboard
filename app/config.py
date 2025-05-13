"""
Configuration and Setup
----------------------
Functions to configure the Streamlit app and manage session state.
"""

import streamlit as st
import pandas as pd


def setup_page():
    """Configure the Streamlit page layout and appearance"""
    st.set_page_config(
        page_title="Stock Sentiment Analysis",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )


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
        st.session_state.num_articles = 3

def create_sidebar():
    """Create the sidebar with settings and options"""
    # Options section
    st.sidebar.header("Settings")

    # Number of articles to fetch for stock news analysis
    st.sidebar.slider(
        "Number of news articles to analyze",
        min_value=1,
        max_value=10,
        value=st.session_state.get('num_articles', 3),
        key="num_articles"
    )
