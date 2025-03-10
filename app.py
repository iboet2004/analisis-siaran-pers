"""
Aplikasi Analisis Siaran Pers Indonesia.
Aplikasi ini menganalisis dokumen siaran pers dan mencari berita terkait.
"""

import streamlit as st
import pandas as pd
from modules.document_processor import DocumentProcessor
from modules.keyword_extractor import KeywordExtractor
from modules.news_finder import NewsFinder  # Import modul pencarian berita

import nltk
import os

# Atur variabel lingkungan NLTK_DATA jika belum diatur
nltk_data_path = os.path.join(os.sep, 'tmp', 'nltk_data')
if 'NLTK_DATA' not in os.environ:
    os.environ['NLTK_DATA'] = nltk_data_path

# Coba buat direktori jika belum ada
try:
    os.makedirs(nltk_data_path, exist_ok=True)
except OSError as e:
    print(f"Error membuat direktori {nltk_data_path}: {e}")

# Download resource punkt jika belum ada
try:
    nltk.data.find('tokenizers/punkt/PY3/english.pickle')
except LookupError:
    nltk.download('punkt', download_dir=nltk_data_path)

# Pastikan path resource NLTK sudah benar
nltk.data.path.append(nltk_data_path)

# Set konfigurasi halaman
st.set_page_config(
    page_title="Analisis Siaran Pers Indonesia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def show_welcome():
    """Menampilkan pesan selamat datang dan informasi aplikasi."""
    st.title("Analisis Siaran Pers Indonesia")
    
    st.markdown("""
    ### Selamat Datang di Aplikasi Analisis Siaran Pers
    
    Aplikasi ini membantu Anda menganalisis dokumen siaran pers dalam Bahasa Indonesia dengan:
    
    1. **Ekstraksi Teks** - Unggah dokumen PDF, DOCX, atau TXT
    2. **Analisis Kata Kunci & Kutipan** - Ekstrak kata kunci penting dan kutipan 
    3. **Pencarian Media** - Temukan berita terkait dari berbagai media
    4. **Analisis Sentimen** - Ketahui bagaimana media menanggapi (Coming Soon)
    5. **Visualisasi Data** - Lihat tren dan laporan interaktif (Coming Soon)
    
    **Untuk Memulai**: Pilih menu di sidebar dan ikuti petunjuk yang diberikan.
    """)

def display_news_results(news_results):
    """Menampilkan hasil pencarian berita dalam bentuk tabel."""
    st.subheader("Hasil Pencarian Berita")
    if not news_results:
        st.warning("Tidak ada berita yang ditemukan untuk kata kunci ini.")
        return
    
    news_df = pd.DataFrame(news_results)
    st.dataframe(news_df, use_container_width=True)

def main():
    """Fungsi utama aplikasi."""
    st.sidebar.title("Navigasi")
    menu_options = [
        "Beranda",
        "Unggah Dokumen",
        "Ekstraksi Kata Kunci & Kutipan",
        "Pencarian Berita",
        "Analisis Sentimen (Coming Soon)",
        "Laporan & Visualisasi (Coming Soon)"
    ]
    choice = st.sidebar.radio("", menu_options, index=0)
    
    keyword_extractor = KeywordExtractor()
    
    if choice == "Beranda":
        show_welcome()
    
    elif choice == "Unggah Dokumen":
        result = DocumentProcessor.upload_document()
        if result:
            text, filename = result
            st.session_state.extracted_text = text
            st.session_state.document_name = filename
            st.success("Dokumen berhasil diunggah dan diproses!")
    
    elif choice == "Ekstraksi Kata Kunci & Kutipan":
        if "extracted_text" not in st.session_state:
            st.warning("Anda belum mengunggah dokumen.")
            return
        with st.spinner("Menganalisis teks..."):
            if "analysis_result" not in st.session_state:
                text = st.session_state.extracted_text
                analysis = keyword_extractor.analyze_text(text)
                st.session_state.analysis_result = analysis
            else:
                analysis = st.session_state.analysis_result
        
        st.subheader("Hasil Analisis Kata Kunci & Kutipan")
        
        st.write("### Kata Kunci")
        keywords = [kw for kw, _ in analysis["keywords"]]
        st.write(", ".join(keywords))
        
        st.write("### Kutipan")
        quotes = [quote_data['quote'] for quote_data in analysis["quotes"]]
        for quote in quotes:
            st.markdown(f"> \"{quote}\"")
    
    elif choice == "Pencarian Berita":
        if "analysis_result" not in st.session_state:
            st.warning("Anda harus mengekstrak kata kunci terlebih dahulu!")
            return
        
        keywords = [kw for kw, _ in st.session_state.analysis_result["keywords"]]
        quotes = [quote_data['quote'] for quote_data in st.session_state.analysis_result["quotes"]]
        
        if not keywords and not quotes:
            st.warning("Tidak ada kata kunci atau kutipan yang ditemukan.")
        else:
            news_finder = NewsFinder()
            with st.spinner("Mengambil berita..."):
                news_results = news_finder.fetch_news(keywords, quotes, max_results=5)
                st.session_state.news_results = news_results
            display_news_results(st.session_state.news_results)
    
    st.sidebar.markdown("---")
    st.sidebar.info("Aplikasi ini memproses dokumen siaran pers dan mencari berita terkait.")
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2025 Analisis Siaran Pers Indonesia")

if __name__ == "__main__":
    main()
