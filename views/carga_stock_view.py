import sys
import os
import customtkinter as ctk
from tkinter import messagebox

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.database import obtener_productos, reponer_stock

class CargaStockFrame(ctk.CTkFrame):
    def __init__(self, parent, usuario_activo="admin"):
        super().__init__(parent, fg_color="transparent")
        self.usuario_activo = usuario_activo

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.productos_cache = {}  # { "Nombre del producto": (id, stock_actual, precio) }

        self.crear_interfaz()
        self.cargar_productos_en_combo()

    def crear_interfaz(self):
        # Tarjeta central
        self.card = ctk.CTkFrame(self, fg_color=("white", "#2A2A2D"), corner_radius=12, width=480)
        self.card.grid(row=0, column=0, padx=20, pady=20)
        self.card.grid_columnconfigure(0, weight=1)

        lbl_titulo = ctk.CTkLabel(
            self.card,
            text="Reposición de Mercadería",
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold")
        )
        lbl_titulo.grid(row=0, column=0, pady=(25, 5))

        lbl_sub = ctk.CTkLabel(
            self.card,
            text="Selecciona un producto existente para sumar nuevas unidades.",
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color=("gray50", "gray70")
        )
        lbl_sub.grid(row=1, column=0, pady=(0, 20), padx=20)

        # Menú desplegable de productos
        self.combo_productos = ctk.CTkComboBox(
            self.card,
            width=340,
            height=38,
            values=["Cargando productos..."],
            command=self.al_seleccionar_producto
        )
        self.combo_productos.grid(row=2, column=0, pady=10)

        # Panel informativo del estado actual
        self.info_frame = ctk.CTkFrame(self.card, fg_color=("#F3EFEA", "#1C1C1E"), corner_radius=8, width=340, height=80)
        self.info_frame.grid(row=3, column=0, pady=15, padx=30, sticky="ew")
        self.info_frame.grid_columnconfigure((0, 1), weight=1)
        self.info_frame.grid_propagate(False)

        self.lbl_stock_actual_titulo = ctk.CTkLabel(
            self.info_frame, 
            text="Stock Actual", 
            font=ctk.CTkFont(size=11), 
            text_color="gray"
        )
        self.lbl_stock_actual_titulo.grid(row=0, column=0, pady=(15, 0))

        self.lbl_stock_actual_valor = ctk.CTkLabel(
            self.info_frame, 
            text="--", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.lbl_stock_actual_valor.grid(row=1, column=0)

        self.lbl_precio_titulo = ctk.CTkLabel(
            self.info_frame, 
            text="Precio Venta", 
            font=ctk.CTkFont(size=11), 
            text_color="gray"
        )
        self.lbl_precio_titulo.grid(row=0, column=1, pady=(15, 0))

        self.lbl_precio_valor = ctk.CTkLabel(
            self.info_frame, 
            text="--", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.lbl_precio_valor.grid(row=1, column=1)

        # Entrada de cantidad
        self.entry_cantidad = ctk.CTkEntry(
            self.card,
            placeholder_text="Cantidad a ingresar (ej: 10)",
            width=340,
            height=38
        )
        self.entry_cantidad.grid(row=4, column=0, pady=10)
        self.entry_cantidad.bind("<Return>", lambda event: self.confirmar_ingreso())

        # Botón para confirmar
        self.btn_guardar = ctk.CTkButton(
            self.card,
            text="Ingresar Unidades al Stock",
            width=340,
            height=40,
            fg_color="#2E7D32",
            hover_color="#256428",
            command=self.confirmar_ingreso
        )
        self.btn_guardar.grid(row=5, column=0, pady=(15, 25))

    def cargar_productos_en_combo(self):
        """Carga la lista de nombres en el menú desplegable."""
        self.productos_cache.clear()
        lista_nombres = []

        for prod in obtener_productos():
            id_prod, nombre, cat, stock, precio = prod
            etiqueta = f"{nombre} ({cat})"
            self.productos_cache[etiqueta] = (id_prod, stock, precio)
            lista_nombres.append(etiqueta)

        if lista_nombres:
            self.combo_productos.configure(values=lista_nombres)
            self.combo_productos.set(lista_nombres[0])
            self.al_seleccionar_producto(lista_nombres[0])
        else:
            self.combo_productos.configure(values=["Sin productos registrados"])
            self.combo_productos.set("Sin productos registrados")

    def al_seleccionar_producto(self, seleccion):
        """Actualiza los valores de stock y precio al cambiar la selección."""
        if seleccion in self.productos_cache:
            _, stock, precio = self.productos_cache[seleccion]
            self.lbl_stock_actual_valor.configure(text=str(stock))
            self.lbl_precio_valor.configure(text=f"${precio:,.2f}")

    def confirmar_ingreso(self):
        seleccion = self.combo_productos.get()
        if seleccion not in self.productos_cache:
            messagebox.showwarning("Atención", "Selecciona un producto válido de la lista.")
            return

        cantidad_str = self.entry_cantidad.get().strip()
        if not cantidad_str.isdigit() or int(cantidad_str) <= 0:
            messagebox.showerror("Error", "Ingresa un número entero positivo para la cantidad.")
            return

        cantidad = int(cantidad_str)
        # Se extrae primero la información del producto antes de ejecutar la reposición
        id_prod, stock_viejo, precio = self.productos_cache[seleccion]

        if reponer_stock(id_prod, cantidad, self.usuario_activo):
            nuevo_stock = stock_viejo + cantidad
            messagebox.showinfo(
                "Éxito", 
                f"Se añadieron {cantidad} unidades correctamente.\nNuevo total: {nuevo_stock}"
            )
            self.entry_cantidad.delete(0, "end")
            self.cargar_productos_en_combo()
            self.combo_productos.set(seleccion)
            self.al_seleccionar_producto(seleccion)
        else:
            messagebox.showerror("Error", "No se pudo actualizar el stock en la base de datos.")