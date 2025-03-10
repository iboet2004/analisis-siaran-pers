"""
Aplikasi Analisis Siaran Pers Indonesia.
Aplikasi ini menganalisis dokumen siaran pers dan mencari berita terkait.
"""

import streamlit as st
import pandas as pd
from .modules.document_processor import DocumentProcessor
from .modules.keyword_extractor import KeywordExtractor
from .modules.news_finder import NewsFinder  # Import modul pencarian berita

import nltk
import os

# Atur variabel lingkungan NLTK_DATA jika belum diatur
nltk_data_path = os.path.join(os.sep, 'tmp', 'nltk_data')
if 'NLTK_DATA' not in os.environ:
    os.environ['NLTK_DATA'] = nltk_data_path

# Buat direktori jika belum ada
os.makedirs(nltk_data_path, exist_ok=True)

# Tambahkan path ke NLTK
nltk.data.path.append(nltk_data_path)

# Download resource punkt jika belum ada
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', download_dir=nltk_data_path)

# Set konfigurasi halaman
st.set_page_config(
    page_title="Analisis Siaran Pers Indonesia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inisialisasi session state
def init_session_state():
    """Inisialisasi variabel session state yang diperlukan"""
    if "extracted_text" not in st.session_state:
        st.session_state.extracted_text = ""
    if "document_name" not in st.session_state:
        st.session_state.document_name = ""
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "keywords" not in st.session_state:
        st.session_state.keywords = []
    if "quotes" not in st.session_state:
        st.session_state.quotes = []
    if "news_results" not in st.session_state:
        st.session_state.news_results = []
    if "menu_index" not in st.session_state:
        st.session_state.menu_index = 0

# Panggil inisialisasi session state
init_session_state()

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
    
    try:
        # Buat DataFrame dari hasil berita
        news_df = pd.DataFrame(news_results)
        st.dataframe(news_df, use_container_width=True)
        
        # Tampilkan artikel dalam format yang lebih detail
        for article in news_results:
            st.write(f"### {article['title']}")
            source_name = article.get('source', {}).get('name', 'Sumber tidak diketahui')
            published_at = article.get('publishedAt', 'Waktu tidak diketahui')
            description = article.get('description', 'Tidak ada deskripsi')
            url = article.get('url', '#')
            
            st.write(f"*{source_name}* - {published_at}")
            st.write(description)
            st.write(f"[Baca selengkapnya]({url})")
            st.markdown("---")
    except Exception as e:
        st.error(f"Error menampilkan hasil berita: {str(e)}")

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
    
    # Gunakan menu_index dari session_state jika ada
    default_index = st.session_state.get("menu_index", 0)
    choice = st.sidebar.radio("", menu_options, index=default_index)
    
    # Reset menu_index setelah digunakan
    st.session_state.menu_index = menu_options.index(choice)
    
    keyword_extractor = KeywordExtractor()
    
    if choice == "Beranda":
        show_welcome()
    
    elif choice == "Unggah Dokumen":
        st.write("### Unggah Dokumen Siaran Pers")
        result = DocumentProcessor.upload_document()
        if result:
            text, filename = result
            st.session_state.extracted_text = text
            st.session_state.document_name = filename
            st.success(f"Dokumen '{filename}' berhasil diunggah dan diproses!")
            
            # Tampilkan contoh teks
            with st.expander("Pratinjau Teks", expanded=False):
                st.text_area("Teks yang Diekstrak", text[:1000] + ("..." if len(text) > 1000 else ""), height=200)
            
            if st.button("Lanjut ke Ekstraksi Kata Kunci"):
                st.session_state.menu_index = 2  # Index untuk menu Ekstraksi Kata Kunci
                st.experimental_rerun()
    
    elif choice == "Ekstraksi Kata Kunci & Kutipan":
        if not st.session_state.extracted_text:
            st.warning("Anda belum mengunggah dokumen.")
            if st.button("Kembali ke Unggah Dokumen"):
                st.session_state.menu_index = 1  # Index untuk menu Unggah Dokumen
                st.experimental_rerun()
            return
            
        with st.spinner("Menganalisis teks..."):
            if not st.session_state.analysis_result:
                text = st.session_state.extracted_text
                try:
                    analysis = keyword_extractor.analyze_text(text)
                    st.session_state.analysis_result = analysis
                except Exception as e:
                    st.error(f"Error saat menganalisis teks: {str(e)}")
                    analysis = {
                        "keywords": [],
                        "key_phrases": [],
                        "quotes": [],
                        "entities": {"organizations": [], "people": [], "locations": []}
                    }
            else:
                analysis = st.session_state.analysis_result
        
        st.subheader(f"Hasil Analisis Dokumen: {st.session_state.document_name}")
        
        # Tampilkan kata kunci
        st.write("### Kata Kunci")
        if not analysis["keywords"]:
            st.info("Tidak ada kata kunci yang ditemukan.")
        else:
            keywords = [kw for kw, _ in analysis["keywords"]]
            st.session_state.keywords = keywords  # Simpan kata kunci untuk pencarian berita
            st.write(", ".join(keywords))
            
            # Tampilkan skor kata kunci dalam tabel
            kw_df = pd.DataFrame(analysis["keywords"], columns=["Kata Kunci", "Skor"])
            st.dataframe(kw_df, use_container_width=True, hide_index=True)
        
        # Tampilkan kutipan
        st.write("### Kutipan")
        if not analysis["quotes"]:
            st.info("Tidak ada kutipan yang ditemukan.")
        else:
            quotes = [quote_data['quote'] for quote_data in analysis["quotes"]]
            st.session_state.quotes = quotes  # Simpan kutipan untuk pencarian berita
            for quote in quotes:
                st.markdown(f"> \"{quote}\"")
        
        # Tampilkan entitas
        with st.expander("Entitas", expanded=False):
            for entity_type, entities in analysis["entities"].items():
                if entities:
                    st.write(f"**{entity_type.capitalize()}**:")
                    for entity in entities:
                        st.write(f"- {entity}")
            
        if st.button("Cari Berita Terkait"):
            st.session_state.menu_index = 3  # Index untuk menu Pencarian Berita
            st.experimental_rerun()
        
        # Tambahkan opsi analisis ulang
        if st.button("Analisis Ulang"):
            st.session_state.analysis_result = None
            st.experimental_rerun()
    
    elif choice == "Pencarian Berita":
        if not st.session_state.analysis_result:
            st.warning("Anda harus mengekstrak kata kunci terlebih dahulu!")
            if st.button("Kembali ke Ekstraksi Kata Kunci"):
                st.session_state.menu_index = 2
                st.experimental_rerun()
            return
        
        keywords = [kw for kw, _ in st.session_state.analysis_result["keywords"]]
        quotes = [quote_data['quote'] for quote_data in st.session_state.analysis_result["quotes"]]
        
        if not keywords and not quotes:
            st.warning("Tidak ada kata kunci atau kutipan yang ditemukan.")
            return
        
        # Tampilkan kata kunci yang akan digunakan
        st.write("### Kata Kunci untuk Pencarian")
        st.write(", ".join(keywords))
        
        # Tombol untuk pencarian berita
        if st.button("Cari Berita Sekarang"):
            try:
                # Ambil API key dari secrets Streamlit
                api_key = st.secrets["news_api_key"]
                news_finder = NewsFinder(api_key)
                
                with st.spinner("Mengambil berita..."):
                    news_results = news_finder.fetch_news(keywords, quotes, max_results=5)
                    st.session_state.news_results = news_results
                
                # Tampilkan hasil pencarian
                display_news_results(news_results)
            except Exception as e:
                st.error(f"Error saat mencari berita: {str(e)}")
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"Dokumen aktif: {st.session_state.document_name or 'Belum ada dokumen'}")
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2025 Analisis Siaran Pers Indonesia")

if __name__ == "__main__":
    main()
