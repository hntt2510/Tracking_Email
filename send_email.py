import smtplib
from email.message import EmailMessage
import time
from mssql_helper import MsSqlHelper
from dotenv import load_dotenv
import os
import random


load_dotenv()

SQL_SERVER_IP = os.getenv('SQL_SERVER_IP')

SMTP_SERVER = "smtp.zoho.com"
SMTP_PORT = 465
EMAIL_SENDER = "erp@infoasia.com.vn"
EMAIL_PASSWORD = "vrFTf82cehmW"

# Danh sách người nhận
sql_helper = MsSqlHelper(
    server=SQL_SERVER_IP,
    database='UNIWIN_TRAIN',
    user='sa',
    password='Abc123!!!'
)

# Lấy thông tin từ bảng đã chuẩn hóa
email_list = sql_helper.execute_query("""
    SELECT [text_2] AS FullName, [text_3] AS Email, [text_4] AS Company, [text_5] AS Phone
    FROM AppCreator_4a9f8a7c_table_1
""")




# Đọc nội dung HTML
with open("email_template.html", "r", encoding="utf-8") as f:
    html_content = f.read()


def sync_email_to_report():
    source_rows = sql_helper.execute_query("""
        SELECT [text_2] AS FullName, [text_3] AS Email
        FROM AppCreator_4a9f8a7c_table_1
    """)
    for row in source_rows:
        email = row['Email']
        fullname = row['FullName']
        sql_helper.execute_non_query("""
            IF NOT EXISTS (
                SELECT 1 FROM AppCreator_9e421964_table_1 WHERE [text_3] = ?
            )
            INSERT INTO AppCreator_9e421964_table_1
            ([text_2], [text_3], [text_4], [text_5], [text_6], [text_7])
            VALUES (?, ?, 'FALSE', 'FALSE', 'FALSE', 'FALSE')
        """, [email, fullname, email])

    print("✅ Đồng bộ email từ EMAIL LIST sang REPORT thành công!")

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

sync_email_to_report()

with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
    smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)

    for receiver in email_list:
        try:
            msg = create_personalized_email(receiver)
            smtp.send_message(msg)
            sql_helper.execute_non_query(
                """
                UPDATE AppCreator_9e421964_table_1
                SET [text_4] = 'TRUE'
                WHERE [text_3] = ?
                """,
                [receiver["Email"]]
            )

            print(f"✅ Đã gửi tới: {receiver['Email']} ({receiver['FullName']})")


        except Exception as e:
            print(f"❌ Lỗi gửi tới: {receiver['Email']} - {e}")
        time.sleep(30)

print("🎉 Gửi xong toàn bộ email HTML!")
