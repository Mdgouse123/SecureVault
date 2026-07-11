"""
AES-256 File Encryption / Decryption Module
Uses AES-256-CBC with PBKDF2 key derivation from password.
"""

import os
import struct
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.backends import default_backend

SALT_SIZE    = 16   # bytes
IV_SIZE      = 16   # bytes (AES block size)
KEY_SIZE     = 32   # bytes → AES-256
ITERATIONS   = 200_000


def _derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit AES key from a password using PBKDF2-HMAC-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(password.encode())


def encrypt_file(input_path: str, output_path: str, password: str) -> dict:
    """
    Encrypt a file with AES-256-CBC.
    Output file layout: [salt(16)] [iv(16)] [ciphertext]
    Returns a dict with status and metadata.
    """
    try:
        salt = os.urandom(SALT_SIZE)
        iv   = os.urandom(IV_SIZE)
        key  = _derive_key(password, salt)

        with open(input_path, 'rb') as f:
            plaintext = f.read()

        # PKCS7 padding
        padder = padding.PKCS7(128).padder()
        padded  = padder.update(plaintext) + padder.finalize()

        cipher     = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor  = cipher.encryptor()
        ciphertext = encryptor.update(padded) + encryptor.finalize()

        with open(output_path, 'wb') as f:
            f.write(salt + iv + ciphertext)

        return {
            'success': True,
            'original_size': len(plaintext),
            'encrypted_size': len(ciphertext),
            'message': 'File encrypted successfully with AES-256-CBC.'
        }

    except Exception as e:
        return {'success': False, 'message': str(e)}


def decrypt_file(input_path: str, output_path: str, password: str) -> dict:
    """
    Decrypt a file encrypted with encrypt_file().
    Returns a dict with status and metadata.
    """
    try:
        with open(input_path, 'rb') as f:
            data = f.read()

        if len(data) < SALT_SIZE + IV_SIZE:
            return {'success': False, 'message': 'File too small — not a valid encrypted file.'}

        salt       = data[:SALT_SIZE]
        iv         = data[SALT_SIZE:SALT_SIZE + IV_SIZE]
        ciphertext = data[SALT_SIZE + IV_SIZE:]

        key = _derive_key(password, salt)

        cipher    = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded    = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove padding
        unpadder  = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded) + unpadder.finalize()

        with open(output_path, 'wb') as f:
            f.write(plaintext)

        return {
            'success': True,
            'decrypted_size': len(plaintext),
            'message': 'File decrypted successfully.'
        }

    except Exception as e:
        return {'success': False, 'message': 'Decryption failed — wrong password or corrupted file.'}
