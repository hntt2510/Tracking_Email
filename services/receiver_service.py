from typing import Tuple

from utils.mssql_helper import MsSqlHelper
from utils.logger import Logger
import config

class ReceiverService:
  def __init__(self):
    self.sql_helper = MsSqlHelper(config.SQL_SERVER_IP, config.SQL_DATABASE, config.SQL_USER, config.SQL_PASSWORD)
  
  def get_import_receiver_file(self, list_id: int):
    query = f"exec sp_crm_GetImportReceiverFile ?"
    data = self.sql_helper.execute_query(query, [list_id])
    return data[0] if data else None
  
  def insert_or_update_receiver(self, list_id: int, import_data: Tuple[Tuple]):
    tvp_data = [
      "type_crm_ImportReceiverAction",
      "dbo",
      *import_data
    ]
    query = f"exec sp_crm_ImportReceiverAction ?, ?"
    result = self.sql_helper.execute_non_query(query, [list_id, tvp_data])
    return result > 0