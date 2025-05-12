# Stock News Sentiment Analyzer

A Streamlit application that analyzes sentiment of stock news articles.

## Features

- Search for news articles by stock ticker symbol
- Sentiment analysis of news article headlines and full text
- Combined sentiment analysis across all articles
- Interactive UI with expandable article details

## Project Structure

- `main.py`: Entry point for the application
- `config.py`: Configuration and session state management
- `ui.py`: User interface components
- `data.py`: Data collection and processing functions
- `sentiment.py`: Sentiment analysis tools
- `scraper.py`: Web scraping utilities

## Requirements

- Python 3.7+
- Streamlit
- TextBlob
- yfinance
- pandas
- requests
- BeautifulSoup4

## Installation

```bash
pip install streamlit textblob yfinance pandas requests beautifulsoup4