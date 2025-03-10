"""
Document Processor Module for Analisis Siaran Pers.
Handles document uploads and text extraction from various file formats.
"""

import io
import streamlit as st
import PyPDF2
import docx2txt
from typing import Optional, Tuple

class DocumentProcessor:
    """Class to handle document processing operations."""
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF file."""
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
            return text
        except Exception as e:
            st.error(f"Error saat mengekstrak teks dari PDF: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX file."""
        try:
            text = docx2txt.process(io.BytesIO(file_content))
            return text
        except Exception as e:
            st.error(f"Error saat mengekstrak teks dari DOCX: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_txt(file_content: bytes) -> str:
        """Extract text from TXT file."""
        try:
            text = file_content.decode("utf-8")
            return text
        except UnicodeDecodeError:
            try:
                # Coba dengan encoding lain jika utf-8 gagal
                text = file_content.decode("latin-1")
                return text
            except Exception as e:
                st.error(f"Error saat mengekstrak teks dari TXT: {e}")
                return ""
    
    @staticmethod
    def extract_text(uploaded_file) -> Tuple[str, bool]:
        """
        Extract text from uploaded file based on file extension.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Tuple of (extracted_text, success_status)
        """
        if uploaded_file is None:
            return "", False
        
        file_extension = uploaded_file.name.split(".")[-1].lower()
        file_content = uploaded_file.getvalue()
        
        if file_extension == "pdf":
            text = DocumentProcessor.extract_text_from_pdf(file_content)
        elif file_extension in ["docx", "doc"]:
            text = DocumentProcessor.extract_text_from_docx(file_content)
        elif file_extension == "txt":
            text = DocumentProcessor.extract_text_from_txt(file_content)
        else:
            st.error(f"Format file tidak didukung: {file_extension}")
            return "", False
        
        if text.strip():
            return text, True
        else:
            st.warning("Tidak ada teks yang dapat diekstrak dari dokumen.")
            return "", False
    
    @staticmethod
    def upload_document() -> Optional[Tuple[str, str]]:
        """
        Handle document upload in Streamlit.
        
        Returns:
            Tuple of (extracted_text, filename) if successful, None otherwise
        """
        st.write("### Unggah Dokumen Siaran Pers")
        
        uploaded_file = st.file_uploader(
            "Pilih dokumen siaran pers dalam format PDF, DOCX, atau TXT",
            type=["pdf", "docx", "doc", "txt"],
            help="Pastikan file tidak terenkripsi dan dapat dibaca."
        )
        
        if uploaded_file is not None:
            with st.spinner("Mengekstrak teks dari dokumen..."):
                text, success = DocumentProcessor.extract_text(uploaded_file)
                
                if success:
                    st.success(f"Berhasil mengekstrak teks dari {uploaded_file.name}")
                    return text, uploaded_file.name
                else:
                    st.error("Gagal mengekstrak teks. Silakan coba file lain.")
                    return None
        
        return None

# Fungsi untuk testing modul ini secara mandiri
def test_document_processor():
    st.title("Test Document Processor")
    result = DocumentProcessor.upload_document()
    
    if result:
        text, filename = result
        st.subheader(f"Teks dari {filename}")
        
        # Tambahkan text area untuk menampilkan hasil ekstraksi
        with st.expander("Lihat Teks Lengkap", expanded=True):
            st.text_area("Teks yang Diekstrak", text, height=400)
        
        # Tambahkan statistik sederhana
        word_count = len(text.split())
        char_count = len(text)
        st.write(f"Jumlah kata: {word_count}")
        st.write(f"Jumlah karakter: {char_count}")

# Menjalankan modul ini secara mandiri jika dipanggil langsung
if __name__ == "__main__":
    test_document_processor()
