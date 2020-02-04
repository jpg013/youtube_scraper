#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask import Flask, request
import os
from config import load_config
from crawler_manager import CrawlerManager
import json

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object("default_settings")
load_config(app)

# instantiate a new crawler manager 
crawler_manager = CrawlerManager(app.config)

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
@app.route("/health")
def handle_health():
    response = app.response_class(
        # response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )

    return response

@app.route("/crawler/<crawler_name>", methods=['POST'])
def handle_crawler(crawler_name):
    app.logger.info("/crawler post endpoint called with for crawler {}".format(crawler_name))
    crawler_id = crawler_manager.schedule_crawl_task(crawler_name, request.json)
    response = app.response_class(
        response=json.dumps({
            "crawler_id": crawler_id,
        }),
        status=200,
        mimetype='application/json'
    )

    return response

#----------------------------------------------------------------------------#
# Start Application.
#----------------------------------------------------------------------------#

if not app.debug:
    app.logger.setLevel(logging.INFO)
    # app.logger.addHandler(file_handler)

if __name__ == '__main__':
    app.run()