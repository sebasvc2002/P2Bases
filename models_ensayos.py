from database import get_ensayos_collection
from datetime import datetime
from bson import ObjectId

class EnsayoClinico:
    """
    Modelo para ensayos clínicos en MongoDB.
    Usa documentos flexibles para almacenar datos semiestructurados.
    """

    @staticmethod
    def crear(medicamento_id, fase, titulo, investigador_principal, datos_ensayo):
        """
        Crear nuevo ensayo clínico.
        datos_ensayo es un diccionario flexible que puede contener cualquier estructura.
        """
        ensayos = get_ensayos_collection()

        documento = {
            'medicamento_id': medicamento_id,
            'fase': fase,  # Fase I, II, III, IV
            'titulo': titulo,
            'investigador_principal': investigador_principal,
            'fecha_inicio': datos_ensayo.get('fecha_inicio', datetime.utcnow()),
            'fecha_fin': datos_ensayo.get('fecha_fin'),
            'estado': datos_ensayo.get('estado', 'en_progreso'),  # en_progreso, completado, suspendido
            'participantes': datos_ensayo.get('participantes', {}),
            'resultados': datos_ensayo.get('resultados', {}),
            'efectos_secundarios': datos_ensayo.get('efectos_secundarios', []),
            'notas_investigacion': datos_ensayo.get('notas_investigacion', []),
            'datos_adicionales': datos_ensayo.get('datos_adicionales', {}),
            'fecha_creacion': datetime.utcnow(),
            'ultima_modificacion': datetime.utcnow()
        }

        result = ensayos.insert_one(documento)
        return str(result.inserted_id)

    @staticmethod
    def listar(filtros=None):
        """Listar ensayos clínicos con filtros opcionales"""
        ensayos = get_ensayos_collection()

        query = {}
        if filtros:
            if 'medicamento_id' in filtros:
                query['medicamento_id'] = filtros['medicamento_id']
            if 'fase' in filtros:
                query['fase'] = filtros['fase']
            if 'estado' in filtros:
                query['estado'] = filtros['estado']

        resultados = []
        for doc in ensayos.find(query).sort('fecha_inicio', -1):
            doc['_id'] = str(doc['_id'])
            resultados.append(doc)

        return resultados

    @staticmethod
    def obtener_por_id(ensayo_id):
        """Obtener ensayo clínico por ID"""
        ensayos = get_ensayos_collection()

        try:
            doc = ensayos.find_one({'_id': ObjectId(ensayo_id)})
            if doc:
                doc['_id'] = str(doc['_id'])
                return doc
        except Exception:
            pass

        return None

    @staticmethod
    def actualizar(ensayo_id, datos_actualizacion):
        """Actualizar ensayo clínico"""
        ensayos = get_ensayos_collection()

        datos_actualizacion['ultima_modificacion'] = datetime.utcnow()

        try:
            result = ensayos.update_one(
                {'_id': ObjectId(ensayo_id)},
                {'$set': datos_actualizacion}
            )
            return result.modified_count > 0
        except Exception:
            return False

    @staticmethod
    def agregar_efecto_secundario(ensayo_id, efecto_secundario):
        """Agregar efecto secundario observado al ensayo"""
        ensayos = get_ensayos_collection()

        efecto = {
            'descripcion': efecto_secundario['descripcion'],
            'severidad': efecto_secundario.get('severidad', 'leve'),
            'frecuencia': efecto_secundario.get('frecuencia', 'rara'),
            'fecha_reporte': datetime.utcnow(),
            'detalles': efecto_secundario.get('detalles', {})
        }

        try:
            result = ensayos.update_one(
                {'_id': ObjectId(ensayo_id)},
                {
                    '$push': {'efectos_secundarios': efecto},
                    '$set': {'ultima_modificacion': datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception:
            return False

    @staticmethod
    def agregar_nota(ensayo_id, nota):
        """Agregar nota de investigación al ensayo"""
        ensayos = get_ensayos_collection()

        nota_documento = {
            'texto': nota['texto'],
            'autor': nota.get('autor', 'Anónimo'),
            'fecha': datetime.utcnow(),
            'categoria': nota.get('categoria', 'general')
        }

        try:
            result = ensayos.update_one(
                {'_id': ObjectId(ensayo_id)},
                {
                    '$push': {'notas_investigacion': nota_documento},
                    '$set': {'ultima_modificacion': datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception:
            return False

    @staticmethod
    def buscar_por_texto(texto_busqueda):
        """Búsqueda de texto en ensayos clínicos"""
        ensayos = get_ensayos_collection()

        query = {
            '$or': [
                {'titulo': {'$regex': texto_busqueda, '$options': 'i'}},
                {'investigador_principal': {'$regex': texto_busqueda, '$options': 'i'}},
                {'fase': {'$regex': texto_busqueda, '$options': 'i'}}
            ]
        }

        resultados = []
        for doc in ensayos.find(query):
            doc['_id'] = str(doc['_id'])
            resultados.append(doc)

        return resultados

    @staticmethod
    def eliminar(ensayo_id):
        """Eliminar ensayo clínico"""
        ensayos = get_ensayos_collection()

        try:
            result = ensayos.delete_one({'_id': ObjectId(ensayo_id)})
            return result.deleted_count > 0
        except Exception:
            return False

