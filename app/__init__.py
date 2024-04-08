from flask import Flask
from logging import FileHandler,WARNING

app = Flask(__name__)

from app import routes