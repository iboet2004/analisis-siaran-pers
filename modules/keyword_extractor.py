"""
Keyword Extractor Module for Analisis Siaran Pers.
Handles the extraction of keywords, key phrases, and quotes from text.
"""

import re
import os
import nltk
import streamlit as st
from typing import List, Dict, Tuple, Optional
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Atur path NLTK
nltk_data_path = os.path.join(os.sep, 'tmp', 'nltk_data')
if 'NLTK_DATA' not in os.environ:
    os.environ['NLTK_DATA'] = nltk_data_path

# Buat direktori jika belum ada
os.makedirs(nltk_data_path, exist_ok=True)

# Tambahkan path ke NLTK
nltk.data.path.append(nltk_data_path)

# Download NLTK resources yang diperlukan
for resource in ['punkt', 'stopwords']:
    try:
        nltk.data.find(f'tokenizers/{resource}')
    except LookupError:
        nltk.download(resource, download_dir=nltk_data_path)


class KeywordExtractor:
    """Class to handle keyword and quote extraction operations."""
    
    def __init__(self):
        """Initialize the KeywordExtractor with necessary resources."""
        # Initialize Indonesian stemmer
        factory = StemmerFactory()
        self.stemmer = factory.create_stemmer()
        
        # Indonesian stopwords from NLTK + custom additions
        try:
            self.stopwords = set(stopwords.words('indonesian'))
        except LookupError:
            nltk.download('stopwords', download_dir=nltk_data_path)
            self.stopwords = set(stopwords.words('indonesian'))
        
        # Add custom Indonesian stopwords
        custom_stopwords = {
            "yang", "dengan", "ini", "itu", "atau", "dan", "di", "ke", "dari",
            "untuk", "pada", "adalah", "dalam", "akan", "bahwa", "sebagai",
            "juga", "dapat", "oleh", "telah", "ada", "mereka", "saya", "kami",
            "kita", "dia", "kepada", "terhadap", "seperti", "tidak", "bisa",
            "lebih", "harus", "sudah", "saat", "ketika", "karena", "jika",
            "tentang", "maka", "merupakan", "tersebut", "terdapat", "adanya",
            "hal", "serta", "yaitu"
        }
        self.stopwords.update(custom_stopwords)
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text by removing special characters, converting to lowercase,
        and removing stopwords.
        
        Args:
            text: Text to preprocess
            
        Returns:
            Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', ' ', text)
        
        # Tokenize
        words = word_tokenize(text)
        
        # Remove stopwords and stem
        filtered_words = [self.stemmer.stem(word) for word in words if word not in self.stopwords and len(word) > 2]
        
        return " ".join(filtered_words)
    
    def extract_keywords_tfidf(self, text: str, num_keywords: int = 10) -> List[Tuple[str, float]]:
        """
        Extract keywords using TF-IDF method.
        
        Args:
            text: Text to extract keywords from
            num_keywords: Number of keywords to extract
            
        Returns:
            List of (keyword, score) tuples
        """
        try:
            # Preprocess text
            processed_text = self.preprocess_text(text)
            
            # Split text into sentences
            sentences = sent_tokenize(text)
            
            # If there are too few sentences, create artificial ones
            if len(sentences) < 2:
                # Split into chunks of ~100 characters
                chunks = [text[i:i+100] for i in range(0, len(text), 100)]
                sentences = chunks if chunks else ["dummy text"]
            
            # Vectorize text using TF-IDF
            vectorizer = TfidfVectorizer(max_features=num_keywords * 2)
            
            # Handle case when vectorizer fails
            try:
                tfidf_matrix = vectorizer.fit_transform(sentences)
            except ValueError:
                # Fallback: use the entire text as one document
                tfidf_matrix = vectorizer.fit_transform([text])
            
            # Get feature names
            feature_names = vectorizer.get_feature_names_out()
            
            # Calculate average TF-IDF scores across sentences
            avg_scores = tfidf_matrix.mean(axis=0).A1
            
            # Get top keywords
            top_indices = avg_scores.argsort()[-num_keywords:][::-1]
            keywords = [(feature_names[i], avg_scores[i]) for i in top_indices]
            
            return keywords
        except Exception as e:
            st.error(f"Error extracting keywords: {str(e)}")
            return [("error", 0.0)]
    
    def extract_keyphrases(self, text: str, num_phrases: int = 5) -> List[str]:
        """
        Extract key phrases from text.
        
        Args:
            text: Text to extract key phrases from
            num_phrases: Number of key phrases to extract
            
        Returns:
            List of key phrases
        """
        try:
            # Split into sentences
            sentences = sent_tokenize(text)
            
            if not sentences:
                return []
                
            # Calculate sentence scores based on keyword presence
            keywords = [kw for kw, _ in self.extract_keywords_tfidf(text, num_keywords=20)]
            sentence_scores = []
            
            for sentence in sentences:
                score = 0
                for keyword in keywords:
                    if keyword.lower() in sentence.lower():
                        score += 1
                sentence_scores.append((sentence, score))
            
            # Sort sentences by score
            sentence_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Return top phrases
            return [sentence for sentence, _ in sentence_scores[:num_phrases]]
        except Exception as e:
            st.error(f"Error extracting key phrases: {str(e)}")
            return []
    
    def extract_quotes(self, text: str) -> List[Dict[str, str]]:
        """
        Extract quotes from text using regex patterns.
        
        Args:
            text: Text to extract quotes from
            
        Returns:
            List of dictionaries containing quote and context
        """
        try:
            quotes = []
            
            # Improved patterns for Indonesian quotes
            # Pattern untuk kutipan dengan tanda petik ganda (berbagai jenis)
            patterns = [
                r'"([^"]{10,})"',             # Standard double quotes
                r'"([^"]{10,})"',             # Curly double quotes
                r'["]([^"]{10,})["]',         # Other double quotes
                r''([^']{10,})''              # Single quotes
            ]
            
            all_quotes = []
            for pattern in patterns:
                matches = re.findall(pattern, text)
                all_quotes.extend(matches)
            
            # Deduplicate quotes
            unique_quotes = list(set(all_quotes))
            
            # Filter out very short quotes
            filtered_quotes = [q for q in unique_quotes if len(q.split()) >= 3]
            
            # Extract context for each quote (the sentence containing the quote)
            sentences = sent_tokenize(text)
            for quote in filtered_quotes:
                quote_pattern = re.escape(quote)
                found = False
                for sentence in sentences:
                    if re.search(quote_pattern, sentence):
                        quotes.append({
                            "quote": quote,
                            "context": sentence
                        })
                        found = True
                        break
                
                # If context not found, use the quote itself
                if not found and len(quote.split()) >= 5:
                    quotes.append({
                        "quote": quote,
                        "context": quote
                    })
            
            return quotes
        except Exception as e:
            st.error(f"Error extracting quotes: {str(e)}")
            return []
    
    def extract_named_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract potential named entities from text.
        This is a simplified approach as we don't have a full NER model for Indonesian.
        
        Args:
            text: Text to extract named entities from
            
        Returns:
            Dictionary of entity types and their instances
        """
        try:
            entities = {
                "organizations": [],
                "people": [],
                "locations": []
            }
            
            # Simple pattern matching for capital words not at the start of sentences
            sentences = sent_tokenize(text)
            for sentence in sentences:
                words = word_tokenize(sentence)
                for i, word in enumerate(words):
                    # Skip first word of sentence
                    if i == 0:
                        continue
                        
                    # Check if word starts with capital letter and is not a stopword
                    if word and word[0].isupper() and word.lower() not in self.stopwords:
                        # Check if it's part of a multiple-word entity
                        entity = word
                        j = i + 1
                        while j < len(words):
                            if words[j] and words[j][0].isupper():
                                entity += " " + words[j]
                                j += 1
                            else:
                                break
                        
                        # Simple heuristic categorization
                        if any(hint in sentence.lower() for hint in ["pt ", "perusahaan", "grup", "kelompok"]):
                            if entity not in entities["organizations"]:
                                entities["organizations"].append(entity)
                        elif any(hint in sentence.lower() for hint in ["kota", "provinsi", "kabupaten", "desa"]):
                            if entity not in entities["locations"]:
                                entities["locations"].append(entity)
                        else:
                            if entity not in entities["people"]:
                                entities["people"].append(entity)
            
            return entities
        except Exception as e:
            st.error(f"Error extracting named entities: {str(e)}")
            return {"organizations": [], "people": [], "locations": []}
    
    def analyze_text(self, text: str) -> Dict:
        """
        Perform comprehensive text analysis including keywords, phrases, quotes, and entities.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        if not text or len(text.strip()) < 50:
            st.warning("Teks terlalu pendek untuk dianalisis.")
            return {
                "keywords": [],
                "key_phrases": [],
                "quotes": [],
                "entities": {"organizations": [], "people": [], "locations": []}
            }
        
        analysis = {}
        
        # Extract keywords
        analysis["keywords"] = self.extract_keywords_tfidf(text, num_keywords=15)
        
        # Extract key phrases
        analysis["key_phrases"] = self.extract_keyphrases(text, num_phrases=5)
        
        # Extract quotes
        analysis["quotes"] = self.extract_quotes(text)
        
        # Extract entities
        analysis["entities"] = self.extract_named_entities(text)
        
        return analysis


# Fungsi untuk testing modul secara mandiri
def test_keyword_extractor():
    st.title("Test Keyword Extractor")
    
    # Initialize the extractor
    extractor = KeywordExtractor()
    
    # Get sample text input
    sample_text = st.text_area(
        "Masukkan teks siaran pers untuk dianalisis:",
        height=300,
        help="Teks dalam bahasa Indonesia, minimal 50 karakter."
    )
    
    if st.button("Analisis Teks"):
        if len(sample_text.strip()) < 50:
            st.error("Teks terlalu pendek. Mohon masukkan teks yang lebih panjang.")
        else:
            with st.spinner("Menganalisis teks..."):
                # Perform analysis
                analysis = extractor.analyze_text(sample_text)
                
                # Display results
                st.subheader("Kata Kunci")
                for keyword, score in analysis["keywords"]:
                    st.write(f"- {keyword}: {score:.4f}")
                
                st.subheader("Frasa Kunci")
                for phrase in analysis["key_phrases"]:
                    st.write(f"- {phrase}")
                
                st.subheader("Kutipan")
                for quote_data in analysis["quotes"]:
                    st.markdown(f"> \"{quote_data['quote']}\"")
                    st.write(f"Konteks: {quote_data['context']}")
                
                st.subheader("Entitas")
                for entity_type, entities in analysis["entities"].items():
                    if entities:
                        st.write(f"**{entity_type.capitalize()}**:")
                        for entity in entities:
                            st.write(f"- {entity}")


# Menjalankan modul ini secara mandiri jika dipanggil langsung
if __name__ == "__main__":
    test_keyword_extractor()
