import smtplib
import time
import random

from email.message import EmailMessage
from services.oadata_service import OaDataService

oadata_service = OaDataService()

def open_smtp_connection(smtp_server, smtp_port, email_sender, email_password):
    try:
        smtp = smtplib.SMTP_SSL(smtp_server, int(smtp_port), timeout=10)
        smtp.login(email_sender, email_password)
        print('Connected with SMTP_SSL')
        return smtp
    except Exception as e:
        print(f'Faild to connect with SMTP_SSL: {e}; try with STARTTLS...')
    try:
        if int(smtp_port) == 465:
            smtp_port = 587
        smtp = smtplib.SMTP(smtp_server, int(smtp_port), timeout=10)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(email_sender, email_password)
        print('Connected with STARTTLS')
        return smtp
    except Exception as e:
        print(f'Faild to connect STARTTLS: {e}')
        raise

def create_personalized_email(row, html_template, email_subject, email_sender, campaign_name, campaign_id: int):
    rand = str(random.randint(100000, 999999))
    open_track_url = f"http://202.43.110.175:5000/open?email={row['Email']}&campaign={campaign_name}&rand={rand}&campaign_id={campaign_id}"
    click_link1_url = f"http://202.43.110.175:5000/click?email={row['Email']}&campaign={campaign_name}&target=https://infoasia.com.vn&campaign_id={campaign_id}"
    click_link2_url = f"http://202.43.110.175:5000/click?email={row['Email']}&campaign={campaign_name}&target=https://zalo.me&campaign_id={campaign_id}"

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

def send_all_emails(campaign_config_id):
    print(f'Start sending email for campaign ID: {campaign_config_id}')
    try:
        # get setting
        campaign_config_data = oadata_service.get_campaign_setting_by_id(campaign_config_id)
        if not campaign_config_data:
            print(f"Not found campaign setting id: {campaign_config_id}.")
            return
        
        campaign_name = campaign_config_data['CampaignName']
        receiver_list_id = campaign_config_data['ReceiverListID']
        email_template_id = campaign_config_data['EmailTemplateID']
        smtp_server    = campaign_config_data['SMTPServer']
        smtp_port      = campaign_config_data['SMTPPort']
        email_sender   = campaign_config_data['SMTPEmail']
        email_password = campaign_config_data['SMTPPass']

        receiver_list = oadata_service.get_receiver_list(receiver_list_id)
        if not receiver_list:
            print(f'Not found receiver list with id: {receiver_list_id}.')
            return

        html_template_content, email_subject = oadata_service.get_email_template_html(email_template_id)
        if not html_template_content:
            print(f'Not found email template with id: {email_template_id}.')
            return

        oadata_service.update_campaign_setting_status(campaign_config_id, 2) # status = 2 is running

        # now we have trigger for that dont need this function
        #sync_email_to_report(campaign_name, receiver_list)
        
        email_to_send = oadata_service.get_list_email_for_send(campaign_config_id)

        if not email_to_send:
            print(f'Not found email need send for campaign ID: {campaign_config_id}')
            return

        smtp = open_smtp_connection(smtp_server, smtp_port, email_sender, email_password)
        with smtp:
            for row in email_to_send:
                recipient = row['Email']
                full_name = row['FullName']
                company = row['Company']
                phone = row['Phone']
                try:
                    msg = create_personalized_email({'FullName': full_name, 'Email': recipient, 'Company': company, 'Phone': phone}, html_template_content, email_subject, email_sender, campaign_name, campaign_config_id)
                    smtp.send_message(msg)
                    oadata_service.update_campaign_dashboard_status_send(campaign_config_id, recipient, True)
                    print(f'Send mail success to {recipient} in campaign: {campaign_name}')
                except Exception as e:
                    print(f'Internal exception when send mail to {recipient} in campaign: {campaign_name} - {e}')
                time.sleep(30)

        print(f'Send all mail complete for campaign ID: {campaign_name}')
        oadata_service.update_campaign_setting_status(campaign_config_id, 1)
    except Exception as e:
        print(f'Internal exception when send mail for campaign ID: {campaign_config_id} - {e}')