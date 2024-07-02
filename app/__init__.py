from flask import Flask

app = Flask(__name__)

from app import routes
from app.errors.handlers import errors
app.register_blueprint(errors)