from pathlib import Path

# Tạo phiên bản mới của report.py có khả năng merge report cũ và batch mới
new_report_py = """
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
    r"\\[(.*?)\\] EVENT: (OPEN|CLICK) \\| EMAIL: (.*?)"
    r"(?: \\| INFO: (link1|link2) -> .*)?$"
)

# === Đọc danh sách email mới ===
sent_emails = []
with open(email_list_path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        sent_emails.append(row["Email"].strip().lower())

# === Đọc report cũ nếu có ===
existing_stats = {}
if os.path.exists(report_file_path):
    with open(report_file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row["Email"].strip().lower()
            existing_stats[email] = {
                "status": row["Status"] == "TRUE",
                "open": row["IsOpen"] == "TRUE",
                "click1": row["IsClick1"] == "TRUE",
                "click2": row["IsClick2"] == "TRUE"
            }

# === Khởi tạo dữ liệu thống kê (ưu tiên từ report cũ nếu có) ===
stats = {}
for email in sent_emails:
    stats[email] = {
        "status": True,
        "open": existing_stats.get(email, {}).get("open", False),
        "click1": existing_stats.get(email, {}).get("click1", False),
        "click2": existing_stats.get(email, {}).get("click2", False),
    }

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
                stats[email] = {
                    "status": True,
                    "open": False,
                    "click1": False,
                    "click2": False,
                }
            if action == "OPEN":
                stats[email]["open"] = True
            elif action == "CLICK":
                if link_name == "link1":
                    stats[email]["click1"] = True
                elif link_name == "link2":
                    stats[email]["click2"] = True

# === Gộp tất cả email từ report cũ và mới ===
all_emails = set(stats.keys()) | set(existing_stats.keys())

# === Ghi file báo cáo mới ===
os.makedirs(os.path.dirname(report_file_path), exist_ok=True)
with open(report_file_path, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["STT", "Email", "Status", "IsOpen", "Link1", "IsClick1", "Link2", "IsClick2"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for i, email in enumerate(sorted(all_emails), 1):
        s = stats.get(email) or existing_stats[email]
        writer.writerow({
            "STT": i,
            "Email": email,
            "Status": "TRUE",
            "IsOpen": str(s["open"]).upper(),
            "Link1": link1,
            "IsClick1": str(s["click1"]).upper(),
            "Link2": link2,
            "IsClick2": str(s["click2"]).upper(),
        })

print(f"✅ Báo cáo đã được cập nhật và giữ nguyên dữ liệu cũ tại: {report_file_path}")
"""

# --- PHẦN ĐÃ ĐƯỢC SỬA Ở ĐÂY ---
# Thay vì ghi ra "/mnt/data/...", ta sẽ ghi file ngay trong thư mục đang chạy
report_path = Path(__file__).parent / "report_merged.py"
Path(report_path).write_text(new_report_py, encoding="utf-8")
print(f"Đã tạo file mới: {report_path}")
