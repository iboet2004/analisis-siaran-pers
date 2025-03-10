import requests
import feedparser
import streamlit as st
import pandas as pd
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

# Integrasi dengan Streamlit
st.title("Pencarian Berita")
api_key = st.secrets["news_api_key"]
news_finder = NewsFinder(api_key)

keywords_input = st.text_input("Masukkan kata kunci pencarian (pisahkan dengan koma)", "politik, ekonomi, magelang")
keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]

if st.button("Cari Berita"):
    with st.spinner("Mengambil berita..."):
        news_results = news_finder.fetch_news(keywords, max_results=5)
        
        if news_results:
            df = pd.DataFrame(news_results)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Tidak ada berita ditemukan.")
