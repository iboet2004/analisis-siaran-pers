import streamlit as st
from modules.document_processor import DocumentProcessor
from modules.keyword_extractor import KeywordExtractor
from modules.news_finder import NewsFinder

def main():
    st.sidebar.title("Navigasi")
    menu_options = ["Beranda", "Unggah Dokumen", 
                    "Ekstraksi Kata Kunci & Kutipan",
                    "Pencarian Berita"]
    
    choice = st.sidebar.radio("", menu_options)

    if choice == "Beranda":
        st.title("Analisis Siaran Pers Indonesia")
    
    elif choice == "Unggah Dokumen":
        result = DocumentProcessor.upload_document()
        
    elif choice ==...
