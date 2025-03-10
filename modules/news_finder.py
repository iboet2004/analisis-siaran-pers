import requests
import feedparser
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
            return []
    
    def fetch_local_news(self, max_results: int = 5) -> List[Dict[str, Any]]:
        """Ambil berita dari API berita lokal Indonesia."""
        response = requests.get(f"{self.local_news_url}cnn")
        if response.status_code == 200:
            articles = response.json().get("data", [])[:max_results]
            return [{"title": art["title"], "link": art["link"], "source": "CNN Indonesia"} for art in articles]
        else:
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
