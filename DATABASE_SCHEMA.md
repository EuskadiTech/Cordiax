# Esquema de Base de Datos - Cordiax

## Diagrama de Relaciones

```
┌─────────────────┐
│     CENTROS     │
├─────────────────┤
│ id (PK)         │
│ nombre          │
│ direccion       │
│ telefono        │
│ email           │
│ notas           │
│ fecha_creacion  │
└─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│      AULAS      │
├─────────────────┤
│ id (PK)         │
│ nombre          │
│ centro_id (FK)  │──────┐
│ capacidad       │      │
│ notas           │      │
│ fecha_creacion  │      │
└─────────────────┘      │
         │               │
         │ 1:N           │
         ▼               │
┌─────────────────┐      │
│  ESTUDIANTES    │      │
├─────────────────┤      │
│ id (PK)         │      │
│ nombre          │      │
│ apellidos       │      │
│ fecha_nac       │      │
│ direccion       │      │
│ telefono        │      │
│ email_familia   │      │
│ notas           │      │
│ activo          │      │
│ centro_id (FK)  │──────┘
│ aula_id (FK)    │──────┐
│ fecha_creacion  │      │
└─────────────────┘      │
         │               │
         │ 1:N           │
         ▼               │
┌─────────────────┐      │
│   ASISTENCIA    │      │
├─────────────────┤      │
│ id (PK)         │      │
│ estudiante_id   │──────┘
│ fecha           │
│ estado          │
│ hora_entrada    │
│ hora_salida     │
│ notas           │
└─────────────────┘

┌─────────────────┐
│   MATERIALES    │
├─────────────────┤
│ id (PK)         │
│ nombre          │
│ categoria       │
│ cantidad        │
│ cantidad_minima │
│ unidad          │
│ notas           │
└─────────────────┘

┌─────────────────┐
│ MENU_CAFETERIA  │
├─────────────────┤
│ id (PK)         │
│ fecha           │
│ tipo_comida     │
│ plato           │
│ descripcion     │
│ alergenos       │
└─────────────────┘

┌─────────────────┐
│    PERMISOS     │
├─────────────────┤
│ id (PK)         │
│ estudiante_id   │────────┐
│ tipo_permiso    │        │
│ respuesta       │        │
│ fecha           │        │
│ notas           │        │
└─────────────────┘        │
                           │
┌─────────────────┐        │
│    MENSAJES     │        │
├─────────────────┤        │
│ id (PK)         │        │
│ estudiante_id   │────────┘
│ asunto          │
│ mensaje         │
│ fecha           │
│ leido           │
└─────────────────┘
```

## Descripción de Tablas

### CENTROS (Nueva)
**Propósito**: Almacenar información de centros escolares/escuelas.

**Campos**:
- `id`: Identificador único (Primary Key)
- `nombre`: Nombre del centro (obligatorio)
- `direccion`: Dirección física del centro
- `telefono`: Número de teléfono de contacto
- `email`: Correo electrónico de contacto
- `notas`: Notas adicionales
- `fecha_creacion`: Timestamp de creación automática

**Relaciones**:
- 1:N con AULAS (un centro puede tener muchas aulas)
- 1:N con ESTUDIANTES (un centro puede tener muchos estudiantes)

### AULAS (Nueva)
**Propósito**: Almacenar información de aulas/salones de clase.

**Campos**:
- `id`: Identificador único (Primary Key)
- `nombre`: Nombre del aula (obligatorio)
- `centro_id`: Referencia al centro (Foreign Key, opcional)
- `capacidad`: Capacidad máxima de estudiantes
- `notas`: Notas adicionales
- `fecha_creacion`: Timestamp de creación automática

**Relaciones**:
- N:1 con CENTROS (muchas aulas pertenecen a un centro)
- 1:N con ESTUDIANTES (un aula puede tener muchos estudiantes)

### ESTUDIANTES (Modificada)
**Propósito**: Almacenar información de estudiantes.

**Campos Nuevos**:
- `centro_id`: Referencia al centro (Foreign Key, opcional)
- `aula_id`: Referencia al aula (Foreign Key, opcional)

**Campos Existentes**:
- `id`: Identificador único (Primary Key)
- `nombre`: Nombre del estudiante (obligatorio)
- `apellidos`: Apellidos del estudiante (obligatorio)
- `fecha_nacimiento`: Fecha de nacimiento
- `direccion`: Dirección del estudiante
- `telefono`: Teléfono de contacto
- `email_familia`: Email de la familia
- `notas`: Notas adicionales
- `activo`: Estado del estudiante (1=activo, 0=inactivo)
- `fecha_creacion`: Timestamp de creación automática

**Relaciones**:
- N:1 con CENTROS (muchos estudiantes pertenecen a un centro)
- N:1 con AULAS (muchos estudiantes pertenecen a un aula)
- 1:N con ASISTENCIA (un estudiante tiene muchos registros de asistencia)
- 1:N con PERMISOS (un estudiante puede tener muchos permisos)
- 1:N con MENSAJES (un estudiante puede tener muchos mensajes)

### ASISTENCIA (Sin cambios)
**Propósito**: Registrar asistencia diaria de estudiantes.

**Campos**:
- `id`: Identificador único (Primary Key)
- `estudiante_id`: Referencia al estudiante (Foreign Key)
- `fecha`: Fecha del registro
- `estado`: Estado de asistencia (Presente, Ausente, Tardanza, etc.)
- `hora_entrada`: Hora de entrada
- `hora_salida`: Hora de salida
- `notas`: Notas del registro

**Relaciones**:
- N:1 con ESTUDIANTES (muchos registros pertenecen a un estudiante)

## Integridad Referencial

### Restricciones de Eliminación

1. **No se puede eliminar un CENTRO si**:
   - Tiene AULAS asociadas
   - Tiene ESTUDIANTES asociados

2. **No se puede eliminar un AULA si**:
   - Tiene ESTUDIANTES asociados

3. **Al eliminar un ESTUDIANTE**:
   - Se eliminan automáticamente sus registros de ASISTENCIA
   - Se eliminan automáticamente sus PERMISOS
   - Se eliminan automáticamente sus MENSAJES

## Consultas Principales

### Listar estudiantes con centro y aula
```sql
SELECT e.*, c.nombre as centro_nombre, a.nombre as aula_nombre
FROM estudiantes e
LEFT JOIN centros c ON e.centro_id = c.id
LEFT JOIN aulas a ON e.aula_id = a.id
WHERE e.activo = 1
ORDER BY e.apellidos, e.nombre
```

### Listar asistencia con información del estudiante y ubicación
```sql
SELECT 
    a.id, a.fecha, a.estado, a.hora_entrada, a.hora_salida,
    e.nombre, e.apellidos,
    c.nombre as centro_nombre,
    au.nombre as aula_nombre
FROM asistencia a
JOIN estudiantes e ON a.estudiante_id = e.id
LEFT JOIN centros c ON e.centro_id = c.id
LEFT JOIN aulas au ON e.aula_id = au.id
WHERE a.fecha = '2024-10-06'
ORDER BY e.apellidos, e.nombre
```

### Contar estudiantes por centro
```sql
SELECT c.nombre, COUNT(e.id) as total_estudiantes
FROM centros c
LEFT JOIN estudiantes e ON c.id = e.centro_id
WHERE e.activo = 1
GROUP BY c.id, c.nombre
ORDER BY c.nombre
```

### Contar estudiantes por aula
```sql
SELECT 
    a.nombre as aula,
    c.nombre as centro,
    COUNT(e.id) as total_estudiantes,
    a.capacidad
FROM aulas a
LEFT JOIN centros c ON a.centro_id = c.id
LEFT JOIN estudiantes e ON a.id = e.aula_id
WHERE e.activo = 1 OR e.id IS NULL
GROUP BY a.id, a.nombre, c.nombre, a.capacidad
ORDER BY c.nombre, a.nombre
```

## Índices Recomendados

Para mejorar el rendimiento, se recomienda crear los siguientes índices:

```sql
-- Índices en ESTUDIANTES
CREATE INDEX idx_estudiantes_centro ON estudiantes(centro_id);
CREATE INDEX idx_estudiantes_aula ON estudiantes(aula_id);
CREATE INDEX idx_estudiantes_activo ON estudiantes(activo);

-- Índices en AULAS
CREATE INDEX idx_aulas_centro ON aulas(centro_id);

-- Índices en ASISTENCIA
CREATE INDEX idx_asistencia_fecha ON asistencia(fecha);
CREATE INDEX idx_asistencia_estudiante ON asistencia(estudiante_id);
```

## Notas de Migración

- Las columnas `centro_id` y `aula_id` en ESTUDIANTES aceptan valores NULL
- Esto permite que estudiantes existentes funcionen sin necesidad de asignarles centro/aula
- Los filtros en la aplicación son opcionales y manejan valores NULL correctamente
- Se utiliza LEFT JOIN en las consultas para incluir estudiantes sin centro/aula asignado
