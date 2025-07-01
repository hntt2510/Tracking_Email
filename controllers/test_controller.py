from flask import Blueprint, jsonify
from utils.mssql_helper import MsSqlHelper
from di_container import resolve
from utils.excel_helper import ExcelHelper
from services.receiver_service import ReceiverService
import config

sqlhelper = resolve(MsSqlHelper)
receiver_service = resolve(ReceiverService)
excel_helper = resolve(ExcelHelper)

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
  a = sqlhelper.execute_query(sql, [tvp_data])
  return str(a), 200

@blueprint.route("t", methods=["GET"])
def t():
  #data = excel_helper.read_data("C:\\workdata\\Tracking_Email\\email.xlsx", "A:D")
  #root = "C:\\workdata\\Tracking_Email"
  file_import = receiver_service.get_import_receiver_file(2)
  file_path = f"{config.RECEIVER_FOLDER_STORE}\\{file_import["FILE_NAME"]}.{file_import["FILE_EXT"]}"
  import_data = excel_helper.read_data(file_path, "A:D")
  #result = receiver_service.insert_or_update_receiver(2, data)
  return str(import_data), 200