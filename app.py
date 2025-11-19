import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from datetime import datetime

from database import get_db_cursor
from models_auth import Usuario, Sesion
from models_inventario import Medicamento, LoteMedicamento, Transaccion
from models_ensayos import EnsayoClinico

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Decorador para requerir autenticación
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debe iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para requerir roles específicos
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debe iniciar sesión', 'warning')
                return redirect(url_for('login'))

            user = Usuario.obtener_por_id(session['user_id'])
            if not user or user['rol'] not in roles:
                flash('No tiene permisos para acceder a esta página', 'danger')
                return redirect(url_for('dashboard'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Rutas de autenticación
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Usuario.autenticar(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['rol'] = user['rol']
            session['nombre_completo'] = user['nombre_completo']

            # Crear sesión en MongoDB
            token = Sesion.crear_sesion(user['id'])
            session['token'] = token

            flash(f'Bienvenido, {user["nombre_completo"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'token' in session:
        Sesion.eliminar_sesion(session['token'])
    session.clear()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('login'))

# Dashboard principal
@app.route('/dashboard')
@login_required
def dashboard():
    user = Usuario.obtener_por_id(session['user_id'])

    # Estadísticas básicas
    with get_db_cursor(commit=False) as cursor:
        cursor.execute("SELECT COUNT(*) FROM medicamentos")
        total_medicamentos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM lotes_medicamentos WHERE cantidad_actual > 0")
        lotes_activos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM transacciones WHERE tipo = 'venta' AND DATE(fecha_transaccion) = CURRENT_DATE")
        ventas_hoy = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM lotes_medicamentos 
            WHERE fecha_caducidad < CURRENT_DATE + INTERVAL '3 months' 
            AND cantidad_actual > 0
        """)
        lotes_por_caducar = cursor.fetchone()[0]

    stats = {
        'total_medicamentos': total_medicamentos,
        'lotes_activos': lotes_activos,
        'ventas_hoy': ventas_hoy,
        'lotes_por_caducar': lotes_por_caducar
    }

    return render_template('dashboard.html', user=user, stats=stats)

# Rutas de Inventario
@app.route('/inventario')
@login_required
def inventario():
    inventario = LoteMedicamento.listar_inventario()
    return render_template('inventario.html', inventario=inventario)

@app.route('/medicamentos')
@login_required
def medicamentos():
    medicamentos = Medicamento.listar()
    return render_template('medicamentos.html', medicamentos=medicamentos)

@app.route('/medicamentos/nuevo', methods=['GET', 'POST'])
@role_required('gerente', 'farmaceutico')
def nuevo_medicamento():
    if request.method == 'POST':
        try:
            medicamento_id = Medicamento.crear(
                nombre=request.form.get('nombre'),
                descripcion=request.form.get('descripcion'),
                principio_activo=request.form.get('principio_activo'),
                categoria=request.form.get('categoria'),
                requiere_receta=request.form.get('requiere_receta') == 'on'
            )
            flash('Medicamento creado exitosamente', 'success')
            return redirect(url_for('medicamentos'))
        except Exception as e:
            flash(f'Error al crear medicamento: {str(e)}', 'danger')

    return render_template('nuevo_medicamento.html')

@app.route('/lotes/nuevo', methods=['GET', 'POST'])
@role_required('gerente', 'farmaceutico')
def nuevo_lote():
    if request.method == 'POST':
        try:
            lote_id = LoteMedicamento.crear(
                medicamento_id=int(request.form.get('medicamento_id')),
                numero_lote=request.form.get('numero_lote'),
                cantidad=int(request.form.get('cantidad')),
                precio_unitario=float(request.form.get('precio_unitario')),
                fecha_fabricacion=request.form.get('fecha_fabricacion'),
                fecha_caducidad=request.form.get('fecha_caducidad'),
                proveedor=request.form.get('proveedor')
            )
            flash('Lote creado exitosamente', 'success')
            return redirect(url_for('inventario'))
        except Exception as e:
            flash(f'Error al crear lote: {str(e)}', 'danger')

    medicamentos = Medicamento.listar()
    return render_template('nuevo_lote.html', medicamentos=medicamentos)

# Rutas de Transacciones (con control de concurrencia)
@app.route('/transacciones')
@login_required
def transacciones():
    historial = Transaccion.listar_historial()
    return render_template('transacciones.html', transacciones=historial)

@app.route('/venta', methods=['GET', 'POST'])
@role_required('gerente', 'farmaceutico')
def registrar_venta():
    if request.method == 'POST':
        try:
            lote_id = int(request.form.get('lote_id'))
            cantidad = int(request.form.get('cantidad'))
            usar_optimista = request.form.get('metodo_concurrencia') == 'optimista'

            exito, mensaje, transaccion_id = Transaccion.registrar_venta(
                lote_id, session['user_id'], cantidad, usar_optimista
            )

            if exito:
                flash(mensaje, 'success')
                return redirect(url_for('transacciones'))
            else:
                flash(mensaje, 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

    inventario = LoteMedicamento.listar_inventario()
    return render_template('registrar_venta.html', inventario=inventario)

# Rutas de Ensayos Clínicos (MongoDB)
@app.route('/ensayos')
@login_required
def ensayos_clinicos():
    fase_filtro = request.args.get('fase')
    estado_filtro = request.args.get('estado')

    filtros = {}
    if fase_filtro:
        filtros['fase'] = fase_filtro
    if estado_filtro:
        filtros['estado'] = estado_filtro

    ensayos = EnsayoClinico.listar(filtros)

    # Obtener nombres de medicamentos
    medicamentos_dict = {}
    for medicamento in Medicamento.listar():
        medicamentos_dict[medicamento['id']] = medicamento['nombre']

    return render_template('ensayos_clinicos.html', ensayos=ensayos, medicamentos=medicamentos_dict)

@app.route('/ensayos/nuevo', methods=['GET', 'POST'])
@role_required('gerente', 'investigador')
def nuevo_ensayo():
    if request.method == 'POST':
        try:
            datos_ensayo = {
                'fecha_inicio': datetime.strptime(request.form.get('fecha_inicio'), '%Y-%m-%d'),
                'estado': request.form.get('estado', 'en_progreso'),
                'participantes': {
                    'total': int(request.form.get('participantes_total', 0)),
                    'completados': int(request.form.get('participantes_completados', 0))
                },
                'notas_investigacion': [],
                'efectos_secundarios': [],
                'datos_adicionales': {}
            }

            ensayo_id = EnsayoClinico.crear(
                medicamento_id=int(request.form.get('medicamento_id')),
                fase=request.form.get('fase'),
                titulo=request.form.get('titulo'),
                investigador_principal=request.form.get('investigador_principal'),
                datos_ensayo=datos_ensayo
            )

            flash('Ensayo clínico creado exitosamente', 'success')
            return redirect(url_for('ensayos_clinicos'))
        except Exception as e:
            flash(f'Error al crear ensayo: {str(e)}', 'danger')

    medicamentos = Medicamento.listar()
    return render_template('nuevo_ensayo.html', medicamentos=medicamentos)

@app.route('/ensayos/<ensayo_id>')
@login_required
def ver_ensayo(ensayo_id):
    ensayo = EnsayoClinico.obtener_por_id(ensayo_id)
    if not ensayo:
        flash('Ensayo no encontrado', 'danger')
        return redirect(url_for('ensayos_clinicos'))

    medicamento = Medicamento.obtener_por_id(ensayo['medicamento_id'])
    return render_template('ver_ensayo.html', ensayo=ensayo, medicamento=medicamento)

@app.route('/ensayos/<ensayo_id>/agregar_efecto', methods=['POST'])
@role_required('gerente', 'investigador')
def agregar_efecto_secundario(ensayo_id):
    try:
        efecto = {
            'descripcion': request.form.get('descripcion'),
            'severidad': request.form.get('severidad', 'leve'),
            'frecuencia': request.form.get('frecuencia', 'rara'),
            'detalles': {}
        }

        if EnsayoClinico.agregar_efecto_secundario(ensayo_id, efecto):
            flash('Efecto secundario agregado', 'success')
        else:
            flash('Error al agregar efecto secundario', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('ver_ensayo', ensayo_id=ensayo_id))

# Rutas de administración (solo gerentes)
@app.route('/usuarios')
@role_required('gerente')
def usuarios():
    usuarios = Usuario.listar_usuarios()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuarios/nuevo', methods=['GET', 'POST'])
@role_required('gerente')
def nuevo_usuario():
    if request.method == 'POST':
        try:
            Usuario.crear_usuario(
                username=request.form.get('username'),
                password=request.form.get('password'),
                nombre_completo=request.form.get('nombre_completo'),
                email=request.form.get('email'),
                rol=request.form.get('rol')
            )
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('usuarios'))
        except Exception as e:
            flash(f'Error al crear usuario: {str(e)}', 'danger')

    return render_template('nuevo_usuario.html')

# API endpoints
@app.route('/api/lote/<int:lote_id>')
@login_required
def api_obtener_lote(lote_id):
    lote = LoteMedicamento.obtener_por_id(lote_id)
    if lote:
        return jsonify(lote)
    return jsonify({'error': 'Lote no encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

