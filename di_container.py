from injector import Binder, Injector, singleton
from typing import Type, TypeVar
from apscheduler.schedulers.background import BackgroundScheduler

import config
from utils.excel_helper import ExcelHelper
from utils.mssql_helper import MsSqlHelper

T = TypeVar("T")

def configuration(binder: Binder):
  sql_helper = MsSqlHelper(config.SQL_SERVER_IP, config.SQL_DATABASE, config.SQL_USER, config.SQL_PASSWORD)
  binder.bind(MsSqlHelper, to=sql_helper)
  
  excel_helper = ExcelHelper()
  binder.bind(ExcelHelper, to=excel_helper)
  
  scheduler = BackgroundScheduler()
  scheduler.start()
  binder.bind(BackgroundScheduler, to=scheduler, scope=singleton)
  
injector = Injector([configuration])

def resolve(cls: Type[T]) -> T:
  return injector.get(cls)