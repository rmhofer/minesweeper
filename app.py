from flask import Flask
from database import init_db
import json

app = Flask(__name__)

# Load configuration from JSON file
with open('./config.json') as config_file:
    config = json.load(config_file)
    app.config.update(config)

app.secret_key = app.config['SECRET_KEY']

# Define variables from the config file
BONUS_AMOUNT = app.config['BONUS_AMOUNT']
PROLIFIC_COMPLETION_URL = app.config['PROLIFIC_COMPLETION_URL']

# Initialize database
init_db()

# Import routes
from routes import *

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])