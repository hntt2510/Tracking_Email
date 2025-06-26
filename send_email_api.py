import os
import time
import random
import threading
import smtplib
from flask import Flask, jsonify
from email.message import EmailMessage
from dotenv import load_dotenv
from mssql_helper import MsSqlHelper

# Load biến môi trường từ file .env
load_dotenv()

# SQL Config
SQL_SERVER_IP = os.getenv('SQL_SERVER_IP')
SQL_DATABASE = os.getenv('SQL_DATABASE')
SQL_USER = os.getenv('SQL_USER')
SQL_PASSWORD = os.getenv('SQL_PASSWORD')
SMTP_CONFIG_TABLE = os.getenv('SMTP_CONFIG_TABLE')  # bảng chứa config SMTP
EMAIL_LIST_TABLE = os.getenv('EMAIL_LIST_TABLE')
REPORT_TABLE = os.getenv('REPORT_TABLE')

# Khởi tạo kết nối SQL
sql_helper = MsSqlHelper(
    server=SQL_SERVER_IP,
    database=SQL_DATABASE,
    user=SQL_USER,
    password=SQL_PASSWORD
)

# Load email template HTML
with open("email_template.html", "r", encoding="utf-8") as f:
    html_content = f.read()


def load_smtp_config(campaign_code):
    """Truy vấn thông tin SMTP theo mã chiến dịch (Campaign Name)"""
    row = sql_helper.execute_query(f"""
        SELECT 
            [text_1] AS SMTP_Server,
            [text_1_copy_1] AS SMTP_Email,
            [text_1_copy_2] AS SMTP_Pass,
            [text_1_copy_4] AS SMTP_Port
        FROM {SMTP_CONFIG_TABLE}
        WHERE [text_1_copy_3] = ?
    """, [campaign_code])

    if not row:
        raise Exception(f"❌ Không tìm thấy SMTP config cho Campaign '{campaign_code}'")

    config = row[0]
    return {
        "SMTP_SERVER": config["SMTP_Server"],
        "SMTP_PORT": int(config["SMTP_Port"]),
        "EMAIL_SENDER": config["SMTP_Email"],
        "EMAIL_PASSWORD": config["SMTP_Pass"]
    }


def sync_email_to_report():
    """Đồng bộ người nhận sang bảng report nếu chưa tồn tại"""
    source_rows = sql_helper.execute_query(f'''
        SELECT [text_2] AS FullName, [text_3] AS Email FROM {EMAIL_LIST_TABLE}
    ''')
    for row in source_rows:
        email = row['Email']
        fullname = row['FullName']
        sql_helper.execute_non_query(f'''
            IF NOT EXISTS (
                SELECT 1 FROM {REPORT_TABLE} WHERE [text_3] = ?
            )
            INSERT INTO {REPORT_TABLE} ([text_2], [text_3], [text_4], [text_5], [text_6], [text_7])
            VALUES (?, ?, 'FALSE', 'FALSE', 'FALSE', 'FALSE')
        ''', [email, fullname, email])
    print("✅ Đồng bộ email từ EMAIL LIST sang REPORT thành công!")


def create_personalized_email(row, sender_email):
    rand = str(random.randint(100000, 999999))
    personalized_html = html_content\
        .replace("[ FULLNAME ]", row["FullName"])\
        .replace("[ COMPANY ]", row["Company"])\
        .replace("[ PHONE ]", row["Phone"])\
        .replace("[ EMAIL ]", row["Email"])\
        .replace("{rand}", rand)

    msg = EmailMessage()
    msg["Subject"] = "[INFOASIA] ERP ENHANCE - NÂNG CẤP ERP TOÀN DIỆN"
    msg["From"] = sender_email
    msg["To"] = row["Email"]
    msg.set_content("Email yêu cầu trình duyệt hỗ trợ HTML.")
    msg.add_alternative(personalized_html, subtype="html")
    return msg


def send_email_background(campaign_code="C01"):
    """Nền: Gửi email hàng loạt theo SMTP của chiến dịch"""
    sync_email_to_report()
    smtp_config = load_smtp_config(campaign_code)

    email_list = sql_helper.execute_query(f'''
        SELECT [text_2] AS FullName, [text_3] AS Email, [text_4] AS Company, [text_5] AS Phone
        FROM {EMAIL_LIST_TABLE}
    ''')

    with smtplib.SMTP_SSL(smtp_config["SMTP_SERVER"], smtp_config["SMTP_PORT"]) as smtp:
        smtp.login(smtp_config["EMAIL_SENDER"], smtp_config["EMAIL_PASSWORD"])
        for receiver in email_list:
            try:
                msg = create_personalized_email(receiver, smtp_config["EMAIL_SENDER"])
                smtp.send_message(msg)
                sql_helper.execute_non_query(f'''
                    UPDATE {REPORT_TABLE}
                    SET [text_4] = 'TRUE'
                    WHERE [text_3] = ?
                ''', [receiver["Email"]])
                print(f"✅ Đã gửi tới: {receiver['Email']} ({receiver['FullName']})")
            except Exception as e:
                print(f"❌ Lỗi gửi tới: {receiver['Email']} - {e}")
            time.sleep(30)

    print("🎉 Gửi xong toàn bộ email HTML!")


# ===== Flask API =====
app = Flask(__name__)

@app.route("/send-email", methods=["GET"])
def trigger_send_email():
    task = threading.Thread(target=send_email_background, args=("C01",))
    task.start()
    return jsonify({"success": True, "message": "Email sending task started"}), 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
