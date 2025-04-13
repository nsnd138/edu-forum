import sqlite3

conn = sqlite3.connect('forum.db')
cursor = conn.execute("SELECT * FROM posts")
posts = cursor.fetchall()

if posts:
    for post in posts:
        print(post)
else:
    print("Không có bài viết nào trong database!")

conn.close()
