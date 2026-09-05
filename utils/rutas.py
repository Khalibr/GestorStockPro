import os
import sys

def ruta_recurso(ruta_relativa: str) -> str:
    """
    Resuelve la ruta absoluta para recursos considerando la estructura
    interna de PyInstaller 6+ (_internal) o el entorno de desarrollo.
    """
    posibles_bases = []

    # 1. En entorno congelado por PyInstaller (.exe)
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        # Carpeta _internal creada en modo --onedir
        posibles_bases.append(os.path.join(exe_dir, "_internal"))
        posibles_bases.append(exe_dir)
        if hasattr(sys, '_MEIPASS'):
            posibles_bases.append(sys._MEIPASS)
            posibles_bases.append(os.path.join(sys._MEIPASS, "_internal"))

    # 2. En entorno de desarrollo (script normal)
    posibles_bases.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    # Buscar la primera coincidencia real en disco
    for base in posibles_bases:
        candidato = os.path.join(base, ruta_relativa)
        if os.path.exists(candidato):
            return candidato

    # Fallback por defecto
    return os.path.join(posibles_bases[0], ruta_relativa)

def ruta_carpeta_comprobantes() -> str:
    """Garantiza que los comprobantes se guarden junto al ejecutable o raiz del proyecto."""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    carpeta = os.path.join(base_dir, "comprobantes")
    os.makedirs(carpeta, exist_ok=True)
    return carpeta