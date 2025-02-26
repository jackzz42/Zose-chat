#!/bin/bash
# Setup script for Secure Chat application

# Create directory structure
mkdir -p static/css static/js templates

# Install Python dependencies
pip install flask flask-socketio flask-sqlalchemy cryptography websockets

# Generate a secure session key
python3 -c "import os; print(f'SESSION_SECRET={os.urandom(24).hex()}')" > .env

# Create empty log file
touch secure.log
chmod 600 secure.log

echo "Setup complete! You can now run the application using:"
echo "Web interface: python main.py"
echo "Terminal interface: python start_chat.py"
