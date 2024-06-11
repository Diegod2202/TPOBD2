from datetime import datetime
from uuid import uuid4
from db_connection import DatabaseConnection
from mongodb_config import get_mongodb_connection

db = get_mongodb_connection()

def verify_user_credentials(username, password, db_connection):
    conn = db_connection.get_sql_server_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM user_log WHERE usuario_nombre = ? AND contraseña = ?", (username, password))
        user = cursor.fetchone()
        if user:
            return user[0]
        else:
            return None
    finally:
        conn.close()

def start_user_session(user_id, db_connection):
    conn = db_connection.get_sql_server_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, direccion, dni FROM usuarios WHERE usuario_id = ?", (user_id,))
        user_info = cursor.fetchone()
        if not user_info:
            return "El usuario no existe en SQL Server."

        name, address, identity_document = user_info

        session = {
            "user_id": user_id,
            "session_id": str(uuid4()),
            "name": name,
            "address": address,
            "identity_document": identity_document,
            "login_time": datetime.now(),
            "logout_time": None
        }
        db.user_sessions.insert_one(session)
        return session["session_id"]
    finally:
        conn.close()

def end_user_session(session_id, db_connection):
    session = db.user_sessions.find_one({"session_id": session_id})
    if session:
        login_time = session['login_time']
        logout_time = datetime.now()
        session_minutes = calculate_session_minutes(login_time, logout_time)

        db.user_sessions.update_one(
            {"session_id": session_id},
            {"$set": {"logout_time": logout_time}}
        )

        update_user_activity(session['user_id'], session_minutes, db_connection)
        return session_minutes
    else:
        return "Session not found."

def get_user_session(session_id):
    return db.user_sessions.find_one({"session_id": session_id})

def calculate_session_minutes(login_time, logout_time):
    return int((logout_time - login_time).total_seconds() / 60)

def update_user_activity(user_id, session_minutes, db_connection):
    conn = db_connection.get_sql_server_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT total_minutes FROM user_activity WHERE usuario_id = ?", (user_id,))
        result = cursor.fetchone()

        if result:
            new_total_minutes = result[0] + session_minutes
            new_category = categorize_user(new_total_minutes)
            cursor.execute(
                "UPDATE user_activity SET total_minutes = ?, category = ? WHERE usuario_id = ?",
                (new_total_minutes, new_category, user_id)
            )
        else:
            new_category = categorize_user(session_minutes)
            cursor.execute(
                "INSERT INTO user_activity (usuario_id, total_minutes, category) VALUES (?, ?, ?)",
                (user_id, session_minutes, new_category)
            )

        conn.commit()
    except Exception as e:
        print(f"Error al actualizar la actividad del usuario: {e}")
    finally:
        conn.close()

def categorize_user(total_minutes):
    if total_minutes > 240:
        return "TOP"
    elif total_minutes > 120:
        return "MEDIUM"
    else:
        return "LOW"
