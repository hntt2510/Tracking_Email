from typing import Any, Dict, List
import pyodbc
from injector import singleton

class MsSqlHelper:
  @singleton
  def __init__(self, server, database, user, password):
    self.conn_str = (
      f'DRIVER={{ODBC Driver 17 for SQL Server}};'
      f'SERVER={server};DATABASE={database};UID={user};PWD={password}'
    )

  def execute_query(self, query: str, params: Any = None) -> List[Dict[str, Any]]:
    with pyodbc.connect(self.conn_str) as conn:
      with conn.cursor() as cursor:
        cursor.execute(query, params or [])
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return results

  def execute_non_query(self, query: str, params: Any = None) -> int:
    with pyodbc.connect(self.conn_str) as conn:
      with conn.cursor() as cursor:
        cursor.execute(query, params or [])
        row_count = cursor.rowcount
        conn.commit()
    return row_count

  def execute_scalar(self, query: str, params: Any = None) -> Any:
    with pyodbc.connect(self.conn_str) as conn:
      with conn.cursor() as cursor:
        cursor.execute(query, params or [])
        val = cursor.fetchone()
        return val[0] if val else 0
