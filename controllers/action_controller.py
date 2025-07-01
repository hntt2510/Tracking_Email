from flask import Blueprint, request
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from services.oadata_service import OaDataService
from send_email import send_all_emails
from controllers.base_controller import redirect_auto_close

scheduler = BackgroundScheduler()
scheduler.start()
oadata_service = OaDataService()
blueprint = Blueprint("action", __name__, url_prefix="/action")

@blueprint.route("/run", methods=['GET'])
def run_send():
  setting_id_param = request.args.get("id", None)

  if not setting_id_param:
    return redirect_auto_close(False, "Campaign ID not found")
  try:
    setting_id = int(setting_id_param)
  except ValueError:
    return redirect_auto_close(False, f"Campaign ID invalid: {setting_id_param}")

  scheduler.add_job(send_all_emails, "date", run_date=datetime.now(), args=[setting_id])
  return redirect_auto_close(True, f"Start send email in background with campaign ID: {setting_id}")

@blueprint.route("/schedule", methods=['GET'])
def schedule_send():
  setting_id_param = request.args.get("id", None)
  if not setting_id_param:
    return redirect_auto_close(False, "Campaign ID not found")
  try:
    setting_id = int(setting_id_param)
  except ValueError:
    return redirect_auto_close(False, f"Campaign ID invalid: {setting_id_param}")
  
  job = scheduler.get_job(str(setting_id))
  if job is None:
    time_setting = oadata_service.get_time_for_schedule_by_id(setting_id)
    hour = int(time_setting["Hour"])
    minute = int(time_setting["Minute"])
    schedule_type = int(time_setting["ScheduleType"])
    if schedule_type == 1:
      now = datetime.now()
      schedule_date = datetime(now.year, now.month, now.day, hour=hour, minute=minute)
      schedule_date = schedule_date if schedule_date > now else schedule_date + timedelta(days=1)
      scheduler.add_job(send_all_emails, "date", run_date=schedule_date, args=[setting_id])
      return redirect_auto_close(True, f"Start one time at {schedule_date.strftime("%d/%m/%Y - %H:%M")} send email in background with campaign ID: {setting_id}")
    elif schedule_type == 2:
      scheduler.add_job(send_all_emails, "cron", hour=hour, minute=minute, args=[setting_id], id=str(setting_id))
      return redirect_auto_close(True, f"Start daily ({hour} : {minute}) send email in background with campaign ID: {setting_id}")
    else:
      return redirect_auto_close(False, f"ScheduleType not found for campaign ID: {setting_id}")
  else:
    scheduler.remove_job(str(setting_id))
    return redirect_auto_close(True, f"Stop daily send email in background with campaign ID: {setting_id}")