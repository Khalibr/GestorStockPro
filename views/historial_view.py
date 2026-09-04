import customtkinter as ctk
from tkinter import ttk
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.database import obtener_movimientos

class HistorialFrame(ctk.CTkFrame):
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

        lbl = ctk.CTkLabel(
            barra,
            text="Registro de Auditoría y Movimientos",
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold")
        )
        lbl.grid(row=0, column=0, sticky="w")

        btn_refrescar = ctk.CTkButton(
            barra,
            text="Refrescar",
            width=90,
            height=35,
            corner_radius=8,
            fg_color="#9B7EBD",
            hover_color="#8668A6",
            command=self.cargar_datos
        )
        btn_refrescar.grid(row=0, column=1)

    def crear_tabla(self):
        self.tabla_frame = ctk.CTkFrame(self, fg_color=("white", "#2A2A2D"), corner_radius=10)
        self.tabla_frame.grid(row=1, column=0, sticky="nsew")
        self.tabla_frame.grid_rowconfigure(0, weight=1)
        self.tabla_frame.grid_columnconfigure(0, weight=1)

        columnas = ("id", "fecha", "tipo", "producto", "cantidad", "usuario")
        self.tree = ttk.Treeview(self.tabla_frame, columns=columnas, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("fecha", text="Fecha / Hora")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("producto", text="Producto")
        self.tree.heading("cantidad", text="Cantidad")
        self.tree.heading("usuario", text="Operador")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("fecha", width=150, anchor="center")
        self.tree.column("tipo", width=100, anchor="center")
        self.tree.column("producto", width=220, anchor="w")
        self.tree.column("cantidad", width=80, anchor="center")
        self.tree.column("usuario", width=100, anchor="center")

        self.scrollbar = ctk.CTkScrollbar(self.tabla_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        self.scrollbar.grid(row=0, column=1, sticky="ns", pady=10, padx=(0, 8))

        self.actualizar_estilos()

    def actualizar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")

        es_oscuro = ctk.get_appearance_mode() == "Dark"
        bg_tabla = "#2A2A2D" if es_oscuro else "#FFFFFF"
        fg_texto = "#EBEBF5" if es_oscuro else "#333333"
        bg_header = "#3A3A3C" if es_oscuro else "#EDE8F5"

        style.configure(
            "Treeview",
            background=bg_tabla,
            foreground=fg_texto,
            fieldbackground=bg_tabla,
            rowheight=30,
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

    def cargar_datos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for m in obtener_movimientos():
            # m: (id, fecha, tipo, nombre_prod, cantidad, usuario)
            self.tree.insert("", "end", values=m)