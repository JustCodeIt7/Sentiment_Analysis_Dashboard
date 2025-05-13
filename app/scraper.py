"""
Web Scraping Utilities
---------------------
Functions for extracting text from news articles.
"""

import requests
from bs4 import BeautifulSoup
import re
import streamlit as st


def extract_article_text(url):
    """
        Extract the main text content from a news article URL

        Parameters:
            url (str): The URL of the news article

        Returns:
            str: The extracted article text or empty string if extraction fails
    """
    try:
        # Add user agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Send request to get the webpage
        response = requests.get(url, headers=headers, timeout=10)

        # Check if request was successful
        if response.status_code != 200:
            return ""

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements that might contain irrelevant text
        for script_or_style in soup(['script', 'style', 'header', 'footer', 'nav']):
            script_or_style.extract()

        # Get all paragraphs which usually contain the main article text
        paragraphs = soup.find_all('p')

        # Join paragraphs to form the complete article text
        article_text = ' '.join([p.get_text().strip() for p in paragraphs])

        # Clean up the text (remove extra whitespace, etc.)
        article_text = re.sub(r'\s+', ' ', article_text).strip()

        # Remove the specific error string that appears in some articles
        article_text = article_text.replace(
            "Oops, something went wrong Unlock stock picks and a broker-level newsfeed that powers Wall", "")

        return article_text

    except Exception as e:
        st.warning(f"Could not extract text from {url}. Error: {str(e)}")
        return ""
