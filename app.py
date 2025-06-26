import threading
import os
from datetime import datetime
#import pytz
from flask import Flask, request, jsonify, redirect
from dotenv import load_dotenv

from mssql_helper import MsSqlHelper
# Import các hàm cần thiết từ send_email.py
from send_email import send_all_emails, get_campaign_full_config_by_id  # Sửa import

# IMPORT HÀM UPDATE_STATUSES MỚI
from update_statuses import update_statuses

# --- Tải biến môi trường ---
load_dotenv()
PORT = int(os.getenv("DEFAULT_PORT", 5000))

# --- Khởi tạo SQL helper cho app.py ---
SQL_SERVER_IP = os.getenv("SQL_SERVER_IP")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

try:
    sql_helper = MsSqlHelper(
        server=SQL_SERVER_IP,
        database=SQL_DATABASE,
        user=SQL_USER,
        password=SQL_PASSWORD,
    )
except Exception as e:
    print(f"❌ Lỗi khởi tạo SQL Helper: {e}")
    raise

# --- Định nghĩa tên bảng SMTP_CONFIG_TABLE cho app.py ---
SMTP_CONFIG_TABLE = 'AppCreator_be2bea7b'

# --- Khởi tạo Flask ---
app = Flask(__name__, static_folder='statics/')

# --- Hàm log sự kiện vào DB ---
def log_event(event_type, email, target_url=""):
    try:
        sql_helper.execute_non_query(
            "INSERT INTO tracking_log (Email, EventType, TargetUrl, Timestamp) "
            "VALUES (?, ?, ?, GETDATE())",
            [email, event_type, target_url or ""]
        )
    except Exception as e:
        print(f"❌ Lỗi khi log event {event_type} cho {email}: {e}")

# --- Hàm lấy Tên Campaign dựa trên ID cấu hình (trong app.py) ---
def get_campaign_name_by_config_id_in_app(config_id):
    """
    Truy vấn SMTP_CONFIG_TABLE để lấy Tên Campaign (text_1_copy_3) dựa trên record_number (ID).
    """
    try:
        config_data = sql_helper.execute_query(f"""
            SELECT [text_1_copy_3] AS CampaignName
            FROM {SMTP_CONFIG_TABLE}
            WHERE [RECORD_NUMBER] = ?
        """, [config_id])
        return config_data[0]['CampaignName'] if config_data else None
    except Exception as e:
        print(f"❌ Lỗi khi lấy tên campaign cho ID {config_id}: {e}")
        return None

# --- Kiểm tra trạng thái máy chủ ---
@app.route("/", methods=["GET"])
def index():
    return "✅ Máy chủ đang chạy! Các routes đã đăng ký: " + ", ".join(sorted(r.rule for r in app.url_map.iter_rules())), 200

# --- Route để kích hoạt gửi email nền ---
@app.route('/run', methods=['GET'])
def run_send():
    campaign_config_id_str = request.args.get("id", None)
    return_url = request.args.get("return_url", None)

    if not campaign_config_id_str:
        return jsonify(success=False, message="Thiếu tham số 'id' (Record Number của cấu hình campaign)."), 400

    try:
        campaign_config_id = int(campaign_config_id_str)
    except ValueError:
        return jsonify(success=False, message="Định dạng ID cấu hình không hợp lệ. Phải là số nguyên."), 400

    campaign_name_for_display = get_campaign_name_by_config_id_in_app(campaign_config_id)
    if not campaign_name_for_display:
        return jsonify(success=False, message=f"Không tìm thấy campaign nào cho ID cấu hình: {campaign_config_id}."), 404

    threading.Thread(target=send_all_emails, args=(campaign_config_id,), daemon=True).start()
    return jsonify(success=True, message=f"Tiến trình nền đã được khởi động cho campaign {campaign_name_for_display} (ID cấu hình: {campaign_config_id})"), 202

# --- Theo dõi mở email ---
@app.route("/open", methods=["GET"])
def track_open():
    email = request.args.get("email", "").strip()
    campaign_name = request.args.get("campaign", None)
    if not email:
        return "", 204
    log_event("OPEN", email)
    # GỌI HÀM CẬP NHẬT TRẠNG THÁI VỚI THAM SỐ campaign_name
    update_statuses(sql_helper, email, "OPEN", campaign_name if campaign_name else None)
    return "", 204

# --- Theo dõi click ---
@app.route("/click", methods=["GET"])
def track_click():
    email = request.args.get("email", "unknown").strip()
    target_url = request.args.get("target", None)
    campaign_name = request.args.get("campaign", None)
    
    if not target_url:
        return "Thiếu URL đích", 400
    
    log_event("CLICK", email, target_url)
    
    # Logic để phân biệt click1/click2 dựa trên TargetUrl
    if "infoasia.com.vn" in target_url.lower():  # Chuyển sang lowercase để tránh lỗi case-sensitive
        update_statuses(sql_helper, email, "CLICK_LINK1", campaign_name)
    elif "zalo.me" in target_url.lower():
        update_statuses(sql_helper, email, "CLICK_LINK2", campaign_name)
    else:
        update_statuses(sql_helper, email, "CLICK_OTHER", campaign_name)
    
    return redirect(target_url)

if __name__ == "__main__":
    print(f">>> Khởi động Flask trên cổng {PORT} …")
    app.run(host="0.0.0.0", port=PORT)