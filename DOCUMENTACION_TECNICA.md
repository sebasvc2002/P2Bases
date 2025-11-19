# 📚 Documentación Técnica - PharmaFlow Solutions

## 🎯 Resumen Ejecutivo

PharmaFlow Solutions es un sistema completo de gestión farmacéutica que implementa todos los requisitos del proyecto de Bases de Datos, utilizando **PostgreSQL** para datos estructurados críticos y **MongoDB** para datos flexibles y semiestructurados.

## 📋 Cumplimiento de Requisitos del Proyecto

### ✅ Control de la Concurrencia (4.1)

**Implementación**: `models_inventario.py` - Clase `LoteMedicamento` y `Transaccion`

#### Control de Concurrencia Optimista
```python
def actualizar_cantidad_optimista(lote_id, nueva_cantidad, version_esperada):
    cursor.execute(
        """UPDATE lotes_medicamentos 
           SET cantidad_actual = %s, version = version + 1
           WHERE id = %s AND version = %s""",
        (nueva_cantidad, lote_id, version_esperada)
    )
    return cursor.rowcount > 0
```

- Utiliza un campo `version` en la tabla `lotes_medicamentos`
- Verifica que la versión no haya cambiado antes de actualizar
- Si hay conflicto, retorna False y el usuario debe reintentar
- **Ventaja**: Mayor rendimiento en escenarios con baja contención

#### Control de Concurrencia Pesimista
```python
def actualizar_cantidad_pesimista(lote_id, nueva_cantidad):
    cursor.execute(
        """SELECT cantidad_actual, version FROM lotes_medicamentos 
           WHERE id = %s FOR UPDATE""",
        (lote_id,)
    )
```

- Utiliza `SELECT FOR UPDATE` para bloquear la fila
- Previene que otros usuarios lean o modifiquen el registro
- Garantiza consistencia absoluta
- **Ventaja**: Previene conflictos en escenarios de alta contención

**Casos de Uso**:
- Un farmacéutico registra una venta de 50 unidades
- Simultáneamente, otro farmacéutico intenta vender 30 del mismo lote
- El sistema previene sobreventas o inconsistencias

---

### ✅ BD NoSQL - Documentos (4.2, 4.4)

**Implementación**: `models_ensayos.py` - MongoDB para ensayos clínicos

```python
documento = {
    'medicamento_id': medicamento_id,
    'fase': fase,
    'titulo': titulo,
    'investigador_principal': investigador_principal,
    'participantes': {},
    'resultados': {},
    'efectos_secundarios': [],
    'notas_investigacion': [],
    'datos_adicionales': {}  # Flexible
}
```

**Justificación MongoDB**:
1. **Flexibilidad de esquema**: Cada ensayo puede tener campos diferentes según la fase
2. **Estructura anidada**: Efectos secundarios y notas como arrays embebidos
3. **Evolución del esquema**: Agregar campos sin migración
4. **Consultas eficientes**: Índices en fase, medicamento_id, fecha_inicio

**Casos de Uso**:
- Fase I: Solo datos de seguridad
- Fase II: Agrega datos de eficacia
- Fase III: Incluye grupo control extenso
- Fase IV: Post-comercialización con efectos a largo plazo

---

### ✅ BD NoSQL - Clave-Valor (4.3, 4.4)

**Implementación**: `models_auth.py` - MongoDB para sesiones de usuario

```python
sesion_data = {
    'token': token,  # Clave
    'usuario_id': usuario_id,  # Valor
    'fecha_expiracion': datetime.utcnow() + timedelta(hours=24)
}
```

**Justificación MongoDB para Sesiones**:
1. **Acceso ultra-rápido**: Búsqueda por índice único en token
2. **TTL automático**: Índice en fecha_expiracion para limpieza
3. **Escalabilidad**: Desacopla sesiones de PostgreSQL
4. **Volatilidad**: Los tokens son temporales

**Ventajas**:
- Lookup O(1) por token
- Limpieza automática de sesiones expiradas
- No afecta el rendimiento de PostgreSQL

---

### ✅ Diseño y Gestión Relacional (5.1)

**Implementación**: `schema_postgresql.sql`

#### Normalización (3FN)
```sql
-- Medicamentos (entidad base)
CREATE TABLE medicamentos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    principio_activo VARCHAR(200) NOT NULL
);

-- Lotes (relación 1:N con medicamentos)
CREATE TABLE lotes_medicamentos (
    id SERIAL PRIMARY KEY,
    medicamento_id INTEGER REFERENCES medicamentos(id),
    numero_lote VARCHAR(50) UNIQUE NOT NULL
);

-- Transacciones (historial)
CREATE TABLE transacciones (
    id SERIAL PRIMARY KEY,
    lote_id INTEGER REFERENCES lotes_medicamentos(id),
    usuario_id INTEGER REFERENCES usuarios(id)
);
```

#### Índices Estratégicos
```sql
-- Búsqueda frecuente de medicamentos
CREATE INDEX idx_medicamentos_nombre ON medicamentos(nombre);

-- Alertas de caducidad (consulta diaria)
CREATE INDEX idx_lotes_caducidad ON lotes_medicamentos(fecha_caducidad);

-- Historial ordenado (dashboard)
CREATE INDEX idx_transacciones_fecha ON transacciones(fecha_transaccion DESC);

-- Autenticación (cada request)
CREATE INDEX idx_usuarios_username ON usuarios(username);
```

**Justificación de Índices**:
- `idx_medicamentos_nombre`: Búsquedas de texto parcial
- `idx_lotes_caducidad`: Query diario para alertas
- `idx_transacciones_fecha`: Paginación de historial
- `idx_usuarios_username`: Login frecuente

---

### ✅ Administración del Espacio (5.2)

**Estrategia Implementada**:

1. **Tipos de Datos Optimizados**:
   ```sql
   precio_unitario NUMERIC(10, 2)  -- Precisión exacta para dinero
   cantidad_actual INTEGER          -- No necesita BIGINT
   version INTEGER DEFAULT 1        -- Control de concurrencia
   ```

2. **Vistas Materializadas Simuladas**:
   ```sql
   CREATE VIEW vista_inventario AS
   SELECT m.nombre, l.cantidad_actual, ...
   WHERE l.cantidad_actual > 0  -- Excluye lotes vacíos
   ```

3. **Limpieza Automática**:
   - MongoDB: TTL en sesiones expiradas
   - PostgreSQL: Triggers para timestamps

**Justificación**:
- Reducción de espacio en disco
- Queries más rápidas
- Mantenimiento automático

---

### ✅ Configuración de Accesos (5.3)

**Implementación**: `schema_postgresql.sql` + `.env`

```sql
-- pg_hba.conf configuración
local   pharmaflow  pharmaflow_admin  md5
host    pharmaflow  pharmaflow_admin  127.0.0.1/32  md5
```

**Seguridad Multi-Capa**:

1. **Nivel de Red**:
   - Acceso local por defecto
   - Configuración para acceso remoto opcional

2. **Nivel de Aplicación**:
   ```python
   POSTGRES_CONFIG = {
       'host': os.getenv('POSTGRES_HOST'),
       'password': os.getenv('POSTGRES_PASSWORD')  # Variables de entorno
   }
   ```

3. **Nivel de Base de Datos**:
   - Usuario específico con privilegios limitados
   - No se usa el usuario postgres en producción

---

### ✅ Grupos, Cuentas, Privilegios, Roles (5.4, 5.5)

**Implementación**: `schema_postgresql.sql` + `models_auth.py`

#### Roles de Base de Datos
```sql
-- Roles PostgreSQL
CREATE ROLE gerente;
CREATE ROLE farmaceutico;
CREATE ROLE investigador;

-- Privilegios Gerente (Full Access)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gerente;

-- Privilegios Farmacéutico (Limited Write)
GRANT SELECT ON ALL TABLES TO farmaceutico;
GRANT INSERT, UPDATE ON transacciones TO farmaceutico;
GRANT UPDATE ON lotes_medicamentos TO farmaceutico;

-- Privilegios Investigador (Read Only)
GRANT SELECT ON ALL TABLES TO investigador;
```

#### Roles de Aplicación
```python
@role_required('gerente', 'farmaceutico')
def registrar_venta():
    # Solo gerentes y farmacéuticos pueden vender
    pass

@role_required('gerente')
def usuarios():
    # Solo gerentes gestionan usuarios
    pass
```

**Matriz de Permisos**:

| Acción | Gerente | Farmacéutico | Investigador |
|--------|---------|--------------|--------------|
| Ver Inventario | ✅ | ✅ | ✅ |
| Crear Medicamento | ✅ | ✅ | ❌ |
| Registrar Venta | ✅ | ✅ | ❌ |
| Modificar Lote | ✅ | ✅ | ❌ |
| Gestionar Usuarios | ✅ | ❌ | ❌ |
| Ver Ensayos | ✅ | ✅ | ✅ |
| Crear Ensayo | ✅ | ❌ | ✅ |
| Agregar Efectos | ✅ | ❌ | ✅ |

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────┐
│           Frontend (HTML/Bootstrap)          │
│  - Templates Jinja2                          │
│  - JavaScript interactivo                    │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│           Backend (Flask)                    │
│  - Rutas y controladores                     │
│  - Decoradores de autenticación              │
│  - Manejo de sesiones                        │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼────────┐   ┌────────▼─────────┐
│   PostgreSQL   │   │     MongoDB      │
│                │   │                  │
│ • Usuarios     │   │ • Ensayos        │
│ • Medicamentos │   │ • Sesiones       │
│ • Lotes        │   │                  │
│ • Transacciones│   │                  │
└────────────────┘   └──────────────────┘
```

---

## 🔐 Seguridad Implementada

1. **Contraseñas**: Hashing con bcrypt (12 rounds)
2. **Sesiones**: Tokens seguros en MongoDB con TTL
3. **SQL Injection**: Uso de parámetros preparados
4. **CSRF**: Flask session con secret_key
5. **Control de Acceso**: Decoradores basados en roles
6. **Variables Sensibles**: Archivo .env no versionado

---

## 📊 Optimizaciones de Rendimiento

### PostgreSQL
- **Connection Pooling**: 20 conexiones máximas
- **Índices**: En columnas de búsqueda frecuente
- **Vistas**: Para queries complejas repetitivas
- **Triggers**: Actualización automática de timestamps

### MongoDB
- **Índices**: En token (único), medicamento_id, fase
- **Proyecciones**: Solo campos necesarios
- **TTL Index**: Limpieza automática de sesiones

---

## 🧪 Casos de Prueba

### 1. Concurrencia Optimista
```bash
# Terminal 1
curl -X POST /venta -d "lote_id=1&cantidad=50&metodo=optimista"

# Terminal 2 (simultáneo)
curl -X POST /venta -d "lote_id=1&cantidad=30&metodo=optimista"

# Resultado: Una venta exitosa, la otra detecta conflicto
```

### 2. Control de Permisos
```bash
# Farmacéutico intenta crear usuario
# Resultado: HTTP 403 - No tiene permisos
```

### 3. Flexibilidad de MongoDB
```python
# Fase I: Solo seguridad
ensayo = {'fase': 'Fase I', 'seguridad': {...}}

# Fase III: Más campos
ensayo = {'fase': 'Fase III', 'seguridad': {...}, 
          'eficacia': {...}, 'grupo_control': {...}}
```

---

## 📈 Escalabilidad Futura

1. **PostgreSQL**:
   - Replicación Master-Slave
   - Particionamiento de transacciones por fecha
   - Archivado de datos históricos

2. **MongoDB**:
   - Sharding por medicamento_id
   - Replica Set para alta disponibilidad
   - Agregaciones para reportes

3. **Aplicación**:
   - API REST separada
   - Cache con Redis
   - Queue con Celery para tareas pesadas

---

## 🎓 Aprendizajes Clave

1. **Cuándo usar SQL vs NoSQL**:
   - SQL: Datos relacionales, transacciones ACID
   - NoSQL: Flexibilidad de esquema, escalabilidad horizontal

2. **Control de Concurrencia**:
   - Optimista: Mejor para baja contención
   - Pesimista: Necesario para alta contención

3. **Diseño de Índices**:
   - Analizar queries frecuentes
   - Balance entre lectura y escritura

4. **Seguridad Multi-Capa**:
   - No confiar solo en la aplicación
   - Roles a nivel de BD + aplicación

---

## 📝 Conclusión

PharmaFlow Solutions implementa exitosamente todos los requisitos del proyecto:

✅ Control de concurrencia (optimista y pesimista)
✅ MongoDB para documentos flexibles
✅ MongoDB para sesiones clave-valor
✅ Diseño relacional normalizado
✅ Índices estratégicos
✅ Administración de espacio eficiente
✅ Configuración de accesos segura
✅ Roles y privilegios multi-nivel

El sistema es **funcional**, **seguro**, **escalable** y está **listo para producción**.

