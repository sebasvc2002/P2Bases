#!/bin/bash

# Script para preparar PharmaFlow Solutions para despliegue en cPanel
# Uso: ./preparar_cpanel.sh

set -e

echo "🚀 Preparando PharmaFlow Solutions para cPanel"
echo "=============================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Verificar archivos necesarios
echo "1. Verificando archivos necesarios..."
REQUIRED_FILES=("app.py" "database.py" "models_auth.py" "models_inventario.py" "models_ensayos.py" "requirements.txt" ".env" "passenger_wsgi.py" ".htaccess")

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file - FALTANTE"
        exit 1
    fi
done

# 2. Verificar .env para producción
echo ""
echo "2. Verificando configuración de producción..."

if grep -q "dev-secret-key-change-in-production" .env; then
    echo -e "${RED}⚠${NC} ADVERTENCIA: SECRET_KEY todavía usa valor por defecto"
    echo "   Genera una nueva con: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
fi

if grep -q "FLASK_ENV=development" .env; then
    echo -e "${YELLOW}⚠${NC} FLASK_ENV está en 'development', debería ser 'production'"
    read -p "¿Cambiar a production? (s/n): " CHANGE_ENV
    if [ "$CHANGE_ENV" = "s" ]; then
        sed -i 's/FLASK_ENV=development/FLASK_ENV=production/' .env
        echo -e "${GREEN}✓${NC} Cambiado a production"
    fi
fi

# 3. Crear directorio para logs
echo ""
echo "3. Creando directorios necesarios..."
mkdir -p logs
mkdir -p tmp
echo -e "${GREEN}✓${NC} Directorios creados"

# 4. Verificar permisos
echo ""
echo "4. Configurando permisos..."
chmod 644 .env
chmod 755 passenger_wsgi.py
chmod 644 .htaccess
echo -e "${GREEN}✓${NC} Permisos configurados"

# 5. Crear archivo de información
echo ""
echo "5. Creando archivo de información del despliegue..."
cat > DEPLOYMENT_INFO.txt << EOF
PharmaFlow Solutions - Información de Despliegue
================================================

Fecha de preparación: $(date)
Versión: 1.0

Archivos listos para subir a cPanel:
- Aplicación Flask (app.py)
- Modelos de datos (models_*.py)
- Base de datos (database.py)
- Templates HTML (templates/)
- Archivos estáticos (static/)
- Configuración cPanel (.cpanel.yml, cpanel.yaml)
- WSGI entry point (passenger_wsgi.py)
- Apache config (.htaccess)
- Variables de entorno (.env)

IMPORTANTE ANTES DE DESPLEGAR:
==============================
1. Edita .env con tus credenciales reales de producción
2. Genera una SECRET_KEY segura
3. Actualiza las rutas en passenger_wsgi.py con tu usuario de cPanel
4. Actualiza las rutas en .htaccess con tu usuario de cPanel
5. Configura PostgreSQL (local o remoto)
6. Configura MongoDB (recomendado: MongoDB Atlas)

Consulta DESPLIEGUE_CPANEL.md para instrucciones detalladas.

EOF
echo -e "${GREEN}✓${NC} Archivo de información creado"

# 6. Crear archivo .zip para subir
echo ""
echo "6. Creando archivo comprimido para subir..."
ZIPFILE="pharmaflow_cpanel_$(date +%Y%m%d_%H%M%S).zip"

zip -r "$ZIPFILE" \
    app.py \
    database.py \
    models_*.py \
    passenger_wsgi.py \
    .htaccess \
    .cpanel.yml \
    cpanel.yaml \
    .env \
    requirements.txt \
    schema_postgresql.sql \
    templates/ \
    static/ \
    DESPLIEGUE_CPANEL.md \
    DEPLOYMENT_INFO.txt \
    README.md \
    -x "*.pyc" "*.pyo" "__pycache__/*" ".venv/*" ".git/*" "*.log"

echo -e "${GREEN}✓${NC} Archivo creado: $ZIPFILE"

# 7. Resumen
echo ""
echo "=============================================="
echo -e "${GREEN}✅ Preparación completada${NC}"
echo "=============================================="
echo ""
echo "Próximos pasos:"
echo "1. Revisa y edita .env con tus credenciales de producción"
echo "2. Edita passenger_wsgi.py y .htaccess (reemplaza USUARIO)"
echo "3. Sube $ZIPFILE a cPanel"
echo "4. Descomprime en tu directorio de aplicación"
echo "5. Sigue las instrucciones en DESPLIEGUE_CPANEL.md"
echo ""
echo "Archivos importantes:"
echo "  - $ZIPFILE (para subir a cPanel)"
echo "  - DESPLIEGUE_CPANEL.md (guía paso a paso)"
echo "  - DEPLOYMENT_INFO.txt (información del despliegue)"
echo ""
echo "¡Buena suerte con el despliegue! 🚀"

