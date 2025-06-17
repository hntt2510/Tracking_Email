# ===== FILE: send_email.py =====

import smtplib
from email.message import EmailMessage
import time
import random
from dotenv import load_dotenv
import os
from mssql_helper import MsSqlHelper

# Load environment variables
load_dotenv()

# SQL Config
SQL_SERVER_IP = os.getenv('SQL_SERVER_IP')
SQL_DATABASE = os.getenv('SQL_DATABASE')
SQL_USER = os.getenv('SQL_USER')
SQL_PASSWORD = os.getenv('SQL_PASSWORD')

# SMTP Config
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 465))
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Table Names
EMAIL_LIST_TABLE = os.getenv('EMAIL_LIST_TABLE')
REPORT_TABLE = os.getenv('REPORT_TABLE')

# SQL Helper
sql_helper = MsSqlHelper(
    server=SQL_SERVER_IP,
    database=SQL_DATABASE,
    user=SQL_USER,
    password=SQL_PASSWORD
)

# Load email list
email_list = sql_helper.execute_query(f'''
    SELECT [text_2] AS FullName, [text_3] AS Email, [text_4] AS Company, [text_5] AS Phone
    FROM {EMAIL_LIST_TABLE}
''')

# Load email template
with open("email_template.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# Sync email list to report

def sync_email_to_report():
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

# Create email

def create_personalized_email(row):
    rand = str(random.randint(100000, 999999))
    personalized_html = html_content\
        .replace("[ FULLNAME ]", row["FullName"])\
        .replace("[ COMPANY ]", row["Company"])\
        .replace("[ PHONE ]", row["Phone"])\
        .replace("[ EMAIL ]", row["Email"])\
        .replace("{rand}", rand)

    msg = EmailMessage()
    msg["Subject"] = "[INFOASIA] ERP ENHANCE - NÂNG CẤP ERP TOÀN DIỆN"
    msg["From"] = EMAIL_SENDER
    msg["To"] = row["Email"]
    msg.set_content("Email yêu cầu trình duyệt hỗ trợ HTML.")
    msg.add_alternative(personalized_html, subtype="html")
    return msg

# Gửi email
sync_email_to_report()

with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
    smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
    for receiver in email_list:
        try:
            msg = create_personalized_email(receiver)
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