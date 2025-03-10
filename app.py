import streamlit as st
import pandas as pd
from modules.document_processor import DocumentProcessor
from modules.keyword_extractor import KeywordExtractor
from modules.news_finder import NewsFinder

# Konfigurasi halaman Streamlit
st.set_page_config(page_title="Dashboard Analisis Siaran Pers", layout="wide")

# Inisialisasi modul
api_key = st.secrets["news_api_key"]
news_finder = NewsFinder(api_key)
keyword_extractor = KeywordExtractor()

def display_news_results(news_results):
    """Menampilkan hasil pencarian berita dalam bentuk tabel."""
    st.subheader("Hasil Pencarian Berita")
    if not news_results:
        st.warning("Tidak ada berita yang ditemukan untuk kata kunci ini.")
        return
    
    df = pd.DataFrame(news_results)
    st.dataframe(df, use_container_width=True)

# Sidebar navigasi
st.sidebar.title("Navigasi")
menu_options = ["Beranda", "Unggah Dokumen", "Ekstraksi Kata Kunci", "Pencarian Berita"]
choice = st.sidebar.radio("Pilih menu:", menu_options)

if choice == "Beranda":
    st.title("Dashboard Analisis Siaran Pers")
    st.write("Aplikasi ini memungkinkan Anda menganalisis dokumen siaran pers dan mencari berita terkait.")
    st.write("Gunakan menu di samping untuk memulai analisis.")

elif choice == "Unggah Dokumen":
    st.title("Unggah Dokumen Siaran Pers")
    result = DocumentProcessor.upload_document()
    if result:
        text, filename = result
        st.session_state.extracted_text = text
        st.session_state.document_name = filename
        st.success("Dokumen berhasil diunggah dan diproses!")

elif choice == "Ekstraksi Kata Kunci":
    st.title("Ekstraksi Kata Kunci & Kutipan")
    if "extracted_text" not in st.session_state:
        st.warning("Anda harus mengunggah dokumen terlebih dahulu!")
    else:
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
            st.markdown(f"> "{quote}"")

elif choice == "Pencarian Berita":
    st.title("Pencarian Berita")
    if "analysis_result" not in st.session_state:
        st.warning("Anda harus mengekstrak kata kunci terlebih dahulu!")
    else:
        keywords = [kw for kw, _ in st.session_state.analysis_result["keywords"]]
        quotes = [quote_data['quote'] for quote_data in st.session_state.analysis_result["quotes"]]
        
        if not keywords and not quotes:
            st.warning("Tidak ada kata kunci atau kutipan yang ditemukan.")
        else:
            with st.spinner("Mengambil berita..."):
                news_results = news_finder.fetch_news(keywords, max_results=5)
                st.session_state.news_results = news_results
            display_news_results(st.session_state.news_results)

st.sidebar.markdown("---")
st.sidebar.info("Aplikasi ini memproses dokumen siaran pers dan mencari berita terkait.")
st.sidebar.caption("© 2025 Analisis Siaran Pers")
