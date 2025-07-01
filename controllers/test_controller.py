from flask import Blueprint, jsonify
from utils.mssql_helper import MsSqlHelper
from di_container import resolve
from utils.excel_helper import ExcelHelper
from services.receiver_service import ReceiverService
from domain.models import SmtpSetting
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
  data = SmtpSetting("1", "2", "3", "4")
  return str(data), 200