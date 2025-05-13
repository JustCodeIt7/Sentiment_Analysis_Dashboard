# -------------- SECTION 1: IMPORTS --------------
import streamlit as st
from textblob import TextBlob

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


# -------------- SECTION 4: TEXT INPUT AREA --------------
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

# -------------- SECTION 5: SENTIMENT ANALYSIS LOGIC --------------
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

# -------------- SECTION 6: ANALYSIS & RESULTS --------------
def perform_analysis(text):
    """Perform sentiment analysis and display results"""
    # Only analyze if there's text
    if not text:
        st.warning("⚠️ Please enter some text above before analyzing.")
        return

    # Show analysis in progress
    with st.spinner('Analyzing the text...'):
        # Optional delay for demonstration purposes
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

    # Add the analysis button using 2 columns
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Analyze Sentiment ✨"):
            perform_analysis(user_text)
    with col2:
        if st.button("Clear", key="clear_button"):
            st.session_state.user_input_text = ""
            st.experimental_rerun()


if __name__ == "__main__":
    main()
