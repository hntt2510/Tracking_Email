import os
import csv
import re

# === Cấu hình ===
log_file_path = "tracking_logs/tracking.log"
report_file_path = "tracking_logs/report.csv"
email_list_path = "email_list.csv"

link1 = "https://infoasia.com.vn/"
link2 = "https://zalo.me/0933823946"

# === Regex log tracking_server.py ===
log_pattern = re.compile(
    r"\[(.*?)\] EVENT: (OPEN|CLICK) \| EMAIL: (.*?)"
    r"(?: \| INFO: (link1|link2) -> .*)?$"
)

# === Đọc danh sách email mới ===
sent_emails = []
with open(email_list_path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        sent_emails.append(row["Email"].strip().lower())

# === Khởi tạo dữ liệu thống kê (mặc định TRUE vì đã gửi) ===
stats = {
    email: {
        "status": True,
        "open": False,
        "click1": False,
        "click2": False
    }
    for email in sent_emails
}

# === Nếu đã có report trước đó → giữ các flag TRUE cũ ===
if os.path.exists(report_file_path):
    with open(report_file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row["Email"].strip().lower()
            if email in stats:
                stats[email]["open"] = row["IsOpen"] == "TRUE" or stats[email]["open"]
                stats[email]["click1"] = row["IsClick1"] == "TRUE" or stats[email]["click1"]
                stats[email]["click2"] = row["IsClick2"] == "TRUE" or stats[email]["click2"]

# === Đọc tracking log mới ===
if os.path.exists(log_file_path):
    with open(log_file_path, encoding="utf-8") as f:
        for line in f:
            match = log_pattern.search(line.strip())
            if not match:
                continue
            _, action, raw_email, link_name = match.groups()
            email = raw_email.strip().lower()
            if email not in stats:
                continue
            if action == "OPEN":
                stats[email]["open"] = True
            elif action == "CLICK":
                if link_name == "link1":
                    stats[email]["click1"] = True
                elif link_name == "link2":
                    stats[email]["click2"] = True

# === Ghi file báo cáo ===
os.makedirs(os.path.dirname(report_file_path), exist_ok=True)

with open(report_file_path, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["STT", "Email", "Status", "IsOpen", "Link1", "IsClick1", "Link2", "IsClick2"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for i, email in enumerate(sent_emails, 1):
        writer.writerow({
            "STT": i,
            "Email": email,
            "Status": "TRUE",
            "IsOpen": str(stats[email]["open"]).upper(),
            "Link1": link1,
            "IsClick1": str(stats[email]["click1"]).upper(),
            "Link2": link2,
            "IsClick2": str(stats[email]["click2"]).upper(),
        })

print(f"✅ Báo cáo đã được cập nhật tại: {report_file_path}")
