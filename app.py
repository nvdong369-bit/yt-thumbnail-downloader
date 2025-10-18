from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import re
import requests
import os
from bs4 import BeautifulSoup 

app = Flask(__name__, template_folder="templates")
CORS(app)

# ========== Helper ========== #

def extract_video_id(url: str):
    """Lấy video_id từ link YouTube"""
    pattern = r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def generate_all_thumbnails(video_id: str):
    """Tạo ra TẤT CẢ các URL thumbnail chuẩn"""
    base_url = f"https://img.youtube.com/vi/{video_id}/"
    qualities = {
        "maxres": "1280x720 (4K/HD) - Max Resolution", 
        "sd": "640x480 (SD) - Standard Definition", 
        "hq": "480x360 (HQ) - High Quality", 
        "mq": "320x180 (MQ) - Medium Quality", 
        "default": "120x90 (Default) - Default Quality"
    }
    
    urls = []
    # Các kích thước chuẩn theo tên
    order = ["maxres", "sd", "hq", "mq", "default"] 
    
    for q in order:
        desc = qualities.get(q, q)
        urls.append({
            "quality": q,
            "description": desc,
            "url": base_url + f"{q}default.jpg"
        })
        
    # Thêm các thumbnail dựa trên số (các frame khác của video)
    for i in range(4):
        urls.append({
            "quality": f"Frame {i}",
            "description": f"Thumbnail Frame ({i})",
            "url": base_url + f"{i}.jpg"
        })
        
    return urls

def get_video_title(url: str):
    """Phân tích HTML để lấy Tiêu đề (thay thế pytube)"""
    # Thêm User-Agent để tránh bị block bởi một số server
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ưu tiên lấy từ meta property="og:title"
        meta_title = soup.find("meta", property="og:title")
        if meta_title:
             title = meta_title.get("content").strip()
             return title.replace(" - YouTube", "").strip()
             
        # Fallback: Nếu không tìm thấy meta og:title, tìm thẻ <title>
        title_tag = soup.find('title')
        if title_tag:
             return title_tag.text.replace(" - YouTube", "").strip()

        return "Không tìm thấy Tiêu đề"
        
    except requests.exceptions.RequestException:
        # Lỗi mạng, timeout, hoặc 404/403
        return "⚠️ Lỗi: Không thể lấy Tiêu đề (Video Private/Không tồn tại)"
    except Exception:
        return "⚠️ Lỗi phân tích Tiêu đề"

# ========== Routes ========== #

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

# Route chính (sửa đổi để trả về tất cả thumbnail và tiêu đề)
@app.route("/get_thumbnail", methods=["POST"])
def get_thumbnail_api():
    data = request.json
    url = data.get("url")
    
    if not url:
        return jsonify({"error": "❌ Bạn chưa nhập link YouTube"}), 400

    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({"error": "❌ Link YouTube không hợp lệ"}), 400

    video_title = get_video_title(url)
    all_thumbnails = generate_all_thumbnails(video_id)
    
    return jsonify({
        "title": video_title,
        "thumbnails": all_thumbnails
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
