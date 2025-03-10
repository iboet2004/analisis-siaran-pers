"""
Aplikasi Analisis Siaran Pers Indonesia.
Aplikasi ini menganalisis dokumen siaran pers dan mencari berita terkait.
"""

import streamlit as st
import pandas as pd
import os
import nltk
from datetime import datetime
from modules.document_processor import DocumentProcessor
from modules.keyword_extractor import KeywordExtractor
from modules.news_finder import NewsFinder

# Atur variabel lingkungan NLTK_DATA jika belum diatur
nltk_data_path = os.path.join(os.sep, 'tmp', 'nltk_data')
if 'NLTK_DATA' not in os.environ:
    os.environ['NLTK_DATA'] = nltk_data_path

# Coba buat direktori jika belum ada
try:
    os.makedirs(nltk_data_path, exist_ok=True)
except OSError as e:
    st.error(f"Error membuat direktori {nltk_data_path}: {e}")

# Download resource NLTK jika belum ada
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    with st.spinner("Mengunduh resource NLTK..."):
        nltk.download('punkt', download_dir=nltk_data_path)
        nltk.download('stopwords', download_dir=nltk_data_path)

# Pastikan path resource NLTK sudah benar
nltk.data.path.append(nltk_data_path)

# Set konfigurasi halaman
st.set_page_config(
    page_title="Analisis Siaran Pers Indonesia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inisialisasi session state jika belum ada
if 'menu_index' not in st.session_state:
    st.session_state.menu_index = 0

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
    
    # Menampilkan tanggal hari ini
    today = datetime.now().strftime("%d %B %Y")
    st.sidebar.write(f"**Tanggal**: {today}")

def display_news_results(news_results):
    """Menampilkan hasil pencarian berita dalam format yang mudah dibaca."""
    st.subheader("Hasil Pencarian Berita")
    if not news_results:
        st.warning("Tidak ada berita yang ditemukan untuk kata kunci ini.")
        return
    
    # Tampilkan artikel dalam format card
    for i, article in enumerate(news_results):
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Placeholder image (bisa diganti dengan gambar article jika available)
            st.image("https://via.placeholder.com/150", use_column_width=True)
        
        with col2:
            st.markdown(f"### {article['title']}")
            
            # Format tanggal publikasi jika tersedia
            pub_date = article.get('publishedAt', '')
            if pub_date:
                try:
                    date_obj = datetime.strptime(pub_date[:19], "%Y-%m-%dT%H:%M:%S")
                    formatted_date = date_obj.strftime("%d %B %Y, %H:%M")
                except ValueError:
                    formatted_date = pub_date
            else:
                formatted_date = "Tanggal tidak tersedia"
                
            st.write(f"*{article['source']['name']}* - {formatted_date}")
            
            # Tampilkan deskripsi jika tersedia
            if article.get('description'):
                st.write(article['description'])
            
            st.write(f"[Baca selengkapnya]({article['url']})")
        
        st.markdown("---")

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
    
    # Gunakan session state untuk mengingat pilihan menu
    choice = st.sidebar.radio("", menu_options, index=st.session_state.menu_index)
    st.session_state.menu_index = menu_options.index(choice)
    
    # Inisialisasi extractor
    keyword_extractor = KeywordExtractor()
    
    if choice == "Beranda":
        show_welcome()
    
    elif choice == "Unggah Dokumen":
        st.title("Unggah Dokumen Siaran Pers")
        st.write("Unggah dokumen siaran pers untuk dianalisis.")
        
        result = DocumentProcessor.upload_document()
        if result:
            text, filename = result
            st.session_state.extracted_text = text
            st.session_state.document_name = filename
            
            # Tampilkan preview teks
            with st.expander("Pratinjau Teks", expanded=False):
                st.text_area("", text, height=200, disabled=True)
            
            st.success(f"Dokumen '{filename}' berhasil diunggah dan diproses!")
            
            if st.button("Lanjut ke Ekstraksi Kata Kunci"):
                st.session_state.menu_index = 2  # Index untuk menu Ekstraksi Kata Kunci
                st.experimental_rerun()
    
    elif choice == "Ekstraksi Kata Kunci & Kutipan":
        st.title("Ekstraksi Kata Kunci & Kutipan")
        
        if "extracted_text" not in st.session_state:
            st.warning("Anda belum mengunggah dokumen. Silakan unggah dokumen terlebih dahulu.")
            if st.button("Kembali ke Unggah Dokumen"):
                st.session_state.menu_index = 1
                st.experimental_rerun()
            return
        
        # Tampilkan nama dokumen
        st.subheader(f"Dokumen: {st.session_state.get('document_name', 'Dokumen')}")
        
        # Tombol untuk menganalisis ulang
        reanalyze = st.button("Analisis Ulang")
        
        with st.spinner("Menganalisis teks..."):
            if "analysis_result" not in st.session_state or reanalyze:
                text = st.session_state.extracted_text
                analysis = keyword_extractor.analyze_text(text)
                st.session_state.analysis_result = analysis
            else:
                analysis = st.session_state.analysis_result
        
        # Tampilkan hasil analisis dalam 3 kolom
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.write("### Kata Kunci")
            keywords = [kw for kw, score in analysis["keywords"]]
            st.session_state.keywords = keywords
            
            for kw, score in analysis["keywords"]:
                st.write(f"- {kw} ({score:.2f})")
        
        with col2:
            st.write("### Frasa Kunci")
            for phrase in analysis["key_phrases"]:
                st.write(f"- {phrase[:100]}...")
        
        with col3:
            st.write("### Entitas")
            for entity_type, entities in analysis["entities"].items():
                if entities:
                    st.write(f"**{entity_type.capitalize()}**:")
                    for entity in entities[:5]:  # Limit to top 5
                        st.write(f"- {entity}")
        
        # Tampilkan kutipan
        st.write("### Kutipan")
        if analysis["quotes"]:
            for i, quote_data in enumerate(analysis["quotes"]):
                with st.expander(f"Kutipan {i+1}", expanded=i==0):
                    st.markdown(f"> \"{quote_data['quote']}\"")
                    st.write(f"Konteks: {quote_data['context']}")
        else:
            st.warning("Tidak ada kutipan yang ditemukan dalam dokumen.")
        
        # Simpan kutipan untuk pencarian berita
        st.session_state.quotes = [q["quote"] for q in analysis["quotes"]]
            
        if st.button("Cari Berita Terkait"):
            st.session_state.menu_index = 3  # Index untuk menu Pencarian Berita
            st.experimental_rerun()
    
    elif choice == "Pencarian Berita":
        st.title("Pencarian Berita Terkait")
        
        if "analysis_result" not in st.session_state:
            st.warning("Anda harus mengekstrak kata kunci terlebih dahulu!")
            if st.button("Kembali ke Ekstraksi Kata Kunci"):
                st.session_state.menu_index = 2
                st.experimental_rerun()
            return
        
        # Ambil keywords dan quotes dari session state
        keywords = st.session_state.get("keywords", [])
        quotes = st.session_state.get("quotes", [])
        
        # Tampilkan kata kunci yang digunakan
        st.write("### Kata Kunci Pencarian")
        st.write(", ".join(keywords[:5]))  # Tampilkan 5 kata kunci teratas
        
        # Opsi untuk menyesuaikan pencarian
        st.write("### Opsi Pencarian")
        language = st.selectbox("Bahasa", ["id", "en"], index=0)
        max_results = st.slider("Jumlah Hasil", min_value=3, max_value=20, value=5)
        
        # Tombol pencarian
        search_button = st.button("Cari Berita")
        
        if search_button or "news_results" in st.session_state:
            if not keywords and not quotes:
                st.warning("Tidak ada kata kunci atau kutipan yang ditemukan.")
            else:
                try:
                    # Dapatkan API key dari secrets Streamlit
                    api_key = st.secrets["news_api_key"]
                    news_finder = NewsFinder(api_key)
                    
                    with st.spinner("Mengambil berita..."):
                        if search_button or "news_results" not in st.session_state:
                            news_results = news_finder.fetch_news(keywords, quotes, max_results=max_results)
                            st.session_state.news_results = news_results
                        
                        display_news_results(st.session_state.news_results)
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat mencari berita: {str(e)}")
                    st.info("Catatan: Untuk menggunakan fitur pencarian berita, pastikan API key telah dikonfigurasi di secrets.toml")
    
    elif choice == "Analisis Sentimen (Coming Soon)":
        st.title("Analisis Sentimen Media")
        st.info("Fitur ini akan segera hadir. Anda akan dapat menganalisis sentimen pemberitaan media terhadap siaran pers Anda.")
        
        # Tampilkan placeholder UI
        st.write("### Fitur yang akan datang:")
        st.write("- Analisis sentimen media dari berita terkait")
        st.write("- Perbandingan sentimen antar media")
        st.write("- Visualisasi tren sentimen")
        st.write("- Laporan sentimen terperinci")
    
    elif choice == "Laporan & Visualisasi (Coming Soon)":
        st.title("Laporan & Visualisasi")
        st.info("Fitur ini akan segera hadir. Anda akan dapat melihat visualisasi dan laporan terperinci dari analisis siaran pers.")
        
        # Tampilkan placeholder UI
        st.write("### Fitur yang akan datang:")
        st.write("- Dashboard interaktif")
        st.write("- Grafik perbandingan kata kunci")
        st.write("- Visualisasi jejaring entitas")
        st.write("- Laporan terpadu yang dapat diunduh")
    
    st.sidebar.markdown("---")
    st.sidebar.info("Aplikasi ini memproses dokumen siaran pers dan mencari berita terkait.")
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2025 Analisis Siaran Pers Indonesia")

if __name__ == "__main__":
    main()
