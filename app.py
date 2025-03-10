"""
Aplikasi Analisis Siaran Pers Indonesia.
Aplikasi ini menganalisis dokumen siaran pers dan mencari berita terkait.
"""

import streamlit as st
from modules.document_processor import DocumentProcessor
from modules.keyword_extractor import KeywordExtractor

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
    2. **Analisis Kata Kunci** - Ekstrak kata kunci penting dan kutipan 
    3. **Pencarian Media** - Temukan berita terkait dari berbagai media (Coming Soon)
    4. **Analisis Sentimen** - Ketahui bagaimana media menanggapi (Coming Soon)
    5. **Visualisasi Data** - Lihat tren dan laporan interaktif (Coming Soon)
    
    **Untuk Memulai**: Pilih menu di sidebar dan ikuti petunjuk yang diberikan.
    """)

def display_extracted_text():
    """Menampilkan teks yang sudah diekstrak dari dokumen."""
    if "extracted_text" in st.session_state and "document_name" in st.session_state:
        text = st.session_state.extracted_text
        filename = st.session_state.document_name
        
        st.subheader(f"Teks dari {filename}")
        
        # Tampilkan teks yang diekstrak
        with st.expander("Lihat Teks Lengkap", expanded=False):
            st.text_area("Teks yang Diekstrak", text, height=300)
        
        # Tampilkan statistik
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"Jumlah kata: {len(text.split())}")
        with col2:
            st.info(f"Jumlah karakter: {len(text)}")
        
        return True
    return False

def main():
    """Fungsi utama aplikasi."""
    # Sidebar navigation
    st.sidebar.title("Navigasi")
    menu_options = [
        "Beranda",
        "Unggah Dokumen",
        "Ekstraksi Kata Kunci",
        "Pencarian Berita",      # Coming soon
        "Analisis Sentimen",     # Coming soon
        "Laporan & Visualisasi"  # Coming soon
    ]
    
    menu_icons = ["🏠", "📄", "🔑", "🔍", "📊", "📈"]
    
    # Tambahkan label "Coming Soon" untuk fitur yang belum tersedia
    menu_labels = []
    for i, (option, icon) in enumerate(zip(menu_options, menu_icons)):
        if i >= 3:  # Menu ke-3 dst masih coming soon
            menu_labels.append(f"{icon} {option} (Coming Soon)")
        else:
            menu_labels.append(f"{icon} {option}")
    
    choice = st.sidebar.radio("", menu_labels, index=0)
    
    # Inisialisasi objek KeywordExtractor
    keyword_extractor = KeywordExtractor()
    
    # Tampilkan konten berdasarkan pilihan menu
    if "Beranda" in choice:
        show_welcome()
    
    elif "Unggah Dokumen" in choice:
        result = DocumentProcessor.upload_document()
        
        if result:
            text, filename = result
            
            # Simpan teks dalam session state untuk digunakan oleh modul berikutnya
            st.session_state.extracted_text = text
            st.session_state.document_name = filename
            
            # Tampilkan teks yang diekstrak
            with st.expander("Lihat Teks Lengkap", expanded=True):
                st.text_area("Teks yang Diekstrak", text, height=400)
            
            # Tampilkan statistik
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"Jumlah kata: {len(text.split())}")
            with col2:
                st.info(f"Jumlah karakter: {len(text)}")
            
            # Tambahkan tombol untuk melanjutkan ke langkah berikutnya
            if st.button("Lanjut ke Ekstraksi Kata Kunci"):
                st.session_state.menu_index = 2  # Index untuk menu Ekstraksi Kata Kunci
                st.experimental_rerun()
    
    elif "Ekstraksi Kata Kunci" in choice:
        # Cek apakah ada teks yang sudah diekstrak
        if not display_extracted_text():
            st.warning("Anda belum mengunggah dokumen. Silakan unggah dokumen terlebih dahulu.")
            if st.button("Kembali ke Unggah Dokumen"):
                st.session_state.menu_index = 1  # Index untuk menu Unggah Dokumen
                st.experimental_rerun()
            return
        
        # Proses ekstraksi kata kunci
        with st.spinner("Menganalisis teks..."):
            if "analysis_result" not in st.session_state:
                # Lakukan analisis jika belum ada hasil
                text = st.session_state.extracted_text
                analysis = keyword_extractor.analyze_text(text)
                st.session_state.analysis_result = analysis
            else:
                # Gunakan hasil yang sudah ada
                analysis = st.session_state.analysis_result
        
        # Tampilkan hasil analisis
        if analysis:
            st.subheader("Hasil Analisis")
            
            tab1, tab2, tab3 = st.tabs(["Kata Kunci & Frasa", "Kutipan", "Entitas"])
            
            with tab1:
                # Tampilkan kata kunci
                st.write("#### Kata Kunci")
                keyword_data = []
                for keyword, score in analysis["keywords"]:
                    keyword_data.append({"Kata Kunci": keyword, "Skor": f"{score:.4f}"})
                
                import pandas as pd
                keywords_df = pd.DataFrame(keyword_data)
                st.dataframe(keywords_df, use_container_width=True)
                
                # Tampilkan frasa kunci
                st.write("#### Frasa Kunci")
                for i, phrase in enumerate(analysis["key_phrases"], 1):
                    st.markdown(f"**{i}.** {phrase}")
            
            with tab2:
                # Tampilkan kutipan
                if analysis["quotes"]:
                    for i, quote_data in enumerate(analysis["quotes"], 1):
                        st.markdown(f"**Kutipan {i}:**")
                        st.markdown(f"> \"{quote_data['quote']}\"")
                        st.write(f"**Konteks:** {quote_data['context']}")
                        st.markdown("---")
                else:
                    st.info("Tidak ditemukan kutipan dalam teks.")
            
            with tab3:
                # Tampilkan entitas
                has_entities = False
                for entity_type, entities in analysis["entities"].items():
                    if entities:
                        has_entities = True
                        st.write(f"#### {entity_type.capitalize()}")
                        for entity in entities:
                            st.write(f"- {entity}")
                        st.markdown("---")
                
                if not has_entities:
                    st.info("Tidak ditemukan entitas dalam teks.")
            
            # Tambahkan tombol untuk melanjutkan ke langkah berikutnya
            st.success("Ekstraksi kata kunci dan kutipan berhasil! Anda dapat melanjutkan ke langkah berikutnya.")
            if st.button("Reset Analisis"):
                if "analysis_result" in st.session_state:
                    del st.session_state.analysis_result
                st.experimental_rerun()
    
    elif "Pencarian Berita" in choice or "Analisis Sentimen" in choice or "Laporan" in choice:
        st.info("Fitur ini sedang dalam pengembangan dan akan segera tersedia.")
        # Placeholder untuk fitur yang akan datang
    
    # Tambahkan info di sidebar
    st.sidebar.markdown("---")
    st.sidebar.info(
        "Aplikasi ini memproses dokumen siaran pers dalam Bahasa Indonesia "
        "dan menganalisis pemberitaan terkait dari berbagai media."
    )
    
    # Tambahkan footer
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2025 Analisis Siaran Pers Indonesia")

if __name__ == "__main__":
    main()
