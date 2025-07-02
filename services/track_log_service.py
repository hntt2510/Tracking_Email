from injector import inject

from utils.mssql_helper import MsSqlHelper
from domain.enums import TrackEvent

class TrackLogService:
  @inject
  def __init__(self, sql_helper: MsSqlHelper):
    self.sql_helper = sql_helper
    
  def log_event(self, event_type: TrackEvent, email: str, target_url: str = ""):
    self.sql_helper.execute_non_query(
      "insert into tracking_log (Email, EventType, TargetUrl, Timestamp) "
      "values (?, ?, ?, getdate())",
      [email, event_type.value, target_url]
    )