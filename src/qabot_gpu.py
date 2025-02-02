# -*- encoding: utf-8 -*-
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import FAISS
from prepare_vector_db import vector_db_path
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

# Kiểm tra GPU
if torch.cuda.is_available():
    print("GPU is available and being used!")
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")
else:
    print("No GPU detected.")
    exit("No GPU found.")

# Cấu hình model
model_path = "../models/vinallama_7b_chat"
vector_db_path = "../vectorstores/db_faiss"

# Tải tokenizer và model từ thư mục local
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float16,  # Dùng float16 để tiết kiệm VRAM
    device_map="auto"           # Tự động sử dụng GPU
)

print(f"Model loaded on: {model.device}")

# Tạo pipeline để chat với model
chatbot = pipeline("text-generation", model=model, tokenizer=tokenizer)

# Tạo prompt template
def create_prompt(template):
    return PromptTemplate(template=template, input_variables=["context", "question"])

# Đọc dữ liệu từ VectorDB
def read_vectors_db():
    embedding_model = GPT4AllEmbeddings(model_file="../models/all-MiniLM-L6-v2-f16.gguf")
    db = FAISS.load_local(vector_db_path, embedding_model, allow_dangerous_deserialization=True)
    return db

# Bắt đầu thử nghiệm
db = read_vectors_db()

# Tạo Prompt
template = """<|im_start|>system
Sử dụng các thông tin mà bạn được cung cấp để trả lời. Hãy trả lời ngắn gọn và chính xác. Nếu bạn không biết câu trả lời, hãy nói không biết, đừng cố tạo ra câu trả lời.
{context}<|im_end|>
<|im_start|>user
{question}<|im_end|>
<|im_start|>assistant"""

prompt = create_prompt(template)

# Chạy mô hình

question = input("Mời nhập câu hỏi: ")
inputs = tokenizer(question, return_tensors="pt").to(model.device)
output = model.generate(**inputs, max_new_tokens=100)

# In kết quả
print(f"AI: {tokenizer.decode(output[0], skip_special_tokens=True)}")