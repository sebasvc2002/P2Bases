-- PharmaFlow Solutions - PostgreSQL Database Schema
-- Sistema de gestión farmacéutica con control de concurrencia

-- Crear roles del sistema
CREATE ROLE gerente;
CREATE ROLE farmaceutico;
CREATE ROLE investigador;

-- Tabla de usuarios con control de acceso
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('gerente', 'farmaceutico', 'investigador')),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para búsquedas rápidas por username
CREATE INDEX idx_usuarios_username ON usuarios(username);
CREATE INDEX idx_usuarios_rol ON usuarios(rol);

-- Tabla de medicamentos
CREATE TABLE medicamentos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    principio_activo VARCHAR(200) NOT NULL,
    categoria VARCHAR(50),
    requiere_receta BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_medicamentos_nombre ON medicamentos(nombre);
CREATE INDEX idx_medicamentos_principio_activo ON medicamentos(principio_activo);

-- Tabla de lotes de medicamentos con control de versión para concurrencia optimista
CREATE TABLE lotes_medicamentos (
    id SERIAL PRIMARY KEY,
    medicamento_id INTEGER REFERENCES medicamentos(id) ON DELETE CASCADE,
    numero_lote VARCHAR(50) UNIQUE NOT NULL,
    cantidad_actual INTEGER NOT NULL CHECK (cantidad_actual >= 0),
    cantidad_inicial INTEGER NOT NULL,
    precio_unitario NUMERIC(10, 2) NOT NULL CHECK (precio_unitario >= 0),
    fecha_fabricacion DATE NOT NULL,
    fecha_caducidad DATE NOT NULL,
    proveedor VARCHAR(100),
    version INTEGER DEFAULT 1, -- Control de concurrencia optimista
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_lotes_medicamento ON lotes_medicamentos(medicamento_id);
CREATE INDEX idx_lotes_numero ON lotes_medicamentos(numero_lote);
CREATE INDEX idx_lotes_caducidad ON lotes_medicamentos(fecha_caducidad);

-- Tabla de transacciones (compras y ventas)
CREATE TABLE transacciones (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('compra', 'venta')),
    lote_id INTEGER REFERENCES lotes_medicamentos(id),
    usuario_id INTEGER REFERENCES usuarios(id),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_total NUMERIC(12, 2) NOT NULL,
    fecha_transaccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notas TEXT
);

CREATE INDEX idx_transacciones_lote ON transacciones(lote_id);
CREATE INDEX idx_transacciones_fecha ON transacciones(fecha_transaccion DESC);
CREATE INDEX idx_transacciones_tipo ON transacciones(tipo);

-- Tabla de compuestos químicos
CREATE TABLE compuestos_quimicos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    formula_quimica VARCHAR(100),
    descripcion TEXT,
    nivel_riesgo VARCHAR(20) CHECK (nivel_riesgo IN ('bajo', 'medio', 'alto'))
);

-- Tabla de interacciones entre medicamentos
CREATE TABLE interacciones_medicamentos (
    id SERIAL PRIMARY KEY,
    medicamento_id_1 INTEGER REFERENCES medicamentos(id),
    medicamento_id_2 INTEGER REFERENCES medicamentos(id),
    tipo_interaccion VARCHAR(50),
    severidad VARCHAR(20) CHECK (severidad IN ('leve', 'moderada', 'severa')),
    descripcion TEXT,
    CHECK (medicamento_id_1 < medicamento_id_2) -- Evitar duplicados
);

CREATE INDEX idx_interacciones_med1 ON interacciones_medicamentos(medicamento_id_1);
CREATE INDEX idx_interacciones_med2 ON interacciones_medicamentos(medicamento_id_2);

-- Función para actualizar timestamp de modificación
CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.ultima_modificacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para actualizar timestamps
CREATE TRIGGER trigger_usuarios_timestamp
    BEFORE UPDATE ON usuarios
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trigger_lotes_timestamp
    BEFORE UPDATE ON lotes_medicamentos
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_timestamp();

-- Privilegios para el rol gerente (acceso total)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gerente;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO gerente;

-- Privilegios para el rol farmacéutico (registrar ventas y modificar lotes)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO farmaceutico;
GRANT INSERT, UPDATE ON transacciones TO farmaceutico;
GRANT UPDATE ON lotes_medicamentos TO farmaceutico;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO farmaceutico;

-- Privilegios para el rol investigador (solo consulta)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO investigador;

-- Vista para consultas de inventario
CREATE VIEW vista_inventario AS
SELECT
    m.id as medicamento_id,
    m.nombre as medicamento,
    m.principio_activo,
    l.id as lote_id,
    l.numero_lote,
    l.cantidad_actual,
    l.precio_unitario,
    l.fecha_caducidad,
    l.version,
    CASE
        WHEN l.fecha_caducidad < CURRENT_DATE THEN 'caducado'
        WHEN l.fecha_caducidad < CURRENT_DATE + INTERVAL '3 months' THEN 'proximo_a_caducar'
        ELSE 'vigente'
    END as estado_caducidad
FROM medicamentos m
JOIN lotes_medicamentos l ON m.id = l.medicamento_id
WHERE l.cantidad_actual > 0
ORDER BY l.fecha_caducidad;

-- Insertar usuario administrador por defecto (password: admin123)
INSERT INTO usuarios (username, password_hash, nombre_completo, email, rol)
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7LAodZG1nS', 'Administrador', 'admin@pharmaflow.com', 'gerente');

