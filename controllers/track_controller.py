from flask import Blueprint, request, redirect

from di_container import resolve
from services.oadata_service import OaDataService
from domain.enums import TrackEvent

oadata_service = resolve(OaDataService)
blueprint = Blueprint("track", __name__, url_prefix="/track")

@blueprint.route("/open", methods=["GET"])
def track_open():
  email = request.args.get("email", "").strip()
  campaign_id = request.args.get("campaign_id", None)
  if not email:
    return "", 204
  
  oadata_service.log_event(TrackEvent.Open, email)
  oadata_service.update_campaign_dashboard_status(campaign_id, email, TrackEvent.Open, True)
  return "", 204

@blueprint.route("/click", methods=["GET"])
def track_click():
  email = request.args.get("email", "unknown").strip()
  target_url = request.args.get("target", None)
  campaign_id = request.args.get("campaign_id", None)
  
  if not target_url:
    return "Destination url not found", 400
  
  if "infoasia.com.vn" in target_url.lower():
    oadata_service.update_campaign_dashboard_status(campaign_id, email, TrackEvent.WebClick, True)
    oadata_service.log_event(TrackEvent.WebClick, email, target_url)
  elif "zalo.me" in target_url.lower():
    oadata_service.update_campaign_dashboard_status(campaign_id, email, TrackEvent.ZaloClick, True)
    oadata_service.log_event(TrackEvent.ZaloClick, email, target_url)
  
  return redirect(target_url)