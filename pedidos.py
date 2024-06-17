import json
from datetime import datetime
from bson import ObjectId
from mongodb_config import get_mongodb_connection
from redis_config import get_redis_connection

redis_conn = get_redis_connection()
db = get_mongodb_connection()


def calcular_descuento(total):
    return total * 0.1 if total > 100 else 0

def calcular_impuestos(total):
    return total * 0.2

def convertir_carrito_a_pedido(user_id, db_connection):
    cart_key = f"cart:{user_id}"
    cart = redis_conn.hget(cart_key, "actual")
    if not cart:
        return "Carrito no encontrado", 404

    cart = json.loads(cart)

    total = 0
    detalles_pedido = []
    # Obtener precios de los productos desde MongoDB
    for product_id, quantity in cart.items():
        producto = db.productos.find_one({'_id': ObjectId(product_id)})
        if not producto:
            return f"Producto {product_id} no encontrado", 404
        precio_unitario = producto['precio']
        subtotal = precio_unitario * quantity
        total += subtotal

        # Construir detalle para MongoDB
        detalle = {
            "producto_id": str(product_id),
            "nombre": producto['nombre'],
            "cantidad": quantity,
            "precio_unitario": precio_unitario,
            "subtotal": subtotal
        }
        detalles_pedido.append(detalle)

    # Calcular descuento, impuestos y total con impuestos
    descuento = calcular_descuento(total)
    impuestos = calcular_impuestos(total - descuento)
    total_con_impuestos = total - descuento + impuestos

    # Conexión a SQL Server
    conn = db_connection.get_sql_server_connection()
    try:
        cursor = conn.cursor()
        # Insertar en pedidos (SQL Server)
        cursor.execute("""
                INSERT INTO pedidos (usuario_id, fecha_pedido, subtotal, descuento, impuestos, total)
                OUTPUT INSERTED.pedido_id
                VALUES (?, ?, ?, ?, ?, ?);
                """, (user_id, datetime.now(), total, descuento, impuestos, total_con_impuestos))

        pedido_id = cursor.fetchone()[0]  # El resultado es un solo valor
        print(pedido_id)
        # Commit en SQL Server
        conn.commit()
        
        # Eliminar el carrito después de convertirlo en pedido
        redis_conn.delete(cart_key)
        cursor.execute("SELECT usuario_id, nombre, direccion, dni FROM usuarios WHERE usuario_id = ?", (user_id,))
        user_info = cursor.fetchone()
        usurio_id, name, address, identity_document = user_info
        user_info = {
            "id" : usurio_id,
            "nombre": name,
            "direccion":  address,
            "DNI": identity_document
        }
        # Insertar pedido en MongoDB
        pedido = {
            "pedido_id": pedido_id,
            "usuario_id": user_id,
            "fecha_pedido": datetime.now(),
            "detalles_cliente": user_info,
            "detalles_pedido": detalles_pedido
        }
        pedido_id_mongo = db.pedidos.insert_one(pedido).inserted_id

        return str(pedido_id), 201

    except Exception as e:
        conn.rollback()
        return str(e), 500

    finally:
        conn.close()

def facturar_pedido(pedido_id, forma_pago, db_connection):
    conn = db_connection.get_sql_server_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT total FROM pedidos WHERE pedido_id = ?", (pedido_id,))
        total = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO facturas (pedido_id, fecha_factura, total, forma_pago)
            OUTPUT INSERTED.factura_id
            VALUES (?, ?, ?, ?)
        """, (pedido_id, datetime.now(), total, forma_pago))
        
        factura_id = cursor.fetchone()[0]
        conn.commit()
        return factura_id, 201
    except Exception as e:
        conn.rollback()
        return 'No existe el pedido: ' + pedido_id, 500
    finally:
        conn.close()