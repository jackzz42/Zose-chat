import os
import json
import logging
from datetime import datetime
from base64 import b64encode, b64decode
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import hmac

class SecureLogger:
    def __init__(self, encryption_key=None):
        """Initialize secure logger with encryption and integrity checks."""
        if not encryption_key:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=os.urandom(16),
                iterations=100000,
            )
            encryption_key = b64encode(kdf.derive(os.urandom(32)))

        self.cipher_suite = Fernet(encryption_key)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Set up encrypted file handler
        self.log_handler = self._setup_encrypted_handler()

    def _setup_encrypted_handler(self):
        """Setup encrypted file handler."""
        handler = logging.FileHandler('secure.log')
        handler.setFormatter(self.formatter)
        return handler

    def encrypt_log(self, log_data):
        """Encrypt log entry."""
        if isinstance(log_data, dict):
            log_data = json.dumps(log_data)
        return self.cipher_suite.encrypt(log_data.encode())

    def decrypt_log(self, encrypted_data):
        """Decrypt log entry."""
        try:
            decrypted = self.cipher_suite.decrypt(encrypted_data)
            return json.loads(decrypted.decode())
        except:
            return None

    def sign_log(self, key, log_data):
        """Generate HMAC signature for log integrity."""
        return hmac.new(key, log_data.encode(), hashes.SHA256()).hexdigest()

    def verify_log(self, key, log_data, signature):
        """Verify log entry integrity."""
        expected_signature = self.sign_log(key, log_data)
        return hmac.compare_digest(expected_signature, signature)

    def log_event(self, event_type, metadata, level=logging.INFO):
        """Log an encrypted event with metadata and integrity check."""
        event_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': event_type,
            'metadata': metadata
        }

        encrypted = self.encrypt_log(event_data)
        signature = self.sign_log(b'secret_key', json.dumps(event_data))  # Replace with secure key
        logging.log(level, b64encode(encrypted).decode() + "|" + signature)

    def get_encrypted_metadata(self, data):
        """Encrypt metadata before storage."""
        return b64encode(self.encrypt_log(data)).decode()

    def get_decrypted_metadata(self, encrypted_data):
        """Decrypt stored metadata."""
        try:
            encrypted = b64decode(encrypted_data)
            return self.decrypt_log(encrypted)
        except:
            return None
