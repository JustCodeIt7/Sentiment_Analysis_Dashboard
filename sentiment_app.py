# -------------- SECTION 1: IMPORTS --------------
import streamlit as st


# -------------- SECTION 2: PAGE CONFIGURATION --------------
def setup_page():
    """Configure the Streamlit page layout and appearance"""
    st.set_page_config(
        page_title="Sentiment Analysis App",
        page_icon="😊",
        layout="wide",
        initial_sidebar_state="expanded"
    )


# -------------- SECTION 3: MAIN APP LAYOUT --------------
def create_sidebar():
    """Create the sidebar with information about the app"""
    st.sidebar.header("About This App")
    st.sidebar.info(
        "This app uses the **TextBlob** library to perform basic sentiment analysis. "
    )

    st.sidebar.header("How It Works")
    st.sidebar.markdown(
        """
        1. You enter text in the text area.
        2. Click the 'Analyze Sentiment' button.
        3. The app uses `TextBlob` to calculate:
            * **Polarity**: Negative (-1) to Positive (+1)
            * **Subjectivity**: Objective (0) to Subjective (1)
        4. It classifies the sentiment based on the polarity score.
        """
    )


def create_main_section():
    """Create the main app title and description"""
    st.title("💬 Simple Sentiment Analysis App")
    st.write(
        "Enter some text below, and we'll analyze its sentiment (Positive, Negative, or Neutral) "
        "using the TextBlob library."
    )
    st.markdown("---")


# -------------- SECTION 4: SENTIMENT ANALYSIS LOGIC --------------
def analyze_sentiment(text):
    """
    Analyze text sentiment using TextBlob.

    Parameters:
        text (str): The text to analyze

    Returns:
        tuple: (polarity, subjectivity, sentiment_label, emoji)
    """


# -------------- SECTION 5: TEXT INPUT AREA --------------
def create_text_input():
    """Create and return the text input area"""


# -------------- SECTION 6: ANALYSIS & RESULTS --------------
def perform_analysis(text):
    """Perform sentiment analysis and display results"""


# -------------- SECTION 8: MAIN FUNCTION --------------
def main():
    """Main function to run the Streamlit app"""
    # Set up the page configuration
    setup_page()

    # Create the main section with title/description
    create_main_section()

    # Create the sidebar
    create_sidebar()

    # Display the text input area
    st.header("Enter Text for Analysis")
    user_text = create_text_input()

    # Add the analysis button
    if st.button("Analyze Sentiment ✨"):
        perform_analysis(user_text)


if __name__ == "__main__":
    main()
