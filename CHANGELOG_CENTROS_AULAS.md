# Cambios: Agrupación por Centro y Aula

## Resumen

Se ha implementado un sistema de organización jerárquica para agrupar estudiantes, informes, asistencia y otros datos por **centros** (escuelas) y **aulas** (clases).

## Nuevas Funcionalidades

### 1. Gestión de Centros

- **Nueva tabla en base de datos**: `centros`
- **Nuevo módulo**: `modules/centros.py`
- **Funcionalidades**:
  - Crear, editar y eliminar centros escolares
  - Registrar información: nombre, dirección, teléfono, email, notas
  - Validación: no se puede eliminar un centro con aulas o estudiantes asociados
- **Acceso**: Botón "Centros" en el menú lateral de navegación

### 2. Gestión de Aulas

- **Nueva tabla en base de datos**: `aulas`
- **Nuevo módulo**: `modules/aulas.py`
- **Funcionalidades**:
  - Crear, editar y eliminar aulas
  - Asignar aulas a centros
  - Registrar capacidad del aula
  - Validación: no se puede eliminar un aula con estudiantes asociados
- **Acceso**: Botón "Aulas" en el menú lateral de navegación

### 3. Estudiantes con Centro y Aula

- **Modificaciones en tabla**: Añadidas columnas `centro_id` y `aula_id` a tabla `estudiantes`
- **Módulo actualizado**: `modules/students.py`
- **Funcionalidades**:
  - Asignar centro y aula a cada estudiante
  - Filtrar lista de estudiantes por centro y/o aula
  - Visualizar centro y aula en la lista de estudiantes
- **Beneficios**:
  - Organización clara de estudiantes por ubicación
  - Facilita la gestión de múltiples centros desde una sola aplicación

### 4. Asistencia Filtrada

- **Módulo actualizado**: `modules/assistance.py`
- **Funcionalidades**:
  - Filtros por centro y aula en la vista de asistencia
  - Check-in rápido respeta los filtros seleccionados
  - Visualizar centro y aula de cada estudiante en registros de asistencia
- **Beneficios**:
  - Tomar asistencia más eficiente por aula
  - Reportes de asistencia segmentados

### 5. Informes Diarios Segmentados

- **Módulo actualizado**: `modules/daily_report.py`
- **Funcionalidades**:
  - Generar informes diarios filtrados por centro y/o aula
  - Resumen de asistencia por centro/aula
  - El informe indica claramente los filtros aplicados
- **Beneficios**:
  - Informes personalizados para cada aula
  - Mejor seguimiento de métricas por ubicación

## Cambios en Base de Datos

### Nuevas Tablas

```sql
-- Tabla de centros
CREATE TABLE centros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    direccion TEXT,
    telefono TEXT,
    email TEXT,
    notas TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de aulas
CREATE TABLE aulas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    centro_id INTEGER,
    capacidad INTEGER,
    notas TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (centro_id) REFERENCES centros(id)
);
```

### Modificación de Tabla Existente

```sql
-- Columnas añadidas a estudiantes
ALTER TABLE estudiantes ADD COLUMN centro_id INTEGER;
ALTER TABLE estudiantes ADD COLUMN aula_id INTEGER;
```

## Migración Automática

La aplicación detecta automáticamente si la base de datos necesita migración y añade las columnas necesarias sin pérdida de datos.

## Compatibilidad

- ✅ Compatible con bases de datos existentes
- ✅ Migración automática al iniciar la aplicación
- ✅ Los estudiantes existentes pueden funcionar sin centro/aula asignado
- ✅ No afecta funcionalidades existentes

## Estructura de Archivos Modificados

```
Cordiax/
├── cordiax.py                    # Añadidos imports y botones de navegación
├── README.md                     # Documentación actualizada
├── modules/
│   ├── database.py               # Nuevas tablas y lógica de migración
│   ├── centros.py                # [NUEVO] Módulo de centros
│   ├── aulas.py                  # [NUEVO] Módulo de aulas
│   ├── students.py               # Añadidos campos y filtros de centro/aula
│   ├── assistance.py             # Añadidos filtros de centro/aula
│   └── daily_report.py           # Añadidos filtros de centro/aula
```

## Instrucciones de Uso

### 1. Configurar Centros

1. Abrir la aplicación Cordiax
2. Hacer clic en el botón "Centros" en el menú lateral
3. Crear uno o más centros con el botón "Nuevo Centro"
4. Rellenar la información del centro y guardar

### 2. Configurar Aulas

1. Hacer clic en el botón "Aulas" en el menú lateral
2. Crear aulas con el botón "Nueva Aula"
3. Asignar cada aula a un centro
4. Opcionalmente, definir la capacidad del aula

### 3. Asignar Estudiantes

1. En "Lista de Estudiantes", editar estudiantes existentes o crear nuevos
2. Seleccionar el centro y aula correspondiente
3. Guardar los cambios

### 4. Usar Filtros

1. En las vistas de Estudiantes, Asistencia e Informe Diario
2. Usar los selectores "Centro" y "Aula" para filtrar
3. Seleccionar "Todos" o "Todas" para ver datos sin filtrar

## Notas Técnicas

- La migración de base de datos se ejecuta automáticamente en cada inicio
- Los filtros son opcionales - se puede seguir usando la aplicación sin asignar centros/aulas
- Las relaciones entre tablas usan claves foráneas para mantener integridad referencial
- Se realizan validaciones para evitar eliminación de datos con dependencias

## Beneficios de esta Implementación

1. **Escalabilidad**: Gestionar múltiples centros desde una sola instalación
2. **Organización**: Estructura jerárquica clara (Centro → Aula → Estudiante)
3. **Reportes precisos**: Informes y estadísticas segmentadas por ubicación
4. **Flexibilidad**: Los filtros son opcionales y no interfieren con flujos existentes
5. **Migración suave**: Compatible con instalaciones existentes sin pérdida de datos
