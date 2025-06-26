import smtplib
from email.message import EmailMessage
import time
import random
import requests
import os

from mssql_helper import MsSqlHelper
    
# --- Cấu hình SQL cố định ---
SQL_SERVER_IP    = '192.168.42.31'
SQL_DATABASE     = 'UNIWIN_TRAIN'
SQL_USER         = 'sa'
SQL_PASSWORD     = 'Abc123!!!'

# --- Tên bảng cố định ---
EMAIL_LIST_MASTER_TABLE   = 'AppCreator_4a9f8a7c_table_1'   # Chứa danh sách email chi tiết (FullName, Email)
EMAIL_TEMPLATE_MASTER_TABLE = 'AppCreator_3a78932b'         # Chứa các mẫu email (Tiêu đề, Link HTML)
SMTP_CONFIG_TABLE         = 'AppCreator_be2bea7b'           # Bảng TỔNG HỢP: Chứa Campaign Name, SMTP config, Receiver List ID, Email Template ID
CAMPAIGN_REPORTING_TABLE  = 'AppCreator_9e421964_table_1'   # Bảng báo cáo, lưu trạng thái gửi từng email. RECORD_NUMBER được điền theo Tên Campaign.

# --- Khởi tạo SQL helper ---
sql_helper = MsSqlHelper(
    server   = SQL_SERVER_IP,
    database = SQL_DATABASE,
    user     = SQL_USER,
    password = SQL_PASSWORD
)

# --- ÁNH XẠ TÊN CAMPAIGN SANG RECORD_NUMBER TRONG BẢNG BÁO CÁO ---
CAMPAIGN_NAME_TO_REPORT_RECORD_NUMBER_MAPPING = {
    'C01': 1,
    'C02': 2,
    # Thêm các campaign khác nếu có (ví dụ: 'C03': 3, ...)
}

# --- Hàm lấy TẤT CẢ Cấu hình Campaign từ SMTP_CONFIG_TABLE bằng RECORD_NUMBER ---
def get_campaign_full_config_by_id(config_id):
    """
    Lấy TẤT CẢ cấu hình campaign từ SMTP_CONFIG_TABLE (AppCreator_be2bea7b) dựa trên RECORD_NUMBER.
    Đây là bảng chứa đầy đủ liên kết tới các ID khác và thông tin SMTP.
    """
    query = f"""
        SELECT
            [text_1_copy_3] AS CampaignName,
            [text_1] AS SMTPServer,
            [text_1_copy_1] AS SMTPEmail,
            [text_1_copy_2] AS SMTPPass,
            [text_1_copy_4] AS SMTPPort,
            [drop_down_1] AS ReceiverListID,
            [drop_down_1_copy_5] AS EmailTemplateID
        FROM {SMTP_CONFIG_TABLE}
        WHERE [RECORD_NUMBER] = ?
    """
    settings = sql_helper.execute_query(query, [config_id])
    return settings[0] if settings else None

# --- Hàm lấy danh sách email dựa trên ReceiverListID ---
def get_receiver_list(receiver_list_id):
    """
    Lấy danh sách email từ EMAIL_LIST_MASTER_TABLE (AppCreator_4a9f8a7c_table_1)
    dựa trên RECORD_NUMBER (là ID của list).
    Cột: text_2 (FullName), text_3 (Email), text_4 (Company), text_5 (Phone).
    """
    query = f"""
        SELECT [text_2] AS FullName,
               [text_3] AS Email,
               [text_4] AS Company,
               [text_5] AS Phone
        FROM {EMAIL_LIST_MASTER_TABLE}
        WHERE [RECORD_NUMBER] = ?
    """
    return sql_helper.execute_query(query, [receiver_list_id])

# --- Hàm lấy nội dung HTML mẫu email dựa trên EmailTemplateID ---
def get_email_template_html(email_template_id):
    """
    Lấy nội dung HTML mẫu email từ EMAIL_TEMPLATE_MASTER_TABLE (AppCreator_3a78932b)
    dựa trên RECORD_NUMBER. Tiêu đề lấy từ text_1_copy_1, link HTML từ text_1_copy_2.
    """
    query = f"""
        SELECT [text_1_copy_1] AS EmailSubject,
               [text_1_copy_2] AS TemplateHtmlLink
        FROM {EMAIL_TEMPLATE_MASTER_TABLE}
        WHERE [RECORD_NUMBER] = ?
    """
    template_data = sql_helper.execute_query(query, [email_template_id])
    if not template_data:
        return None, None

    template_url = template_data[0]['TemplateHtmlLink']
    email_subject = template_data[0]['EmailSubject']

    try:
        response = requests.get(template_url)
        response.raise_for_status()
        return response.text, email_subject
    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi khi lấy mẫu từ URL '{template_url}': {e}")
        return None, None
    except Exception as e:
        print(f"❌ Lỗi không mong muốn khi lấy mẫu từ '{template_url}': {e}")
        return None, None

def open_smtp_connection(smtp_server, smtp_port, email_sender, email_password):
    """
    Cố gắng kết nối qua SSL, nếu thất bại chuyển sang STARTTLS.
    """
    try:
        smtp = smtplib.SMTP_SSL(smtp_server, int(smtp_port), timeout=10)
        smtp.login(email_sender, email_password)
        print('🔒 Kết nối SMTP_SSL đã thiết lập.')
        return smtp
    except Exception as e:
        print(f'⚠️ Kết nối SMTP_SSL thất bại: {e}; thử STARTTLS...')
    try:
        if int(smtp_port) == 465:
            smtp_port = 587
        smtp = smtplib.SMTP(smtp_server, int(smtp_port), timeout=10)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(email_sender, email_password)
        print('🔓 Kết nối STARTTLS đã thiết lập.')
        return smtp
    except Exception as e:
        print(f'❌ Kết nối STARTTLS thất bại: {e}')
        raise

# --- HÀM ĐƯỢC SỬA LỖI: sync_email_to_report ---
def sync_email_to_report(campaign_name, receiver_emails):
    """
    Đồng bộ danh sách email đã được lọc (receiver_emails) vào CAMPAIGN_REPORTING_TABLE.
    Nếu email chưa có trong campaign_name này, INSERT với status FALSE.
    RECORD_NUMBER được điền dựa trên ánh xạ CAMPAIGN_NAME_TO_REPORT_RECORD_NUMBER_MAPPING.
    """
    record_number_for_report = CAMPAIGN_NAME_TO_REPORT_RECORD_NUMBER_MAPPING.get(campaign_name)
    if record_number_for_report is None:
        print(f"⚠️ Không tìm thấy ánh xạ RECORD_NUMBER cho campaign '{campaign_name}'. Vui lòng cập nhật CAMPAIGN_NAME_TO_REPORT_RECORD_NUMBER_MAPPING.")
        return
#
# IF NOT EXISTS (
#                 SELECT 1 FROM {CAMPAIGN_REPORTING_TABLE} WHERE [text_3] = ? AND [text_2] = ?
#             )
#             BEGIN
#                 INSERT INTO {CAMPAIGN_REPORTING_TABLE}
#                     ([RECORD_NUMBER], [text_2], [text_3], [text_4], [text_5], [text_6], [text_7])
#                 VALUES (?, ?, ?, 'FALSE', 'FALSE', 'FALSE', 'FALSE');
#             END
    for r in receiver_emails:
        sql_helper.execute_non_query(f"""
            exec sp_CampaignDashboardAction ?, ?, ? 
        """, [record_number_for_report, campaign_name, r['Email']])
    print(f'✅ Đã đồng bộ danh sách người nhận cho campaign {campaign_name} → Bảng báo cáo.')

# --- HÀM ĐƯỢC SỬA LỖI: create_personalized_email ---
def create_personalized_email(row, html_template, email_subject, email_sender, campaign_name):
    """
    Tạo EmailMessage cá nhân hóa.
    Thêm param {rand} để bust cache tracking.
    Thêm campaign_name vào URL tracking.
    """
    rand = str(random.randint(100000, 999999))
    open_track_url = f"http://202.43.110.175:5000/open?email={row['Email']}&campaign={campaign_name}&rand={rand}"
    click_link1_url = f"http://202.43.110.175:5000/click?email={row['Email']}&campaign={campaign_name}&target=https://infoasia.com.vn"
    click_link2_url = f"http://202.43.110.175:5000/click?email={row['Email']}&campaign={campaign_name}&target=https://zalo.me"

    html = (
        html_template
        .replace('[ FULLNAME ]', row['FullName'])
        .replace('[ EMAIL ]', row['Email'])
        .replace('[ COMPANY ]', row.get('Company', 'N/A'))  # Thêm Company
        .replace('[ PHONE ]', row.get('Phone', 'N/A'))      # Thêm Phone
        .replace('{rand}', rand)
        .replace('[OPEN_TRACK_URL]', open_track_url)
        .replace('[CLICK_LINK1_URL]', click_link1_url)
        .replace('[CLICK_LINK2_URL]', click_link2_url)
    )

    msg = EmailMessage()
    msg['Subject'] = email_subject
    msg['From'] = email_sender
    msg['To'] = row['Email']
    msg.set_content('Vui lòng bật chế độ xem HTML để xem đầy đủ nội dung.')
    msg.add_alternative(html, subtype='html')
    return msg

# --- HÀM ĐƯỢC SỬA LỖI: send_all_emails ---
def send_all_emails(campaign_config_id):
    """
    Thực hiện toàn bộ quá trình gửi email cho một campaign dựa trên ID cấu hình của nó.
    """
    print(f'🚀 Bắt đầu gửi email cho cấu hình campaign ID: {campaign_config_id}')
    try:
        # 1. Lấy Tên Campaign và cấu hình SMTP từ SMTP_CONFIG_TABLE
        campaign_config_data = get_campaign_full_config_by_id(campaign_config_id)
        if not campaign_config_data:
            print(f"❌ Không tìm thấy cấu hình campaign/SMTP cho ID: {campaign_config_id}.")
            return
        
        campaign_name = campaign_config_data['CampaignName']
        receiver_list_id = campaign_config_data['ReceiverListID']
        email_template_id = campaign_config_data['EmailTemplateID']

        # 2. Lấy danh sách người nhận
        receiver_list = get_receiver_list(receiver_list_id)
        if not receiver_list:
            print(f'⚠️ Không tìm thấy email nào trong danh sách người nhận với ID: {receiver_list_id}.')
            return

        # 3. Lấy nội dung và tiêu đề mẫu email
        html_template_content, email_subject = get_email_template_html(email_template_id)
        if not html_template_content:
            print(f'❌ Không thể tải nội dung hoặc tiêu đề mẫu email với ID: {email_template_id}.')
            return
        
        # 4. Lấy cấu hình SMTP
        smtp_server    = campaign_config_data['SMTPServer']
        smtp_port      = campaign_config_data['SMTPPort']
        email_sender   = campaign_config_data['SMTPEmail']
        email_password = campaign_config_data['SMTPPass']

        # 5. Cập nhật radio_button_2 thành 2 (RUNNING) khi bắt đầu gửi
        sql_helper.execute_non_query(f"""
            UPDATE {SMTP_CONFIG_TABLE}
            SET [radio_button_2] = 2
            WHERE [RECORD_NUMBER] = ?
        """, [campaign_config_id])

        # 6. Đồng bộ danh sách email vào CAMPAIGN_REPORTING_TABLE
        sync_email_to_report(campaign_name, receiver_list)

        # 7. Lấy danh sách email cần gửi (bao gồm Company và Phone)
        email_to_send = sql_helper.execute_query(f"""
           exec sp_GetEmailList ?
        """, [campaign_name])

        if not email_to_send:
            print(f'⚠️ Không có email nào cần gửi cho campaign {campaign_name}.')
            return

        # 8. Gửi email
        smtp = open_smtp_connection(smtp_server, smtp_port, email_sender, email_password)
        with smtp:
            for row in email_to_send:
                recipient = row['Email']
                full_name = row['FullName']
                company = row['Company']
                phone = row['Phone']
                try:
                    msg = create_personalized_email({'FullName': full_name, 'Email': recipient, 'Company': company, 'Phone': phone}, html_template_content, email_subject, email_sender, campaign_name)
                    smtp.send_message(msg)
                    sql_helper.execute_non_query(f"""
                        exec sp_UpdateCampaignStatus ?, ?
                    """, [campaign_config_id, recipient])
                    print(f'✅ Đã gửi tới {recipient} cho campaign {campaign_name}')
                except Exception as e:
                    print(f'❌ Lỗi khi gửi tới {recipient} cho campaign {campaign_name}: {e}')
                time.sleep(30)

        print(f'🎉 Hoàn tất gửi email cho campaign {campaign_name}')
    except Exception as e:
        print(f'🔥 Lỗi nghiêm trọng trong send_all_emails cho cấu hình campaign ID {campaign_config_id}: {e}')

if __name__ == "__main__":
    # Ví dụ gọi hàm
    send_all_emails(1)  # Thay 1 bằng RECORD_NUMBER thực tế của campaign