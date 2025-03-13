import os
import ssl
from flask import Flask, render_template, request, session, jsonify, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Secure session key
app.secret_key = os.getenv("SESSION_SECRET", os.urandom(64))

# WebSocket with SSL (WSS enabled)
socketio = SocketIO(app, ssl_context="adhoc")

# Rate Limiting to prevent brute-force attacks
limiter = Limiter(app, key_func=get_remote_address)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/join_room', methods=['POST'])
@limiter.limit("5 per minute")  # Limit to 5 attempts per minute
def join_room_handler():
    room_id = request.form.get('room_id')
    username = request.form.get('username')
    # Room authentication logic here...
    return jsonify({'success': True})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, ssl_context="adhoc")
