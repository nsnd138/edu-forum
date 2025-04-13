import requests

FORUM_API_URL = "http://127.0.0.1:5000"

# Kiểm tra lấy danh sách bài viết
response = requests.get(f"{FORUM_API_URL}/posts")
print("GET /posts:", response.status_code, response.json())

# Thử đăng bài mới
new_post = {
    "title": "Bài test",
    "content": "Đây là nội dung bài viết test",
    "author": "Tester"
}
response = requests.post(f"{FORUM_API_URL}/posts", json=new_post)
print("POST /posts:", response.status_code, response.json())

# Kiểm tra lại danh sách bài viết sau khi đăng
response = requests.get(f"{FORUM_API_URL}/posts")
print("GET /posts (after POST):", response.status_code, response.json())
