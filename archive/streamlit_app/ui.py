import streamlit as st
from datetime import datetime

def display_combined_sentiment(combined):
    """Display combined sentiment metrics."""
    if not combined:
        return
    st.subheader("Combined Sentiment Analysis")
    st.write("Combines all article texts for holistic sentiment.")
    cols = st.columns(3)
    cols[0].metric("Combined Sentiment", f"{combined['sentiment']} {combined['emoji']}")
    cols[1].metric("Combined Polarity", f"{combined['polarity']:.2f}")
    cols[2].metric("Combined Subjectivity", f"{combined['subjectivity']:.2f}")

def display_article_details(row):
    """Display details for an individual article."""
    pub = row['published']
    if isinstance(pub, int): # Assuming 'providerPublishTime' is a Unix timestamp
        pub = datetime.fromtimestamp(pub).strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(pub, str): # If it's already a string, use as is
        pass
    else: # Fallback for unknown format
        pub = str(pub)

    st.write(f"**Publisher:** {row['publisher']} - {pub}")
    st.write("### Sentiment Analysis")
    st.write(f"**Sentiment:** {row['full_text_sentiment']} {row['full_text_emoji']}")
    st.write(f"**Polarity:** {row['full_text_polarity']:.2f}")
    st.write(f"**Subjectivity:** {row['full_text_subjectivity']:.2f}")
    st.write("### Article Preview")
    st.write(row['article_text'])
    st.write(f"**Full Article:** [{row['title']}]({row['link']})")

def display_news_articles(ticker, df):
    """Display news articles in expanders."""
    st.subheader(f"Recent News Articles for {ticker}")
    for _, row in df.iterrows():
        with st.expander(f"{row['title']} {row['full_text_emoji']}"):
            display_article_details(row)

def perform_stock_news_analysis(ticker):
    """Run sentiment analysis and display results."""
    from data_fetcher import analyze_stock_news_sentiment # Keep import here to avoid circular dependency if ui is imported elsewhere
    state = st.session_state
    if not ticker:
        st.warning("Please enter a ticker.")
        return
    if state.ticker == ticker and state.analysis_performed:
        avg_pol, avg_subj, overall, df, combined = (
            state.avg_polarity, state.avg_subjectivity,
            state.overall_sentiment, state.news_df, state.combined_sentiment
        )
    else:
        with st.spinner(f"Analyzing {ticker} news..."):
            avg_pol, avg_subj, overall, df, combined = analyze_stock_news_sentiment(
                ticker, state.num_articles
            )
        state.ticker = ticker
        state.avg_polarity = avg_pol
        state.avg_subjectivity = avg_subj
        state.overall_sentiment = overall
        state.news_df = df
        state.combined_sentiment = combined
        state.analysis_performed = True

    if df.empty:
        st.warning("No news found.")
        return
    display_combined_sentiment(combined)
    display_news_articles(ticker, df)