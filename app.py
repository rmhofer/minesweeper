from flask import Flask
from database import init_db

app = Flask(__name__)
app.secret_key = 'secret_key'

# Define the bonus amount
BONUS_AMOUNT = 0.05

# Initialize database
init_db()

# Import routes
from routes import *

if __name__ == '__main__':
    app.run(debug=True)