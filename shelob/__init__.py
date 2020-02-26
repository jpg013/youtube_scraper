__version__         = "VERSION_NUMBER"
__build_number__    = "BUILD_NUMBER"
__component__       = "shelob"
__namespace__       = "acquisition"

def create_app():
    from flask import Flask, g

    """Initialize the core flask app."""
    app = Flask(__name__, instance_relative_config=False)

    with app.app_context():
        # configure logger
        from shelob.logger import log_provider
        log_provider.config_logger(app.logger)
        
        # config app
        from shelob.config import AppConfig
        app.config.from_object(AppConfig)
        
        # connect kafka
        from shelob.kafka import kafka_producer
        kafka_producer.connect()

        # Include our Routes
        import shelob.routes as routes
        from shelob.errors import add_error_handlers

        # Register Blueprints
        app.register_blueprint(routes.youtube_crawler_bp)
        app.register_blueprint(routes.health_bp)
        app.register_blueprint(routes.config_bp)

        # add error handlers to application
        add_error_handlers(app)

        app.logger.info("application created")
        return app