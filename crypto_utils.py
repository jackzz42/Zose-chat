import os
import time
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.asymmetric import x25519, ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from base64 import b64encode, b64decode

class CryptoManager:
    def __init__(self, cipher_mode='aes-gcm'):
        """Initialize with choice of primary cipher"""
        self.curve = ec.SECP521R1()  # Upgraded to stronger curve
        self.cipher_mode = cipher_mode
        self.key_rotation_interval = 3600  # 1 hour in seconds
        self.last_key_rotation = None
        self.current_key = None

    def generate_room_keys(self):
        """Generate room ID and initial keypair"""
        private_key = ec.generate_private_key(self.curve)
        public_key = private_key.public_key()
        room_id = b64encode(os.urandom(16)).decode('utf-8')
        return room_id, private_key, public_key

    def generate_x25519_keypair(self):
        """Generate X25519 keypair for ECDH"""
        private_key = x25519.X25519PrivateKey.generate()
        public_key = private_key.public_key()
        return private_key, public_key

    def derive_key_argon2(self, password, salt=None):
        """Derive key using Argon2id"""
        if not salt:
            salt = os.urandom(16)
        kdf = Argon2id(
            length=32,
            salt=salt,
            iterations=3,
            memory_cost=65536,
            parallelism=4
        )
        key = kdf.derive(password.encode())
        return key, salt

    def derive_key_hkdf(self, shared_secret, salt=None):
        """Derive key using HKDF"""
        if not salt:
            salt = os.urandom(16)
        hkdf = HKDF(
            algorithm=hashes.SHA384(),  # Upgraded to SHA-384
            length=32,
            salt=salt,
            info=b'handshake data'
        )
        key = hkdf.derive(shared_secret)
        return key, salt

    def get_cipher(self, key):
        """Get the appropriate cipher based on configuration"""
        if self.cipher_mode == 'chacha20':
            return ChaCha20Poly1305(key)
        elif self.cipher_mode == 'aes-256':
            return ('aes-256', key)  # Special case for AES-256 CBC
        else:  # Default to AES-GCM
            return AESGCM(key)

    def rotate_key(self, shared_secret):
        """Generate a new session key"""
        current_time = time.time()
        if (not self.last_key_rotation or 
            current_time - self.last_key_rotation >= self.key_rotation_interval):
            new_key, _ = self.derive_key_hkdf(shared_secret)
            self.current_key = new_key
            self.last_key_rotation = current_time
        return self.current_key

    def encrypt_message(self, key, message):
        """Encrypt a message using chosen cipher"""
        if isinstance(key, tuple) and key[0] == 'aes-256':
            # AES-256 CBC mode with PKCS7 padding
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(message.encode()) + padder.finalize()
            iv = os.urandom(16)
            cipher = Cipher(algorithms.AES256(key[1]), modes.CBC(iv))
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            return b64encode(iv + ciphertext).decode('utf-8')
        else:
            # AEAD modes (AES-GCM or ChaCha20-Poly1305)
            nonce = os.urandom(12)
            if isinstance(key, AESGCM) or isinstance(key, ChaCha20Poly1305):
                ciphertext = key.encrypt(nonce, message.encode(), None)
                return b64encode(nonce + ciphertext).decode('utf-8')
            raise ValueError("Invalid cipher configuration")

    def decrypt_message(self, key, encrypted_message):
        """Decrypt a message using chosen cipher"""
        try:
            data = b64decode(encrypted_message)
            if isinstance(key, tuple) and key[0] == 'aes-256':
                # AES-256 CBC mode
                iv = data[:16]
                ciphertext = data[16:]
                cipher = Cipher(algorithms.AES256(key[1]), modes.CBC(iv))
                decryptor = cipher.decryptor()
                padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
                unpadder = padding.PKCS7(128).unpadder()
                plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
                return plaintext.decode('utf-8')
            else:
                # AEAD modes
                nonce = data[:12]
                ciphertext = data[12:]
                plaintext = key.decrypt(nonce, ciphertext, None)
                return plaintext.decode('utf-8')
        except Exception as e:
            raise ValueError("Decryption failed") from e