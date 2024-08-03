from flask import Flask

app = Flask(__name__, static_url_path='', static_folder='app/static', template_folder='app/templates')

from app import routes
from app.errors.handlers import errors
app.register_blueprint(errors)