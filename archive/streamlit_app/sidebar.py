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