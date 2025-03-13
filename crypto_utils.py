import os
import hmac
import hashlib
import time
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class CryptoManager:
    def __init__(self, cipher_mode='aes-gcm'):
        self.cipher_mode = cipher_mode

    def encrypt_metadata(self, key, metadata):
        """Encrypts metadata (e.g., usernames, timestamps, IPs) before transmission."""
        nonce = os.urandom(12)
        aesgcm = AESGCM(key)
        encrypted_data = aesgcm.encrypt(nonce, metadata.encode(), None)
        return b64encode(nonce + encrypted_data).decode()

    def decrypt_metadata(self, key, encrypted_metadata):
        """Decrypts metadata received from the network."""
        data = b64decode(encrypted_metadata)
        nonce, ciphertext = data[:12], data[12:]
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None).decode()

    def sign_message(self, key, message):
        """Generates an HMAC signature for message integrity."""
        return hmac.new(key, message.encode(), hashlib.sha256).hexdigest()

    def verify_message(self, key, message, signature):
        """Verifies if the message signature matches."""
        expected_signature = self.sign_message(key, message)
        return hmac.compare_digest(expected_signature, signature)

    def encrypt_message(self, key, message):
        """Encrypts a chat message with a timestamp to prevent replay attacks."""
        timestamp = str(int(time.time()))
        nonce = os.urandom(12)
        aesgcm = AESGCM(key)
        encrypted_data = aesgcm.encrypt(nonce, (message + "|" + timestamp).encode(), None)
        return b64encode(nonce + encrypted_data).decode()

    def decrypt_message(self, key, encrypted_message):
        """Decrypts a chat message and verifies timestamp to prevent replay attacks."""
        data = b64decode(encrypted_message)
        nonce, ciphertext = data[:12], data[12:]
        aesgcm = AESGCM(key)
        decrypted_message = aesgcm.decrypt(nonce, ciphertext, None).decode()
        message, timestamp = decrypted_message.rsplit("|", 1)

        if abs(int(time.time()) - int(timestamp)) > 10:  # Allow only 10 seconds delay
            raise ValueError("Replay attack detected!")

        return message
