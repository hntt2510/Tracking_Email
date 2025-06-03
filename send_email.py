import smtplib
from email.message import EmailMessage
import time

SMTP_SERVER = "smtp.zoho.com"
SMTP_PORT = 465
EMAIL_SENDER = "contact@infoasia.com.vn"
EMAIL_PASSWORD = "56nq cmDF NKCQ"

# Danh sách người nhận
email_list = [
    {
        "ID": "1",
        "Full Name": "Thành Tâm",
        "Email": "tam.mapp04@gmail.com",
        "Company": "InfoAsia",
        "Phone": "0909123400"
    },
    {
        "ID": "2",
        "Full Name": "Khang Tàu Khựa",
        "Email": "khangndse180170@fpt.edu.vn",
        "Company": "InfoAsia",
        "Phone": "0909123401"
    },
    {
        "ID": "3",
        "Full Name": "Thiện VĐ",
        "Email": "thienvd@outlook.com",
        "Company": "InfoAsia",
        "Phone": "0909123402"
    },
    {
        "ID": "4",
        "Full Name": "Điền NT",
        "Email": "diennt@infoasia.com",
        "Company": "InfoAsia",
        "Phone": "0909123403"
    }
]
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
        msg = create_personalized_email(receiver)
        smtp.send_message(msg)
        print(f"✅ Đã gửi tới: {receiver}")
        time.sleep(5)

print("🎉 Gửi xong toàn bộ email HTML!")