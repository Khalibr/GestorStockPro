import customtkinter as ctk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.database import (
    obtener_productos, 
    buscar_productos, 
    insertar_producto, 
    actualizar_producto, 
    eliminar_producto
)

class ProductoModal(ctk.CTkToplevel):
    def __init__(self, parent, callback_refresco, producto_datos=None):
        super().__init__(parent)
        self.callback_refresco = callback_refresco
        self.producto_datos = producto_datos

        self.title("Modificar Producto" if producto_datos else "Nuevo Producto")
        ancho, alto = 400, 480
        self.update_idletasks()
        pos_x = (self.winfo_screenwidth() - ancho) // 2
        pos_y = (self.winfo_screenheight() - alto) // 2
        self.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.grab_set()  # Vuelve la ventana modal (bloquea la anterior)

        self.crear_formulario()
        
        # Asegura el foco en el primer campo apenas se termina de renderizar la ventana
        self.after(100, lambda: self.entry_nombre.focus_set())

    def crear_formulario(self):
        lbl_titulo = ctk.CTkLabel(
            self, 
            text="Datos del Producto", 
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold")
        )
        lbl_titulo.pack(pady=(20, 15))

       # Inputs
        self.entry_nombre = ctk.CTkEntry(self, placeholder_text="Nombre del producto", width=300, height=35)
        self.entry_nombre.pack(pady=8)
        self.entry_nombre.bind("<Return>", lambda event: self.guardar())

        self.entry_cat = ctk.CTkEntry(self, placeholder_text="Categoría", width=300, height=35)
        self.entry_cat.pack(pady=8)
        self.entry_cat.bind("<Return>", lambda event: self.guardar())

        self.entry_stock = ctk.CTkEntry(self, placeholder_text="Stock inicial", width=300, height=35)
        self.entry_stock.pack(pady=8)
        self.entry_stock.bind("<Return>", lambda event: self.guardar())

        self.entry_precio = ctk.CTkEntry(self, placeholder_text="Precio unitario ($)", width=300, height=35)
        self.entry_precio.pack(pady=8)
        self.entry_precio.bind("<Return>", lambda event: self.guardar())

        # Hace foco automático en el primer campo al abrir el modal
        self.entry_nombre.focus_set()

        # Si viene en modo edición, precarga los valores
        if self.producto_datos:
            self.entry_nombre.insert(0, self.producto_datos[1])
            self.entry_cat.insert(0, self.producto_datos[2])
            self.entry_stock.insert(0, str(self.producto_datos[3]))
            # Quita formato de moneda para poder editar el número plano
            precio_limpio = str(self.producto_datos[4]).replace("$", "").replace(",", "").strip()
            self.entry_precio.insert(0, precio_limpio)

        # Botones
        btn_guardar = ctk.CTkButton(
            self, 
            text="Guardar", 
            width=300, 
            height=38, 
            fg_color="#9B7EBD", 
            hover_color="#8668A6",
            command=self.guardar
        )
        btn_guardar.pack(pady=(10, 5))

        btn_cancelar = ctk.CTkButton(
            self, 
            text="Cancelar", 
            width=300, 
            height=35, 
            fg_color="transparent", 
            border_width=1,
            text_color=("black", "white"),
            command=self.destroy
        )
        btn_cancelar.pack(pady=5)

    def guardar(self):
        nombre = self.entry_nombre.get().strip()
        cat = self.entry_cat.get().strip()
        stock_str = self.entry_stock.get().strip()
        precio_str = self.entry_precio.get().strip()

        if not (nombre and cat and stock_str and precio_str):
            messagebox.showwarning("Atención", "Todos los campos son obligatorios.")
            return

        try:
            stock = int(stock_str)
            precio = float(precio_str)
        except ValueError:
            messagebox.showerror("Error", "Stock debe ser un número entero y Precio un valor numérico.")
            return

        if self.producto_datos:
            actualizar_producto(self.producto_datos[0], nombre, cat, stock, precio)
        else:
            insertar_producto(nombre, cat, stock, precio)

        self.callback_refresco()
        self.destroy()


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

        self.btn_nuevo = ctk.CTkButton(
            barra,
            text="+ Nuevo",
            width=90,
            height=35,
            corner_radius=8,
            fg_color="#2E7D32",
            hover_color="#256428",
            command=self.abrir_modal_nuevo
        )
        self.btn_nuevo.grid(row=0, column=1, padx=(0, 8))

        self.btn_modificar = ctk.CTkButton(
            barra,
            text="Editar",
            width=80,
            height=35,
            corner_radius=8,
            fg_color="#9B7EBD",
            hover_color="#8668A6",
            command=self.abrir_modal_editar
        )
        self.btn_modificar.grid(row=0, column=2, padx=(0, 8))

        self.btn_eliminar = ctk.CTkButton(
            barra,
            text="Eliminar",
            width=80,
            height=35,
            corner_radius=8,
            fg_color="#D9534F",
            hover_color="#B53B37",
            command=self.borrar_seleccionado
        )
        self.btn_eliminar.grid(row=0, column=3)

    def crear_tabla(self):
        self.tabla_frame = ctk.CTkFrame(self, fg_color=("white", "#2A2A2D"), corner_radius=10)
        self.tabla_frame.grid(row=1, column=0, sticky="nsew")
        self.tabla_frame.grid_rowconfigure(0, weight=1)
        self.tabla_frame.grid_columnconfigure(0, weight=1)

        columnas = ("id", "nombre", "categoria", "stock", "precio")
        self.tree = ttk.Treeview(self.tabla_frame, columns=columnas, show="headings", selectmode="browse")

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

        self.scrollbar = ctk.CTkScrollbar(self.tabla_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        self.scrollbar.grid(row=0, column=1, sticky="ns", pady=10, padx=(0, 8))

        # Doble clic en una fila para editar directo
        self.tree.bind("<Double-1>", lambda event: self.abrir_modal_editar())

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
        style.map("Treeview", background=[("selected", "#9B7EBD")], foreground=[("selected", "#FFFFFF")])

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

    def abrir_modal_nuevo(self):
        ProductoModal(self, callback_refresco=self.cargar_datos)

    def abrir_modal_editar(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor selecciona un producto de la lista.")
            return
        datos_fila = self.tree.item(seleccion[0])["values"]
        ProductoModal(self, callback_refresco=self.cargar_datos, producto_datos=datos_fila)

    def borrar_seleccionado(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor selecciona un producto para eliminar.")
            return

        datos_fila = self.tree.item(seleccion[0])["values"]
        id_prod = datos_fila[0]
        nombre_prod = datos_fila[1]

        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar permanentemente '{nombre_prod}'?"
        )
        if confirmar:
            eliminar_producto(id_prod)
            self.cargar_datos()