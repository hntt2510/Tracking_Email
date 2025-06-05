import re

INPUT_LOG = "tracking_logs/logs.txt"
OUTPUT_LOG = "tracking_logs/tracking.log"

# Regex chấp nhận cả dòng bắt đầu bằng ISO timestamp rồi mới tới [YYYY-MM-DD HH:MM:SS]
log_pattern = re.compile(
    r".*\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] EVENT: (OPEN|CLICK) \| EMAIL: .+"
)

with open(INPUT_LOG, "r", encoding="utf-8") as infile, \
     open(OUTPUT_LOG, "w", encoding="utf-8") as outfile:
    count = 0
    for line in infile:
        if log_pattern.match(line.strip()):
            # Trích xuất phần từ dấu [ trở đi
            start = line.find("[")
            if start != -1:
                clean_line = line[start:].strip()
                outfile.write(clean_line + "\n")
                count += 1

print(f"✅ Đã trích xuất {count} dòng tracking log chuẩn vào '{OUTPUT_LOG}'")
