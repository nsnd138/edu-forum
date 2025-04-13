from prepare_vector_db import create_vector_db
from query_vector_db import query_vector_db

if __name__ == "__main__":
    print("Đang tạo vecto Database..")
    create_vector_db()

    print("\nĐang truy vấn dữ liệu..")
    query_vector_db("Pros and Cons of Lenovo Legion 5i")