import requests
from injector import inject

from utils.mssql_helper import MsSqlHelper
from utils.logger import Logger

TABLE_TEMPLATE_EMAIL = "AppCreator_3a78932b"

class OaDataService:
  @inject
  def __init__(self, sql_helper: MsSqlHelper):
    self.sql_helper = sql_helper
  
  def get_time_for_schedule_by_id(self, setting_id: int):
    query = f"exec sp_crm_GetTimeScheduleById ?"
    time_schedule = self.sql_helper.execute_query(query, [setting_id])
    return time_schedule[0] if time_schedule else None
  
  def get_campaign_setting_by_id(self, setting_id: int):
    query = f"exec sp_crm_GetCampaignSettingById ?"
    settings = self.sql_helper.execute_query(query, [setting_id])
    return settings[0] if settings else None
  
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
    query = f"exec sp_crm_GetListReceiverNeedSend ?"
    email_to_send = self.sql_helper.execute_query(query, [setting_id])
    return email_to_send
  
  def update_campaign_setting_status(self, setting_id: int, status: int = 2):
    query = f"exec sp_crm_CampaignSettingStatusAction ?, ?"
    result = self.sql_helper.execute_non_query(query, [setting_id, status])
    return result > 0
    
  def update_campaign_dashboard_status(self, setting_id: int, email: str, event_type: str, status: bool):
    mappingAction: dict = {
      "SEND": "text_4",
      "OPEN": "text_5",
      "CLICK_LINK1": "text_6",
      "CLICK_LINK2": "text_7",
    }
    update_column = mappingAction.get(event_type, None)
    if update_column is None:
      Logger.info("Event type invalid for update")
      return False
    
    query = f"exec sp_crm_CampaignDashboardStatusAction ?, ?, ?, ?"
    result = self.sql_helper.execute_non_query(query, [setting_id, email, update_column, "TRUE" if status else "FALSE"])
    return result > 0
    
  def log_event(self, event_type: str, email: str, target_url: str = ""):
    self.sql_helper.execute_non_query(
      "insert into tracking_log (Email, EventType, TargetUrl, Timestamp) "
      "values (?, ?, ?, getdate())",
      [email, event_type, target_url]
    )