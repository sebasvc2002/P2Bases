"""
Script para insertar datos de prueba en PharmaFlow Solutions
"""
from datetime import datetime, timedelta
from models_auth import Usuario
from models_inventario import Medicamento, LoteMedicamento, Transaccion
from models_ensayos import EnsayoClinico

def crear_datos_prueba():
    """Crear datos de prueba para el sistema"""

    print("🔧 Creando datos de prueba...")

    # 1. Crear usuarios adicionales
    print("\n1. Creando usuarios...")
    try:
        Usuario.crear_usuario(
            username="farmacia1",
            password="farmacia123",
            nombre_completo="María García",
            email="maria.garcia@pharmaflow.com",
            rol="farmaceutico"
        )
        print("✓ Usuario farmacéutico creado")
    except:
        print("ℹ Usuario farmacéutico ya existe")

    try:
        Usuario.crear_usuario(
            username="investigador1",
            password="invest123",
            nombre_completo="Dr. Carlos Pérez",
            email="carlos.perez@pharmaflow.com",
            rol="investigador"
        )
        print("✓ Usuario investigador creado")
    except:
        print("ℹ Usuario investigador ya existe")

    # 2. Crear medicamentos
    print("\n2. Creando medicamentos...")
    medicamentos_data = [
        {
            'nombre': 'Paracetamol 500mg',
            'descripcion': 'Analgésico y antipirético de uso común',
            'principio_activo': 'Paracetamol',
            'categoria': 'Analgésico',
            'requiere_receta': False
        },
        {
            'nombre': 'Amoxicilina 500mg',
            'descripcion': 'Antibiótico de amplio espectro',
            'principio_activo': 'Amoxicilina',
            'categoria': 'Antibiótico',
            'requiere_receta': True
        },
        {
            'nombre': 'Ibuprofeno 400mg',
            'descripcion': 'Antiinflamatorio no esteroideo',
            'principio_activo': 'Ibuprofeno',
            'categoria': 'Antiinflamatorio',
            'requiere_receta': False
        },
        {
            'nombre': 'Losartán 50mg',
            'descripcion': 'Antihipertensivo antagonista de receptores de angiotensina',
            'principio_activo': 'Losartán Potásico',
            'categoria': 'Antihipertensivo',
            'requiere_receta': True
        },
        {
            'nombre': 'Loratadina 10mg',
            'descripcion': 'Antihistamínico para alergias',
            'principio_activo': 'Loratadina',
            'categoria': 'Antihistamínico',
            'requiere_receta': False
        }
    ]

    medicamentos_ids = []
    for med_data in medicamentos_data:
        try:
            med_id = Medicamento.crear(**med_data)
            medicamentos_ids.append(med_id)
            print(f"✓ Medicamento creado: {med_data['nombre']}")
        except Exception as e:
            print(f"ℹ {med_data['nombre']}: {str(e)}")

    # Obtener todos los medicamentos
    medicamentos = Medicamento.listar()
    if not medicamentos:
        print("✗ Error: No se pudieron crear medicamentos")
        return

    # 3. Crear lotes de medicamentos
    print("\n3. Creando lotes de medicamentos...")
    fecha_hoy = datetime.now()

    lotes_data = [
        {
            'medicamento_id': medicamentos[0]['id'],
            'numero_lote': 'PARA-2024-001',
            'cantidad': 1000,
            'precio_unitario': 2.50,
            'fecha_fabricacion': (fecha_hoy - timedelta(days=60)).strftime('%Y-%m-%d'),
            'fecha_caducidad': (fecha_hoy + timedelta(days=730)).strftime('%Y-%m-%d'),
            'proveedor': 'Laboratorios Farmex'
        },
        {
            'medicamento_id': medicamentos[1]['id'],
            'numero_lote': 'AMOX-2024-001',
            'cantidad': 500,
            'precio_unitario': 8.75,
            'fecha_fabricacion': (fecha_hoy - timedelta(days=45)).strftime('%Y-%m-%d'),
            'fecha_caducidad': (fecha_hoy + timedelta(days=540)).strftime('%Y-%m-%d'),
            'proveedor': 'Pharma Solutions SA'
        },
        {
            'medicamento_id': medicamentos[2]['id'],
            'numero_lote': 'IBUP-2024-002',
            'cantidad': 750,
            'precio_unitario': 3.20,
            'fecha_fabricacion': (fecha_hoy - timedelta(days=30)).strftime('%Y-%m-%d'),
            'fecha_caducidad': (fecha_hoy + timedelta(days=700)).strftime('%Y-%m-%d'),
            'proveedor': 'Laboratorios Farmex'
        },
        {
            'medicamento_id': medicamentos[3]['id'],
            'numero_lote': 'LOSA-2024-001',
            'cantidad': 300,
            'precio_unitario': 12.50,
            'fecha_fabricacion': (fecha_hoy - timedelta(days=20)).strftime('%Y-%m-%d'),
            'fecha_caducidad': (fecha_hoy + timedelta(days=600)).strftime('%Y-%m-%d'),
            'proveedor': 'MediPharma Corp'
        },
        {
            'medicamento_id': medicamentos[4]['id'],
            'numero_lote': 'LORA-2024-003',
            'cantidad': 200,
            'precio_unitario': 4.80,
            'fecha_fabricacion': (fecha_hoy - timedelta(days=90)).strftime('%Y-%m-%d'),
            'fecha_caducidad': (fecha_hoy + timedelta(days=60)).strftime('%Y-%m-%d'),
            'proveedor': 'Laboratorios Farmex'
        }
    ]

    lotes_ids = []
    for lote_data in lotes_data:
        try:
            lote_id = LoteMedicamento.crear(**lote_data)
            lotes_ids.append(lote_id)
            print(f"✓ Lote creado: {lote_data['numero_lote']}")
        except Exception as e:
            print(f"ℹ {lote_data['numero_lote']}: {str(e)}")

    # 4. Crear ensayos clínicos
    print("\n4. Creando ensayos clínicos...")

    if len(medicamentos) >= 2:
        ensayo1_data = {
            'fecha_inicio': fecha_hoy - timedelta(days=180),
            'estado': 'en_progreso',
            'participantes': {
                'total': 100,
                'completados': 65
            },
            'notas_investigacion': [
                {
                    'texto': 'Inicio del estudio con grupo control de 100 pacientes',
                    'autor': 'Dr. Carlos Pérez',
                    'categoria': 'inicio'
                }
            ],
            'efectos_secundarios': [
                {
                    'descripcion': 'Mareo leve en algunos pacientes',
                    'severidad': 'leve',
                    'frecuencia': 'poco_frecuente'
                }
            ],
            'resultados': {
                'eficacia': '85%',
                'reduccion_sintomas': '70%'
            },
            'datos_adicionales': {
                'grupo_edad': '18-65',
                'duracion_tratamiento_dias': 30
            }
        }

        try:
            ensayo1_id = EnsayoClinico.crear(
                medicamento_id=medicamentos[1]['id'],
                fase='Fase III',
                titulo='Estudio de eficacia de Amoxicilina en infecciones respiratorias',
                investigador_principal='Dr. Carlos Pérez',
                datos_ensayo=ensayo1_data
            )
            print(f"✓ Ensayo clínico creado: Fase III Amoxicilina")
        except Exception as e:
            print(f"ℹ Error creando ensayo: {str(e)}")

        ensayo2_data = {
            'fecha_inicio': fecha_hoy - timedelta(days=90),
            'estado': 'en_progreso',
            'participantes': {
                'total': 50,
                'completados': 20
            },
            'notas_investigacion': [],
            'efectos_secundarios': [],
            'resultados': {},
            'datos_adicionales': {
                'grupo_edad': '40-70',
                'condicion': 'hipertension'
            }
        }

        try:
            ensayo2_id = EnsayoClinico.crear(
                medicamento_id=medicamentos[3]['id'],
                fase='Fase II',
                titulo='Evaluación de Losartán en hipertensión arterial moderada',
                investigador_principal='Dra. Ana Martínez',
                datos_ensayo=ensayo2_data
            )
            print(f"✓ Ensayo clínico creado: Fase II Losartán")
        except Exception as e:
            print(f"ℹ Error creando ensayo: {str(e)}")

    print("\n" + "="*50)
    print("✅ Datos de prueba creados exitosamente!")
    print("="*50)
    print("\nPuedes acceder con:")
    print("  - admin / admin123 (Gerente)")
    print("  - farmacia1 / farmacia123 (Farmacéutico)")
    print("  - investigador1 / invest123 (Investigador)")

if __name__ == "__main__":
    crear_datos_prueba()

