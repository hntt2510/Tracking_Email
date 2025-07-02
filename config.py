import os
from dotenv import load_dotenv
from typing import Callable, TypeVar

T = TypeVar("T")

load_dotenv()

def get_env(name: str, as_type: Callable[[str], T], default: T = None) -> T:
  value = os.getenv(name)
  if value is None:
    return default
  
  try:
    return as_type(value)
  except (ValueError, TypeError):
    return default
  
DEFAULT_PORT=get_env("DEFAULT_PORT", int, 5000)

SQL_SERVER_IP = os.getenv("SQL_SERVER_IP")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

RECEIVER_FOLDER_STORE = os.getenv("RECEIVER_FOLDER_STORE")

URL_OPEN_TRACK = os.getenv("URL_OPEN_TRACK")
URL_CLICK_LINK1 = os.getenv("URL_CLICK_LINK1")
URL_CLICK_LINK2 = os.getenv("URL_CLICK_LINK2")

IS_DEV = get_env("IS_DEV", bool, False)