# Flujo de Sincronización - Cordiax

## Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                    Aplicación Cordiax                       │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Módulo de Sincronización                   │  │
│  │                                                      │  │
│  │  ┌────────────────────────────────────────────┐     │  │
│  │  │  Verificación de Encriptación              │     │  │
│  │  │  - ¿Encriptación habilitada?               │     │  │
│  │  │  - ¿Base de datos encriptada?              │     │  │
│  │  │  - Encriptar si es necesario               │     │  │
│  │  └────────────────────────────────────────────┘     │  │
│  │                      ↓                               │  │
│  │  ┌────────────────────────────────────────────┐     │  │
│  │  │  Selección de Protocolo                    │     │  │
│  │  │  - WebDAV                                  │     │  │
│  │  │  - SMB/CIFS                                │     │  │
│  │  │  - Flask-SocketIO                          │     │  │
│  │  └────────────────────────────────────────────┘     │  │
│  │                      ↓                               │  │
│  │  ┌────────────────────────────────────────────┐     │  │
│  │  │  Sincronización                            │     │  │
│  │  │  - Subir base de datos                     │     │  │
│  │  │  - Mantener estado de encriptación         │     │  │
│  │  └────────────────────────────────────────────┘     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   Servidor    │  │   Servidor    │  │   Servidor    │
│   WebDAV      │  │   SMB/CIFS    │  │  SocketIO     │
│               │  │               │  │               │
│  (Nextcloud,  │  │  (Windows,    │  │  (Personaliz) │
│   ownCloud,   │  │   Samba)      │  │               │
│   etc.)       │  │               │  │               │
└───────────────┘  └───────────────┘  └───────────────┘
```

## Flujo de Datos: Sincronización WebDAV/SMB (Polling)

```
┌──────────────────────────────────────────────────────────────┐
│ 1. Usuario Inicia Sincronización                            │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 2. Verificar Estado de Encriptación                         │
│    - Si está habilitada Y base de datos NO está encriptada  │
│    - Encriptar base de datos con contraseña guardada        │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 3. Conectar al Servidor                                      │
│    WebDAV: Autenticación HTTP                               │
│    SMB: Autenticación SMB/CIFS                              │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 4. Subir Base de Datos                                       │
│    - Leer archivo local (encriptado o no)                   │
│    - Transferir a servidor remoto                           │
│    - Guardar en ruta configurada                            │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 5. Restaurar Estado Local                                    │
│    - Si la base de datos fue encriptada temporalmente       │
│    - Restaurar estado de encriptación                       │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 6. Esperar Intervalo (Polling)                               │
│    - Esperar X segundos (configurado, mínimo 60)            │
│    - Repetir desde paso 2                                   │
└──────────────────────────────────────────────────────────────┘
```

## Flujo de Datos: Sincronización SocketIO (Tiempo Real)

```
┌──────────────────────────────────────────────────────────────┐
│ 1. Usuario Inicia Sincronización                            │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 2. Conectar al Servidor SocketIO                             │
│    - Establecer conexión WebSocket                          │
│    - Suscribirse a namespace /cordiax-sync/                 │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 3. Evento: connect                                           │
│    - Servidor envía solicitud de sincronización             │
│    - Cliente ejecuta sincronización automáticamente         │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 4. Verificar y Preparar Base de Datos                        │
│    - Verificar estado de encriptación                       │
│    - Encriptar si es necesario                              │
│    - Leer archivo completo                                  │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 5. Enviar Datos                                              │
│    - Convertir bytes a formato hexadecimal                  │
│    - Emitir evento 'sync_data' con los datos                │
│    - Servidor recibe y guarda base de datos                 │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 6. Mantener Conexión                                         │
│    - Escuchar eventos del servidor                          │
│    - Responder a 'sync_request' automáticamente             │
│    - Mantener hasta que el usuario detenga                  │
└──────────────────────────────────────────────────────────────┘
```

## Tabla de Comparación de Protocolos

| Característica          | WebDAV           | SMB/CIFS         | Flask-SocketIO   |
|------------------------|------------------|------------------|------------------|
| **Tipo**               | Polling          | Polling          | Tiempo Real      |
| **Conexión**           | HTTP/HTTPS       | Red local/VPN    | WebSocket        |
| **Autenticación**      | Usuario/Password | Usuario/Password | Personalizable   |
| **Latencia**           | Media-Alta       | Baja-Media       | Muy Baja         |
| **Ancho de banda**     | Moderado         | Alto             | Bajo             |
| **Mejor para**         | Internet         | Red local        | Red local        |
| **Servidores**         | Nextcloud, etc.  | Windows, Samba   | Personalizado    |
| **Configuración**      | Media            | Media-Alta       | Alta             |

## Seguridad

### Encriptación en Tránsito

- **WebDAV**: Se recomienda usar HTTPS
- **SMB**: Encriptación nativa del protocolo SMB 3.0+
- **SocketIO**: Se puede usar sobre HTTPS (WSS)

### Encriptación en Reposo

El módulo de sincronización **siempre** respeta el estado de encriptación:

1. **Si la encriptación está HABILITADA**:
   - La base de datos se sincroniza en su estado ENCRIPTADO
   - Servidor remoto almacena datos encriptados (no puede leerlos)
   - Solo quien tenga la contraseña puede desencriptar

2. **Si la encriptación está DESHABILITADA**:
   - La base de datos se sincroniza sin encriptar
   - Servidor remoto puede acceder a los datos
   - Útil para backups accesibles

### Recomendaciones de Seguridad

1. ✅ **SIEMPRE** habilitar encriptación si los datos son sensibles
2. ✅ Usar HTTPS/WSS para WebDAV y SocketIO
3. ✅ Usar contraseñas fuertes para todos los servicios
4. ✅ Limitar acceso al servidor de sincronización
5. ✅ Realizar backups regulares del servidor remoto
6. ⚠️  No compartir las credenciales de sincronización
7. ⚠️  Verificar que el servidor remoto esté actualizado

## Casos de Uso

### Caso 1: Organización con Nextcloud

- **Protocolo**: WebDAV
- **Servidor**: Nextcloud en servidor propio
- **Configuración**: HTTPS, autenticación de aplicación
- **Ventajas**: Acceso desde cualquier lugar, interfaz web

### Caso 2: Red Local con Windows Server

- **Protocolo**: SMB/CIFS
- **Servidor**: Windows Server con recurso compartido
- **Configuración**: Autenticación de dominio
- **Ventajas**: Velocidad, integración con AD

### Caso 3: Múltiples Aulas en Tiempo Real

- **Protocolo**: Flask-SocketIO
- **Servidor**: Servidor Python personalizado
- **Configuración**: Red local, sincronización instantánea
- **Ventajas**: Tiempo real, control total del servidor

## Troubleshooting

### Error: "WebDAV no está disponible"
**Solución**: Instalar dependencia
```bash
pip install webdavclient3
```

### Error: "SMB no está disponible"
**Solución**: Instalar dependencia
```bash
pip install pysmb
```

### Error: "SocketIO no está disponible"
**Solución**: Instalar dependencias
```bash
pip install flask-socketio python-socketio[client]
```

### Error: "No se pudo conectar al servidor"
**Solución**: 
1. Verificar que el servidor esté accesible
2. Verificar credenciales
3. Verificar firewall/puertos
4. Usar el botón "Probar Conexión"

### Sincronización muy lenta
**Solución**:
1. Si usa WebDAV/SMB: Aumentar intervalo de polling
2. Considerar cambiar a SocketIO si es red local
3. Verificar velocidad de red
4. Verificar tamaño de base de datos

### Base de datos no se desencripta después de sincronizar
**Solución**:
1. Esto es normal - el módulo restaura el estado
2. Verificar que DB_PASSWORD esté configurado
3. Revisar logs de sincronización
