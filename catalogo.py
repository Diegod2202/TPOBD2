from datetime import datetime
from uuid import uuid4
from db_connection import DatabaseConnection
from mongodb_config import get_mongodb_connection
from bson import ObjectId
from user_sessions import get_user_session

db = get_mongodb_connection()


def verificar_sesion(session_id):
    session = get_user_session(session_id)
    if session and session['logout_time'] is None:
        return session['user_id']
    return None

def agregar_producto(session_id, producto):
    operador = verificar_sesion(session_id)
    if not operador:
        return "Sesión no válida o expirada", 401

    producto['fecha_creacion'] = datetime.now()
    producto_id = db.productos.insert_one(producto).inserted_id
    registrar_actividad('agregar_producto', producto_id, None, operador)
    return str(producto_id), 201

def actualizar_producto(session_id, producto_id, datos_actualizados):
    operador = verificar_sesion(session_id)
    if not operador:
        return "Sesión no válida o expirada", 401

    db.productos.update_one({'_id': ObjectId(producto_id)}, {'$set': datos_actualizados})
    registrar_actividad('actualizar_producto', producto_id, datos_actualizados, operador)
    return "Producto actualizado", 200

def agregar_comentario(session_id, producto_id, comentario):
    operador = verificar_sesion(session_id)
    if not operador:
        return "Sesión no válida o expirada", 401

    comentario['usuario_id'] = operador
    comentario['fecha'] = datetime.utcnow()
    db.productos.update_one({'_id': ObjectId(producto_id)}, {'$push': {'comentarios': comentario}})
    registrar_actividad('agregar_comentario', producto_id, comentario, operador)
    return "Comentario agregado", 201

def actualizar_precio(session_id, producto_id, nuevo_precio):
    operador = verificar_sesion(session_id)
    if not operador:
        return "Sesión no válida o expirada", 401

    db.productos.update_one({'_id': ObjectId(producto_id)}, {'$set': {'precio': nuevo_precio}})
    registrar_actividad('actualizar_precio', producto_id, {'precio': nuevo_precio}, operador)
    return "Precio actualizado", 200

def registrar_actividad(tipo, producto_id, detalles, operador):
    actividad = {
        'tipo': tipo,
        'producto_id': ObjectId(producto_id),
        'detalles': detalles,
        'operador': operador,
        'fecha': datetime.utcnow()
    }
    db.actividades.insert_one(actividad)

def obtener_producto(producto_id):
    return db.productos.find_one({'_id': ObjectId(producto_id)})

def obtener_actividades():
    return list(db.actividades.find())
