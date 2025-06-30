import threading
import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, redirect
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

from services.oadata_service import OaDataService
from send_email import send_all_emails
from utils.logger import Logger

# --- Tải biến môi trường ---
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

@app.route("/test_schedule/<int:id>", methods=["GET"])
def test_schedule(id: int):
    print(id)
    job = scheduler.get_job(str(id))
    if job is not None:
        return "job already running", 200
    
    if id == 1:
        scheduler.add_job(test, "date", run_date=datetime.now(), args=["one_time"])
        return "date job", 200
    elif id == 2:
        scheduler.add_job(test, "interval", seconds=5, args=["interval"], id=str(id))
        return "interval job", 200
    elif id == 3:
        scheduler.add_job(test, "cron", hour=14, minute=10, args=["daily"], id=str(id))
        return "daily job", 200
    else:
        return "no action", 200
    
def test(target: str = ""):
    print(f"test - {target}")

@app.route('/run', methods=['GET'])
def run_send():
    setting_id_param = request.args.get("id", None)

    if not setting_id_param:
        return jsonify(success=False, message="Campaign ID not found"), 400
    try:
        setting_id = int(setting_id_param)
    except ValueError:
        return jsonify(success=False, message=f"Campaign ID invalid: {setting_id_param}"), 400

    #threading.Thread(target=send_all_emails, args=(campaign_config_id,), daemon=True).start()
    scheduler.add_job(send_all_emails, "date", run_date=datetime.now(), args=[setting_id])
    return jsonify(success=True, message=f"Start send email in background with campaign ID: {setting_id}"), 202

@app.route('/schedule', methods=['GET'])
def schedule_send():
    setting_id_param = request.args.get("id", None)
    if not setting_id_param:
        return jsonify(success=False, message="Campaign ID not found"), 400
    try:
        setting_id = int(setting_id_param)
    except ValueError:
        return jsonify(success=False, message=f"Campaign ID invalid: {setting_id_param}"), 400
    
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
            return jsonify(success=True, message=f"Start one time at {schedule_date.strftime("%d/%m/%Y - %H:%M")} send email in background with campaign ID: {setting_id}"), 202
        elif schedule_type == 2:
            scheduler.add_job(send_all_emails, "cron", hour=hour, minute=minute, args=[setting_id], id=str(setting_id))
            return jsonify(success=True, message=f"Start daily ({hour} : {minute}) send email in background with campaign ID: {setting_id}"), 202
        else:
            return jsonify(success=False, message=f"ScheduleType not found for campaign ID: {setting_id}"), 202
    else:
        scheduler.remove_job(str(setting_id))
        return jsonify(success=True, message=f"Stop daily send email in background with campaign ID: {setting_id}"), 202

@app.route("/open", methods=["GET"])
def track_open():
    email = request.args.get("email", "").strip()
    campaign_name = request.args.get("campaign", None)
    campaign_id = request.args.get("campaign_id", None)
    if not email:
        return "", 204
    
    oadata_service.log_event("OPEN", email)
    oadata_service.update_campaign_dashboard_statuses(email, "OPEN", campaign_name, campaign_id, True)
    return "", 204

@app.route("/click", methods=["GET"])
def track_click():
    email = request.args.get("email", "unknown").strip()
    target_url = request.args.get("target", None)
    campaign_name = request.args.get("campaign", None)
    campaign_id = request.args.get("campaign_id", None)
    
    if not target_url:
        return "Destination url not found", 400
    
    oadata_service.log_event("CLICK", email, target_url)
    
    if "infoasia.com.vn" in target_url.lower():
        oadata_service.update_campaign_dashboard_statuses(email, "CLICK_LINK1", campaign_name, campaign_id, True)
    elif "zalo.me" in target_url.lower():
        oadata_service.update_campaign_dashboard_statuses(email, "CLICK_LINK2", campaign_name, campaign_id, True)
    
    return redirect(target_url)