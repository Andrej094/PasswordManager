import base64
import json
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id


def b64e(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def b64d(data: str) -> bytes:
    return base64.b64decode(data.encode("utf-8"))


def derive_key(master_password: str, salt: bytes) -> bytes:
    kdf = Argon2id(
        salt=salt,
        length=32,
        iterations=3,
        lanes=4,
        memory_cost=64 * 1024,
    )
    return kdf.derive(master_password.encode("utf-8"))


def encrypt_vault(master_password: str, vault_data: dict) -> dict:
    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = derive_key(master_password, salt)

    aesgcm = AESGCM(key)
    plaintext = json.dumps(vault_data).encode("utf-8")
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    return {
        "version": 1,
        "salt": b64e(salt),
        "nonce": b64e(nonce),
        "ciphertext": b64e(ciphertext),
    }


def decrypt_vault(master_password: str, payload: dict) -> dict:
    salt = b64d(payload["salt"])
    nonce = b64d(payload["nonce"])
    ciphertext = b64d(payload["ciphertext"])

    key = derive_key(master_password, salt)
    aesgcm = AESGCM(key)

    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return json.loads(plaintext.decode("utf-8"))