# app.py
from flask import Flask, request, jsonify, make_response
from user_sessions import start_user_session, end_user_session, get_user_session, verify_user_credentials
from shopping_cart import add_to_cart, remove_from_cart, update_cart_item, get_cart, revert_cart_changes, get_product_ids_in_cart
from db_connection import DatabaseConnection
from catalogo import agregar_producto, actualizar_producto, agregar_comentario, actualizar_precio, obtener_producto, obtener_actividades
app = Flask(__name__)
db_connection = DatabaseConnection('config.json')

#login - logout GESTION DE SESIONES MONGO / SQLSERVER

def get_session_id_from_cookies():
    return request.cookies.get('session_id')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user_id = verify_user_credentials(username, password, db_connection)

    if not user_id:
        return jsonify({'mensaje': 'Credenciales no válidas'}), 401

    session_id = start_user_session(user_id, db_connection)
    
    if session_id == "El usuario no existe en SQL Server.":
        return jsonify({'mensaje': 'El usuario no existe en SQL Server.'}), 404

    # Crea la respuesta y establece la cookie
    response = make_response(jsonify({'mensaje': 'Sesión iniciada'}))
    response.set_cookie('session_id', session_id, httponly=True)
    return response

@app.route('/logout', methods=['POST'])
def logout():
    session_id = get_session_id_from_cookies()
    if not session_id:
        return jsonify({'mensaje': 'Sesión no válida o expirada'}), 401

    resultado = end_user_session(session_id, db_connection)
    
    if resultado == "Session not found.":
        return jsonify({'mensaje': 'Sesión no encontrada'}), 404

    response = make_response(jsonify({'mensaje': 'Sesión cerrada'}))
    response.set_cookie('session_id', '', expires=0)
    return response


@app.route('/get_session', methods=['GET'])
def get_session():
    session_id = get_session_id_from_cookies()
    if not session_id:
        return jsonify({"error": "Sesión no válida o expirada"}), 401

    session = get_user_session(session_id)
    if session:
        session.pop('_id')  # Eliminar el campo _id que no es serializable
        return jsonify(session)
    else:
        return jsonify({"error": "Sesión no encontrada"}), 404


# REDIS CARRITO

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart_endpoint():
    session_id = get_session_id_from_cookies()
    if not session_id:
        return jsonify({"error": "Sesión no válida o expirada"}), 401
    user_id = get_user_session(session_id)['user_id']
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    if product_id and quantity:
        cart = add_to_cart(user_id, product_id, quantity)
        return jsonify(cart), 200
    else:
        return jsonify({'error': 'Falta ingresar product_id, o quantity.'}), 400

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart_endpoint():
    session_id = get_session_id_from_cookies()
    if not session_id:
        return jsonify({"error": "Sesión no válida o expirada"}), 401
    user_id = get_user_session(session_id)['user_id']
    data = request.json
    product_id = data.get('product_id')
    if product_id:
        cart = remove_from_cart(user_id, product_id)
        return jsonify(cart), 200
    else:
        return jsonify({'error': 'Falta ingresar product_id.'}), 400

@app.route('/update_cart_item', methods=['POST'])
def update_cart_item_endpoint():
    session_id = get_session_id_from_cookies()
    if not session_id:
        return jsonify({"error": "Sesión no válida o expirada"}), 401
    user_id = get_user_session(session_id)['user_id']
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    if product_id and quantity:
        cart = update_cart_item(user_id, product_id, quantity)
        return jsonify(cart), 200
    else:
        return jsonify({'error': 'Falta ingresar product_id, o quantity.'}), 400

@app.route('/get_cart', methods=['GET'])
def get_cart_endpoint():
    session_id = get_session_id_from_cookies()
    if not session_id:
        return jsonify({"error": "Sesión no válida o expirada"}), 401
    user_id = get_user_session(session_id)['user_id']
    if user_id:
        cart = get_cart(user_id)
        return jsonify(cart)
    else:
        return jsonify({'error': 'Falta ingresar user_id.'}), 400

@app.route('/revert_cart_changes', methods=['POST'])
def revert_cart_changes_endpoint():
    session_id = get_session_id_from_cookies()
    if not session_id:
        return jsonify({"error": "Sesión no válida o expirada"}), 401
    user_id = get_user_session(session_id)['user_id']
    if user_id:
        cart = revert_cart_changes(user_id)
        return jsonify(cart), 200
    else:
        return jsonify({'error': 'Falta ingresar user_id.'}), 400

@app.route('/get_product_ids_in_cart', methods=['GET'])
def get_product_ids_in_cart_endpoint():
    session_id = get_session_id_from_cookies()
    if not session_id:
        return jsonify({"error": "Sesión no válida o expirada"}), 401
    user_id = get_user_session(session_id)['user_id']
    if user_id:
        product_ids = get_product_ids_in_cart(user_id)
        return jsonify(product_ids), 200
    else:
        return jsonify({'error': 'Falta ingresar user_id.'}), 400


#CATALOGO MONGO

@app.route('/producto', methods=['POST'])
def agregar_producto_catalogo():
    session_id = get_session_id_from_cookies()
    if not session_id:
        return jsonify({'mensaje': 'Sesión no válida o expirada'}), 401
    producto = request.json
    resultado, status = agregar_producto(session_id, producto)
    return jsonify({'mensaje': resultado}), status


@app.route('/producto/<id>', methods=['PUT'])
def actualizar_producto_catalogo(id):
    session_id = get_session_id_from_cookies()
    if not session_id:
        return jsonify({'mensaje': 'Sesión no válida o expirada'}), 401
    if id:
        datos_actualizados = request.json
        actualizar_producto(session_id, id, datos_actualizados)
        return jsonify({'mensaje': 'Producto actualizado'}), 200
    else:
        return jsonify({'error': 'Falta ingresar el id de la sesion o el id del producto.'}), 400


@app.route('/producto/<id>/comentario', methods=['POST'])
def agregar_comentario_catalogo(id):
    session_id = get_session_id_from_cookies()
    if not session_id:
        return jsonify({'mensaje': 'Sesión no válida o expirada'}), 401
    if id:
        comentario = request.json
        resultado, status = agregar_comentario(session_id, id, comentario)
        return jsonify({'mensaje': resultado}), status
    else:
        return jsonify({'error': 'Falta ingresar el id de la sesion o el id del producto.'}), 400

@app.route('/producto/<id>/precio', methods=['PUT'])
def actualizar_precio_catalogo(id):
    session_id = get_session_id_from_cookies()
    if not session_id:
        return jsonify({'mensaje': 'Sesión no válida o expirada'}), 401
    if session_id and id:
        nuevo_precio = request.json.get('precio')
        resultado, status = actualizar_precio(session_id, id, nuevo_precio)
        return jsonify({'mensaje': resultado}), status
    else:
        return jsonify({'error': 'Falta ingresar el id de la sesion o el id del producto.'}), 400

@app.route('/producto/<id>', methods=['GET'])
def obtener_producto_catalogo(id):
    if id:
        producto = obtener_producto(id)
        if producto:
            producto['_id'] = str(producto['_id'])
            return jsonify(producto), 200
        else:
            return jsonify({'mensaje': 'Producto no encontrado'}), 404
    else:
        return jsonify({'error': 'Falta ingresar el id del producto.'}), 400


@app.route('/actividades', methods=['GET'])
def obtener_actividades_catalogo():
    actividades = obtener_actividades()
    for actividad in actividades:
        actividad['_id'] = str(actividad['_id'])
        actividad['producto_id'] = str(actividad['producto_id'])
    return jsonify(actividades), 200

if __name__ == '__main__':
    app.run(debug=True)
