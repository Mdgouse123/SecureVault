"""
RSA Digital Signature Module
Generates RSA-2048 key pairs, signs files, and verifies signatures.
"""

import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature


def generate_key_pair(username: str, keys_dir: str) -> dict:
    """Generate RSA-2048 key pair and save to keys directory."""
    try:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Serialize public key
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        priv_path = os.path.join(keys_dir, f"{username}_private.pem")
        pub_path  = os.path.join(keys_dir, f"{username}_public.pem")

        with open(priv_path, 'wb') as f:
            f.write(private_pem)
        with open(pub_path, 'wb') as f:
            f.write(public_pem)

        return {
            'success': True,
            'private_key_path': priv_path,
            'public_key_path': pub_path,
            'public_key_pem': public_pem.decode(),
            'message': 'RSA-2048 key pair generated successfully.'
        }

    except Exception as e:
        return {'success': False, 'message': str(e)}


def sign_file(file_path: str, private_key_path: str) -> dict:
    """Sign a file using RSA private key with PSS padding and SHA-256."""
    try:
        with open(private_key_path, 'rb') as f:
            private_key = serialization.load_pem_private_key(
                f.read(), password=None, backend=default_backend()
            )

        with open(file_path, 'rb') as f:
            file_data = f.read()

        signature = private_key.sign(
            file_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Save signature next to file
        sig_path = file_path + '.sig'
        with open(sig_path, 'wb') as f:
            f.write(signature)

        return {
            'success': True,
            'signature_path': sig_path,
            'signature_hex': signature.hex()[:64] + '...',
            'message': 'File signed successfully with RSA-2048.'
        }

    except Exception as e:
        return {'success': False, 'message': str(e)}


def verify_signature(file_path: str, signature_path: str, public_key_path: str) -> dict:
    """Verify a file's RSA digital signature."""
    try:
        with open(public_key_path, 'rb') as f:
            public_key = serialization.load_pem_public_key(
                f.read(), backend=default_backend()
            )

        with open(file_path, 'rb') as f:
            file_data = f.read()

        with open(signature_path, 'rb') as f:
            signature = f.read()

        public_key.verify(
            signature,
            file_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return {
            'success': True,
            'valid': True,
            'message': 'Signature is VALID. File integrity verified.'
        }

    except InvalidSignature:
        return {
            'success': True,
            'valid': False,
            'message': 'Signature is INVALID. File may have been tampered with.'
        }
    except Exception as e:
        return {'success': False, 'message': str(e)}
