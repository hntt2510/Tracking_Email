import smtplib
import random
from typing import Dict, Any
from email.message import EmailMessage

from utils.logger import Logger

MSG_F_SMTPSSL_ERROR = "Faild to connect with SMTP_SSL: {0}; try with STARTTLS..."
MSG_F_SMTP_ERROR = "Faild to connect STARTTLS: {0}"
#URL_OPEN_TRACK = f"http://202.43.110.175:5000/track/open?email={row['Email']}&campaign={campaign_name}&rand={rand}&campaign_id={campaign_id}"
#URL_CLICK_LINK1 = f"http://202.43.110.175:5000/track/click?email={row['Email']}&campaign={campaign_name}&target=https://infoasia.com.vn&campaign_id={campaign_id}"
#URL_CLICK_LINK2 = f"http://202.43.110.175:5000/track/click?email={row['Email']}&campaign={campaign_name}&target=https://zalo.me/0933823946&campaign_id={campaign_id}"

class MailBoxService:
  def __init__(self):
    pass
  
  def open_smtp_connection(self, smtp_server, smtp_port, email_sender, email_password):
    try:
      smtp = smtplib.SMTP_SSL(smtp_server, int(smtp_port), timeout=10)
      smtp.login(email_sender, email_password)
      return smtp
    except Exception as e:
      Logger.error(MSG_F_SMTPSSL_ERROR.format(e))
    try:
      if int(smtp_port) == 465:
        smtp_port = 587
      smtp = smtplib.SMTP(smtp_server, int(smtp_port), timeout=10)
      smtp.ehlo()
      smtp.starttls()
      smtp.login(email_sender, email_password)
      return smtp
    except Exception as e:
      Logger.error(MSG_F_SMTP_ERROR.format(e))
      raise
    
  def create_personalized_email(self, row: Dict[str, str], html_template: str, email_subject, email_sender, campaign_name, campaign_id: int):
    rand = str(random.randint(100000, 999999))
    open_track_url = f"http://202.43.110.175:5000/track/open?email={row['Email']}&campaign={campaign_name}&rand={rand}&campaign_id={campaign_id}"
    click_link1_url = f"http://202.43.110.175:5000/track/click?email={row['Email']}&campaign={campaign_name}&target=https://infoasia.com.vn&campaign_id={campaign_id}"
    click_link2_url = f"http://202.43.110.175:5000/track/click?email={row['Email']}&campaign={campaign_name}&target=https://zalo.me/0933823946&campaign_id={campaign_id}"

    html = (
      html_template
      .replace('[ FULLNAME ]', row['FullName'])
      .replace('[ EMAIL ]', row['Email'])
      .replace('[ COMPANY ]', row['Company'])  # Thêm Company
      .replace('[ PHONE ]', row['Phone'])      # Thêm Phone
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