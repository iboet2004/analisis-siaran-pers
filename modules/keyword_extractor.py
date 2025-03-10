import re
import nltk
import streamlit as st
from typing import List, Dict, Tuple
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Download NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

class KeywordExtractor:
    """Class to handle keyword and quote extraction operations."""

    def __init__(self):
        """Initialize the KeywordExtractor with necessary resources."""
        # Initialize Indonesian stemmer
        factory = StemmerFactory()
        self.stemmer = factory.create_stemmer()
        # Indonesian stopwords from NLTK + custom additions
        self.stopwords = set(stopwords.words('indonesian'))
        custom_stopwords = {
            "yang", "dengan", "ini", "itu", "atau", "dan", "di", "ke", "dari",
            "untuk", "pada", "adalah", "dalam", "akan", "bahwa", "sebagai",
            "juga", "dapat", "oleh", "telah", "ada", "mereka", "saya", "kami",
            "kita", "dia", "kepada", "terhadap", "seperti", "tidak", "bisa",
            "lebih", "harus", "sudah", "saat", "ketika", "karena"
        }
        self.stopwords.update(custom_stopwords)

    def preprocess_text(self, text: str) -> str:
        """Preprocess text by removing special characters, converting to lowercase, and removing stopwords."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', ' ', text)
        words = word_tokenize(text)
        filtered_words = [self.stemmer.stem(word) for word in words if word not in self.stopwords and len(word) > 2]
        return ' '.join(filtered_words)

    def extract_keywords_tfidf(self, text: str, num_keywords: int = 10) -> List[Tuple[str, float]]:
        """Extract keywords using TF-IDF method."""
        processed_text = self.preprocess_text(text)
        sentences = sent_tokenize(text)
        if len(sentences) < 2:
            chunks = [text[i:i+100] for i in range(0, len(text), 100)]
            sentences = chunks if chunks else ["dummy text"]
        
        vectorizer = TfidfVectorizer(max_features=num_keywords * 2)
        tfidf_matrix = vectorizer.fit_transform(sentences)
        feature_names = vectorizer.get_feature_names_out()
        avg_scores = tfidf_matrix.mean(axis=0).A1
        top_indices = avg_scores.argsort()[-num_keywords:][::-1]
        keywords = [(feature_names[i], avg_scores[i]) for i in top_indices]
        return keywords

    def extract_quotes(self, text: str) -> List[Dict[str, str]]:
        """Extract quotes from text."""
        quotes = []
        quote_pattern = r'“([^”]+)”|\"([^\"]+)\"'
        matches = re.finditer(quote_pattern, text)
        
        for match in matches:
            quote = match.group(1) or match.group(2)
            if quote:
                sentences = sent_tokenize(text)
                for sentence in sentences:
                    if quote in sentence:
                        quotes.append({"quote": quote, "context": sentence})
                        break
        
        return quotes
