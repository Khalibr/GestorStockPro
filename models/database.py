import sqlite3
import os

DB_NAME = "stock.db"

def conectar():
    """Establece y retorna una conexión a la base de datos local SQLite."""
    conexion = sqlite3.connect(DB_NAME)
    return conexion

def inicializar_base_de_datos():
    """Crea las tablas iniciales si no existen en el archivo local."""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Tabla de productos / insumos genéricos escalables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            stock INTEGER NOT NULL,
            precio REAL NOT NULL
        )
    """)
    
    conexion.commit()
    conexion.close()

if __name__ == "__main__":
    inicializar_base_de_datos()
    print("Base de datos SQLite inicializada correctamente.")