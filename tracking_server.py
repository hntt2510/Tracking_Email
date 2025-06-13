from flask import Flask, request, redirect
from datetime import datetime
import os
import pytz
from mssql_helper import MsSqlHelper
from dotenv import load_dotenv
from update_statuses import update_statuses  # ✅ Import đúng từ đầu

# Load biến môi trường từ file .env
load_dotenv()

SQL_SERVER_IP = os.getenv('SQL_SERVER_IP')
TRACKING_SERVER_IP = os.getenv('TRACKING_SERVER_IP')
DEFAULT_PORT = os.getenv('DEFAULT_PORT', 5000)

sql_helper = MsSqlHelper(
    server=SQL_SERVER_IP,
    database='UNIWIN_TRAIN',
    user='sa',
    password='Abc123!!!'
)

app = Flask(__name__)
TRACKING_URL = f"http://{TRACKING_SERVER_IP}:{DEFAULT_PORT}/"

def get_vn_time():
    return datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d %H:%M:%S")

def log_event(event_type, email, target_url):
    target_url = target_url or ""
    sql_helper.execute_non_query(
        "INSERT INTO tracking_log (Email, EventType, TargetUrl, Timestamp) VALUES (?, ?, ?, GETDATE())",
        [email, event_type, target_url]
    )

@app.route("/open")
def track_open():
    email = request.args.get("email", "").strip()
    if not email:
        return "", 204

    log_event("OPEN", email, "")
    update_statuses(sql_helper)  # ✅ cập nhật trạng thái
    return "", 204

@app.route("/click")
def track_click():
    email = request.args.get("email", "unknown").strip()
    target_url = request.args.get("target")
    if not target_url:
        return "Missing target URL", 400

    log_event("CLICK", email, target_url)
    update_statuses(sql_helper)  # ✅ cập nhật trạng thái
    return redirect(target_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(DEFAULT_PORT))
