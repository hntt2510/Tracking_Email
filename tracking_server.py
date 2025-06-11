from flask import Flask, request, redirect, send_file
from datetime import datetime
import os
import pytz

app = Flask(__name__)

LOG_DIR = "tracking_logs"
LOG_FILE = os.path.join(LOG_DIR, "tracking.log")
PIXEL_FILE = os.path.join(LOG_DIR, "pixel.gif")

os.makedirs(LOG_DIR, exist_ok=True)

def get_vn_time():
    return datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d %H:%M:%S")

def log_event(event_type, email, extra=""):
    timestamp = get_vn_time()
    log_line = f"[{timestamp}] EVENT: {event_type.upper()} | EMAIL: {email.strip()}"
    if extra:
        log_line += f" | INFO: {extra.strip()}"
    print(log_line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

@app.route("/open")
def track_open():
    email = request.args.get("email", "").strip()
    if not email:
        return "", 204
    log_event("open", email)
    if not os.path.exists(PIXEL_FILE):
        with open(PIXEL_FILE, "wb") as f:
            f.write(
                b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!"
                b"\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01"
                b"\x00\x00\x02\x02L\x01\x00;"
            )
    return send_file(PIXEL_FILE, mimetype="image/gif")

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

@app.route("/log")
def view_log():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return f"<pre>{f.read()}</pre>"
    except Exception as e:
        return str(e)

@app.route("/download_log")
def download_log():
    try:
        return send_file(LOG_FILE, as_attachment=True)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    # Backup log nếu có
    if os.path.exists(LOG_FILE):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(LOG_DIR, f"tracking_backup_{ts}.log")
        os.rename(LOG_FILE, backup_file)
        print(f"📦 Đã backup tracking.log sang: {backup_file}")

    # Tạo file mới
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")

    app.run(host="0.0.0.0", port=5000)
