#!/bin/bash

# PharmaFlow Solutions - Setup Script
# Este script configura el entorno completo para la aplicación

set -e

echo "🚀 PharmaFlow Solutions - Script de Configuración"
echo "=================================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# 1. Verificar Python
echo "1. Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python encontrado: $PYTHON_VERSION"
else
    print_error "Python 3 no está instalado"
    exit 1
fi

# 2. Verificar PostgreSQL
echo ""
echo "2. Verificando PostgreSQL..."
if command -v psql &> /dev/null; then
    POSTGRES_VERSION=$(psql --version)
    print_success "PostgreSQL encontrado: $POSTGRES_VERSION"
else
    print_error "PostgreSQL no está instalado"
    print_info "Instalar con: sudo apt install postgresql postgresql-contrib"
    exit 1
fi

# 3. Verificar MongoDB
echo ""
echo "3. Verificando MongoDB..."
if command -v mongod &> /dev/null; then
    MONGO_VERSION=$(mongod --version | head -n 1)
    print_success "MongoDB encontrado: $MONGO_VERSION"
else
    print_error "MongoDB no está instalado"
    print_info "Instalar siguiendo: https://docs.mongodb.com/manual/installation/"
    exit 1
fi

# 4. Crear entorno virtual
echo ""
echo "4. Configurando entorno virtual..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    print_success "Entorno virtual creado"
else
    print_info "Entorno virtual ya existe"
fi

# 5. Activar entorno virtual e instalar dependencias
echo ""
echo "5. Instalando dependencias..."
source .venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
print_success "Dependencias instaladas"

# 6. Configurar archivo .env
echo ""
echo "6. Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    cp .env.example .env

    # Generar SECRET_KEY aleatoria
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

    # Actualizar .env con valores seguros
    sed -i "s/your_secret_key_here/$SECRET_KEY/" .env

    print_success "Archivo .env creado"
    print_info "Por favor, edita .env con tus credenciales de PostgreSQL"

    # Pedir credenciales de PostgreSQL
    echo ""
    read -p "Usuario de PostgreSQL (pharmaflow_admin): " POSTGRES_USER
    POSTGRES_USER=${POSTGRES_USER:-pharmaflow_admin}

    read -sp "Contraseña de PostgreSQL: " POSTGRES_PASSWORD
    echo ""

    sed -i "s/POSTGRES_USER=.*/POSTGRES_USER=$POSTGRES_USER/" .env
    sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" .env

    print_success "Credenciales configuradas"
else
    print_info "Archivo .env ya existe"
fi

# 7. Configurar PostgreSQL
echo ""
echo "7. Configurando base de datos PostgreSQL..."
read -p "¿Deseas crear la base de datos PostgreSQL ahora? (s/n): " CREATE_DB

if [ "$CREATE_DB" = "s" ]; then
    source .env

    # Crear base de datos y usuario
    sudo -u postgres psql <<EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '$POSTGRES_DB') THEN
        CREATE DATABASE $POSTGRES_DB;
    END IF;
END
\$\$;

DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '$POSTGRES_USER') THEN
        CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';
    END IF;
END
\$\$;

GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;
EOF

    print_success "Base de datos creada"

    # Ejecutar schema
    echo "Ejecutando schema SQL..."
    PGPASSWORD=$POSTGRES_PASSWORD psql -U $POSTGRES_USER -d $POSTGRES_DB -h localhost -f schema_postgresql.sql > /dev/null 2>&1

    print_success "Schema aplicado"
else
    print_info "Recuerda crear la base de datos manualmente"
    print_info "Ejecuta: psql -U postgres -f schema_postgresql.sql"
fi

# 8. Verificar MongoDB
echo ""
echo "8. Verificando MongoDB..."
if systemctl is-active --quiet mongod; then
    print_success "MongoDB está corriendo"
else
    print_info "Iniciando MongoDB..."
    sudo systemctl start mongod
    print_success "MongoDB iniciado"
fi

# 9. Resumen
echo ""
echo "=================================================="
echo "🎉 ¡Configuración completada!"
echo "=================================================="
echo ""
print_success "El sistema está listo para usar"
echo ""
echo "Para iniciar la aplicación:"
echo "  1. Activa el entorno virtual: source .venv/bin/activate"
echo "  2. Ejecuta la aplicación: python app.py"
echo "  3. Abre en el navegador: http://localhost:5000"
echo ""
echo "Credenciales por defecto:"
echo "  Usuario: admin"
echo "  Contraseña: admin123"
echo ""
print_info "¡Disfruta de PharmaFlow Solutions!"

