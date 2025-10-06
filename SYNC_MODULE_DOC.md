# Módulo de Sincronización - Documentación

## Descripción General

El módulo de sincronización permite sincronizar la base de datos de Cordiax junto con todos los documentos y archivos PDF con servidores remotos utilizando diferentes protocolos. La sincronización siempre respeta el estado de encriptación de la base de datos.

## Características Principales

### Protocolos Soportados

1. **WebDAV (Polling)**
   - Sincronización mediante polling periódico
   - Compatible con servidores WebDAV estándar (Nextcloud, ownCloud, etc.)
   - Autenticación con usuario y contraseña

2. **SMB/CIFS (Polling)**
   - Sincronización con recursos compartidos de Windows
   - Compatible con servidores Samba
   - Soporte para dominios de Active Directory

3. **Flask-SocketIO (On Change & Connect)**
   - Sincronización en tiempo real
   - Conecta a servidor personalizado en `/cordiax-sync/`
   - Sincronización automática al conectar y cuando hay cambios

### Archivos Sincronizados

El módulo sincroniza:
- **Base de datos** (`cordiax.db`) - En su estado encriptado si la encriptación está habilitada
- **Documentos** (`documentos/`) - Archivos Word, Excel, PowerPoint, PDF
- **PDFs generados** (`pdfs/`) - Notas familiares y otros PDFs generados

Todos los archivos se empaquetan en un archivo ZIP antes de la sincronización para eficiencia y atomicidad.

### Seguridad

- **Encriptación Respetada**: Si la encriptación está habilitada, solo se sincroniza la versión encriptada de la base de datos
- **Credenciales Protegidas**: Las contraseñas se almacenan en el archivo de configuración local
- **Sincronización Atómica**: Los archivos se empaquetan en ZIP para garantizar consistencia

## Configuración

### WebDAV

- **URL del servidor**: URL completa del servidor WebDAV (ej: `https://cloud.example.com/remote.php/dav`)
- **Usuario**: Nombre de usuario
- **Contraseña**: Contraseña del usuario
- **Ruta remota**: Directorio donde se almacenará el archivo ZIP (ej: `/cordiax_sync/`)

### SMB/CIFS

- **Servidor**: Dirección IP o nombre del servidor SMB
- **Recurso compartido**: Nombre del recurso compartido
- **Usuario**: Nombre de usuario
- **Contraseña**: Contraseña del usuario
- **Dominio**: Dominio de Active Directory (opcional)
- **Ruta remota**: Directorio dentro del recurso compartido (ej: `/cordiax_sync/`)

### Flask-SocketIO

- **URL del servidor**: URL del servidor Flask-SocketIO (ej: `http://localhost:5000`)
- **Namespace**: Namespace del servidor (por defecto: `/cordiax-sync/`)

## Uso

### Sincronización Automática

1. Configure el protocolo deseado
2. Active "Habilitar sincronización automática"
3. Configure el intervalo de sincronización (mínimo 60 segundos)
4. Haga clic en "Guardar Configuración"
5. Haga clic en "Iniciar Sincronización"

### Sincronización Manual

1. Configure el protocolo deseado
2. Haga clic en "Guardar Configuración"
3. Haga clic en "Sincronizar Ahora"

### Prueba de Conexión

Cada protocolo tiene un botón "Probar Conexión" que permite verificar que la configuración es correcta antes de iniciar la sincronización.

## Instalación de Dependencias

Para utilizar todos los protocolos, instale las siguientes dependencias:

```bash
pip install webdavclient3 pysmb flask-socketio python-socketio[client]
```

Si alguna dependencia no está instalada, el protocolo correspondiente aparecerá como no disponible en la interfaz.

## Archivo de Configuración

La configuración se guarda en `~/_SuperCordiax/sync_config.json` con la siguiente estructura:

```json
{
    "enabled": false,
    "protocol": "webdav",
    "polling_interval": 300,
    "webdav": {
        "url": "",
        "username": "",
        "password": "",
        "remote_path": "/cordiax_sync/"
    },
    "smb": {
        "server": "",
        "share_name": "",
        "username": "",
        "password": "",
        "domain": "",
        "remote_path": "/cordiax_sync/"
    },
    "socketio": {
        "server_url": "http://localhost:5000",
        "namespace": "/cordiax-sync/"
    }
}
```

## Registro de Sincronización

El módulo incluye un registro en tiempo real que muestra:
- Eventos de conexión/desconexión
- Inicio y fin de sincronizaciones
- Errores y advertencias
- Estado de las operaciones

## Consideraciones

- El intervalo mínimo de sincronización es de 60 segundos
- La sincronización WebDAV y SMB utiliza polling, consumiendo ancho de banda periódicamente
- SocketIO mantiene una conexión abierta, ideal para redes locales
- **Los archivos se empaquetan en ZIP**: Todos los archivos (base de datos, documentos, PDFs) se comprimen en un archivo ZIP antes de enviar
- **Sincronización completa**: Se sincronizan la base de datos, documentos y PDFs generados

## Servidor Flask-SocketIO Personalizado

Para utilizar el protocolo SocketIO, necesitará un servidor Flask-SocketIO personalizado. El archivo `sync_server_example.py` incluido proporciona una implementación completa que:

- Recibe archivos ZIP con todos los datos
- Extrae el contenido en directorios con timestamp
- Mantiene un directorio `latest/` con la versión más reciente
- Proporciona una interfaz web de estado

Ejemplo de uso del servidor:

```bash
python sync_server_example.py
```

El servidor guardará los datos en `./cordiax_sync_data/` con la siguiente estructura:

```
cordiax_sync_data/
├── cordiax_20240101_120000.zip          # Archivo ZIP recibido
├── version_20240101_120000/             # Datos extraídos
│   ├── cordiax.db
│   ├── documentos/
│   └── pdfs/
└── latest/                              # Última versión
    ├── cordiax.db
    ├── documentos/
    └── pdfs/
```

Código básico del servidor (ver `sync_server_example.py` para la implementación completa):

```python
from flask import Flask
from flask_socketio import SocketIO, emit
import zipfile

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect', namespace='/cordiax-sync/')
def handle_connect():
    print('Cliente conectado')
    emit('sync_request', {})

@socketio.on('sync_data', namespace='/cordiax-sync/')
def handle_sync_data(data):
    # Recibir datos en formato hexadecimal (archivo ZIP)
    zip_bytes = bytes.fromhex(data['data'])
    
    # Guardar archivo ZIP
    with open('cordiax_sync.zip', 'wb') as f:
        f.write(zip_bytes)
    
    # Extraer contenido
    with zipfile.ZipFile('cordiax_sync.zip', 'r') as zipf:
        zipf.extractall('./sync_data/')
    
    emit('sync_complete', {'status': 'success'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
```

## Solución de Problemas

### Error de conexión WebDAV
- Verifique la URL del servidor
- Asegúrese de que las credenciales sean correctas
- Verifique que el servidor WebDAV esté accesible

### Error de conexión SMB
- Verifique que el puerto 139 esté abierto
- Asegúrese de que el recurso compartido exista
- Verifique las credenciales y el dominio

### Error de conexión SocketIO
- Verifique que el servidor esté ejecutándose
- Asegúrese de que el namespace sea correcto
- Revise los logs del servidor
