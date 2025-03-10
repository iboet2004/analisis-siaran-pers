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
