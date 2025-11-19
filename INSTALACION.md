# Guía de Instalación de PharmaFlow Solutions

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

### 1. Python 3.8 o superior
```bash
python3 --version
```

### 2. PostgreSQL 12 o superior
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Verificar instalación
psql --version
```

### 3. MongoDB 4.4 o superior
```bash
# Ubuntu/Debian - Importar la clave pública
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# Crear archivo de lista
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Actualizar e instalar
sudo apt update
sudo apt install -y mongodb-org

# Iniciar MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verificar instalación
mongod --version
```

## 🚀 Instalación Rápida (Script Automático)

Si tienes todos los requisitos instalados:

```bash
cd /home/sebas/PycharmProjects/P2Bases
./setup.sh
```

El script automáticamente:
- ✓ Verifica las dependencias
- ✓ Crea el entorno virtual
- ✓ Instala las librerías de Python
- ✓ Configura las variables de entorno
- ✓ Crea la base de datos PostgreSQL
- ✓ Aplica el schema SQL
- ✓ Verifica MongoDB

## 📝 Instalación Manual (Paso a Paso)

### Paso 1: Crear Entorno Virtual

```bash
cd /home/sebas/PycharmProjects/P2Bases
python3 -m venv .venv
source .venv/bin/activate
```

### Paso 2: Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 3: Configurar PostgreSQL

#### 3.1 Crear Usuario y Base de Datos

```bash
sudo -u postgres psql
```

Dentro de PostgreSQL:

```sql
-- Crear base de datos
CREATE DATABASE pharmaflow;

-- Crear usuario
CREATE USER pharmaflow_admin WITH PASSWORD 'tu_contraseña_segura';

-- Otorgar privilegios
GRANT ALL PRIVILEGES ON DATABASE pharmaflow TO pharmaflow_admin;

-- Salir
\q
```

#### 3.2 Aplicar el Schema

```bash
psql -U pharmaflow_admin -d pharmaflow -h localhost -f schema_postgresql.sql
```

Te pedirá la contraseña que configuraste.

### Paso 4: Configurar Variables de Entorno

El archivo `.env` ya está creado con valores por defecto. Si necesitas modificarlo:

```bash
nano .env
```

Edita las siguientes variables:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=pharmaflow
POSTGRES_USER=pharmaflow_admin
POSTGRES_PASSWORD=tu_contraseña_aqui

MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=pharmaflow

SECRET_KEY=genera_una_clave_secreta_aqui
FLASK_ENV=development
```

### Paso 5: Verificar MongoDB

```bash
# Verificar que esté corriendo
sudo systemctl status mongod

# Si no está corriendo, iniciarlo
sudo systemctl start mongod

# Habilitar inicio automático
sudo systemctl enable mongod
```

### Paso 6: Ejecutar la Aplicación

```bash
# Asegúrate de estar en el entorno virtual
source .venv/bin/activate

# Ejecutar Flask
python app.py
```

La aplicación estará disponible en: **http://localhost:5000**

### Paso 7: (Opcional) Crear Datos de Prueba

```bash
python crear_datos_prueba.py
```

Este script crea:
- 2 usuarios adicionales (farmacéutico e investigador)
- 5 medicamentos
- 5 lotes con diferentes estados
- 2 ensayos clínicos

## 🔐 Acceso al Sistema

### Credenciales por Defecto

**Administrador (Gerente)**
- Usuario: `admin`
- Contraseña: `admin123`

Después de ejecutar `crear_datos_prueba.py`:

**Farmacéutico**
- Usuario: `farmacia1`
- Contraseña: `farmacia123`

**Investigador**
- Usuario: `investigador1`
- Contraseña: `invest123`

## 🧪 Verificar la Instalación

### Verificar PostgreSQL

```bash
psql -U pharmaflow_admin -d pharmaflow -h localhost -c "SELECT COUNT(*) FROM usuarios;"
```

Debería mostrar al menos 1 usuario (admin).

### Verificar MongoDB

```bash
mongosh
use pharmaflow
db.getCollectionNames()
exit
```

Debería mostrar las colecciones: `ensayos_clinicos` y `sesiones`.

### Verificar Flask

```bash
curl http://localhost:5000
```

Debería devolver HTML de la página de login.

## 🐛 Solución de Problemas

### Error: "role 'pharmaflow_admin' does not exist"

```bash
sudo -u postgres psql
CREATE USER pharmaflow_admin WITH PASSWORD 'tu_contraseña';
GRANT ALL PRIVILEGES ON DATABASE pharmaflow TO pharmaflow_admin;
\q
```

### Error: "database 'pharmaflow' does not exist"

```bash
sudo -u postgres psql
CREATE DATABASE pharmaflow;
GRANT ALL PRIVILEGES ON DATABASE pharmaflow TO pharmaflow_admin;
\q
```

### Error: "Could not connect to MongoDB"

```bash
# Verificar estado
sudo systemctl status mongod

# Si está inactivo
sudo systemctl start mongod

# Ver logs si hay errores
sudo journalctl -u mongod -f
```

### Error: "ModuleNotFoundError"

```bash
# Asegúrate de estar en el entorno virtual
source .venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "Connection refused" al conectar a PostgreSQL

Editar configuración de PostgreSQL para permitir conexiones locales:

```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

Asegúrate de tener esta línea:
```
local   all             all                                     md5
```

Reiniciar PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## 📊 Verificar Funcionalidad

### 1. Inventario
- [ ] Crear un medicamento nuevo
- [ ] Crear un lote de medicamento
- [ ] Ver el inventario completo

### 2. Transacciones
- [ ] Registrar una venta (método optimista)
- [ ] Registrar una venta (método pesimista)
- [ ] Ver historial de transacciones

### 3. Ensayos Clínicos
- [ ] Crear un nuevo ensayo
- [ ] Agregar efecto secundario
- [ ] Filtrar por fase

### 4. Usuarios
- [ ] Crear nuevo usuario
- [ ] Verificar permisos según rol
- [ ] Cerrar sesión y volver a entrar

## 🎯 Próximos Pasos

1. Cambiar la contraseña del usuario admin
2. Crear usuarios para tu equipo
3. Configurar copias de seguridad
4. Revisar los logs de la aplicación
5. Personalizar según tus necesidades

## 📞 Soporte

Si encuentras problemas durante la instalación:

1. Verifica los logs de PostgreSQL: `sudo tail -f /var/log/postgresql/postgresql-*-main.log`
2. Verifica los logs de MongoDB: `sudo tail -f /var/log/mongodb/mongod.log`
3. Verifica los logs de Flask en la terminal donde ejecutaste `python app.py`

## ✅ Checklist de Instalación Completa

- [ ] Python 3.8+ instalado
- [ ] PostgreSQL instalado y corriendo
- [ ] MongoDB instalado y corriendo
- [ ] Entorno virtual creado
- [ ] Dependencias instaladas
- [ ] Base de datos PostgreSQL creada
- [ ] Schema SQL aplicado
- [ ] Variables de entorno configuradas
- [ ] Aplicación Flask corriendo
- [ ] Puedo acceder a http://localhost:5000
- [ ] Puedo iniciar sesión con admin/admin123
- [ ] Datos de prueba creados (opcional)

¡Felicidades! Tu instalación de PharmaFlow Solutions está completa. 🎉

