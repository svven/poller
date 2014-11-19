"""
Initialize the poller app.
"""
import config

from redis import Redis

# Set redis instance
r = Redis(config.REDIS_HOST, config.REDIS_PORT)

# from flask import Flask
# from flask.ext.sqlalchemy import SQLAlchemy

# # Define and config the app
# app = Flask(__name__)
# app.config.from_object(config)

# # Set the database
# db = SQLAlchemy(app)
# db.create_all()

def run():
	"Run the poller app."
	pass
