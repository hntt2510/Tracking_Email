import os
import csv
import re

email_list_file = "email_list.csv"
log_file_path = "tracking_logs/tracking.log"
report_file_path = "tracking_logs/report.csv"

sent_emails = []
with open(email_list_file, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        sent_emails.append(row["Email"].strip().lower())

pattern = re.compile(
    r"\[(.*?)\] EVENT: (OPEN|CLICK) \| EMAIL: (.*?)"
    r"(?: \| INFO: (link\d) -> (.*))?"
)

stats = {
    email: {
        "status": False,
        "open": False,
        "click1": False,
        "click2": False
    }
    for email in sent_emails
}

if os.path.exists(log_file_path):
    with open(log_file_path, encoding="utf-8") as f:
        for line in f:
            match = pattern.search(line)
            if not match:
                continue
            _, action, email_raw, link_name, url = match.groups()
            email = email_raw.strip().lower()
            if email not in stats:
                continue
            stats[email]["status"] = True
            if action == "OPEN":
                stats[email]["open"] = True
            elif action == "CLICK":
                link_name = (link_name or "").strip().lower()
                if link_name == "link1":
                    stats[email]["click1"] = True
                elif link_name == "link2":
                    stats[email]["click2"] = True

os.makedirs(os.path.dirname(report_file_path), exist_ok=True)
with open(report_file_path, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
        "STT", "Email", "Status", "IsOpen", "Link1", "IsClick1", "Link2", "IsClick2"
    ])
    writer.writeheader()
    for i, email in enumerate(sent_emails, 1):
        data = stats[email]
        writer.writerow({
            "STT": i,
            "Email": email,
            "Status": str(data["status"]),
            "IsOpen": str(data["open"]),
            "Link1": "https://infoasia.com.vn/",
            "IsClick1": str(data["click1"]),
            "Link2": "https://zalo.me/0933823946",
            "IsClick2": str(data["click2"])
        })

print(f"✅ Báo cáo đã được lưu tại: {report_file_path}")