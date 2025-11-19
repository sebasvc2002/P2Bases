"""
Passenger WSGI file for PharmaFlow Solutions
This file is used by cPanel's Passenger to run the Flask application
"""
import sys
import os

# Ajustar el path según la ubicación en cPanel
# Normalmente será algo como: /home/usuario/pharmaflow
INTERP = os.path.expanduser("~/virtualenv/pharmaflow/3.9/bin/python3")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Agregar el directorio de la aplicación al path
sys.path.insert(0, os.path.dirname(__file__))

# Cargar variables de entorno desde .env
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Importar la aplicación Flask
from app import app as application

# Passenger espera que la aplicación se llame 'application'
# Ya lo hemos hecho en la línea anterior con: from app import app as application

# Opcional: Logging para debugging en producción
import logging
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), 'app.log'),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == '__main__':
    application.run()

