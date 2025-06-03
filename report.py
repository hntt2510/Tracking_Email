import os
import csv
import re

# Đọc danh sách email đã gửi từ email_list.csv
sent_emails = []
with open("email_list.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        sent_emails.append(row["Email"].strip().lower())

# Đường dẫn file log và report
log_file_path = r"D:\ThanhTam\send\tracking_logs\tracking.log"
report_file_path = r"D:\ThanhTam\send\tracking_logs\report.csv"

# Xóa report cũ nếu có
if os.path.exists(report_file_path):
    os.remove(report_file_path)

# Regex đúng theo format log đã được chuẩn hóa
pattern = re.compile(
    r"\[(.*?)\] EVENT: (OPEN|CLICK) \| EMAIL: (.*?)"
    r"(?: \| INFO: (link\d) -> (.*))?"
)

# Khởi tạo thống kê cho từng email đã gửi
stats = {
    email: {
        "status": False,
        "open": False,
        "click1": False,
        "click2": False
    }
    for email in sent_emails
}

# Đọc và xử lý từng dòng trong log
if os.path.exists(log_file_path):
    with open(log_file_path, encoding="utf-8") as f:
        for line in f:
            match = pattern.search(line)
            if not match:
                continue
            _, action, email_raw, link_name, _ = match.groups()
            if not email_raw:
                continue
            email = email_raw.strip().lower()
            if email not in stats:
                continue

            stats[email]["status"] = True
            if action == "OPEN":
                stats[email]["open"] = True
            elif action == "CLICK":
                if (link_name or "").lower() == "link1":
                    stats[email]["click1"] = True
                elif (link_name or "").lower() == "link2":
                    stats[email]["click2"] = True

# Ghi báo cáo ra file CSV
os.makedirs(os.path.dirname(report_file_path), exist_ok=True)
with open(report_file_path, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["STT", "Email", "Status", "IsOpen", "Link1", "IsClick1", "Link2", "IsClick2"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for i, email in enumerate(sent_emails, 1):
        data = stats[email.lower()]
        writer.writerow({
            "STT": i,
            "Email": email,
            "Status": str(data["status"]),
            "IsOpen": str(data["open"]),
            "Link1": "https://infoasia.com.vn/",
            "IsClick1": str(data["click1"]),
            "Link2": "https://zalo.me/0933823946",
            "IsClick2": str(data["click2"]),
        })

print(f"✅ Báo cáo đã được lưu tại: {report_file_path}")
