import os
import inspect
from datetime import datetime

LOG_PATH = "log.txt"

class Logger:
  @staticmethod
  def _get_caller_name() -> str:
    try:
      call_stack = inspect.stack()[3]
      return call_stack.function
    except Exception:
      return ""
  
  @staticmethod
  def _log(level: str, msg: str, func: str = ""):
    timestamp = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
    funcName = Logger._get_caller_name() if func == "" else func
    logMsg = f"[{timestamp}] -> [{level}] -> [func: {funcName}]-[message: {msg}]"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
      f.write(logMsg + "\r\n")

  @staticmethod
  def info(msg: str):
    Logger._log("INFO", msg)
    
  @staticmethod
  def warning(msg: str):
    Logger._log("WARNING", msg)
    
  @staticmethod
  def error(msg: str):
    Logger._log("ERROR", msg)
    
  @staticmethod
  def internal_err(func: str, msg: str):
    Logger._log("ERROR", msg, func)