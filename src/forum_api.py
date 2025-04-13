from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Hỗ trợ UTF-8


@app.route('/posts', methods=['GET'])
def get_posts():
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM posts")  # Kiểm tra query này
    posts = cursor.fetchall()
    conn.close()

    print("DEBUG:", posts)  # In thử danh sách bài viết khi có request

    return jsonify(posts)

@app.route('/posts', methods=['POST'])
def create_post():
    try:
        print("Raw Data:", request.data)  # Debug dữ liệu gốc
        print("Headers:", request.headers)  # Debug headers
        data = request.get_json(force=True)  # Cố gắng parse JSON
        print("Parsed JSON:", data)  # In ra dữ liệu đã parse

        if not data:
            return jsonify({"error": "Dữ liệu không hợp lệ"}), 400
        return jsonify({"message": "Bài viết đã tạo", "data": data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/')
def home():
    return jsonify({"message": "API đang chạy!"})

# Kết nối Database
def get_db_connection():
    conn = sqlite3.connect('forum.db', check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        author TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        image_url TEXT)''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS comments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_id INTEGER NOT NULL,
                        author TEXT NOT NULL,
                        comment TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (post_id) REFERENCES posts (id))''')
    
    return conn

# 📌 API: Lấy danh sách bài viết hoặc đăng bài mới
@app.route('/posts', methods=['GET', 'POST'])
def handle_posts():
    conn = get_db_connection()

    if request.method == 'GET':
        cursor = conn.execute("SELECT id, title, content, author, created_at, image_url FROM posts")
        posts = [{"id": row[0], "title": row[1], "content": row[2], "author": row[3], "created_at": row[4], "image_url": row[5]} for row in cursor.fetchall()]
        conn.close()
        print("📌 Debug: Posts in DB (GET):", posts)  # In ra dữ liệu trong DB
        return jsonify(posts)

    elif request.method == 'POST':
        data = request.json
        if not data or 'title' not in data or 'content' not in data or 'author' not in data:
            return jsonify({"error": "Thiếu thông tin"}), 400

        conn.execute("INSERT INTO posts (title, content, author, created_at, image_url) VALUES (?, ?, ?, datetime('now'), ?)",
                     (data['title'], data['content'], data['author'], None))
        conn.commit()
        
        # Kiểm tra sau khi insert
        cursor = conn.execute("SELECT id, title FROM posts")
        all_posts = cursor.fetchall()
        print("📌 Debug: Posts after INSERT:", all_posts)  # Xem có bài nào trong DB không

        conn.close()
        return jsonify({"message": "Bài viết đã tạo"}), 201

# 📌 API: Lấy bình luận hoặc thêm bình luận mới
@app.route('/comments/<int:post_id>', methods=['GET', 'POST'])
def handle_comments(post_id):
    conn = get_db_connection()

    if request.method == 'GET':
        cursor = conn.execute("SELECT id, post_id, author, comment, created_at FROM comments WHERE post_id = ?", (post_id,))
        comments = [{"id": row[0], "post_id": row[1], "author": row[2], "comment": row[3], "created_at": row[4]} for row in cursor.fetchall()]
        conn.close()
        return jsonify(comments)

    elif request.method == 'POST':
        data = request.json
        if not data or 'author' not in data or 'comment' not in data:
            return jsonify({"error": "Thiếu thông tin"}), 400

        conn.execute("INSERT INTO comments (post_id, author, comment, created_at) VALUES (?, ?, ?, datetime('now'))",
                     (post_id, data['author'], data['comment']))
        conn.commit()
        conn.close()
        return jsonify({"message": "Bình luận đã được thêm!"}), 201

if __name__ == '__main__':
    app.run(debug=True)
