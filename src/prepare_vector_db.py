# -*- encoding: utf-8 -*-
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from extract_text import process_all_pdfs


# Khai bao bien
pdf_data_path = "../data"
vector_db_path = "../vectorstores/db_faiss"
embedding_model_path = "../models/all-MiniLM-L6-v2-f16.gguf"

def format_table_as_text(table):
    """Chuyển bảng thành chuỗi văn bản dễ hiểu."""
    formatted_text = ""
    for row in table:
        # Chuyển None thành chuỗi rỗng
        clean_row = [str(cell) if cell is not None else "" for cell in row]
        formatted_text += " | ".join(clean_row) + "\n"  # Ghép các cột lại thành dòng văn bản
    return formatted_text

def create_vector_db():
    """Tạo FAISS vector database từ dữ liệu PDF."""
    # Lấy văn bản & bảng từ PDF
    raw_text, tables = process_all_pdfs(pdf_data_path)

    # Chuyển bảng thành văn bản và ghép vào dữ liệu
    formatted_tables = [format_table_as_text(table) for table in tables]
    all_text = raw_text + "\n".join(formatted_tables)

    # Chia nhỏ đoạn văn bản
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=256, chunk_overlap=50)
    chunks = text_splitter.split_text(all_text)

    # Tạo vector embeddings
    embedding_model = GPT4AllEmbeddings(model_file=embedding_model_path)
    db = FAISS.from_texts(texts=chunks, embedding=embedding_model)
    db.save_local(vector_db_path)

    print(f"✅ Đã lưu {len(chunks)} đoạn văn bản vào Vector Database!")

if __name__ == "__main__":
    create_vector_db()


