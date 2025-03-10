"""
News Finder Module for Analisis Siaran Pers.
Handles searching for news articles based on keywords.
"""

import requests
import streamlit as st
from typing import List, Dict

class NewsFinder:
    """Class to handle news search operations."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/everything"
    
    def search_news(self, keywords: List[str], language: str = "id", page_size: int = 5) -> List[Dict]:
        """
        Search for news articles based on keywords.
        
        Args:
            keywords: List of keywords to search for
            language: Language of the articles (default is Indonesian)
            page_size: Number of articles to return
            
        Returns:
            List of news articles as dictionaries
        """
        query = " OR ".join(keywords)
        params = {
            "q": query,
            "language": language,
            "pageSize": page_size,
            "apiKey": self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            return articles
        else:
            st.error(f"Error fetching news: {response.status_code} - {response.text}")
            return []
    
    def fetch_news(self, keywords: List[str], quotes: List[str], max_results: int = 5) -> List[Dict]:
        """
        Fetch news articles based on keywords and quotes.
        
        Args:
            keywords: List of keywords to search for
            quotes: List of quotes to include in search
            max_results: Maximum number of articles to return
            
        Returns:
            List of news articles as dictionaries
        """
        # Filter out empty keywords
        valid_keywords = [kw for kw in keywords if kw and len(kw) > 2]
        
        # If no valid keywords, use the first part of quotes
        if not valid_keywords and quotes:
            # Extract first 3 words from each quote to use as keywords
            for quote in quotes:
                words = quote.split()
                if words:
                    keywords_from_quote = words[:min(3, len(words))]
                    valid_keywords.extend(keywords_from_quote)
        
        # If still no valid keywords, return empty result
        if not valid_keywords:
            st.warning("Tidak ada kata kunci yang valid untuk pencarian berita.")
            return []
        
        # Search news with the valid keywords
        try:
            articles = self.search_news(valid_keywords, page_size=max_results)
            return articles
        except Exception as e:
            st.error(f"Error saat mencari berita: {str(e)}")
            return []
