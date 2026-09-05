import os
import sqlite3
import hashlib
from tkinter import Tk, filedialog

def hashear_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def main():
    print("==================================================")
    print("   GESTOR STOCK PRO - RECUPERACIÓN DE ADMIN      ")
    print("==================================================")

    # 1. Buscar automáticamente en rutas cercanas
    posibles_rutas = [
        "stock.db",
        os.path.join("..", "stock.db"),
        os.path.join(os.getcwd(), "stock.db")
    ]

    ruta_db = None
    for ruta in posibles_rutas:
        if os.path.isfile(ruta):
            ruta_db = ruta
            break

    # 2. Si se corre desde un pendrive, pide seleccionar la BD con ventana gráfica
    if not ruta_db:
        print("\n[*] Abriendo selector para ubicar 'stock.db' en el equipo...")
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        ruta_db = filedialog.askopenfilename(
            title="Selecciona la base de datos (stock.db)",
            filetypes=[("Archivos de Base de Datos", "*.db"), ("Todos los archivos", "*.*")]
        )
        root.destroy()

    if not ruta_db or not os.path.exists(ruta_db):
        print("\n[!] Operación cancelada. No se indicó ninguna base de datos válida.")
        input("\nPresiona Enter para salir...")
        return

    print(f"\n[+] Archivo conectado: {ruta_db}")
    confirmar = input("\n¿Restablecer clave de 'admin' a 'admin123'? (s/n): ").strip().lower()

    if confirmar != "s":
        print("\n[!] Operación abortada.")
        input("\nPresiona Enter para salir...")
        return

    try:
        conn = sqlite3.connect(ruta_db)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM usuarios WHERE usuario = 'admin'")
        if not cursor.fetchone():
            print("\n[!] Error: No se encontró el usuario 'admin' en esta base de datos.")
            conn.close()
            input("\nPresiona Enter para salir...")
            return

        pass_hash = hashear_password("admin123")
        cursor.execute("UPDATE usuarios SET password = ? WHERE usuario = 'admin'", (pass_hash,))
        conn.commit()
        conn.close()

        print("\n" + "=" * 50)
        print("[✓] Contraseña de 'admin' restablecida a: admin123")
        print("[*] Tablas de inventario, ventas y configuración intactas.")
        print("==================================================")

    except Exception as e:
        print(f"\n[!] Error al operar sobre SQLite: {e}")

    input("\nPresiona Enter para cerrar...")

if __name__ == "__main__":
    main()