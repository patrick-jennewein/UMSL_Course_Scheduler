from flask import Flask
from logging import FileHandler,WARNING

app = Flask(__name__)
print("This is a test")

from app import routes