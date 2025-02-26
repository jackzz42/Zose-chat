# Secure P2P Chat - Terminal Client

A secure terminal-based chat client with end-to-end encryption using AES-256, ECC P-521, and ChaCha20-Poly1305.

## Features

- End-to-end encryption using multiple cipher options:
  - AES-256 CBC with ECC P-521
  - ChaCha20-Poly1305
  - AES-GCM
- Terminal-based UI with curses
- Cross-platform support (Linux, macOS, Windows)
- Secure room creation and joining
- File transfer capabilities
- Encrypted logging

## Installation

### Linux/Kali Linux
```bash
pip install websockets
```

### macOS
```bash
pip install websockets
```

### Windows
```bash
pip install websockets windows-curses
```

## Usage

1. Start the chat client:
```bash
python start_chat.py
```

2. Follow the prompts to:
   - Enter your username
   - Create or join a room
   - Select encryption mode
   - Start chatting!

3. Commands while chatting:
   - Type message and press Enter to send
   - `/quit` to exit
   - `/help` for more commands

## Security Features

- ECC P-521 for key exchange
- Perfect Forward Secrecy with key rotation
- Multiple cipher options:
  - AES-256 CBC
  - ChaCha20-Poly1305
  - AES-GCM
- Encrypted logging and metadata
- Secure file transfer

## Notes

- For Windows users: If you see curses-related errors, ensure windows-curses is installed
- For Linux/Mac users: Uses native curses implementation
- Terminal must support Unicode and colors for best experience
