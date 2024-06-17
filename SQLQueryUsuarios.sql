/****** Script for SelectTopNRows command from SSMS  ******/
 CREATE TABLE user_log (
            id INT PRIMARY KEY IDENTITY(1,1),
            usuario_nombre Varchar(10) NOT NULL,
            contraseña INT NOT NULL,
        )

CREATE TABLE usuarios (
            usuario_id INT PRIMARY KEY,
            nombre VARCHAR(100),
            email VARCHAR(255) UNIQUE,
            direccion TEXT,
            telefono VARCHAR(15),
			dni Varchar(8)
			FOREIGN KEY (usuario_id) REFERENCES user_log(id)

        )
CREATE TABLE user_activity (
            usuario_id INT PRIMARY KEY,
            total_minutes INT,
            category VARCHAR(50)
            FOREIGN KEY (usuario_id) REFERENCES user_log(id)
        )
CREATE TABLE pedidos (
    pedido_id INT PRIMARY KEY IDENTITY(1,1),
    usuario_id INT,
    fecha_pedido DATETIME,
    subtotal DECIMAL(10, 2),
    descuento DECIMAL(10, 2),
    impuestos DECIMAL(10, 2),
    total DECIMAL(15, 2),
    FOREIGN KEY (usuario_id) REFERENCES user_log(id)
);

CREATE TABLE facturas (
    factura_id INT PRIMARY KEY IDENTITY(1,1),
    pedido_id INT,
    fecha_factura DATETIME,
    total DECIMAL(18, 2),
    forma_pago VARCHAR(50),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(pedido_id)
);
CREATE TABLE pagos (
    pago_id INT PRIMARY KEY IDENTITY(1,1),
    factura_id INT,
    medio_pago VARCHAR(50),
    operador VARCHAR(100),
    fecha_pago DATETIME,
    monto DECIMAL(18, 2),
    FOREIGN KEY (factura_id) REFERENCES facturas(factura_id)
);


INSERT INTO user_log (usuario_nombre, contraseña)
VALUES ('jhon', '1234');


DECLARE @user_id INT;
SET @user_id = SCOPE_IDENTITY();

INSERT INTO usuarios (usuario_id, nombre, email, direccion, telefono, dni)
VALUES (@user_id, 'Jhon', 'email@ejemplo.com', 'Dirección Completa', '911546352', '12345678');
