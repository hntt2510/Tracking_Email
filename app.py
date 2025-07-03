import os
import traceback
from flask import Flask
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from controllers import action_controller, track_controller, test_controller, receivers_controller
from controllers.base import redirect_auto_close
from utils.logger import Logger
from di_container import resolve
from services import ScheduleService
from domain.models import ScheduleInfo

app = Flask(__name__, static_folder='statics/')

with app.app_context():
  print(">>>>>> Start retry schedule job")
  schedule_service = resolve(ScheduleService)
  scheduler = resolve(BackgroundScheduler)
  schedules = schedule_service.get_schedule_for_retry()
  if schedules is not None:
    for row in schedules:
      info = ScheduleInfo.from_dict(row)
      scheduler.add_job(action_controller.send_mail_func, "cron", hour=info.hour, minute=info.minute, args=[info.id], id=str(info.id))
      schedule_service.insert_or_update_schedule(info.id, "daily", datetime.now().replace(hour=info.hour, minute=info.minute), "R")
      print(f"Start daily ({info.hour} : {info.minute}) send email in background with campaign ID: {info.id}")
  print(">>>>>> Complete retry schedule job")
      
  
@app.route("/", methods=["GET"])
def index():
  return "Server is running! Routes: " + ", ".join(sorted(r.rule for r in app.url_map.iter_rules())), 200

@app.route("/ping", methods=["GET"])
def pong():
  return "pong-123", 200

@app.route("/error", methods=["GET"])
def error():
  raise Exception("my error")

@app.errorhandler(Exception)
def exception_handle(e):
  Logger.internal_err(traceback.format_exc(), str(e))
  return redirect_auto_close(False, "Internal Error Occurred")

app.register_blueprint(action_controller.blueprint)
app.register_blueprint(track_controller.blueprint)
app.register_blueprint(receivers_controller.blueprint)
app.register_blueprint(test_controller.blueprint)