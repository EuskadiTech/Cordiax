# -*- coding: utf-8 -*-
"""
Módulo de base de datos para Cordiax
Maneja la conexión SQLite y las operaciones de base de datos
"""

import sqlite3
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta

USER_DATA_DIR = None
DB_PATH = None


def get_db_path():
    """Obtener la ruta de la base de datos"""
    global DB_PATH
    if DB_PATH is None:
        DB_PATH = USER_DATA_DIR / "cordiax.db"
    return DB_PATH


def get_connection():
    """Obtener conexión a la base de datos"""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Inicializar la base de datos y crear tablas"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabla de estudiantes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estudiantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            fecha_nacimiento DATE,
            direccion TEXT,
            telefono TEXT,
            email_familia TEXT,
            notas TEXT,
            activo INTEGER DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabla de asistencia
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asistencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estudiante_id INTEGER NOT NULL,
            fecha DATE NOT NULL,
            estado TEXT NOT NULL,
            hora_entrada TIME,
            hora_salida TIME,
            notas TEXT,
            FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id)
        )
    """)
    
    # Tabla de materiales
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materiales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT,
            cantidad INTEGER DEFAULT 0,
            cantidad_minima INTEGER DEFAULT 0,
            unidad TEXT,
            notas TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabla de menú de cafetería
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_cafeteria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE NOT NULL,
            tipo_comida TEXT NOT NULL,
            plato TEXT NOT NULL,
            descripcion TEXT,
            alergenos TEXT
        )
    """)
    
    # Tabla de permisos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS permisos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estudiante_id INTEGER NOT NULL,
            tipo_permiso TEXT NOT NULL,
            respuesta TEXT,
            fecha DATE,
            notas TEXT,
            FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id)
        )
    """)
    
    # Tabla de mensajes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estudiante_id INTEGER NOT NULL,
            asunto TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            leido INTEGER DEFAULT 0,
            FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    # Realizar backup automático
    backup_database()


def backup_database():
    """Realizar copia de seguridad de la base de datos (últimos 3 días)"""
    if USER_DATA_DIR is None:
        return
        
    db_path = get_db_path()
    if not db_path.exists():
        return
    
    # Crear directorio de backups si no existe
    backup_dir = USER_DATA_DIR / "db_backups"
    backup_dir.mkdir(exist_ok=True)
    
    # Crear backup con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"cordiax_backup_{timestamp}.db"
    
    try:
        shutil.copy2(str(db_path), str(backup_path))
        
        # Eliminar backups antiguos (mantener solo 3 días)
        cleanup_old_backups(backup_dir)
    except Exception as e:
        print(f"Error al hacer backup: {e}")


def cleanup_old_backups(backup_dir):
    """Limpiar backups antiguos, mantener solo los de los últimos 3 días"""
    cutoff_date = datetime.now() - timedelta(days=3)
    
    for backup_file in backup_dir.glob("cordiax_backup_*.db"):
        try:
            # Obtener fecha del archivo
            file_stat = backup_file.stat()
            file_date = datetime.fromtimestamp(file_stat.st_mtime)
            
            if file_date < cutoff_date:
                backup_file.unlink()
        except Exception as e:
            print(f"Error al limpiar backup {backup_file}: {e}")


def execute_query(query, params=None):
    """Ejecutar consulta SQL"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    
    return last_id


def fetch_all(query, params=None):
    """Obtener todos los resultados de una consulta"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    results = cursor.fetchall()
    conn.close()
    
    return results


def fetch_one(query, params=None):
    """Obtener un resultado de una consulta"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    result = cursor.fetchone()
    conn.close()
    
    return result
