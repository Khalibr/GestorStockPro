import os
import sys
import subprocess
import customtkinter as ctk
from tkinter import ttk, messagebox

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


        # 9 columnas de auditoría contable
        columnas = ("id", "fecha", "ticket", "tipo", "producto", "cantidad", "precio", "total", "usuario")
        self.tree = ttk.Treeview(self.tabla_frame, columns=columnas, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("fecha", text="Fecha / Hora")
        self.tree.heading("ticket", text="N° Ticket")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("producto", text="Producto")
        self.tree.heading("cantidad", text="Cant.")
        self.tree.heading("precio", text="P. Unit.")
        self.tree.heading("total", text="Total")
        self.tree.heading("usuario", text="Operador")

        # Anchos compactos: ocupan ~770px en total para entrar directos en pantalla sin scroll
        self.tree.column("id", width=35, minwidth=30, anchor="center")
        self.tree.column("fecha", width=125, minwidth=115, anchor="center")
        self.tree.column("ticket", width=95, minwidth=90, anchor="center")
        self.tree.column("tipo", width=65, minwidth=60, anchor="center")
        self.tree.column("producto", width=155, minwidth=120, anchor="w")
        self.tree.column("cantidad", width=45, minwidth=40, anchor="center")
        self.tree.column("precio", width=75, minwidth=65, anchor="e")
        self.tree.column("total", width=85, minwidth=75, anchor="e")
        self.tree.column("usuario", width=75, minwidth=65, anchor="center")

        # Scrollbar Vertical (idéntico al actual)
        self.scrollbar_y = ctk.CTkScrollbar(self.tabla_frame, orientation="vertical", command=self.tree.yview)
        
        # Scrollbar Horizontal (mantiene el mismo estilo y curvatura)
        self.scrollbar_x = ctk.CTkScrollbar(self.tabla_frame, orientation="horizontal", command=self.tree.xview)

        # Vincular ambos scrolls al Treeview
        self.tree.configure(
            yscrollcommand=self.scrollbar_y.set,
            xscrollcommand=self.scrollbar_x.set
        )

        # Ubicación en grid
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=(10, 0))
        self.scrollbar_y.grid(row=0, column=1, sticky="ns", pady=10, padx=(0, 8))
        self.scrollbar_x.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))

        # Eventos: doble clic para PDF y soporte de scroll con rueda
        self.tree.bind("<Double-1>", self.abrir_comprobante_ticket)
        self.tree.bind("<Shift-MouseWheel>", self.scrollear_horizontal_rueda)
        
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
            # m[0]: id, m[1]: fecha, m[2]: producto, m[3]: tipo, m[4]: cantidad
            # m[5]: precio_unitario, m[6]: total, m[7]: ticket_id, m[8]: usuario
            self.tree.insert("", "end", values=(
                m[0],
                m[1],
                m[7],
                m[3],
                m[2],
                m[4],
                f"${m[5]:,.2f}",
                f"${m[6]:,.2f}",
                m[8]
            ))

    def abrir_comprobante_ticket(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return

        item = self.tree.item(seleccion[0])
        valores = item.get("values", [])
        if not valores:
            return

        # Columna ticket: valores[2]
        ticket_id = str(valores[2]).strip()

        if not ticket_id or ticket_id == "-":
            messagebox.showinfo("Sin Comprobante", "Este movimiento no tiene un comprobante de venta asociado.")
            return

        # Directorio base
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        carpeta_comprobantes = os.path.join(base_dir, "comprobantes")
        if not os.path.exists(carpeta_comprobantes):
            messagebox.showwarning("Aviso", "La carpeta 'comprobantes' aún no existe.")
            return

        # Buscar cualquier PDF que contenga el identificador en su nombre
        archivo_encontrado = None
        for archivo in os.listdir(carpeta_comprobantes):
            if archivo.lower().endswith(".pdf") and ticket_id.lower() in archivo.lower():
                archivo_encontrado = os.path.join(carpeta_comprobantes, archivo)
                break

        if not archivo_encontrado:
            messagebox.showwarning(
                "Archivo no encontrado", 
                f"No se encontró un comprobante que contenga el ID:\n{ticket_id}"
            )
            return

        # Abrir archivo
        try:
            if sys.platform == "win32":
                os.startfile(archivo_encontrado)
            else:
                subprocess.call(["xdg-open", archivo_encontrado])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el comprobante: {e}")

    def scrollear_horizontal_rueda(self, event):
        """Permite mover la vista horizontalmente usando Shift + Rueda del ratón."""
        if event.delta:
            self.tree.xview_scroll(int(-1 * (event.delta / 120)), "units")
