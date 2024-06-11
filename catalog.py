from mongodb_config import get_mongodb_connection
from datetime import datetime


def add_product(product_id, nombre, descripcion, precio, imagenes, comentarios, videos, actualizado_por):
    db = get_mongodb_connection()
    producto = {
        "product_id": product_id,
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": precio,
        "imagenes": imagenes,
        "comentarios": comentarios,
        "videos": videos,
        "actualizado_por": actualizado_por,
        "fecha_actualizacion": datetime.now()
    }
    db.catalogo.insert_one(producto)
    return "Producto añadido con éxito."