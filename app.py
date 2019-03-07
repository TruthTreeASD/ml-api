import os
import logging.config
from .apis.namespacestate import api
from flask import Flask, Blueprint


logging_conf_path = os.path.normpath(
    os.path.join(os.path.dirname(__file__), 'logging.conf'))
logging.config.fileConfig(logging_conf_path)
log = logging.getLogger(__name__)

app = Flask(__name__)


def initialize_app():
    app.config.from_object(os.environ['APP_SETTINGS'])
    # app.register_blueprint(api, url_prefix='api')
    api.init_app(app)


if __name__ == "__main__":
    # db.init_db()
    initialize_app()
    app.run()
