from flask import Flask
from database import init_db

app = Flask(__name__)
app.secret_key = 'secret_key'

# Define variables
BONUS_AMOUNT = 0.05
PROLIFIC_COMPLETION_URL = ''

# Initialize database
init_db()

# Import routes
from routes import *

if __name__ == '__main__':
    app.run(debug=True)