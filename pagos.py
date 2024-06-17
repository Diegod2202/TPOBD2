from datetime import datetime

def registrar_pago(factura_id, medio_pago, operador, monto, db_connection):
    conn = db_connection.get_sql_server_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM pagos WHERE factura_id = ?", (factura_id,))
        if cursor.fetchone()[0] > 0:
            return f"La factura {factura_id} ya ha sido pagada previamente", 400
        
        cursor.execute("SELECT total FROM facturas WHERE factura_id = ?", (factura_id,))
        total = cursor.fetchone()[0]
        if not total:
            return "Factura no encontrada", 404
        if f"{monto:.2f}" != f"{total:.2f}":
            return "El monto a pagar debe ser igual al total de la factura", 400

        cursor.execute("""
            INSERT INTO pagos (factura_id, medio_pago, operador, fecha_pago, monto)
            OUTPUT INSERTED.pago_id
            VALUES (?, ?, ?, ?, ?)
        """, (factura_id, medio_pago, operador, datetime.now(), monto))
        
        pago_id = cursor.fetchone()[0]
        conn.commit()
        return f"Pago registrado correctamente {pago_id}", 201
    except Exception as e:
        conn.rollback()
        return str(e), 500
    finally:
        conn.close()

def registrar_pago_multiple(facturas, medio_pago, operador, db_connection):
    conn = db_connection.get_sql_server_connection()
    try:
        cursor = conn.cursor()
        pagos_ids = []
        for factura in facturas:
            factura_id = factura['factura_id']
            monto = factura['monto']

            cursor.execute("SELECT COUNT(*) FROM pagos WHERE factura_id = ?", (factura_id,))
            if cursor.fetchone()[0] > 0:
                print(f"La factura {factura_id} ya ha sido pagada previamente")
                continue  # Saltar a la siguiente factura en el ciclo

            cursor.execute("SELECT total FROM facturas WHERE factura_id = ?", (factura_id,))
            total = cursor.fetchone()[0]
            if not factura:
                return f"Factura {factura_id} no encontrada", 404
            if f"{monto:.2f}" != f"{total:.2f}":
                print(total, monto)
                print(round(monto, 2), round(total, 2))
                return f"El monto: {monto} a pagar debe ser igual al total de la factura {total}", 400
            cursor.execute("""
                INSERT INTO pagos (factura_id, medio_pago, operador, fecha_pago, monto)
                OUTPUT INSERTED.pago_id
                VALUES (?, ?, ?, ?, ?)
            """, (factura_id, medio_pago, operador, datetime.now(), monto))
            pago_id = cursor.fetchone()[0]
            pagos_ids.append(pago_id)
        conn.commit()
        return f"Pago registrado correctamente {pagos_ids}", 201
    except Exception as e:
        conn.rollback()
        return str(e), 500
    finally:
        conn.close()
