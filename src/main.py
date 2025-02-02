from src.prepare_vector_db import create_vector_db
from src.query_vector_db import query_vector_db

if __name__ == "__main__":
    print("Đang tạo vecto Database..")
    create_vector_db()

    print("\nĐang truy vấn dữ liệu..")
    query_vector_db("Tạo cáp mạng theo chuẩn T568B")