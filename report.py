import os
import csv
import re

# === Cấu hình ===
log_file_path    = "tracking_logs/tracking.log"
report_file_path = "tracking_logs/report.csv"
email_list_path  = "email_list.csv"

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

# === Đọc report cũ nếu có ===
existing_stats = {}
if os.path.exists(report_file_path):
    with open(report_file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Lưu vào existing_stats: key=email, value={…}
        for row in reader:
            email = row["Email"].strip().lower()
            existing_stats[email] = {
                "status":  row["Status"]  == "TRUE",
                "open":    row["IsOpen"]  == "TRUE",
                "click1":  row["IsClick1"] == "TRUE",
                "click2":  row["IsClick2"] == "TRUE"
            }

# === Chuẩn bị dữ liệu thống kê ===
# stats sẽ chứa tất cả email “được gửi batch này” (theo email_list.csv)
# và sẽ được khởi tạo dựa trên existing_stats nếu email đó đã có trong report cũ
stats = {}
for email in sent_emails:
    stats[email] = {
        "status": True,
        "open":    existing_stats.get(email, {}).get("open", False),
        "click1":  existing_stats.get(email, {}).get("click1", False),
        "click2":  existing_stats.get(email, {}).get("click2", False),
    }

# === Đọc tracking log mới (nếu có) ===
if os.path.exists(log_file_path):
    with open(log_file_path, encoding="utf-8") as f:
        for line in f:
            match = log_pattern.search(line.strip())
            if not match:
                continue
            _, action, raw_email, link_name = match.groups()
            email = raw_email.strip().lower()

            # Nếu log từ email nào mà chưa có trong stats, khởi tạo
            if email not in stats:
                stats[email] = {
                    "status": True,
                    "open":    False,
                    "click1":  False,
                    "click2":  False,
                }

            # Cập nhật trạng thái từ log
            if action == "OPEN":
                stats[email]["open"] = True
            elif action == "CLICK":
                if link_name == "link1":
                    stats[email]["click1"] = True
                elif link_name == "link2":
                    stats[email]["click2"] = True

# === Xác định thứ tự email khi ghi report ===
#
#   Bước 1: Lấy tất cả email “cũ” từ existing_stats, giữ nguyên thứ tự đọc từ file CSV cũ.
#   Bước 2: Tìm xem trong sent_emails (batch mới) có những email nào chưa xuất hiện trong existing_stats,
#           xem đó là email mới, và đẩy xuống cuối danh sách.
#   Bước 3 (tùy chọn): Nếu có email chỉ xuất hiện trong stats (do đọc log) nhưng không nằm trong existing_stats
#           và cũng không nằm trong sent_emails, có thể thêm vào mục “log-only” ở sau cùng.
#
# Ví dụ:
#   existing_stats.keys() = ["a@example.com", "b@example.com", "c@example.com"]
#   sent_emails = ["b@example.com", "c@example.com", "d@example.com", "e@example.com"]
#   -> old_emails = ["a@example.com", "b@example.com", "c@example.com"]
#   -> new_batch_emails = ["d@example.com", "e@example.com"]   (vì "b" và "c" đã nằm trong existing_stats)
#   -> log_only_emails = những email trong stats.keys() mà không có trong old_emails và không có trong new_batch_emails

ordered_emails = []

# --- Bước 1: Thêm tất cả email cũ (existing_stats) vào ordered_emails,
#             giữ nguyên thứ tự đọc từ report cũ.
for email in existing_stats.keys():
    ordered_emails.append(email)

# --- Bước 2: Thêm các email mới (thuộc sent_emails nhưng chưa có trong existing_stats)
for email in sent_emails:
    if email not in existing_stats:
        ordered_emails.append(email)

# --- Bước 3 (tùy chọn): Nếu có email chỉ xuất hiện qua log (stats) mà không nằm trong existing_stats
#                       và cũng không nằm trong sent_emails, thì thêm vào cuối cùng.
for email in stats.keys():
    if (email not in existing_stats) and (email not in sent_emails):
        ordered_emails.append(email)

# === Ghi file báo cáo mới ===
os.makedirs(os.path.dirname(report_file_path), exist_ok=True)
with open(report_file_path, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["STT", "Email", "Status", "IsOpen", "Link1", "IsClick1", "Link2", "IsClick2"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Ghi từng email theo thứ tự trong ordered_emails, đánh STT tăng dần bắt đầu từ 1
    for i, email in enumerate(ordered_emails, 1):
        # Nếu email thuộc batch mới (stats), lấy số liệu từ stats; 
        # ngược lại (email cũ hoặc log-only), lấy từ existing_stats hoặc từ stats nếu chỉ có log-only
        if email in stats:
            s = stats[email]
        else:
            # Chắc chắn email trong existing_stats, vì chúng ta lấy ordered_emails từ existing_stats trước tiên
            s = existing_stats[email]

        writer.writerow({
            "STT":      i,
            "Email":    email,
            "Status":   "TRUE",
            "IsOpen":   str(s["open"]).upper(),
            "Link1":    link1,
            "IsClick1": str(s["click1"]).upper(),
            "Link2":    link2,
            "IsClick2": str(s["click2"]).upper(),
        })

print(f"✅ Báo cáo đã được cập nhật và giữ nguyên dữ liệu cũ tại: {report_file_path}")
