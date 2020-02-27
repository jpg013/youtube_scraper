from shelob.config import AppConfig
from shelob import create_app

def bootstrap_app():
    return create_app()

if __name__ == "__main__":
    app = bootstrap_app()
    # use_reloader will spawn a child process running the 
    # app to listen for changes. Set to false if you don't want 
    # this functionality.
    app.run(use_reloader=AppConfig.DEBUG, debug=AppConfig.DEBUG)