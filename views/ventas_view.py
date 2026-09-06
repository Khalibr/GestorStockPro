import sys
import os
import subprocess
import customtkinter as ctk
from tkinter import ttk, messagebox

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.database import obtener_productos, procesar_venta
from utils.ticket_generator import generar_ticket_pdf

class VentasFrame(ctk.CTkFrame):
    def __init__(self, parent, usuario_activo="admin"):
        super().__init__(parent, fg_color="transparent")
        self.usuario_activo = usuario_activo

        # Estructura del carrito en memoria: [{'id', 'nombre', 'cantidad', 'precio', 'subtotal'}]
        self.carrito = []
        self.productos_cache = {}

        self.grid_columnconfigure(0, weight=4)  # Columna izquierda: Selección
        self.grid_columnconfigure(1, weight=6)  # Columna derecha: Carrito / Total
        self.grid_rowconfigure(0, weight=1)

        self.crear_panel_seleccion()
        self.crear_panel_carrito()
        self.cargar_productos()

    def crear_panel_seleccion(self):
        self.card_izq = ctk.CTkFrame(self, fg_color=("white", "#2A2A2D"), corner_radius=12)
        self.card_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        self.card_izq.grid_columnconfigure(0, weight=1)

        lbl_tit = ctk.CTkLabel(
            self.card_izq, 
            text="Punto de Venta", 
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold")
        )
        lbl_tit.grid(row=0, column=0, pady=(20, 5), padx=20, sticky="w")

        lbl_sub = ctk.CTkLabel(
            self.card_izq, 
            text="Selecciona artículos para agregar a la orden.", 
            font=ctk.CTkFont(size=12), 
            text_color="gray"
        )
        lbl_sub.grid(row=1, column=0, pady=(0, 15), padx=20, sticky="w")

        # Desplegable de productos
        self.combo_productos = ctk.CTkComboBox(
            self.card_izq,
            height=38,
            values=["Cargando..."],
            command=self.al_seleccionar_producto
        )
        self.combo_productos.grid(row=2, column=0, pady=10, padx=20, sticky="ew")

        # Visor de existencias y precio
        self.info_box = ctk.CTkFrame(self.card_izq, fg_color=("#F3EFEA", "#1C1C1E"), corner_radius=8, height=75)
        self.info_box.grid(row=3, column=0, pady=10, padx=20, sticky="ew")
        self.info_box.grid_columnconfigure((0, 1), weight=1)
        self.info_box.grid_propagate(False)

        ctk.CTkLabel(self.info_box, text="Stock Disponible", font=ctk.CTkFont(size=11), text_color="gray").grid(row=0, column=0, pady=(12, 0))
        self.lbl_disp = ctk.CTkLabel(self.info_box, text="--", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_disp.grid(row=1, column=0)

        ctk.CTkLabel(self.info_box, text="Precio Unit.", font=ctk.CTkFont(size=11), text_color="gray").grid(row=0, column=1, pady=(12, 0))
        self.lbl_precio = ctk.CTkLabel(self.info_box, text="--", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_precio.grid(row=1, column=1)

        # Cantidad
        self.entry_cantidad = ctk.CTkEntry(self.card_izq, placeholder_text="Cantidad a vender", height=38)
        self.entry_cantidad.grid(row=4, column=0, pady=15, padx=20, sticky="ew")
        self.entry_cantidad.bind("<Return>", lambda event: self.agregar_al_carrito())

        # Botón agregar
        self.btn_agregar = ctk.CTkButton(
            self.card_izq,
            text="+ Agregar al Carrito",
            height=40,
            fg_color="#9B7EBD",
            hover_color="#8668A6",
            command=self.agregar_al_carrito
        )
        self.btn_agregar.grid(row=5, column=0, pady=(0, 20), padx=20, sticky="ew")

    def crear_panel_carrito(self):
        self.card_der = ctk.CTkFrame(self, fg_color=("white", "#2A2A2D"), corner_radius=12)
        self.card_der.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        self.card_der.grid_rowconfigure(1, weight=1)
        self.card_der.grid_columnconfigure(0, weight=1)

        # Barra superior del carrito
        top_der = ctk.CTkFrame(self.card_der, fg_color="transparent")
        top_der.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        top_der.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top_der, 
            text="Resumen de Venta", 
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        btn_quitar = ctk.CTkButton(
            top_der,
            text="Eliminar Ítem",
            width=100,
            height=30,
            fg_color="#D9534F",
            hover_color="#C9302C",
            command=self.quitar_item_carrito
        )
        btn_quitar.grid(row=0, column=1, sticky="e")

        # Grilla de ítems agregados
        columnas = ("cant", "prod", "precio", "subtotal")
        self.tree_carrito = ttk.Treeview(self.card_der, columns=columnas, show="headings", selectmode="browse")
        self.tree_carrito.heading("cant", text="Cant.")
        self.tree_carrito.heading("prod", text="Producto")
        self.tree_carrito.heading("precio", text="Unitario")
        self.tree_carrito.heading("subtotal", text="Subtotal")

        self.tree_carrito.column("cant", width=50, anchor="center")
        self.tree_carrito.column("prod", width=180, anchor="w")
        self.tree_carrito.column("precio", width=80, anchor="e")
        self.tree_carrito.column("subtotal", width=90, anchor="e")

        self.tree_carrito.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)
        self.actualizar_estilos()

        # Panel inferior: Total acumulado y Botón de Venta
        bottom_frame = ctk.CTkFrame(self.card_der, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=15)
        bottom_frame.grid_columnconfigure(0, weight=1)

        self.lbl_total_general = ctk.CTkLabel(
            bottom_frame,
            text="TOTAL: $0.00",
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=("#2A2A2D", "#81C784")
        )
        self.lbl_total_general.grid(row=0, column=0, sticky="w")

        self.btn_confirmar_venta = ctk.CTkButton(
            bottom_frame,
            text="Confirmar y Generar Ticket",
            height=42,
            fg_color="#2E7D32",
            hover_color="#256428",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.finalizar_venta
        )
        self.btn_confirmar_venta.grid(row=0, column=1, sticky="e")

    def actualizar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        es_oscuro = ctk.get_appearance_mode() == "Dark"
        bg = "#2A2A2D" if es_oscuro else "#FFFFFF"
        fg = "#EBEBF5" if es_oscuro else "#333333"
        bg_head = "#3A3A3C" if es_oscuro else "#EDE8F5"

        style.configure("Treeview", background=bg, foreground=fg, fieldbackground=bg, rowheight=28, borderwidth=0)
        style.configure("Treeview.Heading", background=bg_head, foreground=fg, font=("Segoe UI", 9, "bold"), relief="flat")

    def cargar_productos(self):
        self.productos_cache.clear()
        nombres = []
        for p in obtener_productos():
            id_p, nom, cat, stock, precio = p
            etiqueta = f"{nom} ({cat})"
            self.productos_cache[etiqueta] = {"id": id_p, "nombre": nom, "stock": stock, "precio": precio}
            nombres.append(etiqueta)

        if nombres:
            self.combo_productos.configure(values=nombres)
            self.combo_productos.set(nombres[0])
            self.al_seleccionar_producto(nombres[0])

    def al_seleccionar_producto(self, seleccion):
        if seleccion in self.productos_cache:
            p = self.productos_cache[seleccion]
            self.lbl_disp.configure(text=str(p["stock"]))
            self.lbl_precio.configure(text=f"${p['precio']:,.2f}")

    def agregar_al_carrito(self):
        seleccion = self.combo_productos.get()
        if seleccion not in self.productos_cache:
            return

        cant_str = self.entry_cantidad.get().strip()
        if not cant_str.isdigit() or int(cant_str) <= 0:
            messagebox.showerror("Error", "Ingresa una cantidad entera válida.")
            return

        cantidad = int(cant_str)
        p = self.productos_cache[seleccion]

        # Comprobar existencias contra lo que ya está en el carrito
        ya_en_carrito = sum(item["cantidad"] for item in self.carrito if item["id"] == p["id"])
        if (ya_en_carrito + cantidad) > p["stock"]:
            messagebox.showwarning("Sin existencias", f"Stock insuficiente. Disponible: {p['stock']} (Ya añadiste {ya_en_carrito}).")
            return

        subtotal = cantidad * p["precio"]
        self.carrito.append({
            "id": p["id"],
            "nombre": p["nombre"],
            "cantidad": cantidad,
            "precio": p["precio"],
            "subtotal": subtotal
        })

        self.entry_cantidad.delete(0, "end")
        self.refrescar_tabla_carrito()

    def quitar_item_carrito(self):
        sel = self.tree_carrito.selection()
        if not sel:
            messagebox.showinfo("Atención", "Selecciona una fila del carrito para remover.")
            return
        idx = self.tree_carrito.index(sel[0])
        self.carrito.pop(idx)
        self.refrescar_tabla_carrito()

    def refrescar_tabla_carrito(self):
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)

        total = 0.0
        for item in self.carrito:
            total += item["subtotal"]
            self.tree_carrito.insert("", "end", values=(
                item["cantidad"],
                item["nombre"],
                f"${item['precio']:,.2f}",
                f"${item['subtotal']:,.2f}"
            ))

        self.lbl_total_general.configure(text=f"TOTAL: ${total:,.2f}")

    def finalizar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Carrito vacío", "Añade al menos un producto para procesar la venta.")
            return

        total = sum(i["subtotal"] for i in self.carrito)

        # 1. Impacto transaccional en Base de Datos (recibe ticket_id alfanumérico)
        exito, msj, ticket_id = procesar_venta(self.carrito, self.usuario_activo)

        if exito:
            # 2. Generación del ticket térmico en PDF con el ticket_id
            ruta_pdf = generar_ticket_pdf(ticket_id, self.carrito, total, self.usuario_activo)

            # 3. Apertura automática del comprobante
            try:
                if sys.platform == "win32":
                    os.startfile(ruta_pdf)
                else:
                    subprocess.call(["xdg-open", ruta_pdf])
            except Exception as e:
                print(f"No se pudo abrir el visor de PDF: {e}")

            messagebox.showinfo("Venta Exitosa", f"{msj}\nComprobante: {ticket_id}")

            # Limpiar estado
            self.carrito.clear()
            self.refrescar_tabla_carrito()
            self.cargar_productos()
        else:
            messagebox.showerror("Error en Venta", msj)