import os
import csv
import re
from collections import defaultdict

# Đường dẫn file
log_file_path = r"D:\ThanhTam\send\tracking_logs\tracking.log"
report_file_path = r"D:\ThanhTam\send\tracking_logs\report.csv"

# Tạo thư mục nếu chưa có
os.makedirs(os.path.dirname(report_file_path), exist_ok=True)

# Xóa file cũ nếu có
if os.path.exists(report_file_path):
    os.remove(report_file_path)

# Regex mới khớp format hiện tại
pattern = re.compile(
    r"\[(.*?)\] EVENT: (OPEN|CLICK) \| EMAIL: (.*?)"
    r"(?: \| INFO: (link\d) -> (.*))?"
)


# Link cần tracking
link1 = "https://infoasia.com.vn/"
link2 = "https://zalo.me/0933823946"

# Thống kê theo email
stats = defaultdict(lambda: {
    "open": False,
    "click1": False,
    "click2": False
})

# Đọc log
if not os.path.exists(log_file_path):
    raise FileNotFoundError("Không tìm thấy file log.")

with open(log_file_path, encoding="utf-8") as f:
    for line in f:
        match = pattern.search(line)
        if match:
            _, action, email_raw, link_name, url = match.groups()
            email = email_raw.strip().lower()

            if action == "OPEN":
                stats[email]["open"] = True
            elif action == "CLICK":
                if link_name == "link1":
                    stats[email]["click1"] = True
                if link_name == "link2":
                    stats[email]["click2"] = True

            email = email_raw.strip().lower().split()[0]  # Làm sạch email để bỏ phần 'link1/link2'
            if action == "OPEN":
                stats[email]["open"] = True
            elif action == "CLICK" and url:
                url = url.strip()
                if link1 in url:
                    stats[email]["click1"] = True
                if link2 in url:
                    stats[email]["click2"] = True

# Ghi file báo cáo
with open(report_file_path, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["STT", "Email", "Status", "Check", "IsOpen", "Link1", "IsClick1", "Link2", "IsClick2"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for i, (email, data) in enumerate(stats.items(), 1):
        writer.writerow({
            "STT": i,
            "Email": email,
            "Status": str(data["open"]),
            "Check": str(data["click1"] or data["click2"]),
            "IsOpen": str(data["open"]),
            "Link1": link1,
            "IsClick1": str(data["click1"]),
            "Link2": link2,
            "IsClick2": str(data["click2"]),
        })

print(f"✅ Báo cáo đã được lưu tại: {report_file_path}")
