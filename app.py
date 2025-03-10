import streamlit as st
from modules.document_processor import DocumentProcessor
from modules.keyword_extractor import KeywordExtractor
from modules.news_finder import NewsFinder  # Import NewsFinder

# Set konfigurasi halaman
st.set_page_config(
    page_title="Analisis Siaran Pers Indonesia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Fungsi utama aplikasi."""
    # Sidebar navigation
    st.sidebar.title("Navigasi")
    menu_options = [
        "Beranda",
        "Unggah Dokumen",
        "Ekstraksi Kata Kunci",
        "Pencarian Berita",      # Menu baru untuk pencarian berita
        "Analisis Sentimen",     # Coming soon
        "Laporan & Visualisasi"  # Coming soon
    ]
    
    choice = st.sidebar.radio("", menu_options)
    
    if choice == "Unggah Dokumen":
        result = DocumentProcessor.upload_document()
        
        if result:
            text, filename = result
            
            # Simpan teks dalam session state untuk digunakan oleh modul berikutnya
            st.session_state.extracted_text = text
            
            if st.button("Lanjut ke Ekstraksi Kata Kunci"):
                st.session_state.menu_index = 2  # Index untuk menu Ekstraksi Kata Kunci

    elif choice == "Ekstraksi Kata Kunci":
        if "extracted_text" in st.session_state:
            keyword_extractor = KeywordExtractor()
            analysis = keyword_extractor.analyze_text(st.session_state.extracted_text)
            
            # Tampilkan hasil analisis...
            
            if analysis:
                keywords = [kw for kw, _ in analysis["keywords"]]
                
                # Menyimpan kata kunci dalam session state untuk digunakan di pencarian berita
                st.session_state.keywords = keywords
                
                if st.button("Cari Berita Terkait"):
                    api_key = st.secrets["news_api_key"]  # Ambil API key dari secrets Streamlit
                    
                    news_finder = NewsFinder(api_key)
                    articles = news_finder.search_news(keywords)
                    
                    # Tampilkan artikel yang ditemukan...
                    for article in articles:
                        st.write(f"### {article['title']}")
                        st.write(f"*{article['source']['name']}* - {article['publishedAt']}")
                        st.write(article['description'])
                        st.write(f"[Baca selengkapnya]({article['url']})")
                        st.markdown("---")

if __name__ == "__main__":
    main()
