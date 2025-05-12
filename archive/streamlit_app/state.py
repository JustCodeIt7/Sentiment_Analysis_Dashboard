import streamlit as st
import pandas as pd

def initialize_session_state():
    """Initialize the session state variables for the app"""
    defaults = {
        'ticker': "",
        'avg_polarity': 0.0,
        'avg_subjectivity': 0.0,
        'overall_sentiment': "Neutral",
        'news_df': pd.DataFrame(),
        'combined_sentiment': None,
        'analysis_performed': False,
        'num_articles': 5,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value