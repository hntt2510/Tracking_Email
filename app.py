import os
import traceback
from flask import Flask
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

from controllers import action_controller, track_controller, test_controller, receivers_controller
from controllers.base import redirect_auto_close
from utils.logger import Logger

load_dotenv()
PORT = int(os.getenv("DEFAULT_PORT", 5000))

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
  Logger.internal_err(traceback.format_exc(), str(e))
  return redirect_auto_close(False, "Internal Error Occurred")

app.register_blueprint(action_controller.blueprint)
app.register_blueprint(track_controller.blueprint)
app.register_blueprint(receivers_controller.blueprint)
app.register_blueprint(test_controller.blueprint)