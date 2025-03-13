#!/usr/bin/env python3
import os
import sys
import asyncio
import argparse
import curses
import socket
import json
from datetime import datetime
from crypto_utils import CryptoManager
from secure_logging import SecureLogger
from websockets import connect
from curses.textpad import Textbox, rectangle

class TerminalChat:
    def __init__(self, screen, username, room_id, is_host=False, cipher_mode='aes-gcm'):
        self.screen = screen
        self.username = username
        self.room_id = room_id
        self.is_host = is_host
        self.cipher_mode = cipher_mode
        self.crypto = CryptoManager(cipher_mode=cipher_mode)
        self.logger = SecureLogger()
        self.messages = []
        self.connected_users = set()
        
        # Initialize curses colors
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_CYAN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        
        # Setup windows
        self.setup_windows()

    def setup_windows(self):
        height, width = self.screen.getmaxyx()
        
        # Chat window (messages)
        self.chat_win = curses.newwin(height - 5, width - 20, 0, 0)
        self.chat_win.scrollok(True)
        
        # Users window
        self.users_win = curses.newwin(height - 5, 20, 0, width - 20)
        self.users_win.border()
        
        # Input window
        self.input_win = curses.newwin(3, width, height - 3, 0)
        self.input_box = Textbox(self.input_win)

    async def connect(self):
        uri = f"wss://localhost:5000/ws/{self.room_id}"  # Use secure WSS instead of WS
        self.websocket = await connect(uri)
        
        # Send join message with encryption
        encrypted_message = self.crypto.encrypt_message(
            self.crypto.current_key,
            json.dumps({
                'type': 'join',
                'username': self.username,
                'room_id': self.room_id,
                'is_host': self.is_host,
                'cipher_mode': self.cipher_mode
            })
        )

        await self.websocket.send(encrypted_message)

    def display_message(self, sender, content, is_system=False):
        timestamp = datetime.now().strftime("%H:%M")
        if is_system:
            self.chat_win.addstr(f"[{timestamp}] ", curses.color_pair(2))
            self.chat_win.addstr(content + "\n", curses.color_pair(3))
        else:
            self.chat_win.addstr(f"[{timestamp}] ", curses.color_pair(2))
            self.chat_win.addstr(f"{sender}: ", curses.color_pair(1))
            self.chat_win.addstr(content + "\n")
        self.chat_win.refresh()

    def update_users_list(self):
        self.users_win.clear()
        self.users_win.border()
        self.users_win.addstr(1, 2, "Users", curses.color_pair(1))
        for i, user in enumerate(sorted(self.connected_users)):
            self.users_win.addstr(i + 2, 2, user[:16])
        self.users_win.refresh()

    async def handle_input(self):
        while True:
            self.input_win.clear()
            self.input_win.refresh()
            message = self.input_box.edit().strip()
            
            if message.lower() == '/quit':
                return False
                
            if message:
                # Encrypt message and add integrity check
                signature = self.crypto.sign_message(self.crypto.current_key, message)
                encrypted = self.crypto.encrypt_message(
                    self.crypto.current_key,
                    json.dumps({
                        'type': 'message',
                        'content': message,
                        'sender': self.username,
                        'signature': signature
                    })
                )
                
                await self.websocket.send(encrypted)
            
            self.input_win.clear()
            self.input_win.refresh()
        
        return True

    async def handle_messages(self):
        while True:
            try:
                message = await self.websocket.recv()
                decrypted_data = json.loads(self.crypto.decrypt_message(
                    self.crypto.current_key,
                    message
                ))

                # Verify integrity of the received message
                if not self.crypto.verify_message(self.crypto.current_key, decrypted_data['content'], decrypted_data['signature']):
                    self.display_message(None, "⚠ Integrity Check Failed: Possible Tampering!", True)
                    continue
                
                if decrypted_data['type'] == 'user_joined':
                    self.connected_users.add(decrypted_data['username'])
                    self.display_message(None, f"{decrypted_data['username']} joined the room", True)
                    self.update_users_list()
                
                elif decrypted_data['type'] == 'user_left':
                    self.connected_users.remove(decrypted_data['username'])
                    self.display_message(None, f"{decrypted_data['username']} left the room", True)
                    self.update_users_list()
                
                elif decrypted_data['type'] == 'message':
                    self.display_message(decrypted_data['sender'], decrypted_data['content'])
                
            except Exception as e:
                self.display_message(None, f"Error: {str(e)}", True)

async def main(screen):
    parser = argparse.ArgumentParser(description='Secure Terminal Chat')
    parser.add_argument('--username', '-u', required=True)
    parser.add_argument('--room', '-r', required=True)
    parser.add_argument('--host', '-H', action='store_true')
    parser.add_argument('--cipher', '-c', choices=['aes-gcm', 'aes-256', 'chacha20'],
                       default='aes-gcm')
    
    args = parser.parse_args()
    
    chat = TerminalChat(
        screen=screen,
        username=args.username,
        room_id=args.room,
        is_host=args.host,
        cipher_mode=args.cipher
    )
    
    await chat.connect()
    
    # Start message handling in background
    message_task = asyncio.create_task(chat.handle_messages())
    
    # Handle input in main loop
    while await chat.handle_input():
        pass
    
    message_task.cancel()

if __name__ == "__main__":
    try:
        curses.wrapper(lambda screen: asyncio.run(main(screen)))
    except KeyboardInterrupt:
        print("\nExiting...")
    sys.exit(0)
