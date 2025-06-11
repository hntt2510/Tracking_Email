import shutil
import time
import datetime

src = r"E:\Tracking_Email\Tracking_Email\tracking_logs\tracking.log"
dst = r"E:\Tracking_Email\Tracking_Email\tracking_backup.log"  # chỉ xuất 1 file duy nhất

while True:
    try:
        shutil.copyfile(src, dst)
        print(f"{datetime.datetime.now()}: Backup completed.")
    except Exception as e:
        print(f"Backup error: {e}")
    time.sleep(600)  # 600 giây = 10 phút
