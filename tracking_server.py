# tracking_server.py

from flask import Flask, request, redirect, jsonify
from datetime import datetime
import os
import pytz
import threading

from mssql_helper import MsSqlHelper
from dotenv import load_dotenv
from update_statuses import update_statuses
from send_email import sync_email_to_report   # nếu bạn đã có hàm send_all_emails thì import thay

# Load .env
load_dotenv()

# SQL Config
SQL_SERVER_IP   = os.getenv('SQL_SERVER_IP')
SQL_DATABASE    = os.getenv('SQL_DATABASE')
SQL_USER        = os.getenv('SQL_USER')
SQL_PASSWORD    = os.getenv('SQL_PASSWORD')

# Tracking config
TRACKING_SERVER_IP = os.getenv('TRACKING_SERVER_IP')
DEFAULT_PORT       = int(os.getenv('DEFAULT_PORT', 8081))

# SQL helper
sql_helper = MsSqlHelper(
    server=SQL_SERVER_IP,
    database=SQL_DATABASE,
    user=SQL_USER,
    password=SQL_PASSWORD
)

# Flask app
app = Flask(__name__)

def get_vn_time():
    return datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")) \
                   .strftime("%Y-%m-%d %H:%M:%S")

def log_event(event_type, email, target_url=""):
    sql_helper.execute_non_query(
        """
        INSERT INTO tracking_log (Email, EventType, TargetUrl, Timestamp)
        VALUES (?, ?, ?, GETDATE())
        """,
        [email, event_type, target_url or ""]
    )

@app.route('/send', methods=['POST'])
def send_email_endpoint():
    """
    Gọi endpoint này sẽ khởi động quá trình gửi email
    (non-blocking) và trả về 202 Accepted ngay lập tức.
    """
    threading.Thread(target=sync_email_to_report, daemon=True).start()
    return jsonify({
        "success": True,
        "message": "Email sending started in background"
    }), 202

@app.route('/open', methods=['GET'])
def track_open():
    email = request.args.get("email", "").strip()
    if not email:
        return "", 204
    log_event("OPEN", email)
    update_statuses(sql_helper, email)
    return "", 204

@app.route('/click', methods=['GET'])
def track_click():
    email      = request.args.get("email",  "unknown").strip()
    target_url = request.args.get("target", None)
    if not target_url:
        return "Missing target URL", 400

    log_event("CLICK", email, target_url)
    update_statuses(sql_helper, email)
    return redirect(target_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=DEFAULT_PORT)
