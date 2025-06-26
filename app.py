import threading
import os
from flask import Flask, request, jsonify, redirect
from dotenv import load_dotenv

from services.oadata_service import OaDataService
from send_email import send_all_emails

# --- Tải biến môi trường ---
load_dotenv()
PORT = int(os.getenv("DEFAULT_PORT", 5000))

oadata_service = OaDataService()

app = Flask(__name__, static_folder='statics/')

@app.route("/", methods=["GET"])
def index():
    return "Server is running! Routes: " + ", ".join(sorted(r.rule for r in app.url_map.iter_rules())), 200

@app.route("/ping", methods=["GET"])
def pong():
    return "pong", 200

@app.route('/run', methods=['GET'])
def run_send():
    campaign_config_id_str = request.args.get("id", None)
    return_url = request.args.get("return_url", None)

    if not campaign_config_id_str:
        return jsonify(success=False, message="Campaign ID not found"), 400

    try:
        campaign_config_id = int(campaign_config_id_str)
    except ValueError:
        return jsonify(success=False, message=f"Campaign ID invalid: {campaign_config_id_str}"), 400

    threading.Thread(target=send_all_emails, args=(campaign_config_id,), daemon=True).start()
    return jsonify(success=True, message=f"Start send email in background with campaign ID: {campaign_config_id}"), 202

@app.route("/open", methods=["GET"])
def track_open():
    email = request.args.get("email", "").strip()
    campaign_name = request.args.get("campaign", None)
    campaign_id = request.args.get("campaign_id", None)
    if not email:
        return "", 204
    
    oadata_service.log_event("OPEN", email)
    oadata_service.update_campaign_dashboard_statuses(email, "OPEN", campaign_name, campaign_id)
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
        oadata_service.update_campaign_dashboard_statuses(email, "CLICK_LINK1", campaign_name, campaign_id)
    elif "zalo.me" in target_url.lower():
        oadata_service.update_campaign_dashboard_statuses(email, "CLICK_LINK2", campaign_name, campaign_id)
    
    return redirect(target_url)