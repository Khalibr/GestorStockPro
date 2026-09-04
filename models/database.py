import sqlite3
import hashlib

DB_NAME = "stock.db"

def conectar():
    """Establece y retorna una conexión a la base de datos local SQLite."""
    return sqlite3.connect(DB_NAME)

def hashear_password(password: str) -> str:
    """Genera un hash SHA-256 para no guardar contraseñas en texto plano."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def inicializar_base_de_datos():
    """Crea las tablas y asegura la existencia de un usuario demo."""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Tabla de productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            stock INTEGER NOT NULL,
            precio REAL NOT NULL
        )
    """)

    # Tabla de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Tabla de movimientos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tipo TEXT NOT NULL, -- 'INGRESO' o 'VENTA'
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            usuario TEXT NOT NULL,
            FOREIGN KEY (producto_id) REFERENCES productos (id)
        )
    """)

    # Tabla de configuración del comercio
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config_comercio (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            nombre_fantasia TEXT NOT NULL,
            direccion TEXT,
            telefono TEXT,
            cuit TEXT,
            leyenda TEXT
        )
    """)

    # Valores por defecto si la tabla está vacía
    cursor.execute("""
        INSERT OR IGNORE INTO config_comercio (id, nombre_fantasia, direccion, telefono, cuit, leyenda)
        VALUES (1, 'GESTOR STOCK PRO', 'Av. Central 1234', '+54 11 0000-0000', '20-12345678-9', '¡Gracias por su compra!')
    """)

    # Usuario demo inicial: admin / admin123
    usuario_demo = "admin"
    pass_demo_hash = hashear_password("admin123")

    cursor.execute("""
        INSERT OR IGNORE INTO usuarios (usuario, password)
        VALUES (?, ?)
    """, (usuario_demo, pass_demo_hash))
    
    conexion.commit()
    conexion.close()

def validar_credenciales(usuario: str, password_plana: str) -> bool:
    """Verifica si el usuario y la contraseña coinciden en la base de datos."""
    conexion = conectar()
    cursor = conexion.cursor()
    
    pass_hash = hashear_password(password_plana)
    
    cursor.execute("""
        SELECT id FROM usuarios 
        WHERE usuario = ? AND password = ?
    """, (usuario, pass_hash))
    
    resultado = cursor.fetchone()
    conexion.close()
    
    return resultado is not None

def obtener_productos():
    """Recupera todos los registros de la tabla productos."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, categoria, stock, precio FROM productos ORDER BY id DESC")
    productos = cursor.fetchall()
    conexion.close()
    return productos

def buscar_productos(termino: str):
    """Filtra productos por nombre o categoría."""
    conexion = conectar()
    cursor = conexion.cursor()
    query = """
        SELECT id, nombre, categoria, stock, precio 
        FROM productos 
        WHERE nombre LIKE ? OR categoria LIKE ?
        ORDER BY id DESC
    """
    cursor.execute(query, (f"%{termino}%", f"%{termino}%"))
    productos = cursor.fetchall()
    conexion.close()
    return productos

def insertar_producto(nombre: str, categoria: str, stock: int, precio: float) -> bool:
    """Inserta un nuevo producto en la base de datos."""
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO productos (nombre, categoria, stock, precio) VALUES (?, ?, ?, ?)",
            (nombre, categoria, stock, precio)
        )
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print(f"Error al insertar producto: {e}")
        return False


def actualizar_producto(id_prod: int, nombre: str, categoria: str, stock: int, precio: float) -> bool:
    """Modifica los datos de un producto existente."""
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute(
            """
            UPDATE productos 
            SET nombre = ?, categoria = ?, stock = ?, precio = ? 
            WHERE id = ?
            """,
            (nombre, categoria, stock, precio, id_prod)
        )
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print(f"Error al actualizar: {e}")
        return False


def eliminar_producto(id_prod: int) -> bool:
    """Elimina un producto por su ID."""
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE id = ?", (id_prod,))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print(f"Error al eliminar: {e}")
        return False

def reponer_stock(id_prod: int, cantidad_a_sumar: int, usuario: str = "admin") -> bool:
    """Incrementa las existencias y audita el movimiento."""
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE productos SET stock = stock + ? WHERE id = ?",
            (cantidad_a_sumar, id_prod)
        )
        conexion.commit()
        conexion.close()
        registrar_movimiento("INGRESO", id_prod, cantidad_a_sumar, usuario)
        return True
    except Exception as e:
        print(f"Error al reponer stock: {e}")
        return False

def registrar_movimiento(tipo: str, id_prod: int, cantidad: int, usuario: str) -> bool:
    """Registra una entrada o salida en el historial."""
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO movimientos (tipo, producto_id, cantidad, usuario) VALUES (?, ?, ?, ?)",
            (tipo, id_prod, cantidad, usuario)
        )
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print(f"Error al registrar movimiento: {e}")
        return False

def obtener_movimientos():
    """Recupera los movimientos cruzados con el nombre del producto."""
    conexion = conectar()
    cursor = conexion.cursor()
    query = """
        SELECT m.id, m.fecha, m.tipo, p.nombre, m.cantidad, m.usuario
        FROM movimientos m
        JOIN productos p ON m.producto_id = p.id
        ORDER BY m.id DESC
    """
    cursor.execute(query)
    movimientos = cursor.fetchall()
    conexion.close()
    return movimientos

def procesar_venta(items_carrito: list, usuario: str) -> tuple[bool, str, int]:
    """
    Procesa una venta compuesta por múltiples productos.
    items_carrito es una lista de diccionarios:
    [{'id': int, 'nombre': str, 'cantidad': int, 'precio': float, 'subtotal': float}]

    Retorna: (exito: bool, mensaje: str, id_venta: int)
    """
    if not items_carrito:
        return False, "El carrito está vacío.", 0

    conexion = conectar()
    cursor = conexion.cursor()

    try:
        # Iniciar transacción explícita
        cursor.execute("BEGIN TRANSACTION")

        # 1. Validar existencias de todos los items
        for item in items_carrito:
            cursor.execute("SELECT stock, nombre FROM productos WHERE id = ?", (item['id'],))
            resultado = cursor.fetchone()
            if not resultado:
                conexion.rollback()
                conexion.close()
                return False, f"El producto {item['nombre']} ya no existe.", 0

            stock_actual, nombre = resultado
            if stock_actual < item['cantidad']:
                conexion.rollback()
                conexion.close()
                return False, f"Stock insuficiente para '{nombre}'. Disponible: {stock_actual}", 0

    # 2. Descontar stock y registrar movimiento de auditoría por cada item
        for item in items_carrito:
            cursor.execute(
                "UPDATE productos SET stock = stock - ? WHERE id = ?",
                (item['cantidad'], item['id'])
            )
            cursor.execute(
                "INSERT INTO movimientos (tipo, producto_id, cantidad, usuario) VALUES (?, ?, ?, ?)",
                ("VENTA", item['id'], item['cantidad'], usuario)
            )

            conexion.commit()
            # Usamos el id del último movimiento como número de operación de referencia
            id_operacion = cursor.lastrowid
            conexion.close()
            return True, "Venta completada exitosamente.", id_operacion

    except Exception as e:
        conexion.rollback()
        conexion.close()
        print(f"Error crítico en venta: {e}")
        return False, f"Error al procesar la venta: {e}", 0

def obtener_config_comercio() -> dict:
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre_fantasia, direccion, telefono, cuit, leyenda FROM config_comercio WHERE id = 1")
    row = cursor.fetchone()
    conexion.close()
    if row:
        return {"nombre": row[0], "direccion": row[1], "telefono": row[2], "cuit": row[3], "leyenda": row[4]}
    return {"nombre": "GESTOR STOCK PRO", "direccion": "", "telefono": "", "cuit": "", "leyenda": ""}

def guardar_config_comercio(nombre: str, direccion: str, telefono: str, cuit: str, leyenda: str) -> bool:
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute(
            """
            UPDATE config_comercio 
            SET nombre_fantasia = ?, direccion = ?, telefono = ?, cuit = ?, leyenda = ?
            WHERE id = 1
            """,
            (nombre, direccion, telefono, cuit, leyenda)
        )
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print(f"Error al guardar config: {e}")
        return False

def cambiar_password_usuario(usuario: str, password_actual: str, password_nueva: str) -> tuple[bool, str]:
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT password FROM usuarios WHERE username = ?", (usuario,))
    row = cursor.fetchone()
    if not row or row[0] != password_actual:
        conexion.close()
        return False, "La contraseña actual no coincide."

    cursor.execute("UPDATE usuarios SET password = ? WHERE username = ?", (password_nueva, usuario))
    conexion.commit()
    conexion.close()
    return True, "Contraseña actualizada correctamente."

def crear_nuevo_operador(nuevo_usuario: str, password: str) -> tuple[bool, str]:
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (nuevo_usuario, password))
        conexion.commit()
        conexion.close()
        return True, f"Usuario '{nuevo_usuario}' creado exitosamente."
    except Exception:
        return False, f"El usuario '{nuevo_usuario}' ya existe en el sistema."

if __name__ == "__main__":
    inicializar_base_de_datos()
    print("Base de datos y usuario demo ('admin' / 'admin123') listos.")
