import requests
import feedparser
import streamlit as st
from typing import List, Dict, Any

class NewsFinder:
    """
    Modul pencarian berita yang menggabungkan NewsAPI, API Berita Lokal Indonesia, dan Twitter Trends API.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.newsapi_url = "https://newsapi.org/v2/everything"
        self.local_news_url = "https://berita-indo-api.vercel.app/v1/"
        self.twitter_trends_url = "https://api.trends24.in/indonesia"
    
    def fetch_newsapi(self, keywords: List[str], max_results: int = 5) -> List[Dict[str, Any]]:
        """Ambil berita dari NewsAPI."""
        query = " OR ".join(keywords)
        params = {
            "q": query,
            "language": "id",
            "pageSize": max_results,
            "apiKey": self.api_key
        }
        response = requests.get(self.newsapi_url, params=params)
        if response.status_code == 200:
            return response.json().get("articles", [])
        else:
            st.error(f"Gagal mengambil berita dari NewsAPI: {response.status_code}")
            return []
    
    def fetch_local_news(self, max_results: int = 5) -> List[Dict[str, Any]]:
        """Ambil berita dari API berita lokal Indonesia."""
        response = requests.get(f"{self.local_news_url}cnn")
        if response.status_code == 200:
            articles = response.json().get("data", [])[:max_results]
            return [{"title": art["title"], "link": art["link"], "source": "CNN Indonesia"} for art in articles]
        else:
            st.error(f"Gagal mengambil berita dari API berita lokal: {response.status_code}")
            return []
    
    def fetch_twitter_trends(self) -> List[str]:
        """Ambil tren Twitter Indonesia."""
        response = requests.get(self.twitter_trends_url)
        if response.status_code == 200:
            return response.json().get("trends", [])[:5]  # Ambil 5 tren teratas
        else:
            st.error(f"Gagal mengambil tren Twitter: {response.status_code}")
            return []
    
    def fetch_news(self, keywords: List[str], max_results: int = 5) -> List[Dict[str, Any]]:
        """Gabungkan berita dari berbagai sumber."""
        news_results = []
        news_results.extend(self.fetch_newsapi(keywords, max_results))
        news_results.extend(self.fetch_local_news(max_results))
        
        # Hapus duplikasi berdasarkan judul
        seen_titles = set()
        final_results = []
        for news in news_results:
            if news["title"] not in seen_titles:
                seen_titles.add(news["title"])
                final_results.append(news)
        
        return final_results

# Contoh pemakaian mandiri
if __name__ == "__main__":
    api_key = st.secrets["news_api_key"]  # Gantilah dengan API key yang valid
    finder = NewsFinder(api_key)
    sample_keywords = ["politik", "ekonomi", "magelang"]
    news = finder.fetch_news(sample_keywords, max_results=5)
    
    for i, article in enumerate(news, 1):
        print(f"{i}. {article['title']} - {article['source']}")
        print(f"   {article['link']}")
