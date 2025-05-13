"""
Stock News Sentiment Analyzer - Main Application
------------------------------------------------
This Streamlit app analyzes sentiment of news articles for any stock ticker.
"""

import streamlit as st

# Import local modules
from config import setup_page, initialize_session_state, create_sidebar
from ui import create_main_section, display_analysis_results
from data import perform_stock_news_analysis
import pandas as pd

def main():
    """Main entry point for the Stock Sentiment Analysis application"""
    # Step 1: Configure the page layout
    setup_page()

    # Step 2: Set up app state
    initialize_session_state()

    # Step 3: Create sidebar with settings
    create_sidebar()

    # Step 4: Create the main app header and description
    create_main_section()

    # Step 5: Main functionality - Stock analysis section
    st.header("Analyze Stock News Sentiment")

    # Step 6: Input for stock ticker
    ticker = st.text_input(
        "Enter Stock Ticker Symbol:",
        value=st.session_state.get('ticker', ''),
        placeholder="e.g., AAPL, MSFT, GOOGL",
        help="Enter the ticker symbol for the stock you want to analyze"
    ).upper()

    # Update ticker in session state when it changes
    if ticker:
        st.session_state.ticker = ticker



    col1, col2 = st.columns(2)
    with col1:
        # Step 7: Button to trigger analysis
        analyze_button = st.button("Analyze Stock News 📰")
    with col2:
        # Add a button to clear results
        if st.button("Clear Saved Results"):
            st.session_state.analysis_performed = False
            st.session_state.ticker = ""
            st.session_state.news_df = pd.DataFrame()
            st.session_state.combined_sentiment = None
            st.rerun()

    # Step 8: Perform analysis when button is pressed or if we have saved results
    if analyze_button:
        results = perform_stock_news_analysis(ticker)
        if results:
            display_analysis_results(ticker, *results)
    elif st.session_state.analysis_performed and st.session_state.ticker:
        # Display saved results
        display_analysis_results(
            st.session_state.ticker,
            st.session_state.avg_polarity,
            st.session_state.avg_subjectivity,
            st.session_state.overall_sentiment,
            st.session_state.news_df,
            st.session_state.combined_sentiment
        )



# Run the app
if __name__ == "__main__":
    main()
