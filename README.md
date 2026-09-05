# GestorStockPro 📦💼

**GestorStockPro** es un sistema de escritorio integral de gestión comercial, control de inventario y punto de venta (POS). Desarrollado en **Python**, combina una arquitectura modular orientada al backend con una interfaz gráfica moderna, reactiva y adaptable construida sobre **CustomTkinter**.

Diseñado bajo estándares de producción comercial, el sistema opera de manera local y offline, garantizando alta disponibilidad, persistencia de datos segura en SQLite y distribución autocontenida sin requerir configuraciones previas en el equipo del cliente.

---

## 🚀 Características Principales

*   **Punto de Venta Dinámico (POS):**
    *   Búsqueda y carga de productos en tiempo real con validación estricta de stock disponible.
    *   Cálculo automático de subtotales, totales y soporte multi-ítem.
    *   Transacciones atómicas en base de datos (prevención de inconsistencias en ventas y stock).
*   **Emisión de Comprobantes (PDF):**
    *   Generación automática de tickets de venta con formato térmico estándar utilizando **ReportLab**.
    *   Configuración dinámica de datos fiscales del comercio (Nombre comercial, CUIT/RUT, Dirección, Teléfono y Leyenda).
    *   Apertura automática del comprobante tras concretar la transacción.
*   **Control de Inventario y Auditoría:**
    *   Módulo de stock con filtrado dinámico, alertas visuales por quiebre de stock y edición rápida.
    *   Módulo de auditoría e historial para trazabilidad completa de operaciones.
*   **Seguridad y Control de Acceso:**
    *   Autenticación de usuarios por roles segregados (**Administrador** y **Vendedor/Operador**).
    *   Almacenamiento de contraseñas mediante hashing criptográfico (`SHA-256`).
    *   Módulo de gestión de usuarios y restablecimiento de credenciales con visores protegidos contra miradas indiscretas.
*   **Interfaz Moderna y Adaptativa:**
    *   Soporte nativo para alternancia entre **Tema Claro (Light)** y **Tema Oscuro (Dark)**.
    *   Iconografía adaptativa procesada dinámicamente según la luminosidad del entorno.
    *   Barra lateral retráctil para maximizar el área útil de trabajo.

---

## 🛠️ Stack Tecnológico

*   **Lenguaje:** Python 3.11+
*   **GUI:** CustomTkinter (interfaz visual moderna y adaptativa)
*   **Base de Datos:** SQLite3 (motor relacional embebido y transaccional)
*   **Generación de Documentos:** ReportLab
*   **Procesamiento de Imágenes:** Pillow (PIL)
*   **Empaquetado y Distribución:** PyInstaller (binario `.exe` autocontenido)

---

## 📁 Estructura del Proyecto

```text
GestorStockPro/
├── assets/                  # Recursos gráficos (iconos, branding, .ico)
├── models/
│   └── database.py          # Capa de datos, esquemas SQLite y lógica de negocio
├── utils/
│   ├── rutas.py             # Resolución de rutas absolutas (desarrollo y PyInstaller)
│   └── ticket_generator.py  # Renderizado y armado de tickets PDF
├── views/
│   ├── login_view.py        # Ventana de autenticación y acceso
│   ├── main_view.py         # Ventana principal, navegación y sidebar
│   ├── inventario_view.py   # Consulta y edición de catálogo
│   ├── carga_stock_view.py  # Entrada de mercadería
│   ├── ventas_view.py       # Terminal de punto de venta (POS)
│   ├── historial_view.py    # Auditoría de ventas
│   └── configuracion_view.py# Parámetros fiscales y administración de usuarios
├── tools/
│   └── reset_admin.py       # Script de rescate y recuperación técnica de credenciales
├── requirements.txt         # Especificación de dependencias congeladas
├── main.py                  # Punto de entrada de la aplicación
└── README.md