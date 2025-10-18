from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import re
import requests
import os
# Đã thêm import pytube
from pytube import YouTube 

app = Flask(__name__, template_folder="templates")
CORS(app)

# ========== Helper ========== #
def extract_video_id(url: str):
    """Lấy video_id từ link YouTube"""
    pattern = r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

# Hàm mới: Tạo ra TẤT CẢ các URL thumbnail chuẩn
def generate_all_thumbnails(video_id: str):
    base_url = f"https://img.youtube.com/vi/{video_id}/"
    qualities = {
        "maxres": "1280x720 (4K/HD)", 
        "sd": "640x480 (SD)", 
        "hq": "480x360 (HQ)", 
        "mq": "320x180 (MQ)", 
        "default": "120x90 (Default)"
    }
    
    urls = []
    # Thứ tự này đảm bảo maxres được kiểm tra/hiển thị đầu tiên
    order = ["maxres", "sd", "hq", "mq", "default"] 
    
    for q in order:
        desc = qualities.get(q, q)
        urls.append({
            "quality": q,
            "description": desc,
            "url": base_url + f"{q}default.jpg"
        })
    return urls

# ========== Routes ========== #
@app.route("/")
def home():
    return render_template("index.html")

# Thêm lại các route /about và /privacy (để footer hoạt động)
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

# Route chính được sửa để dùng pytube
@app.route("/get_thumbnail", methods=["POST"])
def get_thumbnail_api():
    data = request.json
    url = data.get("url")
    
    if not url:
        return jsonify({"error": "❌ Bạn chưa nhập link YouTube"}), 400

    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({"error": "❌ Link YouTube không hợp lệ"}), 400

    try:
        # Sử dụng pytube để lấy title (và kiểm tra xem video có tồn tại không)
        yt = YouTube(url)
        video_title = yt.title
        
        # Tạo danh sách TẤT CẢ các thumbnail URL
        all_thumbnails = generate_all_thumbnails(video_id)
        
        # Trả về Tiêu đề và TẤT CẢ các URL
        return jsonify({
            "title": video_title,
            "thumbnails": all_thumbnails
        })

    except Exception as e:
        # Xử lý lỗi pytube (video không tồn tại, private, hoặc bị giới hạn)
        return jsonify({
            "error": f"❌ Lỗi: Video không hợp lệ (Private/Không tồn tại). Chi tiết: {str(e)}"
        }), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port)
