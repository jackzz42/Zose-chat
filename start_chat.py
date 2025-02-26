#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import pkg_resources

def check_dependencies():
    required = {'websockets'}
    if platform.system() == "Windows":
        required.add('windows-curses')

    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed

    if missing:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])

def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def main():
    try:
        check_dependencies()
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        print("Please install the required packages manually:")
        print("pip install websockets")
        if platform.system() == "Windows":
            print("pip install windows-curses")
        sys.exit(1)

    clear_screen()
    print("Welcome to Secure Terminal Chat")
    print("===============================")
    print("\nThis chat client supports:")
    print("- AES-256 CBC with ECC P-521")
    print("- ChaCha20-Poly1305")
    print("- AES-GCM (default)")
    print("\nAll communications are end-to-end encrypted.")

    username = input("\nEnter your username: ")
    room_id = input("Enter room ID: ")

    print("\nSelect encryption mode:")
    print("1. AES-GCM (default)")
    print("2. AES-256 CBC")
    print("3. ChaCha20-Poly1305")

    choice = input("\nEnter choice (1-3): ").strip()

    cipher_mode = {
        '1': 'aes-gcm',
        '2': 'aes-256',
        '3': 'chacha20'
    }.get(choice, 'aes-gcm')

    host = input("\nAre you the room host? (y/N): ").lower() == 'y'

    cmd = [
        sys.executable, 'cli_chat.py',
        '--username', username,
        '--room', room_id,
        '--cipher', cipher_mode
    ]

    if host:
        cmd.append('--host')

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nError: {str(e)}")
        if platform.system() == "Windows":
            print("\nNote: On Windows, make sure 'windows-curses' is installed:")
            print("pip install windows-curses")

if __name__ == "__main__":
    main()