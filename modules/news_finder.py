import requests
import feedparser
import time
from typing import List, Dict

class NewsFinder:
    """
    Modul untuk mencari berita berdasarkan kata kunci dan kutipan menggunakan Google News RSS dan metode tambahan.
    """
    
    def __init__(self):
        self.base_url = "https://news.google.com/rss/search?q="
    
    def fetch_news(self, keywords: List[str], quotes: List[str], max_results: int = 10) -> List[Dict[str, str]]:
        """
        Mengambil berita dari Google News RSS berdasarkan kata kunci dan kutipan.
        
        Args:
            keywords (List[str]): Daftar kata kunci untuk pencarian berita.
            quotes (List[str]): Daftar kutipan untuk pencarian berita.
            max_results (int): Jumlah maksimum berita yang akan diambil.
        
        Returns:
            List[Dict[str, str]]: Daftar berita dengan judul, link, dan sumber media.
        """
        news_results = []
        search_terms = keywords + quotes  # Gabungkan kata kunci dan kutipan
        
        for term in search_terms:
            search_url = f"{self.base_url}{term.replace(' ', '+')}&hl=id&gl=ID&ceid=ID:id"
            feed = feedparser.parse(search_url)
            
            for entry in feed.entries[:max_results]:
                news_results.append({
                    "title": entry.title,
                    "link": entry.link,
                    "source": entry.source.title if 'source' in entry else "Unknown"
                })
            
            time.sleep(1)  # Delay untuk menghindari limit request
        
        return news_results

# Contoh pemakaian mandiri
if __name__ == "__main__":
    finder = NewsFinder()
    sample_keywords = ["pemerintah", "ekonomi"]
    sample_quotes = ["Pertumbuhan ekonomi Indonesia meningkat"]
    news = finder.fetch_news(sample_keywords, sample_quotes, max_results=5)
    
    for i, article in enumerate(news, 1):
        print(f"{i}. {article['title']} - {article['source']}")
        print(f"   {article['link']}")
