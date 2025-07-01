from flask import Blueprint, request

import config
from controllers.base import redirect_auto_close, try_get_param
from services.receiver_service import ReceiverService
from utils.excel_helper import ExcelHelper

receiver_service = ReceiverService()
excel_helper = ExcelHelper()
blueprint = Blueprint("receivers", __name__, url_prefix="/receivers")

@blueprint.route("/import", methods=["GET"])
def import_receivers():
  list_id_status, list_id = try_get_param("id", int)
  if not list_id_status:
    return redirect_auto_close(False, f"List receiver ID is not number.")
  file_import = receiver_service.get_import_receiver_file(list_id)
  file_path = f"{config.RECEIVER_FOLDER_STORE}\\{file_import["FILE_NAME"]}.{file_import["FILE_EXT"]}"
  import_data = excel_helper.read_data(file_path, "A:D")
  print(import_data)
  #result = receiver_service.insert_or_update_receiver(list_id, import_data)
  
  return redirect_auto_close(True, f"Import receiver list for \"{file_import["LIST_NAME"]}\" successful.")