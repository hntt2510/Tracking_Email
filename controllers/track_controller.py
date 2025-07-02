from flask import Blueprint, request, redirect

from di_container import resolve
from controllers.base import try_get_param
from services import OaDataService, TrackLogService
from domain.enums import TrackEvent

oadata_service = resolve(OaDataService)
track_log_service = resolve(TrackLogService)
blueprint = Blueprint("track", __name__, url_prefix="/track")

@blueprint.route("/open", methods=["GET"])
def track_open():
  _, email = try_get_param("email", str)
  _, campaign_id = try_get_param("campaign_id", str)
  if not email:
    return "", 204
  
  oadata_service.update_campaign_dashboard_status(campaign_id, email, TrackEvent.Open, True)
  track_log_service.log_event(TrackEvent.Open, email)
  return "", 204

@blueprint.route("/click", methods=["GET"])
def track_click():
  _, email = try_get_param("email", str)
  _, target_url = try_get_param("target", str)
  _, campaign_id = try_get_param("campaign_id", str)
  
  if not target_url:
    return "Destination url not found", 400
  
  if "infoasia.com.vn" in target_url.lower():
    oadata_service.update_campaign_dashboard_status(campaign_id, email, TrackEvent.WebClick, True)
    track_log_service.log_event(TrackEvent.WebClick, email, target_url)
  elif "zalo.me" in target_url.lower():
    oadata_service.update_campaign_dashboard_status(campaign_id, email, TrackEvent.ZaloClick, True)
    track_log_service.log_event(TrackEvent.ZaloClick, email, target_url)
  
  return redirect(target_url)