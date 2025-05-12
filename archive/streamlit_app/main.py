import streamlit as st
# from config import setup_page  # Assuming setup_page is defined in config.py
from state import initialize_session_state
from sidebar import create_sidebar
from ui import perform_stock_news_analysis

# Placeholder for setup_page if not defined in config.py or if config.py is empty
def setup_page():
    st.set_page_config(
        page_title="Stock News Sentiment Analyzer",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )

def main():
    """Main function to run the Streamlit app."""
    setup_page() # Call the page setup
    initialize_session_state()

    st.title("📈 Stock News Sentiment Analyzer")
    st.write("Enter a stock ticker to get sentiment analysis based on recent news.")
    st.markdown("---")

    create_sidebar()

    st.header("Analyze Stock News Sentiment")
    ticker_input = st.text_input( # Changed variable name to avoid conflict with session_state.ticker
        "Enter Stock Ticker Symbol:",
        value=st.session_state.ticker,
        placeholder="e.g., AAPL, MSFT, GOOGL",
        help="Enter the ticker symbol for the stock you want to analyze"
    ).upper()
    
    # Update session state ticker only if a new value is entered
    if ticker_input and ticker_input != st.session_state.ticker:
        st.session_state.ticker = ticker_input
        # Reset analysis_performed if ticker changes to force re-analysis
        st.session_state.analysis_performed = False 


    if st.button("Analyze Stock News 📰"):
        if st.session_state.ticker: # Ensure ticker is not empty before analyzing
            perform_stock_news_analysis(st.session_state.ticker)
        else:
            st.warning("Please enter a stock ticker.")
    elif st.session_state.analysis_performed and st.session_state.ticker:
        # This block allows re-displaying results if already analyzed, 
        # e.g., after changing number of articles or other settings
        perform_stock_news_analysis(st.session_state.ticker)

if __name__ == "__main__":
    main()