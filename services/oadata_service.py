import requests
from injector import inject

from utils.mssql_helper import MsSqlHelper
from utils.logger import Logger

TABLE_CAMPAIGN_SETTING = "AppCreator_be2bea7b"
TABLE_CAMPAIGN_DASHBOARD = "AppCreator_9e421964"
TABLE_DASHBOARD_STATUS = "AppCreator_9e421964_table_1"
TABLE_EMAIL_LIST = "AppCreator_4a9f8a7c_table_1"
TABLE_TEMPLATE_EMAIL = "AppCreator_3a78932b"

class OaDataService:
  @inject
  def __init__(self, sql_helper: MsSqlHelper):
    self.sql_helper = sql_helper
    
  def get_dashboard_id_from_campaign_id(self, setting_id: int):
    query = f"""
      select t0.RECORD_NUMBER from {TABLE_CAMPAIGN_DASHBOARD} t0
      left join {TABLE_CAMPAIGN_SETTING} t1 on t0.Campaign_ID = t1.RECORD_NUMBER
      where t1.RECORD_NUMBER = ?
    """
    dashboardId = self.sql_helper.execute_scalar(query, [setting_id])
    return dashboardId
  
  def get_time_for_schedule_by_id(self, setting_id: int):
    query = f"""
      select 
        datepart(hour, time_1) as [Hour],
        datepart(minute, time_1) as [Minute],
        radio_button_1 as [ScheduleType]
      from AppCreator_be2bea7b where RECORD_NUMBER = ?
    """
    time_schedule = self.sql_helper.execute_query(query, [setting_id])
    return time_schedule[0] if time_schedule else None
  
  def get_campaign_setting_by_id(self, setting_id: int):
    query = f"""
      select
        [text_1_copy_3] as CampaignName,
        [text_1] as SMTPServer,
        [text_1_copy_1] as SMTPEmail,
        [text_1_copy_2] as SMTPPass,
        [text_1_copy_4] as SMTPPort,
        [drop_down_1] as ReceiverListID,
        [drop_down_1_copy_5] as EmailTemplateID
      from {TABLE_CAMPAIGN_SETTING}
      where [RECORD_NUMBER] = ?
    """
    settings = self.sql_helper.execute_query(query, [setting_id])
    return settings[0] if settings else None
  
  def get_receiver_list(self, receiver_list_id: int):
    query = f"""
      select 
        [text_2] AS FullName,
        [text_3] AS Email,
        [text_4] AS Company,
        [text_5] AS Phone
      from {TABLE_EMAIL_LIST}
      where RECORD_NUMBER = ?
    """
    return self.sql_helper.execute_query(query, [receiver_list_id])
  
  def get_email_template_html(self, email_template_id: int):
    query = f"""
      select 
        [text_1_copy_1] as EmailSubject,
        [text_1_copy_2] as TemplateHtmlLink
      from {TABLE_TEMPLATE_EMAIL}
      where RECORD_NUMBER = ?
    """
    template_data = self.sql_helper.execute_query(query, [email_template_id])
    if not template_data:
      return None, None

    template_url = template_data[0]['TemplateHtmlLink']
    email_subject = template_data[0]['EmailSubject']

    try:
        response = requests.get(template_url)
        response.raise_for_status()
        return response.text, email_subject
    except requests.exceptions.RequestException as e:
        Logger.error(f"Error when get email template from '{template_url}': {e}")
        return None, None
    except Exception as e:
        Logger.error(f"Error when get email template from '{template_url}': {e}")
        return None, None
  
  def get_list_email_for_send(self, setting_id: int):
    query = f"""
      select 
        t0.Campaign_ID as [CampaignId],
        t0.RECORD_NUMBER as [DashboardId],
        t1.text_3 as Email,
        t1.text_2 as FullName,
        t1.text_4 as Company,
        t1.text_5 as Phone
      from (
        select b.Campaign_ID, a.* from {TABLE_DASHBOARD_STATUS} a
        left join {TABLE_CAMPAIGN_DASHBOARD} b on a.RECORD_NUMBER = b.RECORD_NUMBER
      ) t0
      right join {TABLE_EMAIL_LIST} t1 on t0.text_3 = t1.text_3 and t0.text_2 = t1.text_2
      where t0.Campaign_ID = ? --and t0.text_4 = 'FALSE'
    """
    email_to_send = self.sql_helper.execute_query(query, [setting_id])
    return email_to_send
  
  def update_campaign_setting_status(self, setting_id: int, status: int = 2):
    query = f"""
      update {TABLE_CAMPAIGN_SETTING}
        set [radio_button_2] = ?
      where RECORD_NUMBER = ?
    """
    self.sql_helper.execute_non_query(query, [status, setting_id])
    
  def update_campaign_dashboard_status_send(self, setting_id: int, email: str ,status: bool):
    query = f"""
      update {TABLE_DASHBOARD_STATUS}
        set text_4 = ?
      where text_3 = ? and RECORD_NUMBER = (select top 1 RECORD_NUMBER from {TABLE_CAMPAIGN_DASHBOARD} where Campaign_ID = ?)
    """
    self.sql_helper.execute_non_query(query, ["TRUE" if status else "FALSE", email, setting_id])
    
  def update_campaign_dashboard_statuses(self, email: str, event_type: str, campaign_name: str, campaign_id: int, status: bool):
    mappingAction: dict = {
      "OPEN": "text_5",
      "CLICK_LINK1": "text_6",
      "CLICK_LINK2": "text_7",
    }
    update_column = mappingAction.get(event_type, None)
    if update_column is None:
      Logger.info("Event type invalid for update")
      return
    
    try:
      self.sql_helper.execute_non_query(f"""
        UPDATE {TABLE_DASHBOARD_STATUS}
        SET {update_column} = ?
        where text_3 = ? and RECORD_NUMBER = (select top 1 RECORD_NUMBER from {TABLE_CAMPAIGN_DASHBOARD} where Campaign_ID = ?)
      """, ["TRUE" if status else "FALSE", email, campaign_id])
      Logger.info(f"Update success {update_column} for email {email} (campaign: {campaign_name}) thành {"TRUE" if status else "FALSE"}")
    except Exception as e:
      Logger.error(f"Internal exception when update status for {email} (campaign: {campaign_name}): {e}")
      
  def log_event(self, event_type: str, email: str, target_url: str = ""):
    try:
      self.sql_helper.execute_non_query(
        "insert into tracking_log (Email, EventType, TargetUrl, Timestamp) "
        "values (?, ?, ?, getdate())",
        [email, event_type, target_url]
      )
    except Exception as e:
      Logger.error(f"Internal exception when insert log event {event_type} for {email}: {e}")