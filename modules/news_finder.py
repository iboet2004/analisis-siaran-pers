"""
News Finder Module for Analisis Siaran Pers.
Handles searching for news articles based on keywords.
"""

import requests
import streamlit as st
from typing import List, Dict, Any, Optional

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
    
    def fetch_news(self, keywords: List[str], quotes: List[str], max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch news related to keywords and quotes.
        
        Args:
            keywords: List of keywords to search for
            quotes: List of quotes to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of news articles as dictionaries
        """
        # Combine keywords and quotes for search
        search_terms = keywords[:5]  # Limit to top 5 keywords
        
        # Add notable quotes if available (using first 20 chars of each quote)
        if quotes:
            for quote in quotes[:2]:  # Limit to first 2 quotes
                # Take first few words of quote for search
                short_quote = " ".join(quote.split()[:3])
                if short_quote and short_quote not in search_terms:
                    search_terms.append(short_quote)
        
        # If no search terms, use a generic term
        if not search_terms:
            search_terms = ["berita terkini"]
        
        # Search for news using the combined terms
        return self.search_news(search_terms, page_size=max_results)
