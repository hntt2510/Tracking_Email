import threading
import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, redirect, render_template_string
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

def redirect_auto_close(status: bool, message: str, close_time: int = 5):
    status_str = "Success" if status else "Failure"
    status_color = "#28a745" if status else "#dc3545"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Email Tracking</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f8f9fa;
                color: #343a40;
                text-align: center;
                padding-top: 100px;
            }}
            .header {{
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 30px;
                color: #007bff;
            }}
            .status {{
                font-size: 28px;
                font-weight: bold;
                color: {status_color};
            }}
            .message {{
                font-size: 22px;
                margin-top: 20px;
            }}
            .countdown {{
                font-size: 18px;
                margin-top: 40px;
                color: #6c757d;
            }}
        </style>
        <script type="text/javascript">
            let countdown = {close_time};
            function updateCountdown() {{
                document.getElementById('countdown').textContent = countdown;
                if (countdown === 0) {{
                    window.open('', '_self', '');
                    window.close();
                }}
                countdown--;
            }}
            window.onload = function() {{
                updateCountdown();
                setInterval(updateCountdown, 1000);
            }};
        </script>
    </head>
    <body>
        <div class="header">Response from Email Tracking System</div>
        <div class="status">Status: {status_str}</div>
        <div class="message">{message}</div>
        <div class="countdown">
            This page will close automatically after <span id="countdown">{close_time}</span> seconds.
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/run', methods=['GET'])
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

@app.route('/schedule', methods=['GET'])
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