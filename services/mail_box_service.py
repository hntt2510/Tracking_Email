import smtplib
import random
import time
import requests
from email.message import EmailMessage
from typing import Tuple
from injector import inject

import config
from domain.models import ReceiverInfo, SmtpSetting, TemplateInfo
from services.oadata_service import OaDataService
from domain.enums import TrackEvent
from utils.logger import Logger

MSG_F_SMTPSSL_ERROR = "Faild to connect with SMTP_SSL: {0}; try with STARTTLS..."
MSG_F_SMTP_ERROR = "Faild to connect STARTTLS: {0}"
HTML_FULLNAME = "[ FULLNAME ]"
HTML_EMAIL = "[ EMAIL ]"
HTML_COMPANY = "[ COMPANY ]"
HTML_PHONE = "[ PHONE ]"
HTML_RAND = "{rand}"
HTML_OPEN_TRACK = "[OPEN_TRACK_URL]"
HTML_CLICK_LINK1 = "[CLICK_LINK1_URL]"
HTML_CLICK_LINK2 = "[CLICK_LINK2_URL]"

class MailBoxService:
  @inject
  def __init__(self, oadata_service: OaDataService):
    self.oadata_service = oadata_service
  
  def open_smtp_connection(self, smtp_setting: SmtpSetting):
    try:
      smtp = smtplib.SMTP_SSL(smtp_setting.server, smtp_setting.port, timeout=10)
      smtp.login(smtp_setting.email, smtp_setting.password)
      return smtp
    except Exception as e:
      Logger.error(MSG_F_SMTPSSL_ERROR.format(e))
    try:
      if int(smtp_port) == 465:
        smtp_port = 587
      smtp = smtplib.SMTP(smtp_setting.server, smtp_setting.port, timeout=10)
      smtp.ehlo()
      smtp.starttls()
      smtp.login(smtp_setting.email, smtp_setting.password)
      return smtp
    except Exception as e:
      Logger.error(MSG_F_SMTP_ERROR.format(e))
      raise
    
  def create_personalized_email(self, receiver: ReceiverInfo, html_template: str, email_subject, email_sender, campaign_name, campaign_id: int):
    rand = str(random.randint(100000, 999999))
    
    open_track_url = config.URL_OPEN_TRACK.format(receiver.email, campaign_name, rand, campaign_id)
    click_link1_url = config.URL_CLICK_LINK1.format(receiver.email, campaign_name, campaign_id)
    click_link2_url = config.URL_CLICK_LINK2.format(receiver.email, campaign_name, campaign_id)

    html = (
      html_template
      .replace(HTML_FULLNAME, receiver.email)
      .replace(HTML_EMAIL, receiver.email)
      .replace(HTML_COMPANY, receiver.email)
      .replace(HTML_PHONE, receiver.email)
      .replace(HTML_RAND, rand)
      .replace(HTML_OPEN_TRACK, open_track_url)
      .replace(HTML_CLICK_LINK1, click_link1_url)
      .replace(HTML_CLICK_LINK2, click_link2_url)
    )
    
    msg = EmailMessage()
    msg["Subject"] = email_subject
    msg["From"] = email_sender
    msg["To"] = receiver.email
    msg.set_content("Vui lòng bật chế độ xem HTML để xem đầy đủ nội dung.")
    msg.add_alternative(html, subtype="html")
    return msg
  
  def get_html_template(self, html_url: str) -> Tuple[bool, str]:
    try:
      response = requests.get(html_url)
      response.raise_for_status()
      return True, response.text
    except Exception as e:
      Logger.error(f"Error when get email template from '{html_url}': {e}")
      return False, None
  
  def send_all_emails(self, setting_id: int):
    Logger.info(f'Start sending email for campaign ID: {setting_id}')
    try:
      campaign_setting = self.oadata_service.get_campaign_setting_by_id(setting_id)
      if not campaign_setting:
        Logger.warning(f"Not found campaign setting id: {setting_id}.")
        return
      
      campaign_name = campaign_setting['CampaignName']
      email_template = TemplateInfo.from_dict(campaign_setting)
      smtp_setting = SmtpSetting.from_dict(campaign_setting)

      html_template_success, html_template = self.get_html_template(email_template.html_url)
      if not html_template_success:
        Logger.warning(f'Not found email template with id: {email_template.id}.')
        return

      self.oadata_service.update_campaign_setting_status(setting_id, 2) # status = 2 is running
      
      email_to_send = self.oadata_service.get_list_email_for_send(setting_id)

      if not email_to_send:
        Logger.warning(f'Not found email need send for campaign ID: {setting_id}')
        return

      smtp = self.open_smtp_connection(smtp_setting)
      with smtp:
        for row in email_to_send:
          receiver = ReceiverInfo.from_dict(row)
          try:
            msg = self.create_personalized_email(receiver, html_template, email_template.subject, smtp_setting.email, campaign_name, setting_id)
            smtp.send_message(msg)
            self.oadata_service.update_campaign_dashboard_status(setting_id, receiver.email, TrackEvent.Send, True)
            Logger.info(f'Send mail success to {receiver.email} in campaign: {campaign_name}')
          except Exception as e:
            Logger.error(f'Internal exception when send mail to {receiver.email} in campaign: {campaign_name} - {e}')
          time.sleep(30)

      Logger.info(f'Send all mail complete for campaign ID: {campaign_name}')
      self.oadata_service.update_campaign_setting_status(setting_id, 1)
    except Exception as e:
      Logger.error(f"Internal exception when send mail for campaign ID: {setting_id} - {e}")
      
  def send_all_emails_dev(self, setting_id: int):
    Logger.info(f'Start sending email for campaign ID: {setting_id}')
    try:
      campaign_setting = self.oadata_service.get_campaign_setting_by_id(setting_id)
      if not campaign_setting:
        Logger.warning(f"Not found campaign setting id: {setting_id}.")
        return
      
      campaign_name = campaign_setting['CampaignName']
      email_template = TemplateInfo.from_dict(campaign_setting)
      smtp_setting = SmtpSetting.from_dict(campaign_setting)
      
      print(str(smtp_setting))

      html_template_success, html_template = self.get_html_template(email_template.html_url)
      if not html_template_success:
        print(f'Not found email template with id: {email_template.id}.')
        return

      self.oadata_service.update_campaign_setting_status(setting_id, 2)
      
      email_to_send = self.oadata_service.get_list_email_for_send(setting_id)

      if not email_to_send:
        print(f'Not found email need send for campaign ID: {setting_id}')
        return

      for row in email_to_send:
        receiver = ReceiverInfo.from_dict(row)
        try:
          msg = self.create_personalized_email(receiver, html_template, email_template.subject, smtp_setting.email, campaign_name, setting_id)
          self.oadata_service.update_campaign_dashboard_status(setting_id, receiver.email, TrackEvent.Send, True)
          print(f'Send mail success to {receiver.email} in campaign: {campaign_name}')
          print(config.URL_OPEN_TRACK.format(receiver.email, campaign_name, 0, setting_id))
          print(config.URL_CLICK_LINK1.format(receiver.email, campaign_name, setting_id))
          print(config.URL_CLICK_LINK2.format(receiver.email, campaign_name, setting_id))
        except Exception as e:
          print(f'Internal exception when send mail to {receiver.email} in campaign: {campaign_name} - {e}')
        time.sleep(2)

      print(f'Send all mail complete for campaign ID: {campaign_name}')
      self.oadata_service.update_campaign_setting_status(setting_id, 1)
    except Exception as e:
      print(f"Internal exception when send mail for campaign ID: {setting_id} - {e}")