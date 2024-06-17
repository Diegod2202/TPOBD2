import json
from redis_config import get_redis_connection
from mongodb_config import get_mongodb_connection
from bson import ObjectId

redis_conn = get_redis_connection()
db = get_mongodb_connection()

def verificar_producto(producto_id):
    return db.productos.find_one({'_id': ObjectId(producto_id)}) is not None

def add_to_cart(user_id, product_id, quantity):
    if not verificar_producto(product_id):
        return "Producto no existe en el catálogo", 404
    
    cart_key = f"cart:{user_id}"
    # Obtener el carrito actual del hash
    cart = redis_conn.hget(cart_key, "actual")
    if cart:
        cart = json.loads(cart)
        # Guardar el carrito original si no está guardado ya
        #if redis_conn.hexists(cart_key, "original"):
        redis_conn.hset(cart_key, "original", json.dumps(cart))
    else:
        cart = {}
    
    # Actualizar la cantidad del producto en el carrito
    if product_id in cart:
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity
    
    redis_conn.hset(cart_key, "actual", json.dumps(cart))
    return cart

def remove_from_cart(user_id, product_id):
    cart_key = f"cart:{user_id}"
    
    # Obtener el carrito actual del hash
    cart = redis_conn.hget(cart_key, "actual")
    if cart:
        cart = json.loads(cart)
        # Guardar el carrito original si no está guardado ya
        #if redis_conn.hexists(cart_key, "original"):
        redis_conn.hset(cart_key, "original", json.dumps(cart))
        # Eliminar el producto del carrito
        if product_id in cart:
            del cart[product_id]
            redis_conn.hset(cart_key, "actual", json.dumps(cart))
    return cart

def update_cart_item(user_id, product_id, quantity):
    cart_key = f"cart:{user_id}"
    
    # Obtener el carrito actual del hash
    cart = redis_conn.hget(cart_key, "actual")
    if cart:
        cart = json.loads(cart)
        # Guardar el carrito original si no está guardado ya
        #if redis_conn.hexists(cart_key, "original"):
        redis_conn.hset(cart_key, "original", json.dumps(cart))
        # Actualizar la cantidad del producto en el carrito
        cart[product_id] = quantity
        redis_conn.hset(cart_key, "actual", json.dumps(cart))
    return cart

def get_cart(user_id):
    cart_key = f"cart:{user_id}"
    cart = redis_conn.hget(cart_key, "actual")
    if cart:
        return json.loads(cart)
    return {}

def revert_cart_changes(user_id):
    cart_key = f"cart:{user_id}"
    
    # Obtener el carrito original del hash
    original_cart = redis_conn.hget(cart_key, "original")
    if original_cart:
        redis_conn.hset(cart_key, "actual", original_cart)
        return json.loads(original_cart)
    return {}

def get_product_ids_in_cart(user_id):
    cart = get_cart(user_id)
    product_ids = list(cart.keys())  # Obtener todos los IDs de productos en el carrito
    return product_ids