# Módulo de Sincronización - Documentación

## Descripción General

El módulo de sincronización permite sincronizar la base de datos de Cordiax con servidores remotos utilizando diferentes protocolos. La sincronización siempre respeta el estado de encriptación de la base de datos.

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

### Seguridad

- **Encriptación Respetada**: Si la encriptación está habilitada, solo se sincroniza la versión encriptada de la base de datos
- **Credenciales Protegidas**: Las contraseñas se almacenan en el archivo de configuración local
- **Restauración Automática**: Después de sincronizar, se restaura el estado de encriptación original

## Configuración

### WebDAV

- **URL del servidor**: URL completa del servidor WebDAV (ej: `https://cloud.example.com/remote.php/dav`)
- **Usuario**: Nombre de usuario
- **Contraseña**: Contraseña del usuario
- **Ruta remota**: Directorio donde se almacenará la base de datos (ej: `/cordiax_sync/`)

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
- **IMPORTANTE**: Solo se sincroniza el archivo de base de datos, no los documentos ni PDFs adjuntos

## Servidor Flask-SocketIO Personalizado

Para utilizar el protocolo SocketIO, necesitará un servidor Flask-SocketIO personalizado. Ejemplo básico:

```python
from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect', namespace='/cordiax-sync/')
def handle_connect():
    print('Cliente conectado')
    emit('sync_request', {})

@socketio.on('sync_data', namespace='/cordiax-sync/')
def handle_sync_data(data):
    print('Datos recibidos para sincronización')
    # Guardar data['data'] en el servidor
    # El dato viene en formato hexadecimal
    db_bytes = bytes.fromhex(data['data'])
    with open('cordiax_sync.db', 'wb') as f:
        f.write(db_bytes)

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
