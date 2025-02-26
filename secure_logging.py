import os
import json
import logging
from datetime import datetime
from base64 import b64encode, b64decode
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecureLogger:
    def __init__(self, encryption_key=None):
        """Initialize secure logger with encryption"""
        if not encryption_key:
            # Generate a secure key if none provided
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
        """Setup encrypted file handler"""
        handler = logging.FileHandler('secure.log')
        handler.setFormatter(self.formatter)
        return handler
        
    def encrypt_log(self, log_data):
        """Encrypt log entry"""
        if isinstance(log_data, dict):
            log_data = json.dumps(log_data)
        return self.cipher_suite.encrypt(log_data.encode())
    
    def decrypt_log(self, encrypted_data):
        """Decrypt log entry"""
        try:
            decrypted = self.cipher_suite.decrypt(encrypted_data)
            return json.loads(decrypted.decode())
        except:
            return None
            
    def log_event(self, event_type, metadata, level=logging.INFO):
        """Log an encrypted event with metadata"""
        event_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': event_type,
            'metadata': metadata
        }
        
        encrypted = self.encrypt_log(event_data)
        logging.log(level, b64encode(encrypted).decode())
        
    def get_encrypted_metadata(self, data):
        """Encrypt metadata before storage"""
        return b64encode(self.encrypt_log(data)).decode()
        
    def get_decrypted_metadata(self, encrypted_data):
        """Decrypt stored metadata"""
        try:
            encrypted = b64decode(encrypted_data)
            return self.decrypt_log(encrypted)
        except:
            return None
