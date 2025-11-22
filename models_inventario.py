from database import get_db_cursor
from psycopg2 import sql
import psycopg2

class Medicamento:
    """Modelo para medicamentos"""

    @staticmethod
    def crear(nombre, descripcion, principio_activo, categoria, requiere_receta):
        """Crear nuevo medicamento"""
        with get_db_cursor() as cursor:
            cursor.execute(
                """INSERT INTO medicamentos (nombre, descripcion, principio_activo, categoria, requiere_receta)
                   VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                (nombre, descripcion, principio_activo, categoria, requiere_receta)
            )
            return cursor.fetchone()[0]

    @staticmethod
    def listar():
        """Listar todos los medicamentos"""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                """SELECT id, nombre, descripcion, principio_activo, categoria, requiere_receta
                   FROM medicamentos ORDER BY nombre"""
            )
            medicamentos = []
            for row in cursor.fetchall():
                medicamentos.append({
                    'id': row[0],
                    'nombre': row[1],
                    'descripcion': row[2],
                    'principio_activo': row[3],
                    'categoria': row[4],
                    'requiere_receta': row[5]
                })
            return medicamentos

    @staticmethod
    def obtener_por_id(medicamento_id):
        """Obtener medicamento por ID"""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                """SELECT id, nombre, descripcion, principio_activo, categoria, requiere_receta
                   FROM medicamentos WHERE id = %s""",
                (medicamento_id,)
            )
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'nombre': row[1],
                    'descripcion': row[2],
                    'principio_activo': row[3],
                    'categoria': row[4],
                    'requiere_receta': row[5]
                }
        return None

    @staticmethod
    def actualizar(medicamento_id, nombre, descripcion, principio_activo, categoria, requiere_receta):
        """Actualizar medicamento existente"""
        with get_db_cursor() as cursor:
            cursor.execute(
                """UPDATE medicamentos 
                   SET nombre = %s, descripcion = %s, principio_activo = %s, 
                       categoria = %s, requiere_receta = %s
                   WHERE id = %s""",
                (nombre, descripcion, principio_activo, categoria, requiere_receta, medicamento_id)
            )
            return cursor.rowcount > 0

    @staticmethod
    def eliminar(medicamento_id):
        """Eliminar medicamento (solo si no tiene lotes asociados)"""
        with get_db_cursor() as cursor:
            cursor.execute("DELETE FROM medicamentos WHERE id = %s", (medicamento_id,))
            return cursor.rowcount > 0

class LoteMedicamento:
    """Modelo para lotes de medicamentos con control de concurrencia"""

    @staticmethod
    def crear(medicamento_id, numero_lote, cantidad, precio_unitario,
              fecha_fabricacion, fecha_caducidad, proveedor):
        """Crear nuevo lote"""
        with get_db_cursor() as cursor:
            cursor.execute(
                """INSERT INTO lotes_medicamentos 
                   (medicamento_id, numero_lote, cantidad_actual, cantidad_inicial, 
                    precio_unitario, fecha_fabricacion, fecha_caducidad, proveedor)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                (medicamento_id, numero_lote, cantidad, cantidad, precio_unitario,
                 fecha_fabricacion, fecha_caducidad, proveedor)
            )
            return cursor.fetchone()[0]

    @staticmethod
    def listar_inventario():
        """Listar inventario usando la vista optimizada"""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                """SELECT medicamento_id, medicamento, principio_activo, lote_id, 
                          numero_lote, cantidad_actual, precio_unitario, fecha_caducidad, 
                          version, estado_caducidad
                   FROM vista_inventario"""
            )
            inventario = []
            for row in cursor.fetchall():
                inventario.append({
                    'medicamento_id': row[0],
                    'medicamento': row[1],
                    'principio_activo': row[2],
                    'lote_id': row[3],
                    'numero_lote': row[4],
                    'cantidad_actual': row[5],
                    'precio_unitario': float(row[6]),
                    'fecha_caducidad': row[7],
                    'version': row[8],
                    'estado_caducidad': row[9]
                })
            return inventario

    @staticmethod
    def obtener_por_id(lote_id):
        """Obtener lote por ID con información del medicamento"""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                """SELECT l.id, l.medicamento_id, m.nombre, l.numero_lote, 
                          l.cantidad_actual, l.precio_unitario, l.fecha_fabricacion,
                          l.fecha_caducidad, l.proveedor, l.version
                   FROM lotes_medicamentos l
                   JOIN medicamentos m ON l.medicamento_id = m.id
                   WHERE l.id = %s""",
                (lote_id,)
            )
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'medicamento_id': row[1],
                    'medicamento_nombre': row[2],
                    'numero_lote': row[3],
                    'cantidad_actual': row[4],
                    'precio_unitario': float(row[5]),
                    'fecha_fabricacion': row[6],
                    'fecha_caducidad': row[7],
                    'proveedor': row[8],
                    'version': row[9]
                }
        return None

    @staticmethod
    def actualizar_cantidad_optimista(lote_id, nueva_cantidad, version_esperada):
        """
        Actualizar cantidad con control de concurrencia optimista.
        Retorna True si tuvo éxito, False si hubo conflicto de versión.
        """
        with get_db_cursor() as cursor:
            # Intentar actualizar solo si la versión coincide
            cursor.execute(
                """UPDATE lotes_medicamentos 
                   SET cantidad_actual = %s, version = version + 1
                   WHERE id = %s AND version = %s""",
                (nueva_cantidad, lote_id, version_esperada)
            )

            # Verificar si se actualizó alguna fila
            return cursor.rowcount > 0

    @staticmethod
    def actualizar_cantidad_pesimista(lote_id, nueva_cantidad):
        """
        Actualizar cantidad con control de concurrencia pesimista (row lock).
        Usa SELECT FOR UPDATE para bloquear la fila.
        """
        with get_db_cursor() as cursor:
            # Bloquear la fila para evitar modificaciones concurrentes
            cursor.execute(
                """SELECT cantidad_actual, version FROM lotes_medicamentos 
                   WHERE id = %s FOR UPDATE""",
                (lote_id,)
            )
            result = cursor.fetchone()

            if result:
                cursor.execute(
                    """UPDATE lotes_medicamentos 
                       SET cantidad_actual = %s, version = version + 1
                       WHERE id = %s""",
                    (nueva_cantidad, lote_id)
                )
                return True
        return False

    @staticmethod
    def actualizar(lote_id, numero_lote, cantidad_actual, precio_unitario, fecha_fabricacion, fecha_caducidad, proveedor):
        """Actualizar lote de medicamento"""
        with get_db_cursor() as cursor:
            cursor.execute(
                """UPDATE lotes_medicamentos 
                   SET numero_lote = %s, cantidad_actual = %s, precio_unitario = %s,
                       fecha_fabricacion = %s, fecha_caducidad = %s, proveedor = %s,
                       version = version + 1
                   WHERE id = %s""",
                (numero_lote, cantidad_actual, precio_unitario, fecha_fabricacion,
                 fecha_caducidad, proveedor, lote_id)
            )
            return cursor.rowcount > 0

    @staticmethod
    def eliminar(lote_id):
        """Eliminar lote (solo si no tiene transacciones)"""
        with get_db_cursor() as cursor:
            cursor.execute("DELETE FROM lotes_medicamentos WHERE id = %s", (lote_id,))
            return cursor.rowcount > 0

class Transaccion:
    """Modelo para transacciones de compra/venta"""

    @staticmethod
    def registrar_venta(lote_id, usuario_id, cantidad, usar_optimista=True):
        """
        Registrar una venta con control de concurrencia.
        Retorna (exito, mensaje, transaccion_id)
        """
        try:
            with get_db_cursor() as cursor:
                # Obtener información del lote
                if usar_optimista:
                    cursor.execute(
                        """SELECT cantidad_actual, precio_unitario, version 
                           FROM lotes_medicamentos WHERE id = %s""",
                        (lote_id,)
                    )
                else:
                    # Lock pesimista
                    cursor.execute(
                        """SELECT cantidad_actual, precio_unitario, version 
                           FROM lotes_medicamentos WHERE id = %s FOR UPDATE""",
                        (lote_id,)
                    )

                result = cursor.fetchone()
                if not result:
                    return (False, "Lote no encontrado", None)

                cantidad_actual, precio_unitario, version = result

                if cantidad_actual < cantidad:
                    return (False, f"Stock insuficiente. Disponible: {cantidad_actual}", None)

                nueva_cantidad = cantidad_actual - cantidad
                precio_total = float(precio_unitario) * cantidad

                # Actualizar cantidad según el método de concurrencia
                if usar_optimista:
                    exito = LoteMedicamento.actualizar_cantidad_optimista(
                        lote_id, nueva_cantidad, version
                    )
                    if not exito:
                        return (False, "Conflicto de concurrencia. Intente nuevamente.", None)
                else:
                    cursor.execute(
                        """UPDATE lotes_medicamentos 
                           SET cantidad_actual = %s, version = version + 1
                           WHERE id = %s""",
                        (nueva_cantidad, lote_id)
                    )

                # Registrar transacción
                cursor.execute(
                    """INSERT INTO transacciones 
                       (tipo, lote_id, usuario_id, cantidad, precio_total)
                       VALUES ('venta', %s, %s, %s, %s) RETURNING id""",
                    (lote_id, usuario_id, cantidad, precio_total)
                )
                transaccion_id = cursor.fetchone()[0]

                return (True, "Venta registrada exitosamente", transaccion_id)

        except psycopg2.Error as e:
            return (False, f"Error en la base de datos: {str(e)}", None)

    @staticmethod
    def registrar_compra(lote_id, usuario_id, cantidad):
        """Registrar una compra (incrementa el stock)"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """SELECT cantidad_actual, precio_unitario 
                       FROM lotes_medicamentos WHERE id = %s FOR UPDATE""",
                    (lote_id,)
                )
                result = cursor.fetchone()

                if not result:
                    return (False, "Lote no encontrado", None)

                cantidad_actual, precio_unitario = result
                nueva_cantidad = cantidad_actual + cantidad
                precio_total = float(precio_unitario) * cantidad

                cursor.execute(
                    """UPDATE lotes_medicamentos 
                       SET cantidad_actual = %s, version = version + 1
                       WHERE id = %s""",
                    (nueva_cantidad, lote_id)
                )

                cursor.execute(
                    """INSERT INTO transacciones 
                       (tipo, lote_id, usuario_id, cantidad, precio_total)
                       VALUES ('compra', %s, %s, %s, %s) RETURNING id""",
                    (lote_id, usuario_id, cantidad, precio_total)
                )
                transaccion_id = cursor.fetchone()[0]

                return (True, "Compra registrada exitosamente", transaccion_id)
        except psycopg2.Error as e:
            return (False, f"Error: {str(e)}", None)

    @staticmethod
    def listar_historial(limite=50):
        """Listar historial de transacciones"""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                """SELECT t.id, t.tipo, m.nombre as medicamento, l.numero_lote,
                          u.nombre_completo as usuario, t.cantidad, t.precio_total,
                          t.fecha_transaccion
                   FROM transacciones t
                   JOIN lotes_medicamentos l ON t.lote_id = l.id
                   JOIN medicamentos m ON l.medicamento_id = m.id
                   JOIN usuarios u ON t.usuario_id = u.id
                   ORDER BY t.fecha_transaccion DESC
                   LIMIT %s""",
                (limite,)
            )
            transacciones = []
            for row in cursor.fetchall():
                transacciones.append({
                    'id': row[0],
                    'tipo': row[1],
                    'medicamento': row[2],
                    'numero_lote': row[3],
                    'usuario': row[4],
                    'cantidad': row[5],
                    'precio_total': float(row[6]),
                    'fecha': row[7]
                })
            return transacciones

