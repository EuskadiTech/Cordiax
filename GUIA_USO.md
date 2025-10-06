# Guía de Uso - Cordiax

## Inicio Rápido

1. **Primera Ejecución**
   - Ejecutar `cordiax.py` o el ejecutable `Cordiax.exe`
   - La aplicación creará automáticamente el directorio `_SuperCordiax` en su carpeta de usuario
   - Se inicializará la base de datos SQLite

2. **Navegación**
   - Usar los botones del panel lateral para cambiar entre módulos
   - Cada módulo tiene su propia interfaz con botones de acción específicos

## Módulos

### 1. Lista de Estudiantes
- **Nuevo Estudiante**: Registrar un nuevo estudiante con todos sus datos
- **Editar**: Modificar información de estudiante seleccionado
- **Eliminar**: Borrar un estudiante (con confirmación)
- Campos: Nombre, apellidos, fecha de nacimiento, dirección, teléfono, email, notas, estado activo/inactivo

### 2. Asistencia
- **Registrar Asistencia**: Marcar asistencia individual
- **Check-in Rápido**: Registrar todos los estudiantes activos como presentes
- Estados: Presente, Ausente, Tardanza, Permiso
- Incluye hora de entrada/salida y notas

### 3. Materiales Escolares
- Control de inventario con cantidad actual y mínima
- Alertas visuales cuando la cantidad está bajo mínimo
- Categorías predefinidas: Papelería, Útiles, Limpieza, Didáctico, Tecnología

### 4. Menú de Cafetería
- Planificar menús por fecha y tipo de comida
- Tipos: Desayuno, Almuerzo, Merienda, Cena
- Incluye descripción y alérgenos

### 5. Informe Diario
- Genera automáticamente un reporte con:
  - Materiales bajo mínimo (para comprar)
  - Menú del día
  - Resumen de asistencia
- **Imprimir**: Copia el informe al portapapeles

### 6. Notas Familiares
- Crear notas profesionales en formato PDF
- Incluye encabezado, fecha, asunto y contenido
- El PDF incluye espacio para firma

### 7. Permisos
- Gestionar permisos individuales por estudiante
- **Generar Plantilla PDF**: Crea una lista de todos los estudiantes con casillas SÍ/NO
- Ideal para permisos de fotografía, excursiones, etc.

### 8. Documentos
- **Importar Documento**: Añadir archivos Word, Excel, PowerPoint, PDF
- **Abrir**: Abre el documento con la aplicación predeterminada
- **Abrir Carpeta**: Acceso directo a la carpeta de documentos
- Formatos soportados: .docx, .doc, .xlsx, .xls, .pptx, .ppt, .pdf

### 9. Mensajes
- Sistema de mensajes internos por estudiante
- Filtros: Todos, No Leídos, Leídos
- Doble clic para ver mensaje completo
- Los mensajes se marcan automáticamente como leídos al verlos

### 10. Copia de Seguridad
- **Crear Backup**: Genera archivo `.cordiax.zip` con fecha y hora
- **Restaurar**: Recuperar datos desde un backup (requiere reinicio)
- **Exportar**: Guardar backup en ubicación externa (DVD, USB)
- **Importar**: Cargar backup desde ubicación externa
- El backup incluye: base de datos, documentos, PDFs

## Estructura de Archivos

```
C:\Users\[Usuario]\_SuperCordiax\     (Windows)
/home/[usuario]/_SuperCordiax/        (Linux/Mac)
├── cordiax.db              # Base de datos principal
├── documentos/             # Archivos Word, Excel, etc.
├── pdfs/                   # PDFs generados
├── backups/                # Backups manuales (.cordiax.zip)
└── db_backups/             # Backups automáticos diarios (3 días)
```

## Consejos

1. **Backups Regulares**: Crear backups antes de cambios importantes
2. **Exportar a DVD/USB**: Usar "Exportar Backup" para copias externas
3. **Materiales**: Revisar el Informe Diario para saber qué comprar
4. **Permisos**: Usar "Generar Plantilla PDF" al inicio del curso escolar
5. **Documentos**: Organizar por año escolar usando subcarpetas

## Problemas Comunes

**P: ¿Dónde están mis datos?**
R: En la carpeta `_SuperCordiax` de su directorio de usuario

**P: ¿Puedo mover la aplicación a otra computadora?**
R: Sí, crear un backup y restaurarlo en la nueva computadora

**P: ¿Se puede usar sin internet?**
R: Sí, Cordiax funciona completamente offline

**P: ¿Cómo actualizar la aplicación?**
R: Descargar nueva versión, crear backup, instalar nueva versión, restaurar backup

## Atajos de Teclado

- **Doble clic** en lista de mensajes: Ver mensaje
- Los diálogos se pueden cerrar con **Escape** (en algunos casos)

## Soporte

Para ayuda adicional, consultar:
- README.md en el repositorio
- Issues en GitHub: https://github.com/EuskadiTech/Cordiax/issues
