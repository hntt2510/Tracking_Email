from flask import Blueprint, jsonify
from utils.mssql_helper import MsSqlHelper
from utils.excel_helper import ExcelHelper
from services.receiver_service import ReceiverService
import config

sqlhelper = MsSqlHelper(config.SQL_SERVER_IP, config.SQL_DATABASE, config.SQL_USER, config.SQL_PASSWORD)
receiver_service = ReceiverService()
excel_helper = ExcelHelper()
blueprint = Blueprint("test", __name__, url_prefix="/test")

@blueprint.route("pass-tvp", methods=["GET"])
def pass_tvp():
  tvp_data = [
    "type_GiaTest",
    "dbo",
    (1, "Foo"),
    (2, "Bar")
  ]
  sql = "exec sp_GiaTest ?"
  print(tvp_data)
  a = sqlhelper.execute_query(sql, [tvp_data])
  print(a)
  return "Ok", 200

@blueprint.route("t", methods=["GET"])
def t():
  #data = excel_helper.read_data("C:\\workdata\\Tracking_Email\\email.xlsx", "A:D")
  #root = "C:\\workdata\\Tracking_Email"
  file_import = receiver_service.get_import_receiver_file(2)
  file_path = f"{config.RECEIVER_FOLDER_STORE}\\{file_import["FILE_NAME"]}.{file_import["FILE_EXT"]}"
  
  #result = receiver_service.insert_or_update_receiver(2, data)
  return str(file_path), 200