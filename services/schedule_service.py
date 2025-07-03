from injector import inject
from datetime import datetime

from utils.mssql_helper import MsSqlHelper

class ScheduleService:
  @inject
  def __init__(self, sql_helper: MsSqlHelper):
    self.sql_helper = sql_helper
    
  def insert_or_update_schedule(self, id: int, type: str, schedule_time: datetime, status: str):
    query = f"exec sp_crm_InsertOrUpdateScheduleHistory ?, ?, ?, ?"
    result = self.sql_helper.execute_non_query(query, [id, type, schedule_time, status])
    return result > 0
  
  def get_schedule_for_retry(self):
    query = f"exec sp_crm_GetScheduleForRetry"
    schedules = self.sql_helper.execute_query(query)
    return schedules if schedules.__len__() > 0 else None