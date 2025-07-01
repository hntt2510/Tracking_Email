from injector import singleton
import pandas
from typing import List, Tuple

class ExcelHelper:
  @singleton
  def __init__(self):
    pass
  
  def read_data(sefl, file_path: str, columns: str, sheet: str = 0) -> Tuple[Tuple]:
    if file_path.endswith(".csv"):
      df = pandas.read_csv(file_path, usecols=columns)
    elif file_path.endswith("xlsx"):
      df = pandas.read_excel(file_path, sheet_name=sheet, usecols=columns)
    else:
      raise ValueError("Unsupport file type")
    
    if df.empty:
      raise ValueError("Empty file")
    
    rows = tuple(tuple(row) for row in df.itertuples(index=False, name=None))
    return rows