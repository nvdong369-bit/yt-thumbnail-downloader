from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import re
import requests
import os

app = Flask(__name__, template_folder="templates")
CORS(app)

# ========== Helper ========== #
def extract_video_id(url: str):
    """Lấy video_id từ link YouTube"""
    pattern = r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def check_url_exists(url: str) -> bool:
    """Kiểm tra URL có tồn tại không (tránh 404)"""
    try:
        r = requests.head(url, timeout=5)
        return r.status_code == 200
    except:
        return False

def get_thumbnail(video_id: str, quality: str = "maxres"):
    """Lấy thumbnail theo chất lượng, fallback nếu link 404"""
    quality_map = {
        "default": "default.jpg",
        "mq": "mqdefault.jpg",
        "hq": "hqdefault.jpg",
        "sd": "sddefault.jpg",
        "maxres": "maxresdefault.jpg"
    }

    order = ["maxres", "sd", "hq", "mq", "default"]
    if quality not in quality_map:
        quality = "maxres"

    url = f"https://img.youtube.com/vi/{video_id}/{quality_map[quality]}"
    if check_url_exists(url):
        return url

    # fallback
    for q in order:
        url = f"https://img.youtube.com/vi/{video_id}/{quality_map[q]}"
        if check_url_exists(url):
            return url
    return None

# ========== Routes ========== #
@app.route("/")
def home():
    return render_template("index.html")

# NEW ROUTES FOR NAVIGATION
@app.route("/about")
def about():
    # Giả sử bạn có file about.html trong thư mục templates
    return render_template("about.html")

@app.route("/privacy")
def privacy():
    # Giả sử bạn có file privacy.html trong thư mục templates
    return render_template("privacy.html")
# END NEW ROUTES

@app.route("/get_thumbnail", methods=["POST"])
def get_thumbnail_api():
    data = request.json
    url = data.get("url")
    size = data.get("size", "maxres")

    if not url:
        return jsonify({"error": "❌ Bạn chưa nhập link YouTube"}), 400

    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({"error": "❌ Link YouTube không hợp lệ"}), 400

    thumb_url = get_thumbnail(video_id, size)
    if not thumb_url:
        return jsonify({"error": "⚠️ Không tìm thấy thumbnail"}), 404

    return jsonify({"thumbnail_url": thumb_url})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
