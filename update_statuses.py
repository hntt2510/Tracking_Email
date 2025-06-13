# update_statuses.py

from mssql_helper import MsSqlHelper
from dotenv import load_dotenv
import os

load_dotenv()
SQL_SERVER_IP = os.getenv('SQL_SERVER_IP')

sql = MsSqlHelper(
    server=SQL_SERVER_IP,
    database='UNIWIN_TRAIN',
    user='sa',
    password='Abc123!!!'
)

# Lấy danh sách tất cả email có trong tracking_log
def update_statuses(sql_helper):
    # Lấy danh sách tất cả email có trong tracking_log
    emails = sql_helper.execute_query("SELECT DISTINCT Email FROM tracking_log")

    for row in emails:
        email = row["Email"]

        # Nếu có bất kỳ log nào => Status = TRUE
        sql.execute_non_query("""
            UPDATE AppCreator_9e421964_table_1 SET [text_4] = 'TRUE' WHERE [text_3] = ?
        """, [email])

        # Nếu có OPEN => IsOpen = TRUE
        sql.execute_non_query("""
            IF EXISTS (
                SELECT 1 FROM tracking_log WHERE Email = ? AND EventType = 'OPEN'
            )
            UPDATE AppCreator_9e421964_table_1 SET [text_5] = 'TRUE' WHERE [text_3] = ?
        """, [email, email])

        # Nếu CLICK vào infoasia.com.vn => IsClick1 = TRUE
        sql.execute_non_query("""
            IF EXISTS (
                SELECT 1 FROM tracking_log 
                WHERE Email = ? AND EventType = 'CLICK' AND TargetUrl LIKE '%infoasia.com.vn%'
            )
            UPDATE AppCreator_9e421964_table_1 SET [text_6] = 'TRUE' WHERE [text_3] = ?
        """, [email, email])

        # Nếu CLICK vào zalo.me => IsClick2 = TRUE
        sql.execute_non_query("""
            IF EXISTS (
                SELECT 1 FROM tracking_log 
                WHERE Email = ? AND EventType = 'CLICK' AND TargetUrl LIKE '%zalo.me%'
            )
            UPDATE AppCreator_9e421964_table_1 SET [text_7] = 'TRUE' WHERE [text_3] = ?
        """, [email, email])
    print("✅ Cập nhật trạng thái thành công!")