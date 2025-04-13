import streamlit as st
import streamlit.components.v1 as stc
import pandas as pd
import requests
import os
from fuzzywuzzy import process
import subprocess

qa_bot_script = os.path.abspath(r"D:\\clone_github\\LangChain\\src\\QA_Bot_app.py")
DATA_PATH = 'D:\\clone_github\\LangChain\\nguoimiennuichat.csv'
IMAGE_PATH = 'D:\\clone_github\\LangChain\\Picture1.jpg'
FORUM_API_URL = "http://127.0.0.1:5000/apiapi"

# Tải dataset
@st.cache_data
def load_data(data):
    try:
        df = pd.read_csv(data)
        return df
    except FileNotFoundError:
        st.error("File lỗi mất tiêu.")
        return None

def vectorize_text_to_cosine_mat(data):
    count_vect = CountVectorizer()
    cv_mat = count_vect.fit_transform(data)
    cosine_sim_mat = cosine_similarity(cv_mat)
    return cosine_sim_mat

@st.cache_data
def get_recommendation(title, cosine_sim_mat, df, num_of_rec=5):
    course_indices = pd.Series(df.index, index=df['course_title']).drop_duplicates()
    idx = course_indices[title]
    sim_scores = list(enumerate(cosine_sim_mat[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    selected_course_indices = [i[0] for i in sim_scores[:num_of_rec]]
    selected_course_scores = [i[1] for i in sim_scores[:num_of_rec]]
    result_df = df.iloc[selected_course_indices].copy()
    result_df['number_of_hits'] = selected_course_scores
    final_recommend_courses = result_df[['course_title', 'number_of_hits','subject_area', 'year', 'author']]
    return final_recommend_courses.head(num_of_rec)

@st.cache_data
def search_term_if_not_found(term, df, column='course_title', threshold=60):
    # Lọc danh sách các tên tài liệu
    course_titles = df[column].dropna().tolist()
    
    # Sử dụng fuzzy matching để tìm tài liệu gần đúng
    matches = process.extract(term, course_titles, limit=10)
    
    # Lọc ra các kết quả có độ tương đồng lớn hơn ngưỡng (threshold)
    filtered_matches = [match[0] for match in matches if match[1] >= threshold]
    
    # Trả về các hàng tương ứng trong DataFrame
    if filtered_matches:
        return df[df[column].isin(filtered_matches)]
    else:
        return pd.DataFrame()  # Không tìm thấy kết quả

# Hàm gọi API từ YEScale
def get_chatbot_response(messages):
    api_key = "sk-e8mmpl2JTOX99ZjCKDK0WgcmpOUACEAjCtoU1fRvTyj0StGO"  # Sử dụng biến môi trường để lưu trữ khóa API
    try:
        response = requests.post(
            'https://api.yescale.io/v1/chat/completions',
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'},
            json={
                'max_tokens': 800,
                'messages': messages,
                'model': 'gpt-4-turbo',
                'temperature': 1,
                'top_p': 1
            }
        )
        
        if response.status_code == 200:
            return response.json().get('choices', [{}])[0].get('message', {}).get('content', 'Anh không nhận được tín hiệu.')
        elif response.status_code == 503:
            st.warning("Tớ hơi mệt, thử lại sau nhé!")
            return "Tớ hơi mệt, thử lại sau nhé!"
        else:
            st.error(f"API không nghe máy vì: {response.status_code} - {response.text}")
            return "API không nghe máy"
    except requests.exceptions.RequestException as e:
        st.error(f"API không nghe máy vì: {e}")
        return "API không nghe máy"
def get_study_advice(study_time, break_time):
    api_key = "sk-e8mmpl2JTOX99ZjCKDK0WgcmpOUACEAjCtoU1fRvTyj0StGO"  # Thay API key của bạn vào đây
    messages = [
        {"role": "system", "content": "Bạn là một chuyên gia tư vấn về phương pháp học tập hiệu quả."},
        {"role": "user", "content": f"Tôi học {study_time} giờ mỗi ngày và nghỉ {break_time} phút sau mỗi giờ học. Bạn có thể tư vấn cho tôi phương pháp học tập hiệu quả không?"}
    ]
    
    try:
        response = requests.post(
            'https://api.yescale.io/v1/chat/completions',
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'},
            json={
                'max_tokens': 800,
                'messages': messages,
                'model': 'gpt-4-turbo',
                'temperature': 1,
                'top_p': 1
            }
        )
        
        if response.status_code == 200:
            return response.json().get('choices', [{}])[0].get('message', {}).get('content', 'Tôi không nhận được tín hiệu. Thử lại sau nhé.')
        elif response.status_code == 503:
            st.warning("Tôi hơi mệt, thử lại sau nhé!")
            return "Tôi hơi mệt, thử lại sau nhé!"
        else:
            st.error(f"API không nghe máy vì: {response.status_code} - {response.text}")
            return "API không nghe máy"
    except requests.exceptions.RequestException as e:
        st.error(f"API không nghe máy vì: {e}")
        return "API không nghe máy"

    


suggested_questions = [
    "Tài liệu nào phù hợp cho người mới bắt đầu học Python?",
    "Có tài liệu nào về học máy (machine learning) không?",
    "Làm thế nào để cài đặt thư viện scikit-learn?",
    "Có khóa học nào về trí tuệ nhân tạo không?",
    "Tài liệu nào tốt nhất để học lập trình web?"
]

def get_forum_posts():
    response = requests.get(f"{FORUM_API_URL}/posts")
    if response.status_code == 200:
        return response.json()
    return []

def post_forum(title, content, author, image_file):
    data = {"title": title, "content": content, "author": author}
    try:
        # Chỉnh sửa URL API
        response = requests.post(f"{FORUM_API_URL}/posts", json=data)
        response.raise_for_status()  # Kiểm tra nếu có lỗi
        return response.json()  # Trả về dữ liệu bài viết đã đăng
    except requests.exceptions.RequestException as e:
        st.error(f"Lỗi đăng bài: {e}")
        return {"error": "Không thể đăng bài"}



def get_comments(post_id):
    response = requests.get(f"{FORUM_API_URL}/comments/{post_id}")
    if response.status_code == 200:
        return response.json()
    return []

def post_comment(post_id, author, comment):
    data = {"author": author, "comment": comment}
    response = requests.post(f"{FORUM_API_URL}/comments/{post_id}", json=data)
    return response.json()

def main():
    st.image(IMAGE_PATH, caption="VMUva ^^", width=150)
    st.title('VMUBOT')
    st.sidebar.image(IMAGE_PATH, use_container_width=True)
    menu = ('Quản lý thời gian học', 'VMUBot', 'Q&A trên tài liệu', 'Diễn đàn')
    choices = st.sidebar.selectbox('Menu', menu)
    df = load_data(DATA_PATH)
    
    if choices == 'Diễn đàn':
        st.subheader("Diễn đàn VMU")
        
        # Lấy danh sách bài viết từ API
        posts = get_forum_posts()
        
        # Kiểm tra xem có bài viết nào không
        if not posts:
            st.write("Hiện tại không có bài viết nào.")
        
        # Tìm kiếm bài viết theo từ khóa
        search_query = st.text_input("Tìm kiếm bài viết:", "")
        if search_query:
            posts = [post for post in posts if search_query.lower() in post['title'].lower() or search_query.lower() in post['content'].lower()]
        
        # Hiển thị danh sách bài viết
        for post in posts:
            # Hiển thị tiêu đề bài viết với các thông tin chi tiết
            st.markdown(f"### {post['title']}")
            st.write(f"**Tác giả:** {post['author']} | **Ngày tạo:** {post['created_at']} | **Lượt xem:** {post.get('views', 0)}")
            
            # Hiển thị ảnh nếu có
            if 'image_url' in post and post['image_url']:
                st.image(post['image_url'], use_column_width=True)

            # Nội dung bài viết
            st.write(post['content'])
            
            # Các nút hành động (Thích, Chia sẻ)
            like_button = st.button(f"Thích bài {post['id']}")
            if like_button:
                st.write("Cảm ơn bạn đã thích bài viết này!")
            
            share_button = st.button(f"Chia sẻ bài {post['id']}")
            if share_button:
                st.write("Chia sẻ bài viết này trên mạng xã hội!")
            
            # Hiển thị bình luận
            comments = get_comments(post['id'])
            with st.expander("Bình luận"):
                for comment in comments:
                    st.write(f"**{comment['author']}**: {comment['comment']} ({comment['created_at']})")
                
                # Form để đăng bình luận mới
                new_comment = st.text_input(f"Viết bình luận cho {post['title']}")
                if st.button(f"Bình luận {post['id']}"):
                    post_comment(post['id'], "Người dùng", new_comment)
                    st.rerun()

        # Form để tạo bài viết mới
        with st.form("new_post"):
            title = st.text_input("Tiêu đề bài viết")
            content = st.text_area("Nội dung bài viết")
            image_file = st.file_uploader("Tải ảnh lên (tùy chọn)", type=["jpg", "jpeg", "png"])
            if st.form_submit_button("Đăng bài"):
                if title and content:
                    post_forum(title, content, "Người dùng", image_file)
                    st.success("Bài viết đã được đăng thành công!")
                    st.rerun()
                else:
                    st.error("Vui lòng nhập tiêu đề và nội dung bài viết.")



    
    elif choices == 'Quản lý thời gian học':
        
        st.subheader("Quản lý thời gian học tập")
        study_time = st.number_input("Nhập số giờ học mỗi ngày", min_value=0, max_value=24, value=2)
        break_time = st.number_input("Nhập số phút nghỉ sau mỗi giờ học", min_value=0, max_value=60, value=10)
        st.write(f"Bạn học {study_time} giờ mỗi ngày và nghỉ {break_time} phút sau mỗi giờ học.")
        if st.button("Nhận lời khuyên học tập"):
        # Gọi API tư vấn phương pháp học
            advice = get_study_advice(study_time, break_time)
            st.subheader("Lời khuyên của chúng tôi:")
            st.write(advice)

    
    elif choices == 'VMUBot':
        st.subheader('VMUBot')
        st.write("VMUBot sẵn sàng hỗ trợ bạn!")
        
        st.title('Hỏi gì hỏi đi bạn ^^')



        st.write("Bạn có thể hỏi những câu hỏi sau:")
        for question in suggested_questions:
            if st.button(question):
                st.session_state.chat_history.append({"role": "user", "content": question})
                response = get_chatbot_response(st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        user_input = st.text_input('Tôi: ', '')

        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            response = get_chatbot_response(st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                st.write(f"**Tôi:** {chat['content']}")
            else:
                st.write(f"**VMUbot:** {chat['content']}")
    elif choices == 'Q&A trên tài liệu':
        st.write("Khởi chạy ứng dụng Chatbot hỏi đáp tài liệu...")
        subprocess.run(["streamlit", "run", qa_bot_script], shell=True)

if __name__ == '__main__':
    main()
