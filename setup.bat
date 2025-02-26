@echo off
REM Setup script for Secure Chat application on Windows

REM Create directory structure
mkdir static\css static\js templates

REM Install Python dependencies
pip install flask flask-socketio flask-sqlalchemy cryptography websockets windows-curses

REM Generate a secure session key
python -c "import os; print(f'SESSION_SECRET={os.urandom(24).hex()}')" > .env

REM Create empty log file
type nul > secure.log

echo Setup complete! You can now run the application using:
echo Web interface: python main.py
echo Terminal interface: python start_chat.py
pause
