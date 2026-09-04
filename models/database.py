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

if __name__ == "__main__":
    inicializar_base_de_datos()
    print("Base de datos y usuario demo ('admin' / 'admin123') listos.")
