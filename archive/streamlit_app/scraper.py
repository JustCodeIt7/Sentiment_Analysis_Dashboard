import requests
from bs4 import BeautifulSoup
import re
import streamlit as st

def extract_article_text(url: str) -> str:
    """Extract main text content from a news article URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return ""
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup(['script', 'style', 'header', 'footer', 'nav']):
            tag.extract()
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text().strip() for p in paragraphs])
        text = re.sub(r'\s+', ' ', text).strip()
        text = text.replace(
            "Oops, something went wrong Unlock stock picks and a broker-level newsfeed that powers Wall", ""
        )
        return text
    except Exception as e:
        st.warning(f"Could not extract text from {url}: {e}")
        return ""