"""
Initialize poller app.
"""

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://svven@localhost/svven'
db = SQLAlchemy(app)
