from werkzeug import exceptions
import json

def add_error_handlers(app):
    def handle_bad_request(e):
        return app.response_class(
            response=json.dumps({
                "message": e.description,
            }),
            status=400,
            mimetype='application/json'
        )
    
    app.register_error_handler(400, handle_bad_request)

