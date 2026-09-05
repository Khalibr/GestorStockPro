import os
import sys

def ruta_recurso(ruta_relativa: str) -> str:
    """Obtiene la ruta absoluta a recursos empaquetados por PyInstaller o en desarrollo."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    return os.path.join(base_path, ruta_relativa)

def ruta_carpeta_comprobantes() -> str:
    """Garantiza que los comprobantes se guarden junto al ejecutable o raiz del proyecto."""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    carpeta = os.path.join(base_dir, "comprobantes")
    os.makedirs(carpeta, exist_ok=True)
    return carpeta