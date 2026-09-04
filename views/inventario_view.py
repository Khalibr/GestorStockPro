import customtkinter as ctk
from tkinter import ttk
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.database import obtener_productos, buscar_productos

class InventarioFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.crear_barra_superior()
        self.crear_tabla()
        self.cargar_datos()

    def crear_barra_superior(self):
        barra = ctk.CTkFrame(self, fg_color="transparent", height=45)
        barra.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        barra.grid_columnconfigure(0, weight=1)

        self.entry_buscar = ctk.CTkEntry(
            barra,
            placeholder_text="Buscar por producto o categoría...",
            height=35,
            corner_radius=8
        )
        self.entry_buscar.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry_buscar.bind("<KeyRelease>", lambda event: self.filtrar_tabla())

        self.btn_recargar = ctk.CTkButton(
            barra,
            text="Refrescar",
            width=90,
            height=35,
            corner_radius=8,
            fg_color="#9B7EBD",
            hover_color="#8668A6",
            command=self.cargar_datos
        )
        self.btn_recargar.grid(row=0, column=1)

    def crear_tabla(self):
        # Contenedor con esquinas redondeadas
        self.tabla_frame = ctk.CTkFrame(
            self, 
            fg_color=("white", "#2A2A2D"), 
            corner_radius=10
        )
        self.tabla_frame.grid(row=1, column=0, sticky="nsew")
        self.tabla_frame.grid_rowconfigure(0, weight=1)
        self.tabla_frame.grid_columnconfigure(0, weight=1)

        columnas = ("id", "nombre", "categoria", "stock", "precio")
        self.tree = ttk.Treeview(
            self.tabla_frame,
            columns=columnas,
            show="headings",
            selectmode="browse"
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Producto")
        self.tree.heading("categoria", text="Categoría")
        self.tree.heading("stock", text="Stock")
        self.tree.heading("precio", text="Precio ($)")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("nombre", width=260, anchor="w")
        self.tree.column("categoria", width=160, anchor="w")
        self.tree.column("stock", width=90, anchor="center")
        self.tree.column("precio", width=120, anchor="e")

        # Scrollbar moderna nativa de CustomTkinter
        self.scrollbar = ctk.CTkScrollbar(
            self.tabla_frame, 
            orientation="vertical", 
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        self.scrollbar.grid(row=0, column=1, sticky="ns", pady=10, padx=(0, 8))

        self.actualizar_estilos()

    def actualizar_estilos(self):
        """Aplica colores adaptados al tema actual y unifica tipografías."""
        style = ttk.Style()
        style.theme_use("clam")

        es_oscuro = ctk.get_appearance_mode() == "Dark"
        bg_tabla = "#2A2A2D" if es_oscuro else "#FFFFFF"
        fg_texto = "#EBEBF5" if es_oscuro else "#333333"
        bg_header = "#3A3A3C" if es_oscuro else "#EDE8F5"
        bg_seleccion = "#9B7EBD"

        style.configure(
            "Treeview",
            background=bg_tabla,
            foreground=fg_texto,
            fieldbackground=bg_tabla,
            rowheight=32,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background=bg_header,
            foreground=fg_texto,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            borderwidth=0
        )
        style.map(
            "Treeview", 
            background=[("selected", bg_seleccion)],
            foreground=[("selected", "#FFFFFF")]
        )

    def cargar_datos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for p in obtener_productos():
            precio_formateado = f"${p[4]:,.2f}"
            self.tree.insert("", "end", values=(p[0], p[1], p[2], p[3], precio_formateado))

    def filtrar_tabla(self):
        termino = self.entry_buscar.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)

        resultados = buscar_productos(termino) if termino else obtener_productos()
        for p in resultados:
            precio_formateado = f"${p[4]:,.2f}"
            self.tree.insert("", "end", values=(p[0], p[1], p[2], p[3], precio_formateado))