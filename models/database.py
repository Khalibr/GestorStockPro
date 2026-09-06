import os
import sys
import sqlite3
import hashlib
import uuid
from decimal import Decimal, ROUND_HALF_UP

# Obtiene la ruta absoluta del directorio base (sea en desarrollo o empaquetado)
if getattr(sys, 'frozen', False):
    # Si corre como ejecutable compilado con PyInstaller (.exe)
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Si corre en modo script de desarrollo (apunta a la raíz del proyecto)
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

DB_NAME = os.path.join(BASE_DIR, "stock.db")

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
            producto_nombre TEXT,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL DEFAULT 0.0,
            total REAL DEFAULT 0.0,
            ticket_id TEXT,
            usuario TEXT NOT NULL,
            FOREIGN KEY (producto_id) REFERENCES productos (id)
        )
    """)

    # Migración automática segura para bases de datos existentes
    cursor.execute("PRAGMA table_info(movimientos)")
    columnas = [col[1] for col in cursor.fetchall()]
    
    if "producto_nombre" not in columnas:
        cursor.execute("ALTER TABLE movimientos ADD COLUMN producto_nombre TEXT")
    if "precio_unitario" not in columnas:
        cursor.execute("ALTER TABLE movimientos ADD COLUMN precio_unitario REAL DEFAULT 0.0")
    if "total" not in columnas:
        cursor.execute("ALTER TABLE movimientos ADD COLUMN total REAL DEFAULT 0.0")
    if "ticket_id" not in columnas:
        cursor.execute("ALTER TABLE movimientos ADD COLUMN ticket_id TEXT")

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


def eliminar_producto(producto_id):
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
        conexion.commit()
        conexion.close()
        return True, "Producto eliminado correctamente."
    except Exception as e:
        return False, f"Error al eliminar: {e}"

def reponer_stock(id_prod: int, cantidad_a_sumar: int, usuario: str = "admin") -> bool:
    """Incrementa las existencias y audita el movimiento."""
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        
        cursor.execute("SELECT nombre, precio FROM productos WHERE id = ?", (id_prod,))
        res = cursor.fetchone()
        nombre_prod = res[0] if res else "Desconocido"
        precio = res[1] if res else 0.0

        cursor.execute(
            "UPDATE productos SET stock = stock + ? WHERE id = ?",
            (cantidad_a_sumar, id_prod)
        )
        conexion.commit()
        conexion.close()
        
        registrar_movimiento(
            tipo="INGRESO", 
            id_prod=id_prod, 
            cantidad=cantidad_a_sumar, 
            usuario=usuario, 
            nombre_prod=nombre_prod, 
            precio_unitario=precio
        )
        return True
    except Exception as e:
        print(f"Error al reponer stock: {e}")
        return False

def registrar_movimiento(tipo: str, id_prod: int, cantidad: int, usuario: str, nombre_prod: str = None, precio_unitario: float = 0.0, ticket_id: str = None) -> bool:
    """Registra una entrada o salida en el historial con snapshot y valores monetarios."""
    try:
        conexion = conectar()
        cursor = conexion.cursor()

        if not nombre_prod:
            cursor.execute("SELECT nombre, precio FROM productos WHERE id = ?", (id_prod,))
            res = cursor.fetchone()
            if res:
                nombre_prod = res[0]
                if precio_unitario == 0.0:
                    precio_unitario = res[1]
            else:
                nombre_prod = "Desconocido"

        # Cálculo preciso con Decimal
        p_unit = Decimal(str(precio_unitario))
        tot = (p_unit * Decimal(str(cantidad))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        cursor.execute(
            """
            INSERT INTO movimientos (tipo, producto_id, producto_nombre, cantidad, precio_unitario, total, ticket_id, usuario)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (tipo, id_prod, nombre_prod, cantidad, float(p_unit), float(tot), ticket_id, usuario)
        )
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print(f"Error al registrar movimiento: {e}")
        return False

def obtener_movimientos(filtro=None):
    conexion = conectar()
    cursor = conexion.cursor()
    
    query = """
        SELECT 
            m.id,
            m.fecha,
            COALESCE(m.producto_nombre, p.nombre, '[Producto Eliminado]') AS producto,
            m.tipo,
            m.cantidad,
            COALESCE(m.precio_unitario, 0.0),
            COALESCE(m.total, 0.0),
            COALESCE(m.ticket_id, '-'),
            m.usuario
        FROM movimientos m
        LEFT JOIN productos p ON m.producto_id = p.id
        ORDER BY m.id DESC
    """
    cursor.execute(query)
    filas = cursor.fetchall()
    conexion.close()
    return filas

def procesar_venta(items_carrito: list, usuario: str) -> tuple[bool, str, str]:
    """
    Procesa una venta compuesta por múltiples productos.
    Retorna (éxito, mensaje, ticket_id).
    """
    if not items_carrito:
        return False, "El carrito está vacío.", ""

    conexion = conectar()
    cursor = conexion.cursor()

    try:
        cursor.execute("BEGIN TRANSACTION")

        # 1. Validar existencias
        for item in items_carrito:
            cursor.execute("SELECT stock, nombre FROM productos WHERE id = ?", (item['id'],))
            resultado = cursor.fetchone()
            if not resultado:
                conexion.rollback()
                conexion.close()
                return False, f"El producto {item['nombre']} ya no existe.", ""

            stock_actual, nombre = resultado
            if stock_actual < item['cantidad']:
                conexion.rollback()
                conexion.close()
                return False, f"Stock insuficiente para '{nombre}'. Disponible: {stock_actual}", ""

        # 2. Generar Ticket ID único para agrupar la operación contable
        ticket_id = f"TICK-{uuid.uuid4().hex[:8].upper()}"

        # 3. Descontar existencias y asentar movimientos
        for item in items_carrito:
            cursor.execute(
                "UPDATE productos SET stock = stock - ? WHERE id = ?",
                (item['cantidad'], item['id'])
            )

            p_unit = Decimal(str(item['precio']))
            subtotal = (p_unit * Decimal(str(item['cantidad']))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            cursor.execute(
                """
                INSERT INTO movimientos (tipo, producto_id, producto_nombre, cantidad, precio_unitario, total, ticket_id, usuario) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                ("VENTA", item['id'], item['nombre'], item['cantidad'], float(p_unit), float(subtotal), ticket_id, usuario)
            )

        conexion.commit()
        conexion.close()
        return True, "Venta completada exitosamente.", ticket_id

    except Exception as e:
        conexion.rollback()
        conexion.close()
        print(f"Error crítico en venta: {e}")
        return False, f"Error al procesar la venta: {e}", ""

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
    try:
        # 1. Buscamos por la columna real 'usuario'
        cursor.execute("SELECT password FROM usuarios WHERE usuario = ?", (usuario,))
        row = cursor.fetchone()
        
        if not row:
            conexion.close()
            return False, f"Usuario '{usuario}' no encontrado."

        # 2. Comparamos contra el hash SHA-256
        hash_actual = hashear_password(password_actual)
        if row[0] != hash_actual:
            conexion.close()
            return False, "La contraseña actual no coincide."

        # 3. Guardamos la nueva clave hasheada
        nuevo_hash = hashear_password(password_nueva)
        cursor.execute("UPDATE usuarios SET password = ? WHERE usuario = ?", (nuevo_hash, usuario))
        conexion.commit()
        conexion.close()
        return True, "Contraseña actualizada correctamente."
    except Exception as e:
        conexion.close()
        return False, f"Error en BD: {e}"

def crear_nuevo_operador(nuevo_usuario: str, password: str) -> tuple[bool, str]:
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        # Validar si ya existe usando la columna 'usuario'
        cursor.execute("SELECT 1 FROM usuarios WHERE usuario = ?", (nuevo_usuario.strip(),))
        if cursor.fetchone():
            conexion.close()
            return False, f"El usuario '{nuevo_usuario}' ya existe en el sistema."

        # Insertar con hash SHA-256
        hash_pass = hashear_password(password.strip())
        cursor.execute(
            "INSERT INTO usuarios (usuario, password) VALUES (?, ?)", 
            (nuevo_usuario.strip(), hash_pass)
        )
        conexion.commit()
        conexion.close()
        return True, f"Usuario '{nuevo_usuario}' creado exitosamente."
    except Exception as e:
        conexion.close()
        return False, f"Error al registrar: {e}"

def obtener_operadores() -> list[str]:
    """Retorna la lista de usuarios que no sean admin."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT usuario FROM usuarios WHERE usuario != 'admin' ORDER BY usuario ASC")
    rows = cursor.fetchall()
    conexion.close()
    return [r[0] for r in rows]

def resetear_password_por_admin(usuario_objetivo: str, password_nueva: str) -> tuple[bool, str]:
    """Permite al admin redefinir la clave de un operador sin conocer la actual."""
    if usuario_objetivo == "admin":
        return False, "Para cambiar la clave de admin usa 'Cambiar Contraseña'."

    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", (usuario_objetivo,))
        if not cursor.fetchone():
            conexion.close()
            return False, f"El usuario '{usuario_objetivo}' no existe."

        nuevo_hash = hashear_password(password_nueva)
        cursor.execute("UPDATE usuarios SET password = ? WHERE usuario = ?", (nuevo_hash, usuario_objetivo))
        conexion.commit()
        conexion.close()
        return True, f"Contraseña de '{usuario_objetivo}' restablecida con éxito."
    except Exception as e:
        conexion.close()
        return False, f"Error en BD: {e}"

if __name__ == "__main__":
    inicializar_base_de_datos()
    print("Base de datos y usuario demo ('admin' / 'admin123') listos.")
