import requests
from injector import inject

from domain.enums import TrackEvent
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
  
  def get_list_email_for_send(self, setting_id: int):
    query = f"exec sp_crm_GetListReceiverNeedSend ?"
    email_to_send = self.sql_helper.execute_query(query, [setting_id])
    return email_to_send if email_to_send.count != 0 else None
  
  def update_campaign_setting_status(self, setting_id: int, status: int = 2):
    query = f"exec sp_crm_CampaignSettingStatusAction ?, ?"
    result = self.sql_helper.execute_non_query(query, [setting_id, status])
    return result > 0
    
  def update_campaign_dashboard_status(self, setting_id: int, email: str, event_type: TrackEvent, status: bool):
    mappingAction: dict = {
      "SEND": "text_4",
      "OPEN": "text_5",
      "CLICK_LINK1": "text_6",
      "CLICK_LINK2": "text_7",
    }
    update_column = mappingAction.get(event_type.value, None)
    if update_column is None:
      Logger.info("Event type invalid for update")
      return False
    
    query = f"exec sp_crm_CampaignDashboardStatusAction ?, ?, ?, ?"
    result = self.sql_helper.execute_non_query(query, [setting_id, email, update_column, "TRUE" if status else "FALSE"])
    return result > 0