import os
from flask import Flask
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

from services.oadata_service import OaDataService
from controllers import action_controller, track_controller
from controllers.base_controller import redirect_auto_close
from utils.logger import Logger

load_dotenv()
PORT = int(os.getenv("DEFAULT_PORT", 5000))

oadata_service = OaDataService()
scheduler = BackgroundScheduler()
scheduler.start()

app = Flask(__name__, static_folder='statics/')

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
  Logger.error(str(e))
  return redirect_auto_close(False, "Internal Error Occurred")

app.register_blueprint(action_controller.blueprint)
app.register_blueprint(track_controller.blueprint)