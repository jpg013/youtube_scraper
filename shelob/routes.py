from flask import Blueprint, request, current_app as app
from werkzeug import exceptions
import json
from shelob.config import AppConfig
from shelob.crawler_manager import CrawlerManager

crawler_manager = CrawlerManager()

# Set up a blueprint for crawlers
crawlers_bp = Blueprint('crawlers_bp', __name__)

# Setup a Blueprint for health endpoint
health_bp = Blueprint("health_bp", __name__)

config_bp = Blueprint("config_bp", __name__)

@config_bp.route("/config", methods=["GET"])
def get_config():
    """Return application config"""
    response=json.dumps(AppConfig.get_dict())
    return response, 200

@app.before_request
def log_request_info():
    app.logger.info("incoming request at path \"{}\" with data {}".format(request.path, request.get_data()))

@health_bp.route("/health", methods=["GET"])
def get_health():
    """Return health status"""
    response=json.dumps({ 
        "status": "OK",
        "build_number": AppConfig.BUILD_NUMBER,
        "version": AppConfig.VERSION,
        "component": AppConfig.COMPONENT,
        "namespace": AppConfig.NAMESPACE,
        "environment": AppConfig.ENVIRONMENT,
        "sub_environment": AppConfig.SUB_ENVIRONMENT
    })
    return response, 200

@crawlers_bp.route('/crawlers/youtube_profile', methods=["POST"])
def crawl_youtube_profile():
    """Crawl youtube profile"""
    channel_id = request.json.get("context", {}).get("channel_id", None)
    task_id = request.json.get("task_id", None)

    if channel_id is None:
        raise exceptions.BadRequest("invalid channel_id")

    if task_id is None:
        raise exceptions.BadRequest("invalid task_id")

    crawler_manager.schedule_crawl_task(
        crawler_name="youtube_profile_spider",
        task_id=task_id,
        channel_id=channel_id,
    )
    
    # Return 200 status
    return app.response_class(
        response=json.dumps({
            "status": "OK",
        }),
        status=200,
        mimetype='application/json'
    )