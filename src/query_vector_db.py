# src/query_vector_db.py
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import GPT4AllEmbeddings

# Khai báo đường dẫn
vector_db_path = "../vectorstores/db_faiss"
embedding_model_path = "../models/all-MiniLM-L6-v2-f16.gguf"

def load_vector_db():
    """Tải vector database từ FAISS."""
    embedding_model = GPT4AllEmbeddings(model_file=embedding_model_path)
    db = FAISS.load_local(vector_db_path, embedding_model, allow_dangerous_deserialization=True)
    return db

def query_vector_db(question, top_k=5):
    """Tìm kiếm câu trả lời trong Vector Database."""
    db = load_vector_db()
    retriever = db.as_retriever(search_kwargs={"k": top_k})
    results = retriever.get_relevant_documents(question)

    print(f"\n🔍 Câu hỏi: {question}")
    for i, doc in enumerate(results):
        print(f"--- Đoạn văn {i+1} ---\n{doc.page_content}\n")

if __name__ == "__main__":
    query_vector_db("Nội dung mục 4.5.1.2 của chương trình đào tạo ngành CNTT?")
