# create_tables.py
from db_connection import DatabaseConnection

def create_tables(db_connection):
    commands = [
        """
        CREATE TABLE usuarios (
            id INT PRIMARY KEY IDENTITY(1,1),
            nombre VARCHAR(100),
            email VARCHAR(255) UNIQUE,
            direccion TEXT,
            telefono VARCHAR(15)
        )
        """,
        """
        CREATE TABLE facturas (
            id INT PRIMARY KEY IDENTITY(1,1),
            usuario_id INT NOT NULL,
            fecha DATETIME DEFAULT GETDATE(),
            total DECIMAL(10, 2),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
        """,
        """
        CREATE TABLE detalles_factura (
            id INT PRIMARY KEY IDENTITY(1,1),
            factura_id INT NOT NULL,
            producto VARCHAR(100),
            cantidad INT,
            precio_unitario DECIMAL(10, 2),
            FOREIGN KEY (factura_id) REFERENCES facturas(id)
        )
        """,
        """
        CREATE TABLE pagos (
            id INT PRIMARY KEY IDENTITY(1,1),
            factura_id INT UNIQUE NOT NULL,
            monto DECIMAL(10, 2),
            fecha DATETIME DEFAULT GETDATE(),
            metodo_pago VARCHAR(50),
            FOREIGN KEY (factura_id) REFERENCES facturas(id)
        )
        """,
        """
        CREATE TABLE user_activity (
            user_id INT PRIMARY KEY,
            total_minutes INT,
            category VARCHAR(50)
            FOREIGN KEY (user_id) REFERENCES usuarios(id)
        )
        """
    ]

    conn = None
    try:
        conn = db_connection.get_sql_server_connection()
        cursor = conn.cursor()
        for command in commands:
            cursor.execute(command)
        print("Tablas creadas con éxito.")
    except Exception as error:
        print(f"Error al crear las tablas: {error}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    db_connection = DatabaseConnection('config.json')
    create_tables(db_connection)
