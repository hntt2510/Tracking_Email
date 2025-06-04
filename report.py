import os
import csv
import re

# === Cấu hình ===
log_file_path = r"D:\ThanhTam\send\tracking_logs\tracking.log"
report_file_path = r"D:\ThanhTam\send\tracking_logs\report.csv"
email_list_path = r"D:\ThanhTam\send\email_list.csv"

link1 = "https://infoasia.com.vn/"
link2 = "https://zalo.me/0933823946"

# === Đọc danh sách email đã gửi ===
sent_emails = []
with open(email_list_path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row["Email"].strip().lower()
        if email:
            sent_emails.append(email)

# === Regex khớp log theo chuẩn server mới ===
log_pattern = re.compile(
    r"\[(.*?)\] EVENT: (OPEN|CLICK) \| EMAIL: (.*?)"
    r"(?: \| INFO: (link1|link2) -> (.*))?$"
)

# === Khởi tạo thống kê mặc định ===
stats = {
    email: {
        "status": True,          # ✅ Mặc định TRUE nếu nằm trong danh sách gửi
        "open": False,
        "click1": False,
        "click2": False
    }
    for email in sent_emails
}

# === Đọc và phân tích log nếu có ===
if os.path.exists(log_file_path):
    with open(log_file_path, encoding="utf-8") as f:
        for line in f:
            match = log_pattern.search(line.strip())
            if not match:
                continue

            _, action, raw_email, link_name, _ = match.groups()
            email = raw_email.strip().lower()

            if email not in stats:
                continue  # Bỏ qua email không nằm trong danh sách gửi

            if action == "OPEN":
                stats[email]["open"] = True
            elif action == "CLICK":
                if link_name == "link1":
                    stats[email]["click1"] = True
                elif link_name == "link2":
                    stats[email]["click2"] = True

# === Ghi file báo cáo CSV ===
os.makedirs(os.path.dirname(report_file_path), exist_ok=True)

with open(report_file_path, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["STT", "Email", "Status", "IsOpen", "Link1", "IsClick1", "Link2", "IsClick2"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for i, email in enumerate(sent_emails, 1):
        data = stats[email]
        writer.writerow({
            "STT": i,
            "Email": email,
            "Status": str(data["status"]),
            "IsOpen": str(data["open"]),
            "Link1": link1,
            "IsClick1": str(data["click1"]),
            "Link2": link2,
            "IsClick2": str(data["click2"]),
        })

print(f"✅ Báo cáo đã được tạo tại: {report_file_path}")
