import sys
import os
import customtkinter as ctk
from tkinter import messagebox

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.database import (
    obtener_config_comercio, 
    guardar_config_comercio, 
    cambiar_password_usuario, 
    crear_nuevo_operador
)

class ConfiguracionFrame(ctk.CTkFrame):
    def __init__(self, parent, usuario_activo="admin"):
        super().__init__(parent, fg_color="transparent")
        self.usuario_activo = usuario_activo

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_panel_comercio()
        self.crear_panel_seguridad()
        self.cargar_datos_comercio()

    def crear_panel_comercio(self):
        card = ctk.CTkFrame(self, fg_color=("white", "#2A2A2D"), corner_radius=12)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, 
            text="Datos del Comercio (Ticket)", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, pady=(20, 5), padx=20, sticky="w")

        es_admin = (self.usuario_activo == "admin")

        if es_admin:
            # VISTA ADMIN: Inputs editables
            ctk.CTkLabel(
                card, 
                text="Esta información figurará en el comprobante impreso.", 
                font=ctk.CTkFont(size=12), 
                text_color="gray"
            ).grid(row=1, column=0, pady=(0, 15), padx=20, sticky="w")

            self.txt_nombre = self.crear_campo(card, "Nombre Comercial", 2)
            self.txt_direccion = self.crear_campo(card, "Dirección del Local", 3)
            self.txt_telefono = self.crear_campo(card, "Teléfono de Contacto", 4)
            self.txt_cuit = self.crear_campo(card, "CUIT / RUT / Identificación", 5)
            self.txt_leyenda = self.crear_campo(card, "Mensaje al pie (Ej: Gracias por su compra)", 6)

            btn_guardar = ctk.CTkButton(
                card, 
                text="Guardar Cambios del Ticket", 
                height=38, 
                fg_color="#9B7EBD", 
                hover_color="#8668A6", 
                command=self.guardar_comercio
            )
            btn_guardar.grid(row=7, column=0, pady=(15, 20), padx=20, sticky="ew")

        else:
            # VISTA VENDEDOR: Tarjetas de solo lectura con Labels
            ctk.CTkLabel(
                card, 
                text="Ficha institucional del comercio (Solo lectura).", 
                font=ctk.CTkFont(size=12), 
                text_color="gray"
            ).grid(row=1, column=0, pady=(0, 15), padx=20, sticky="w")

            self.labels_comercio = {}
            campos_info = [
                ("nombre", "Nombre Comercial:", 2),
                ("direccion", "Dirección:", 3),
                ("telefono", "Teléfono:", 4),
                ("cuit", "Identificación Tributaria:", 5),
                ("leyenda", "Leyenda Ticket:", 6)
            ]

            for clave, etiqueta, fila in campos_info:
                contenedor = ctk.CTkFrame(card, fg_color=("#F3EFEA", "#202023"), corner_radius=8)
                contenedor.grid(row=fila, column=0, pady=5, padx=20, sticky="ew")
                contenedor.grid_columnconfigure(1, weight=1)

                ctk.CTkLabel(
                    contenedor, 
                    text=f"  {etiqueta}", 
                    font=ctk.CTkFont(size=12, weight="bold"), 
                    text_color="#8E8E93"
                ).grid(row=0, column=0, padx=(10, 5), pady=8, sticky="w")

                lbl_valor = ctk.CTkLabel(
                    contenedor, 
                    text="---", 
                    font=ctk.CTkFont(size=13)
                )
                lbl_valor.grid(row=0, column=1, padx=10, pady=8, sticky="e")
                self.labels_comercio[clave] = lbl_valor

    def crear_campo(self, parent, placeholder, fila):
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, height=35)
        entry.grid(row=fila, column=0, pady=6, padx=20, sticky="ew")
        return entry

    def cargar_datos_comercio(self):
        c = obtener_config_comercio()
        if self.usuario_activo == "admin":
            self.txt_nombre.insert(0, c["nombre"])
            self.txt_direccion.insert(0, c["direccion"])
            self.txt_telefono.insert(0, c["telefono"])
            self.txt_cuit.insert(0, c["cuit"])
            self.txt_leyenda.insert(0, c["leyenda"])
        else:
            self.labels_comercio["nombre"].configure(text=c.get("nombre", ""))
            self.labels_comercio["direccion"].configure(text=c.get("direccion", ""))
            self.labels_comercio["telefono"].configure(text=c.get("telefono", ""))
            self.labels_comercio["cuit"].configure(text=c.get("cuit", ""))
            self.labels_comercio["leyenda"].configure(text=c.get("leyenda", ""))

    def crear_panel_seguridad(self):
        card = ctk.CTkFrame(self, fg_color=("white", "#2A2A2D"), corner_radius=12)
        card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Seguridad y Usuarios", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=(20, 5), padx=20, sticky="w")
        ctk.CTkLabel(card, text=f"Sesión iniciada como: {self.usuario_activo}", font=ctk.CTkFont(size=12), text_color="#81C784").grid(row=1, column=0, pady=(0, 15), padx=20, sticky="w")

        # Cambio de password
        ctk.CTkLabel(card, text="Cambiar Contraseña", font=ctk.CTkFont(size=14, weight="bold")).grid(row=2, column=0, pady=(5, 5), padx=20, sticky="w")
        self.txt_pass_actual = ctk.CTkEntry(card, placeholder_text="Contraseña actual", show="*", height=35)
        self.txt_pass_actual.grid(row=3, column=0, pady=5, padx=20, sticky="ew")
        self.txt_pass_nueva = ctk.CTkEntry(card, placeholder_text="Nueva contraseña", show="*", height=35)
        self.txt_pass_nueva.grid(row=4, column=0, pady=5, padx=20, sticky="ew")

        btn_cambiar_pass = ctk.CTkButton(card, text="Actualizar Contraseña", height=35, fg_color="#4A4A4D", hover_color="#3A3A3D", command=self.cambiar_password)
        btn_cambiar_pass.grid(row=5, column=0, pady=(5, 20), padx=20, sticky="ew")

        # Crear nuevo usuario (solo visible si es admin)
        if self.usuario_activo == "admin":
            ctk.CTkLabel(card, text="Alta de Operador / Vendedor", font=ctk.CTkFont(size=14, weight="bold")).grid(row=6, column=0, pady=(10, 5), padx=20, sticky="w")
            self.txt_nuevo_user = ctk.CTkEntry(card, placeholder_text="Nuevo nombre de usuario", height=35)
            self.txt_nuevo_user.grid(row=7, column=0, pady=5, padx=20, sticky="ew")
            self.txt_nuevo_pass = ctk.CTkEntry(card, placeholder_text="Contraseña provisoria", show="*", height=35)
            self.txt_nuevo_pass.grid(row=8, column=0, pady=5, padx=20, sticky="ew")

            btn_crear_op = ctk.CTkButton(card, text="+ Registrar Nuevo Operador", height=35, fg_color="#2E7D32", hover_color="#256428", command=self.crear_operador)
            btn_crear_op.grid(row=9, column=0, pady=(5, 20), padx=20, sticky="ew")

    def guardar_comercio(self):
        ok = guardar_config_comercio(
            self.txt_nombre.get().strip(),
            self.txt_direccion.get().strip(),
            self.txt_telefono.get().strip(),
            self.txt_cuit.get().strip(),
            self.txt_leyenda.get().strip()
        )
        if ok:
            messagebox.showinfo("Éxito", "Datos comerciales guardados correctamente.")
        else:
            messagebox.showerror("Error", "No se pudo guardar la configuración.")

    def cambiar_password(self):
        p_act = self.txt_pass_actual.get().strip()
        p_nueva = self.txt_pass_nueva.get().strip()
        if not p_act or not p_nueva:
            messagebox.showwarning("Atención", "Completa ambos campos de contraseña.")
            return

        ok, msj = cambiar_password_usuario(self.usuario_activo, p_act, p_nueva)
        if ok:
            messagebox.showinfo("Éxito", msj)
            self.txt_pass_actual.delete(0, "end")
            self.txt_pass_nueva.delete(0, "end")
        else:
            messagebox.showerror("Error", msj)

    def crear_operador(self):
        u = self.txt_nuevo_user.get().strip()
        p = self.txt_nuevo_pass.get().strip()
        if not u or not p:
            messagebox.showwarning("Atención", "Debes ingresar usuario y contraseña.")
            return

        ok, msj = crear_nuevo_operador(u, p)
        if ok:
            messagebox.showinfo("Éxito", msj)
            self.txt_nuevo_user.delete(0, "end")
            self.txt_nuevo_pass.delete(0, "end")
        else:
            messagebox.showerror("Error", msj)