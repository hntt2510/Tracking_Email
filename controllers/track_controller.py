from flask import Blueprint, request, redirect
from services.oadata_service import OaDataService

oadata_service = OaDataService()
blueprint = Blueprint("track", __name__, url_prefix="/track")

@blueprint.route("/open", methods=["GET"])
def track_open():
  email = request.args.get("email", "").strip()
  campaign_name = request.args.get("campaign", None)
  campaign_id = request.args.get("campaign_id", None)
  if not email:
    return "", 204
  
  oadata_service.log_event("OPEN", email)
  oadata_service.update_campaign_dashboard_statuses(email, "OPEN", campaign_name, campaign_id, True)
  return "", 204

@blueprint.route("/click", methods=["GET"])
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