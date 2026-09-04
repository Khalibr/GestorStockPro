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

if __name__ == "__main__":
    inicializar_base_de_datos()
    print("Base de datos y usuario demo ('admin' / 'admin123') listos.")