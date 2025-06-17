# update_statuses.py

from mssql_helper import MsSqlHelper
from dotenv import load_dotenv
import os

load_dotenv()
SQL_SERVER_IP = os.getenv('SQL_SERVER_IP')


# Lấy danh sách tất cả email có trong tracking_log
def update_statuses(sql_helper, email):
    # Kiểm tra OPEN
    result_open = sql_helper.execute_query("""
        SELECT TOP 1 1 FROM tracking_log 
        WHERE Email = ? AND EventType = 'OPEN'
    """, [email])
    if result_open:
        sql_helper.execute_non_query("""
            UPDATE AppCreator_9e421964_table_1
            SET [text_5] = 'TRUE'
            WHERE [text_3] = ?
        """, [email])

    # Kiểm tra CLICK link1
    result_click1 = sql_helper.execute_query("""
        SELECT TOP 1 1 FROM tracking_log 
        WHERE Email = ? AND EventType = 'CLICK' AND TargetUrl LIKE '%infoasia.com.vn%'
    """, [email])
    if result_click1:
        sql_helper.execute_non_query("""
            UPDATE AppCreator_9e421964_table_1
            SET [text_6] = 'TRUE'
            WHERE [text_3] = ?
        """, [email])

    # Kiểm tra CLICK link2
    result_click2 = sql_helper.execute_query("""
        SELECT TOP 1 1 FROM tracking_log 
        WHERE Email = ? AND EventType = 'CLICK' AND TargetUrl LIKE '%zalo.me%'
    """, [email])
    if result_click2:
        sql_helper.execute_non_query("""
            UPDATE AppCreator_9e421964_table_1
            SET [text_7] = 'TRUE'
            WHERE [text_3] = ?
        """, [email])

    print(f"✅ Đã cập nhật trạng thái cho: {email}")
