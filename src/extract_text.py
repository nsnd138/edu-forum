import pdfplumber
import os


def extract_text_and_tables(pdf_path):
    """Trích xuất văn bản và bảng từ một file PDF."""
    text = ""
    tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n" if page.extract_text() else ""  # Tránh lỗi None
            extracted_tables = page.extract_tables()
            tables.extend(extracted_tables)  # Lưu tất cả bảng

    return text, tables


def process_all_pdfs(pdf_data_path):
    """Xử lý tất cả các file PDF trong thư mục."""
    all_text = ""
    all_tables = []

    for file in os.listdir(pdf_data_path):
        if file.endswith(".pdf"):
            text, tables = extract_text_and_tables(os.path.join(pdf_data_path, file))
            all_text += text + "\n"
            all_tables.extend(tables)

    return all_text, all_tables