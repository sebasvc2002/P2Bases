# PharmaFlow Solutions

Sistema de Gestión Farmacéutica implementado con Flask, PostgreSQL y MongoDB

## 📋 Descripción

PharmaFlow Solutions es una aplicación web completa que gestiona:
- **Inventario de Medicamentos** con control de concurrencia (PostgreSQL)
- **Ensayos Clínicos** con documentos flexibles (MongoDB)
- **Transacciones** de compra/venta con control de stock
- **Gestión de Usuarios** con roles y privilegios
- **Sesiones de Usuario** almacenadas en MongoDB

## 🛠️ Tecnologías Utilizadas

- **Backend**: Flask (Python)
- **Base de Datos Relacional**: PostgreSQL
- **Base de Datos NoSQL**: MongoDB
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Autenticación**: bcrypt para hash de contraseñas
- **Control de Concurrencia**: Optimista y Pesimista

## 📦 Instalación

### 1. Requisitos Previos

- Python 3.8+
- PostgreSQL 12+
- MongoDB 4.4+

### 2. Clonar el Repositorio

```bash
cd /home/sebas/PycharmProjects/P2Bases
```

### 3. Crear Entorno Virtual

```bash
python -m venv .venv
source .venv/bin/activate  # En Linux/Mac
# .venv\Scripts\activate   # En Windows
```

### 4. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar Variables de Entorno

Copiar el archivo de ejemplo y configurar:

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:

```env
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=pharmaflow
POSTGRES_USER=pharmaflow_admin
POSTGRES_PASSWORD=tu_contraseña_segura

# MongoDB
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=pharmaflow

# Flask
SECRET_KEY=tu_clave_secreta_muy_segura
FLASK_ENV=development
```

### 6. Configurar PostgreSQL

```bash
# Crear base de datos y usuario
sudo -u postgres psql

CREATE DATABASE pharmaflow;
CREATE USER pharmaflow_admin WITH PASSWORD 'tu_contraseña';
GRANT ALL PRIVILEGES ON DATABASE pharmaflow TO pharmaflow_admin;
\q

# Ejecutar el schema
psql -U pharmaflow_admin -d pharmaflow -f schema_postgresql.sql
```

### 7. Verificar MongoDB

```bash
# Verificar que MongoDB esté corriendo
sudo systemctl status mongod

# Si no está corriendo, iniciarlo
sudo systemctl start mongod
```

### 8. Ejecutar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en: http://localhost:5000

## 👤 Credenciales por Defecto

- **Usuario**: admin
- **Contraseña**: admin123
- **Rol**: Gerente (acceso completo)

## 🎯 Características Principales

### 1. Control de Concurrencia

El sistema implementa dos métodos de control de concurrencia:

#### **Concurrencia Optimista**
- Verifica conflictos al momento de la transacción
- Usa un campo `version` en la tabla `lotes_medicamentos`
- Más eficiente cuando los conflictos son raros

#### **Concurrencia Pesimista**
- Bloquea registros durante la transacción con `SELECT FOR UPDATE`
- Garantiza consistencia absoluta
- Mejor cuando los conflictos son frecuentes

### 2. Roles y Privilegios

#### **Gerente**
- Acceso total al sistema
- Gestión de usuarios
- Todas las transacciones
- Administración completa

#### **Farmacéutico**
- Registrar ventas y compras
- Modificar lotes de medicamentos
- Consultar inventario
- Sin acceso a gestión de usuarios

#### **Investigador**
- Solo consulta de datos
- Acceso completo a ensayos clínicos
- Agregar notas y efectos secundarios
- Sin modificación de inventario

### 3. PostgreSQL - Datos Estructurados

Almacena:
- **Usuarios** con roles y permisos
- **Medicamentos** y sus propiedades
- **Lotes de Medicamentos** con control de stock
- **Transacciones** de compra/venta
- **Compuestos Químicos** e interacciones

Características:
- Esquema normalizado
- Índices optimizados para consultas frecuentes
- Triggers para actualización automática de timestamps
- Vistas para consultas complejas

### 4. MongoDB - Datos Flexibles

Almacena:
- **Ensayos Clínicos** con estructura flexible
- **Sesiones de Usuario** (clave-valor)

Ventajas:
- Esquema flexible para datos semiestructurados
- Fácil agregación de campos sin migración
- Consultas rápidas con índices

## 📁 Estructura del Proyecto

```
P2Bases/
├── app.py                      # Aplicación Flask principal
├── database.py                 # Configuración de BD
├── models_auth.py              # Modelos de autenticación
├── models_inventario.py        # Modelos de inventario
├── models_ensayos.py           # Modelos de ensayos clínicos
├── requirements.txt            # Dependencias Python
├── schema_postgresql.sql       # Schema de PostgreSQL
├── .env.example                # Ejemplo de variables de entorno
├── templates/                  # Plantillas HTML
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── inventario.html
│   ├── medicamentos.html
│   ├── nuevo_medicamento.html
│   ├── nuevo_lote.html
│   ├── registrar_venta.html
│   ├── transacciones.html
│   ├── ensayos_clinicos.html
│   ├── nuevo_ensayo.html
│   ├── ver_ensayo.html
│   ├── usuarios.html
│   └── nuevo_usuario.html
└── static/
    ├── css/
    │   └── style.css           # Estilos personalizados
    └── js/
        └── main.js             # JavaScript principal
```

## 🔧 Uso del Sistema

### Gestión de Inventario

1. **Agregar Medicamento**: Navegue a Medicamentos → Nuevo Medicamento
2. **Crear Lote**: Navegue a Inventario → Nuevo Lote
3. **Registrar Venta**: Navegue a Transacciones → Nueva Venta
4. **Ver Historial**: Navegue a Transacciones

### Ensayos Clínicos

1. **Crear Ensayo**: Navegue a Ensayos Clínicos → Nuevo Ensayo
2. **Ver Detalles**: Clic en "Ver Detalles" en cualquier ensayo
3. **Agregar Efecto Secundario**: Dentro del ensayo, use el botón correspondiente

### Gestión de Usuarios (Solo Gerentes)

1. **Crear Usuario**: Navegue a Usuarios → Nuevo Usuario
2. **Asignar Rol**: Seleccione el rol apropiado según responsabilidades

## 🔐 Seguridad

- Contraseñas hasheadas con bcrypt
- Sesiones almacenadas en MongoDB con expiración
- Control de acceso basado en roles
- Validación de permisos en cada ruta
- Protección contra inyección SQL usando parámetros

## 📊 Optimizaciones

### Índices PostgreSQL
- `idx_usuarios_username` - Búsqueda rápida de usuarios
- `idx_medicamentos_nombre` - Búsqueda de medicamentos
- `idx_lotes_caducidad` - Alertas de medicamentos por caducar
- `idx_transacciones_fecha` - Historial ordenado

### Índices MongoDB
- Índice en `token` para sesiones
- Índice en `medicamento_id` para ensayos
- Índice en `fase` para filtrado de ensayos

## 🐛 Troubleshooting

### Error de conexión a PostgreSQL

```bash
# Verificar que PostgreSQL esté corriendo
sudo systemctl status postgresql

# Verificar credenciales en .env
```

### Error de conexión a MongoDB

```bash
# Verificar que MongoDB esté corriendo
sudo systemctl status mongod

# Iniciar MongoDB si está detenido
sudo systemctl start mongod
```

### Error de importación de módulos

```bash
# Reinstalar dependencias
pip install -r requirements.txt
```

## 📝 Licencia

Este proyecto fue desarrollado como parte de un proyecto académico.

## 👥 Autor

Desarrollado para PharmaFlow Solutions - 2024

## 🚀 Próximas Mejoras

- [ ] Reportes PDF de transacciones
- [ ] Gráficos de estadísticas
- [ ] API REST completa
- [ ] Notificaciones por email
- [ ] Sistema de respaldo automatizado
- [ ] Dashboard analítico avanzado

