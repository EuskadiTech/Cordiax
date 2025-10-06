# Cordiax

Sistema de gestión para aulas escolares.

## Descripción

Cordiax es una aplicación de escritorio para la gestión integral de aulas escolares. Permite gestionar estudiantes, asistencia, materiales, menús de cafetería, generar informes, notas familiares, permisos, documentos, mensajes y realizar copias de seguridad de todos los datos.

## Características

1. **Lista de Estudiantes (CRUD)** - Gestión completa de estudiantes con sus datos personales
2. **Asistencia de Estudiantes** - Registro diario de asistencia con check-in rápido y notas
3. **Materiales Escolares** - Control de inventario con alertas de niveles mínimos
4. **Menú de Cafetería** - Planificación de menús diarios con información de alérgenos
5. **Informe Diario** - Resumen automático de materiales bajo mínimo, menú del día y asistencia
6. **Notas Familiares** - Generación de PDFs profesionales con encabezado
7. **Permisos** - Gestión de permisos con plantillas imprimibles en PDF
8. **Documentos** - Gestión de archivos Word, Excel, PowerPoint y PDF
9. **Mensajes de Estudiantes** - Sistema de mensajes internos para referencia
10. **Copia de Seguridad** - Backup y restauración completa en formato .cordiax.zip

## Requisitos

- Python 3.8 o superior
- Tkinter (incluido en la mayoría de instalaciones de Python)
- Dependencias listadas en `requirements.txt`

## Instalación

### Opción 1: Ejecutar desde código fuente

```bash
# Clonar el repositorio
git clone https://github.com/EuskadiTech/Cordiax.git
cd Cordiax

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python cordiax.py
```

### Opción 2: Ejecutable de Windows

Descarga el ejecutable pre-compilado desde la sección de [Releases](https://github.com/EuskadiTech/Cordiax/releases).

## Compilación con PyInstaller

Para crear un ejecutable independiente:

```bash
# Instalar PyInstaller
pip install pyinstaller

# Compilar (genera un archivo .exe en la carpeta dist/)
pyinstaller cordiax.spec
```

El ejecutable generado es un archivo único (onefile) sin consola, ideal para grabar en DVD y distribuir.

## Estructura de Datos

La aplicación almacena todos los datos en el directorio del usuario:
- **Windows**: `C:\Users\[usuario]\_SuperCordiax\`
- **Linux/Mac**: `/home/[usuario]/_SuperCordiax/`

### Contenido del directorio de datos:

```
_SuperCordiax/
├── cordiax.db           # Base de datos SQLite principal
├── documentos/          # Archivos Word, Excel, PowerPoint, PDF
├── pdfs/                # PDFs generados (notas familiares, etc.)
├── backups/             # Copias de seguridad .cordiax.zip
└── db_backups/          # Backups automáticos de la BD (últimos 3 días)
```

## Base de Datos

Cordiax utiliza SQLite para almacenar los datos estructurados y archivos planos para documentos. La aplicación realiza automáticamente:

- Backup diario de la base de datos
- Mantiene copias de los últimos 3 días
- Permite crear backups manuales completos (.cordiax.zip)

## Backups

### Crear Backup

1. Ir al módulo "Copia de Seguridad"
2. Hacer clic en "Crear Backup"
3. Se genera automáticamente un archivo `.cordiax.zip` con fecha y hora

### Restaurar Backup

1. Ir al módulo "Copia de Seguridad"
2. Seleccionar el backup deseado
3. Hacer clic en "Restaurar"
4. Confirmar la restauración
5. Reiniciar la aplicación

### Exportar/Importar Backups

- **Exportar**: Guarda una copia del backup en cualquier ubicación (útil para DVD, USB, etc.)
- **Importar**: Carga un backup desde una ubicación externa

## Desarrollo

### Estructura del proyecto

```
Cordiax/
├── cordiax.py              # Aplicación principal
├── cordiax.spec            # Configuración de PyInstaller
├── requirements.txt        # Dependencias de Python
├── modules/
│   ├── __init__.py
│   ├── database.py         # Gestión de base de datos
│   ├── students.py         # Módulo de estudiantes
│   ├── assistance.py       # Módulo de asistencia
│   ├── materials.py        # Módulo de materiales
│   ├── cafeteria.py        # Módulo de cafetería
│   ├── daily_report.py     # Módulo de informe diario
│   ├── family_notes.py     # Módulo de notas familiares
│   ├── permissions.py      # Módulo de permisos
│   ├── documents.py        # Módulo de documentos
│   ├── messages.py         # Módulo de mensajes
│   └── backup.py           # Módulo de backup
└── .github/
    └── workflows/
        └── build.yml       # GitHub Actions para releases
```

## GitHub Actions

El proyecto incluye un workflow de GitHub Actions que:

1. Se activa automáticamente al crear un Release en GitHub
2. Compila la aplicación con PyInstaller en Windows
3. Genera el ejecutable `Cordiax-Windows.exe`
4. Lo adjunta automáticamente al Release

### Crear un Release:

1. Ir a la pestaña "Releases" en GitHub
2. Hacer clic en "Create a new release"
3. Crear un tag (ej: `v1.0.0`)
4. Publicar el release
5. El workflow compilará y adjuntará el ejecutable automáticamente

## Licencia

MIT License - Ver el archivo [LICENSE](LICENSE) para más detalles.

## Soporte

Para reportar problemas o solicitar nuevas características, por favor abre un [Issue](https://github.com/EuskadiTech/Cordiax/issues) en GitHub.

## Capturas de Pantalla

(Las capturas de pantalla se agregarán en futuras actualizaciones)

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu característica (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## Autor

EuskadiTech

## Agradecimientos

- ReportLab para generación de PDFs
- OpenPyXL para manejo de Excel
- python-docx para manejo de Word
- PyInstaller para la compilación