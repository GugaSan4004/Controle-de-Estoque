import sys
import psutil
import modules
import datetime

from flask_socketio import SocketIO
from flask import Flask, request, jsonify, render_template
            
db = modules.DBCore()

app = Flask(__name__)

Socket = SocketIO(
    app,
    async_mode="eventlet",
    ping_interval=25,
    ping_timeout=60,
    cors_allowed_origins="*"
)

with app.app_context():
    print("\n> Server initiated successfully!")
    
if __name__ == "__main__":
    Socket.run(
        app,
        host="127.0.0.1",
        port=5000,
        debug=False
    )