from flask import Blueprint, request, current_app as app
from werkzeug import exceptions
import json
from shelob.task_queue import TaskQueue
from shelob.config import AppConfig
from shelob.crawler_manager import CrawlerManager

crawler_manager = CrawlerManager()

# Set up a blueprint for youtube crawler
youtube_crawler_bp = Blueprint('youtube_crawler_bp', __name__)

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

@youtube_crawler_bp.route('/youtube_crawler/channel_about', methods=["POST"])
def crawl_youtube_channel_about():
    """Crawl youtube channel about."""
    
    # get the body json
    channel_id = request.json.get("channel_id", None)
    callback_url = request.json.get("callback_url", None)

    if channel_id is None:
        raise exceptions.BadRequest("invalid channel_id")

    if callback_url is None:
        raise exceptions.BadRequest("invalid callback")

    args = {
        "channel_id": channel_id,
        "callback_url": callback_url,
    }

    crawler_id = crawler_manager.schedule_crawl_task(
        crawler_name="youtube_channel_about",
        crawler_args=args
    )
    
    # Return 200 status
    return app.response_class(
        response=json.dumps({
            "crawler_id": crawler_id,
        }),
        status=200,
        mimetype='application/json'
    )

# Run the task queue
# task_queue.run()