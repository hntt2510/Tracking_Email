from flask import Flask, request, redirect, send_file, Response
from datetime import datetime
import os
import requests
import pytz
import traceback

app = Flask(__name__)

LOG_DIR = "tracking_logs"
LOG_FILE = os.path.join(LOG_DIR, "tracking.log")
PIXEL_FILE = os.path.join(LOG_DIR, "pixel.gif")
RENDER_LOG_URL = "https://tracking-email-x9x4.onrender.com/download_log"

# Khởi tạo folder nếu chưa có
os.makedirs(LOG_DIR, exist_ok=True)

# 🔥 Nếu chạy LOCAL → xóa cache và tải log từ Render
try:
    if os.getenv("RENDER") is None:
        for path in [LOG_FILE, PIXEL_FILE]:
            if os.path.exists(path):
                os.remove(path)
                print(f"🧹 Đã xóa: {path}")

        if not os.path.exists(LOG_FILE):
            r = requests.get(RENDER_LOG_URL)
            if r.status_code == 200:
                with open(LOG_FILE, "wb") as f:
                    f.write(r.content)
                print("✅ Đã tải tracking.log từ Render.")
            else:
                print("⚠️ Không thể tải log từ Render.")
except Exception as e:
    print("🔥 Lỗi khi khởi tạo môi trường:")
    traceback.print_exc()
    exit(1)

# ✅ Lấy giờ Việt Nam
def get_vn_time():
    tz = pytz.timezone("Asia/Ho_Chi_Minh")
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

# ✅ Ghi log sự kiện
def log_event(event_type, email, extra=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] EVENT: {event_type.upper()} | EMAIL: {email}"
    if extra:
        # Xóa ký tự xuống dòng nếu có
        extra = extra.replace("\n", "").replace("\r", "").strip()
        log_line += f" | INFO: {extra}"
    print(log_line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

# ✅ Ghi open bằng pixel.gif
@app.route("/open")
def track_open():
    email = request.args.get("email", "unknown")
    log_event("open", email)

    if not os.path.exists(PIXEL_FILE):
        with open(PIXEL_FILE, "wb") as f:
            f.write(
                b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!"
                b"\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01"
                b"\x00\x00\x02\x02L\x01\x00;"
            )
    return send_file(PIXEL_FILE, mimetype="image/gif")

# ✅ Ghi click & redirect
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

# ✅ Xem log trực tiếp
@app.route("/log")
def view_log():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        return f"<pre>{content}</pre>"
    except Exception as e:
        return f"Lỗi khi đọc log: {e}"

# ✅ Tải log
@app.route("/download_log")
def download_log():
    try:
        return send_file(LOG_FILE, as_attachment=True)
    except Exception as e:
        return f"Lỗi khi tải log: {e}"

# ✅ Chạy local
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
