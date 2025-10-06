#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor de Sincronización Flask-SocketIO para Cordiax
Este es un ejemplo de servidor que puede usarse con el módulo de sincronización
"""

from flask import Flask
from flask_socketio import SocketIO, emit
from pathlib import Path
from datetime import datetime
import zipfile
import shutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cordiax-sync-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Directorio donde se almacenarán las bases de datos sincronizadas
SYNC_DIR = Path('./cordiax_sync_data')
SYNC_DIR.mkdir(exist_ok=True)


@socketio.on('connect', namespace='/cordiax-sync/')
def handle_connect():
    """Manejar conexión de cliente"""
    print(f'[{datetime.now()}] Cliente conectado')
    # Solicitar sincronización al conectar
    emit('sync_request', {})


@socketio.on('disconnect', namespace='/cordiax-sync/')
def handle_disconnect():
    """Manejar desconexión de cliente"""
    print(f'[{datetime.now()}] Cliente desconectado')


@socketio.on('sync_data', namespace='/cordiax-sync/')
def handle_sync_data(data):
    """Recibir datos de sincronización"""
    print(f'[{datetime.now()}] Datos recibidos para sincronización')
    
    try:
        # Los datos vienen en formato hexadecimal (archivo ZIP)
        zip_bytes = bytes.fromhex(data['data'])
        
        # Guardar con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_path = SYNC_DIR / f'cordiax_{timestamp}.zip'
        
        with open(zip_path, 'wb') as f:
            f.write(zip_bytes)
        
        # Crear directorio para esta versión
        version_dir = SYNC_DIR / f'version_{timestamp}'
        version_dir.mkdir(exist_ok=True)
        
        # Extraer contenido del ZIP
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(version_dir)
            file_list = zipf.namelist()
        
        # Crear un enlace a la versión más reciente
        latest_dir = SYNC_DIR / 'latest'
        if latest_dir.exists():
            shutil.rmtree(latest_dir)
        shutil.copytree(version_dir, latest_dir)
        
        print(f'[{datetime.now()}] Archivo ZIP guardado: {zip_path}')
        print(f'[{datetime.now()}] Tamaño: {len(zip_bytes)} bytes')
        print(f'[{datetime.now()}] Archivos extraídos en: {version_dir}')
        print(f'[{datetime.now()}] Archivos sincronizados: {len(file_list)}')
        for fname in file_list:
            print(f'  - {fname}')
        
        # Confirmar recepción
        emit('sync_complete', {
            'status': 'success', 
            'timestamp': timestamp,
            'files_count': len(file_list)
        })
        
    except Exception as e:
        print(f'[{datetime.now()}] Error al procesar datos: {e}')
        import traceback
        traceback.print_exc()
        emit('sync_complete', {'status': 'error', 'message': str(e)})


@app.route('/')
def index():
    """Página de inicio"""
    return """
    <html>
        <head>
            <title>Cordiax Sync Server</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    max-width: 800px; 
                    margin: 50px auto; 
                    padding: 20px; 
                }
                h1 { color: #2E86AB; }
                .status { 
                    background: #E8F4F8; 
                    padding: 15px; 
                    border-radius: 5px; 
                    margin-top: 20px;
                }
                code { 
                    background: #f4f4f4; 
                    padding: 2px 6px; 
                    border-radius: 3px; 
                }
            </style>
        </head>
        <body>
            <h1>🔄 Cordiax Sync Server</h1>
            <div class="status">
                <p><strong>Estado:</strong> ✅ Servidor activo</p>
                <p><strong>Namespace:</strong> <code>/cordiax-sync/</code></p>
                <p><strong>Directorio de datos:</strong> <code>./cordiax_sync_data/</code></p>
            </div>
            <h2>Cómo usar</h2>
            <ol>
                <li>Asegúrese de que este servidor esté ejecutándose</li>
                <li>En Cordiax, vaya al módulo de Sincronización</li>
                <li>Seleccione el protocolo "Flask-SocketIO"</li>
                <li>Configure la URL: <code>http://localhost:5000</code></li>
                <li>Configure el namespace: <code>/cordiax-sync/</code></li>
                <li>Pruebe la conexión y active la sincronización</li>
            </ol>
            <h2>Estructura de Datos</h2>
            <p>El servidor recibe archivos ZIP que contienen:</p>
            <ul>
                <li><strong>cordiax.db</strong> - Base de datos principal (encriptada si está habilitada)</li>
                <li><strong>documentos/</strong> - Documentos Word, Excel, PowerPoint, PDF</li>
                <li><strong>pdfs/</strong> - PDFs generados (notas familiares, etc.)</li>
            </ul>
            <p>Los archivos se extraen en directorios con timestamp y se mantiene un directorio <code>latest/</code> con la versión más reciente.</p>
            <h2>Logs</h2>
            <p>Los logs del servidor se muestran en la consola donde se ejecutó el servidor.</p>
        </body>
    </html>
    """


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║          Cordiax Sync Server - Flask-SocketIO               ║
╚══════════════════════════════════════════════════════════════╝

Servidor iniciando...
- URL: http://0.0.0.0:5000
- Namespace: /cordiax-sync/
- Directorio de datos: ./cordiax_sync_data/
- Formato: ZIP con base de datos + documentos + PDFs

Presione Ctrl+C para detener el servidor.
    """)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
