from flask import Flask, request, redirect, send_file
from datetime import datetime
from time import time
import os
import requests
import pytz

app = Flask(__name__)

LOG_DIR = "tracking_logs"
LOG_FILE = os.path.join(LOG_DIR, "tracking.log")
PIXEL_FILE = os.path.join(LOG_DIR, "pixel.gif")
RENDER_LOG_URL = "https://tracking-email-x9x4.onrender.com/download_log"
tracking_url = f"https://tracking-email-x9x4.onrender.com/open?email={{email}}&ts={int(time())}"


os.makedirs(LOG_DIR, exist_ok=True)

# Chạy local: xoá log cũ, tải từ Render
if os.getenv("RENDER") is None:
    for file_path in [LOG_FILE, PIXEL_FILE]:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🧹 Đã xóa: {file_path}")

    try:
        r = requests.get(RENDER_LOG_URL)
        if r.status_code == 200:
            with open(LOG_FILE, "wb") as f:
                f.write(r.content)
            print("✅ Tải log từ Render thành công.")
        else:
            print("⚠️ Không thể tải log từ Render.")
    except Exception as e:
        print("❌ Lỗi khi tải log từ Render:", e)

# Lấy thời gian theo múi giờ Việt Nam
def get_vn_time():
    return datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d %H:%M:%S")

# Ghi log vào file
def log_event(event_type, email, extra=""):
    timestamp = get_vn_time()
    log_line = f"[{timestamp}] EVENT: {event_type.upper()} | EMAIL: {email.strip()}"

    # Nếu có thêm thông tin (click link), ghi thêm
    if extra:
        extra = extra.replace("\n", "").replace("\r", "").strip()
        log_line += f" | INFO: {extra}"

    print(log_line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

# Pixel tracking
@app.route("/open")
def track_open():
    email = request.args.get("email", "unknown")
    ip = request.remote_addr
    ua = request.headers.get("User-Agent", "")
    log_event("open", email, f"ip={ip} | ua={ua}")

    if not os.path.exists(PIXEL_FILE):
        with open(PIXEL_FILE, "wb") as f:
            f.write(
                b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!"
                b"\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01"
                b"\x00\x00\x02\x02L\x01\x00;"
            )

    return send_file(PIXEL_FILE, mimetype="image/gif")

# Redirect click tracking
@app.route("/click")
def track_click():
    email = request.args.get("email", "unknown")
    target_url = request.args.get("target")

    if not target_url:
        return "Missing target URL", 400

    if "infoasia.com.vn" in target_url:
        link_name = "link1"
    elif "zalo.me" in target_url:
        link_name = "link2"
    else:
        link_name = "other"

    log_event("click", email, f"{link_name} -> {target_url}")
    return redirect(target_url)

# Xem log trong trình duyệt
@app.route("/log")
def view_log():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return f"<pre>{f.read()}</pre>"
    except Exception as e:
        return f"Lỗi đọc log: {e}"

# Tải log về
@app.route("/download_log")
def download_log():
    try:
        return send_file(LOG_FILE, as_attachment=True)
    except Exception as e:
        return f"Lỗi tải log: {e}"

# Chạy local
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
