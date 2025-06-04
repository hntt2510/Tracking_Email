import smtplib
from email.message import EmailMessage
import time
import csv

SMTP_SERVER = "smtp.zoho.com"
SMTP_PORT = 465
EMAIL_SENDER = "erp@infoasia.com.vn"
EMAIL_PASSWORD = "vrFTf82cehmW"

# Danh sách người nhận
email_list = []
with open("email_list.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email_list.append(row)


with open("email_template.html", "r", encoding="utf-8") as f:
    html_content = f.read()
# 
def create_personalized_email(row):
    # Tạo HTML cá nhân hóa
    personalized_html = html_content\
        .replace("[ FULLNAME ]", row["Full Name"])\
        .replace("[ COMPANY ]", row["Company"])\
        .replace("[ PHONE ]", row["Phone"])\
        .replace("[ EMAIL ]", row["Email"])

    msg = EmailMessage()
    msg["Subject"] = "[INFOASIA] ERP ENHANCE - NÂNG CẤP ERP TOÀN DIỆN"
    msg["From"] = EMAIL_SENDER
    msg["To"] = row["Email"]
    
    msg.set_content("Email yêu cầu trình duyệt hỗ trợ HTML.")
    msg.add_alternative(personalized_html, subtype="html")

    return msg

with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
    smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)

    for receiver in email_list:
        try:
            msg = create_personalized_email(receiver)
            smtp.send_message(msg)
            print(f"✅ Đã gửi tới: {receiver['Email']} ({receiver['Full Name']})")
        except Exception as e:
            print(f"❌ Lỗi gửi tới: {receiver['Email']} - {e}")
        time.sleep(30)

print("🎉 Gửi xong toàn bộ email HTML!")