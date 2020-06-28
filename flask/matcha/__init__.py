from flask import Flask
from flask_socketio import SocketIO
from matcha.models import DB
import secrets, re, bcrypt, html
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kueghfo734yfo8g387'

logged_in_users = {}

# Set up the socket
socket = SocketIO(app, Threaded=True, cors_allowed_origins='*')

# Set up the database
db = DB()

from matcha.seed import *

if not db.get_user({'_id': ObjectId(b'bobisadmin!!')}, {'username': 1}):
	seed_users()

valid_users = []
# all_users = list(db.users())


# Import all the blueprints.
from matcha.views.profile import user
from matcha.views.auth import auth
from matcha.views.home import main
from matcha.views.chat import chatting
# Register the blurprints
app.register_blueprint(main)
app.register_blueprint(user)
app.register_blueprint(auth)
app.register_blueprint(chatting)

from matcha import sockets
