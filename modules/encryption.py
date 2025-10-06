# -*- coding: utf-8 -*-
"""
Módulo de encriptación para Cordiax
Maneja la encriptación de la base de datos
"""

import os
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64


def derive_key(password: str, salt: bytes) -> bytes:
    """Derivar clave de encriptación desde contraseña"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def encrypt_file(file_path: Path, password: str) -> bool:
    """Encriptar archivo de base de datos"""
    try:
        # Generar salt aleatorio
        salt = os.urandom(16)
        
        # Derivar clave
        key = derive_key(password, salt)
        fernet = Fernet(key)
        
        # Leer archivo original
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Encriptar datos
        encrypted_data = fernet.encrypt(data)
        
        # Guardar archivo encriptado (salt + datos encriptados)
        encrypted_path = Path(str(file_path) + '.encrypted')
        with open(encrypted_path, 'wb') as f:
            f.write(salt)
            f.write(encrypted_data)
        
        # Reemplazar archivo original con el encriptado
        encrypted_path.replace(file_path)
        
        return True
    except Exception as e:
        print(f"Error al encriptar archivo: {e}")
        return False


def decrypt_file(file_path: Path, password: str) -> bool:
    """Desencriptar archivo de base de datos"""
    try:
        # Leer archivo encriptado
        with open(file_path, 'rb') as f:
            salt = f.read(16)
            encrypted_data = f.read()
        
        # Derivar clave
        key = derive_key(password, salt)
        fernet = Fernet(key)
        
        # Desencriptar datos
        decrypted_data = fernet.decrypt(encrypted_data)
        
        # Guardar archivo desencriptado temporalmente
        decrypted_path = Path(str(file_path) + '.decrypted')
        with open(decrypted_path, 'wb') as f:
            f.write(decrypted_data)
        
        # Reemplazar archivo encriptado con el desencriptado
        decrypted_path.replace(file_path)
        
        return True
    except Exception as e:
        print(f"Error al desencriptar archivo: {e}")
        return False


def is_encrypted(file_path: Path) -> bool:
    """Verificar si un archivo está encriptado"""
    if not file_path.exists():
        return False
    
    try:
        # Intentar abrir como base de datos SQLite
        import sqlite3
        conn = sqlite3.connect(str(file_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
        conn.close()
        return False  # Si se puede abrir, no está encriptado
    except:
        return True  # Si no se puede abrir, probablemente está encriptado


def get_encryption_key_file(user_data_dir: Path) -> Path:
    """Obtener ruta del archivo que indica si la encriptación está habilitada"""
    return user_data_dir / ".encryption_enabled"


def is_encryption_enabled(user_data_dir: Path) -> bool:
    """Verificar si la encriptación está habilitada"""
    return get_encryption_key_file(user_data_dir).exists()


def enable_encryption(user_data_dir: Path):
    """Marcar la encriptación como habilitada"""
    get_encryption_key_file(user_data_dir).touch()


def disable_encryption(user_data_dir: Path):
    """Marcar la encriptación como deshabilitada"""
    key_file = get_encryption_key_file(user_data_dir)
    if key_file.exists():
        key_file.unlink()
