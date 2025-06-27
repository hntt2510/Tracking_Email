# Bảng báo cáo nơi lưu trạng thái email
CAMPAIGN_REPORTING_TABLE = 'AppCreator_9e421964_table_1'

# Hàm cập nhật trạng thái đã được sửa đổi để nhận event_type
def update_statuses(sql_helper, email, event_type, campaign_name=None):
    """
    Cập nhật trạng thái mở (text_5) hoặc click (text_6, text_7) trong CAMPAIGN_REPORTING_TABLE.
    Cột: text_3 (Email), text_5 (isopen), text_6 (isclick1), text_7 (isclick2).
    Có thể tùy chọn thêm campaign_name để cập nhật chính xác hơn.
    """
    print(f"🔄 Đang cập nhật trạng thái cho email: {email}, sự kiện: {event_type}, campaign: {campaign_name if campaign_name else 'N/A'}")

    update_column = None
    if event_type == "OPEN":
        update_column = "[text_5]"  # text_5 là isopen
    elif event_type == "CLICK_LINK1":
        update_column = "[text_6]"  # text_6 là isclick1
    elif event_type == "CLICK_LINK2":
        update_column = "[text_7]"  # text_7 là isclick2
    elif event_type == "CLICK_OTHER":
        print(f"Thông báo: Event type CLICK_OTHER không có cột cập nhật cụ thể. Bỏ qua cập nhật cột.")
        return  # Thoát hàm nếu không có cột cần cập nhật
    else:
        print(f"Cảnh báo: Event type '{event_type}' không được xử lý trong update_statuses.")
        return  # Thoát hàm nếu event_type không hợp lệ

    if update_column:  # Chỉ thực hiện UPDATE nếu update_column đã được xác định
        try:
            where_clause = "[text_3] = ?"  # text_3 là Email
            params = [email]

            if campaign_name:
                where_clause += " AND [text_2] = ?"  # text_2 là Tên Campaign
                params.append(campaign_name)

            sql_helper.execute_non_query(f"""
                UPDATE {CAMPAIGN_REPORTING_TABLE}
                SET {update_column} = 'TRUE'
                WHERE {where_clause}
            """, params)
            print(f"✅ Đã cập nhật {update_column} cho email {email} (campaign: {campaign_name if campaign_name else 'ALL'}) thành 'TRUE'.")
        except Exception as e:
            print(f"❌ Lỗi khi cập nhật trạng thái trong {CAMPAIGN_REPORTING_TABLE} cho {email}: {e}")

if __name__ == "__main__":
    # Ví dụ sử dụng (thay bằng thực tế)
    from utils.mssql_helper import MsSqlHelper
    sql_helper = MsSqlHelper(server='192.168.42.31', database='UNIWIN_TRAIN', user='sa', password='Abc123!!!')
    update_statuses(sql_helper, "example@email.com", "OPEN", "C01")