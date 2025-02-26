import os
import logging
from flask import Flask, render_template, request, session, jsonify, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room
from crypto_utils import CryptoManager
from room_manager import RoomManager
from secure_logging import SecureLogger

# Configure secure logging
secure_logger = SecureLogger()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.urandom(24))
socketio = SocketIO(app)

room_manager = RoomManager()
crypto_manager = CryptoManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_room', methods=['POST'])
def create_room():
    username = request.form.get('username')
    room_password = request.form.get('room_password')
    security_key = request.form.get('security_key')
    custom_room_id = request.form.get('custom_room_id')
    cipher_mode = request.form.get('cipher_mode', 'aes-gcm')  # Default to AES-GCM

    # Log room creation attempt with encrypted metadata
    metadata = {
        'username': username,
        'room_id': custom_room_id,
        'cipher_mode': cipher_mode
    }
    secure_logger.log_event('room_creation_attempt', metadata)

    logger.debug(f"Creating room with ID: {custom_room_id}, cipher mode: {cipher_mode}")

    # Validate that the room ID is unique
    if room_manager.room_exists(custom_room_id):
        secure_logger.log_event('room_creation_failed', {'reason': 'room_exists'})
        return jsonify({
            'success': False,
            'error': 'Room ID already exists. Please choose a different one.'
        }), 400

    room_manager.create_room(custom_room_id, room_password, username, security_key)

    session['username'] = username
    session['room_id'] = custom_room_id
    session['is_host'] = True
    session['security_key'] = security_key  # Store for encryption/decryption
    session['cipher_mode'] = cipher_mode  # Store chosen encryption mode

    # Log successful room creation
    secure_logger.log_event('room_created', {'room_id': custom_room_id})

    return jsonify({
        'success': True,
        'room_id': custom_room_id
    })

@app.route('/join_room', methods=['POST'])
def join_room_handler():
    room_id = request.form.get('room_id')
    username = request.form.get('username')
    room_password = request.form.get('room_password')
    security_key = request.form.get('security_key')
    cipher_mode = request.form.get('cipher_mode', 'aes-gcm')

    # Log join attempt with encrypted metadata
    metadata = {
        'username': username,
        'room_id': room_id,
        'cipher_mode': cipher_mode
    }
    secure_logger.log_event('room_join_attempt', metadata)

    logger.debug(f"Attempting to join room: {room_id}, cipher mode: {cipher_mode}")

    if room_manager.validate_room(room_id, room_password, security_key):
        session['username'] = username
        session['room_id'] = room_id
        session['is_host'] = False
        session['security_key'] = security_key
        session['cipher_mode'] = cipher_mode

        secure_logger.log_event('room_joined', {'room_id': room_id})
        return jsonify({'success': True})

    secure_logger.log_event('room_join_failed', {'reason': 'invalid_credentials'})
    return jsonify({'success': False, 'error': 'Invalid room credentials'})

@app.route('/room/<room_id>')
def room(room_id):
    if 'username' not in session or session['room_id'] != room_id:
        return redirect('/')
    return render_template('room.html', 
                         username=session['username'],
                         room_id=room_id,
                         is_host=session.get('is_host', False),
                         cipher_mode=session.get('cipher_mode', 'aes-gcm'))

@socketio.on('join')
def on_join(data):
    room = data['room']
    username = session.get('username')
    join_room(room)
    # Add user to room with their IP
    ip_address = request.remote_addr
    room_manager.add_user(room, username, ip_address)

    # Log join event with encrypted metadata
    metadata = {
        'username': username,
        'room': room,
        'ip_address': secure_logger.get_encrypted_metadata(ip_address)
    }
    secure_logger.log_event('user_joined_room', metadata)

    logger.debug(f"User {username} joined room {room}")
    emit('user_joined', {
        'username': username,
        'ip': ip_address if session.get('is_host') else None
    }, to=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    username = session.get('username')
    ip_address = request.remote_addr
    leave_room(room)
    room_manager.remove_user(room, ip_address)

    metadata = {
        'username': username,
        'room': room,
        'ip_address': secure_logger.get_encrypted_metadata(ip_address)
    }
    secure_logger.log_event('user_left_room', metadata)

    logger.debug(f"User {username} left room {room}")
    emit('user_left', {'username': username}, to=room)

@socketio.on('chat_message')
def on_chat_message(data):
    room = data['room']
    message = data['message']
    username = session.get('username')

    metadata = {
        'username': username,
        'room': room,
        'message_length': len(message)
    }
    secure_logger.log_event('chat_message_sent', metadata)

    logger.debug(f"Chat message in room {room} from {username}")
    emit('chat_message', {
        'sender': username,
        'content': message,
        'timestamp': data.get('timestamp')
    }, to=room)

@socketio.on('file_share')
def on_file_share(data):
    room = data['room']
    username = session.get('username')

    metadata = {
        'username': username,
        'room': room,
        'file_name': data['fileName'],
        'file_size': len(data['fileData'])
    }
    secure_logger.log_event('file_shared', metadata)

    logger.debug(f"File share in room {room} from {username}: {data['fileName']}")
    emit('file_share', {
        'sender': username,
        'fileName': data['fileName'],
        'fileData': data['fileData']
    }, to=room)

@socketio.on('kick_user')
def on_kick_user(data):
    if session.get('is_host'):
        room = session['room_id']
        target_username = data['username']
        user_ip = room_manager.get_user_ip(room, target_username)
        if user_ip:
            metadata = {
                'host': session.get('username'),
                'target_user': target_username,
                'room': room
            }
            secure_logger.log_event('user_kicked', metadata)

            logger.debug(f"Kicking user {target_username} from room {room}")
            room_manager.remove_user(room, user_ip)
            emit('kicked', {'username': target_username}, to=room)

@socketio.on('ban_user')
def on_ban_user(data):
    if session.get('is_host'):
        room = session['room_id']
        target_username = data['username']
        user_ip = room_manager.get_user_ip(room, target_username)
        if user_ip:
            metadata = {
                'host': session.get('username'),
                'target_user': target_username,
                'room': room
            }
            secure_logger.log_event('user_banned', metadata)

            logger.debug(f"Banning user {target_username} from room {room}")
            room_manager.ban_user(room, user_ip)
            emit('banned', {'username': target_username}, to=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=True, log_output=True)