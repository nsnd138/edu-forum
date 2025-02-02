import streamlit as st
from langchain_community.llms import CTransformers
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import FAISS
import re
from langchain_community.llms import  LlamaCpp

# Cấu hình
model_file = "../models/vinallama-7b-chat_q5_0.gguf"
vector_db_path = "../vectorstores/db_faiss"

# Load LLM
def load_llm(model_file):
    llm = CTransformers(
        model=model_file,
        model_type="llama",
        gpu_layers=8,  # Thử giảm xuống 20 layers
        n_ctx=256,  # Giảm số tokens context để tiết kiệm VRAM
        temperature=0.1,
    )
    return llm

# Tạo prompt template
def create_prompt(template):
    prompt = PromptTemplate(template=template, input_variables=["context", "question"])
    return prompt

# Tạo simple chain
def create_qa_chain(prompt, llm, db):
    llm_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={"k": 1}, max_tokens_limit=512),
        return_source_documents=False,
        chain_type_kwargs={'prompt': prompt}
    )
    return llm_chain

# Đọc từ VectorDB
def read_vectors_db():
    embedding_model = GPT4AllEmbeddings(model_file="../models/all-MiniLM-L6-v2-f16.gguf")
    db = FAISS.load_local(vector_db_path, embedding_model, allow_dangerous_deserialization=True)
    return db

# Làm sạch câu trả lời
def clean_response(response):
    cleaned_response = re.sub(r'<\|.*?\|>', '', response)
    cleaned_response = re.sub(r'\|.*?\|', '', cleaned_response)
    return cleaned_response.strip()

# Khởi tạo ứng dụng Streamlit
st.title("Chatbot Hỏi Đáp về Tài Liệu")
st.write("Ứng dụng này cho phép bạn đặt câu hỏi và nhận câu trả lời dựa trên tài liệu được cung cấp.")

# Load các thành phần cần thiết
db = read_vectors_db()
llm = load_llm(model_file)

# Tạo Prompt
template = """Sử dụng thông tin sau đây để trả lời câu hỏi. Nếu bạn không biết câu trả lời, hãy nói không biết, đừng cố tạo ra câu trả lời.
Thông tin: {context}
Câu hỏi: {question}
Câu trả lời:"""
prompt = create_prompt(template)

# Tạo QA chain
llm_chain = create_qa_chain(prompt, llm, db)

# Nhập câu hỏi từ người dùng
question = st.text_input("Nhập câu hỏi của bạn:")

# Xử lý và hiển thị câu trả lời
if st.button("Gửi câu hỏi"):
    if question:
        response = llm_chain.invoke({"query": question})
        cleaned_response = clean_response(response['result'])
        st.write("Câu trả lời:")
        st.write(cleaned_response)
    else:
        st.write("Vui lòng nhập câu hỏi.")