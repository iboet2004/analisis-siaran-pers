"""
Aplikasi Analisis Siaran Pers Indonesia.
Aplikasi ini menganalisis dokumen siaran pers dan mencari berita terkait.
"""

import streamlit as st
from modules.document_processor import DocumentProcessor

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
    2. **Analisis Kata Kunci** - Ekstrak kata kunci penting dan kutipan (Coming Soon)
    3. **Pencarian Media** - Temukan berita terkait dari berbagai media (Coming Soon)
    4. **Analisis Sentimen** - Ketahui bagaimana media menanggapi (Coming Soon)
    5. **Visualisasi Data** - Lihat tren dan laporan interaktif (Coming Soon)
    
    **Untuk Memulai**: Pilih menu di sidebar dan ikuti petunjuk yang diberikan.
    """)

def main():
    """Fungsi utama aplikasi."""
    # Sidebar navigation
    st.sidebar.title("Navigasi")
    menu_options = [
        "Beranda",
        "Unggah Dokumen",
        "Ekstraksi Kata Kunci",  # Coming soon
        "Pencarian Berita",      # Coming soon
        "Analisis Sentimen",     # Coming soon
        "Laporan & Visualisasi"  # Coming soon
    ]
    
    menu_icons = ["🏠", "📄", "🔑", "🔍", "📊", "📈"]
    
    # Tambahkan label "Coming Soon" untuk fitur yang belum tersedia
    menu_labels = [
        f"{icon} {option}" if i < 2 else f"{icon} {option} (Coming Soon)" 
        for i, (option, icon) in enumerate(zip(menu_options, menu_icons))
    ]
    
    choice = st.sidebar.radio("", menu_labels, index=0)
    
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
            st.success("Dokumen berhasil diekstrak! Fitur analisis lebih lanjut akan segera hadir.")
    
    elif "Ekstraksi Kata Kunci" in choice or "Pencarian Berita" in choice or "Analisis Sentimen" in choice or "Laporan" in choice:
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
