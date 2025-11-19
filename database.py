import os
from dotenv import load_dotenv
from psycopg2 import pool
from pymongo import MongoClient
from contextlib import contextmanager

load_dotenv()

# Configuración de PostgreSQL
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'pharmaflow'),
    'user': os.getenv('POSTGRES_USER', 'pharmaflow_admin'),
    'password': os.getenv('POSTGRES_PASSWORD', 'your_password_here')
}

# Pool de conexiones PostgreSQL
try:
    postgres_pool = pool.SimpleConnectionPool(1, 20, **POSTGRES_CONFIG)
    print("✓ PostgreSQL connection pool created successfully")
except Exception as e:
    print(f"✗ Error creating PostgreSQL pool: {e}")
    postgres_pool = None

# Configuración de MongoDB
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB = os.getenv('MONGODB_DB', 'pharmaflow')

try:
    mongo_client = MongoClient(MONGODB_URI)
    mongo_db = mongo_client[MONGODB_DB]
    print("✓ MongoDB connected successfully")
except Exception as e:
    print(f"✗ Error connecting to MongoDB: {e}")
    mongo_client = None
    mongo_db = None

# Colecciones de MongoDB
def get_ensayos_collection():
    """Colección para reportes de ensayos clínicos (documentos flexibles)"""
    return mongo_db.ensayos_clinicos if mongo_db is not None else None

def get_sesiones_collection():
    """Colección para tokens de sesión (clave-valor)"""
    return mongo_db.sesiones if mongo_db is not None else None

@contextmanager
def get_db_connection():
    """Context manager para conexiones PostgreSQL con manejo de transacciones"""
    conn = None
    try:
        conn = postgres_pool.getconn()
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            postgres_pool.putconn(conn)

@contextmanager
def get_db_cursor(commit=True):
    """Context manager para cursor PostgreSQL"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

def init_mongodb_indexes():
    """Crear índices en MongoDB para optimizar consultas"""
    if mongo_db is not None:
        try:
            # Índices para ensayos clínicos
            ensayos = get_ensayos_collection()
            ensayos.create_index("medicamento_id")
            ensayos.create_index("fase")
            ensayos.create_index("fecha_inicio")

            # Índices para sesiones
            sesiones = get_sesiones_collection()
            sesiones.create_index("token", unique=True)
            sesiones.create_index("usuario_id")
            sesiones.create_index("fecha_expiracion")

            print("✓ MongoDB indexes created successfully")
        except Exception as e:
            print(f"✗ Error creating MongoDB indexes: {e}")

# Inicializar índices al importar el módulo
if mongo_db is not None:
    init_mongodb_indexes()

