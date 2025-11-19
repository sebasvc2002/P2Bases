# 🚀 Inicio Rápido - PharmaFlow Solutions

## ⚡ Instalación en 5 Minutos

### 1. Pre-requisitos
```bash
# Verificar que tengas instalado:
python3 --version  # 3.8+
psql --version     # PostgreSQL 12+
mongod --version   # MongoDB 4.4+
```

### 2. Configurar Base de Datos
```bash
# PostgreSQL
sudo -u postgres psql
CREATE DATABASE pharmaflow;
CREATE USER pharmaflow_admin WITH PASSWORD 'pharmaflow2024';
GRANT ALL PRIVILEGES ON DATABASE pharmaflow TO pharmaflow_admin;
\q

# Aplicar schema
psql -U pharmaflow_admin -d pharmaflow -h localhost -f schema_postgresql.sql
```

### 3. Instalar y Ejecutar
```bash
# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias (si no están instaladas)
pip install -r requirements.txt

# Iniciar MongoDB (si no está corriendo)
sudo systemctl start mongod

# Ejecutar aplicación
python app.py
```

### 4. Acceder
Abre tu navegador en: **http://localhost:5000**

**Credenciales:**
- Usuario: `admin`
- Contraseña: `admin123`

### 5. (Opcional) Cargar Datos de Prueba
```bash
python crear_datos_prueba.py
```

---

## 📚 Archivos Importantes

| Archivo | Descripción |
|---------|-------------|
| `README.md` | Documentación completa del proyecto |
| `INSTALACION.md` | Guía paso a paso de instalación |
| `DOCUMENTACION_TECNICA.md` | Explicación técnica detallada |
| `schema_postgresql.sql` | Schema completo de PostgreSQL |
| `app.py` | Aplicación Flask principal |
| `.env` | Configuración (ya pre-configurado) |

---

## 🎯 Funcionalidades Principales

### 1. Gestión de Inventario
- ✅ Crear medicamentos
- ✅ Crear lotes con fechas de caducidad
- ✅ Ver inventario en tiempo real
- ✅ Alertas de lotes por caducar

### 2. Transacciones
- ✅ Registrar ventas (concurrencia optimista/pesimista)
- ✅ Registrar compras
- ✅ Historial completo
- ✅ Control de stock automático

### 3. Ensayos Clínicos (MongoDB)
- ✅ Crear ensayos con estructura flexible
- ✅ Agregar efectos secundarios
- ✅ Notas de investigación
- ✅ Filtros por fase y estado

### 4. Gestión de Usuarios
- ✅ 3 roles: Gerente, Farmacéutico, Investigador
- ✅ Permisos diferenciados
- ✅ Autenticación segura

---

## 🔑 Roles y Permisos

### Gerente (admin)
- ✅ Acceso total
- ✅ Crear usuarios
- ✅ Todas las operaciones

### Farmacéutico (farmacia1 / farmacia123)
- ✅ Registrar ventas
- ✅ Modificar lotes
- ❌ Crear usuarios

### Investigador (investigador1 / invest123)
- ✅ Ver inventario
- ✅ Gestionar ensayos clínicos
- ❌ Ventas o compras

---

## 🛠️ Comandos Útiles

```bash
# Ver logs de PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*-main.log

# Ver logs de MongoDB
sudo tail -f /var/log/mongodb/mongod.log

# Reiniciar PostgreSQL
sudo systemctl restart postgresql

# Reiniciar MongoDB
sudo systemctl restart mongod

# Limpiar sesiones expiradas (MongoDB)
mongosh
use pharmaflow
db.sesiones.deleteMany({fecha_expiracion: {$lt: new Date()}})

# Backup PostgreSQL
pg_dump -U pharmaflow_admin pharmaflow > backup.sql

# Backup MongoDB
mongodump --db pharmaflow --out backup_mongo/
```

---

## 🐛 Problemas Comunes

### "Connection refused" PostgreSQL
```bash
sudo systemctl start postgresql
```

### "Connection refused" MongoDB
```bash
sudo systemctl start mongod
```

### Error de módulos Python
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### No puedo acceder en el navegador
Verifica que Flask esté corriendo:
```bash
curl http://localhost:5000
```

---

## 📞 Ayuda Adicional

1. **README.md** - Documentación completa
2. **INSTALACION.md** - Guía detallada de instalación
3. **DOCUMENTACION_TECNICA.md** - Detalles técnicos

---

## ✅ Checklist de Verificación

- [ ] PostgreSQL instalado y corriendo
- [ ] MongoDB instalado y corriendo
- [ ] Base de datos `pharmaflow` creada
- [ ] Schema SQL aplicado
- [ ] Entorno virtual activado
- [ ] Dependencias instaladas
- [ ] Aplicación corriendo en puerto 5000
- [ ] Puedo iniciar sesión con admin/admin123

---

## 🎉 ¡Listo!

Si completaste el checklist, **tu sistema está funcionando**.

Ahora puedes:
1. Explorar el dashboard
2. Crear medicamentos y lotes
3. Registrar ventas (prueba los métodos de concurrencia)
4. Crear ensayos clínicos
5. Gestionar usuarios

**¡Disfruta de PharmaFlow Solutions!** 💊

