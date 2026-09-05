import os
import customtkinter as ctk
from PIL import Image, ImageOps
from models.database import validar_credenciales
from tkinter import messagebox
from utils.rutas import ruta_recurso

class LoginView(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Ícono de la ventana
        ruta_ico = ruta_recurso(os.path.join("assets", "icons", "app.ico"))
        if os.path.exists(ruta_ico):
            self.iconbitmap(ruta_ico)
        # ...
        
        self.usuario_autenticado = None
        self.title("GestorStockPro - Iniciar Sesión")
        ancho, alto = 400, 520
        self.update_idletasks()
        pos_x = (self.winfo_screenwidth() - ancho) // 2
        pos_y = (self.winfo_screenheight() - alto) // 2
        self.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")
        self.resizable(False, False)

        # Paleta dinámica (Modo Claro, Modo Oscuro)
        self.color_bg = ("#F9F6F0", "#1C1C1E")
        self.color_primario = "#9B7EBD"
        self.color_primario_hover = "#8668A6"
        self.color_texto = ("#333333", "#EBEBF5")
        self.color_subtexto = ("#7C7C7C", "#8E8E93")
        self.color_hover_ojo = ("#EDE8F5", "#2C2C2E")
        self.color_error = "#D9534F"

        self.configure(fg_color=self.color_bg)

        self.cargar_iconos_pass()
        self.crear_componentes()
        self.vincular_eventos()

    def cargar_iconos_pass(self):
        ruta_ojo = ruta_recurso(os.path.join("assets", "icons", "eye.png"))
        ruta_ojo_closed = ruta_recurso(os.path.join("assets", "icons", "eye-closed.png"))

        def procesar(ruta):
            if not os.path.exists(ruta):
                return None
            img_negro = Image.open(ruta).convert("RGBA")
            r, g, b, a = img_negro.split()
            inverted = ImageOps.invert(Image.merge("RGB", (r, g, b)))
            r2, g2, b2 = inverted.split()
            img_blanco = Image.merge("RGBA", (r2, g2, b2, a))
            return ctk.CTkImage(light_image=img_negro, dark_image=img_blanco, size=(18, 18))

        self.icono_ojo = procesar(ruta_ojo)
        self.icono_ojo_closed = procesar(ruta_ojo_closed)

    def crear_componentes(self):
        self.lbl_titulo = ctk.CTkLabel(
            self, 
            text="GestorStockPro", 
            font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
            text_color=self.color_texto
        )
        self.lbl_titulo.pack(pady=(35, 10))

        self.lbl_sub = ctk.CTkLabel(
            self, 
            text="Inicia sesión para continuar", 
            font=ctk.CTkFont(family="Helvetica", size=13),
            text_color=self.color_subtexto
        )
        self.lbl_sub.pack(pady=(0, 15))

        self.lbl_mensaje = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            text_color=self.color_error
        )
        self.lbl_mensaje.pack(pady=(0, 10))

        self.entry_usuario = ctk.CTkEntry(
            self, 
            placeholder_text="Usuario", 
            width=280, 
            height=40,
            corner_radius=8
        )
        self.entry_usuario.pack(pady=8)

        # Contenedor Contraseña + Botón Ver/Ocultar
        frame_pass = ctk.CTkFrame(self, fg_color="transparent", width=280)
        frame_pass.pack(pady=8)

        self.entry_pass = ctk.CTkEntry(
            frame_pass, 
            placeholder_text="Contraseña", 
            width=235, 
            height=40,
            corner_radius=8,
            show="*"
        )
        self.entry_pass.pack(side="left", padx=(0, 5))

        self.btn_ojo_login = ctk.CTkButton(
            frame_pass,
            text="" if self.icono_ojo_closed else "👁",
            image=self.icono_ojo_closed,
            width=40,
            height=40,
            corner_radius=8,
            fg_color="transparent",
            hover_color=self.color_hover_ojo,
            command=self.toggle_pass_login
        )
        self.btn_ojo_login.pack(side="left")

        self.btn_ingresar = ctk.CTkButton(
            self, 
            text="Ingresar", 
            width=280, 
            height=40,
            corner_radius=8,
            fg_color=self.color_primario,
            hover_color=self.color_primario_hover,
            command=self.intentar_login
        )
        self.btn_ingresar.pack(pady=(20, 10))

        self.btn_recuperar = ctk.CTkButton(
            self,
            text="¿Olvidaste tu clave o no tienes cuenta?",
            font=ctk.CTkFont(family="Helvetica", size=11, underline=True),
            fg_color="transparent",
            text_color=self.color_subtexto,
            hover=False,
            command=self.accion_ayuda_cuenta
        )
        self.btn_recuperar.pack(pady=(0, 10))

        self.lbl_footer = ctk.CTkLabel(
            self, 
            text="Dev Khalibr - v1.0", 
            font=ctk.CTkFont(family="Helvetica", size=11),
            text_color=self.color_subtexto
        )
        self.lbl_footer.pack(side="bottom", pady=15)

    def toggle_pass_login(self):
        if self.entry_pass.cget("show") == "*":
            self.entry_pass.configure(show="")
            self.btn_ojo_login.configure(
                image=self.icono_ojo,
                text="" if self.icono_ojo else "🙈"
            )
        else:
            self.entry_pass.configure(show="*")
            self.btn_ojo_login.configure(
                image=self.icono_ojo_closed,
                text="" if self.icono_ojo_closed else "👁"
            )

    def vincular_eventos(self):
        self.bind("<Return>", lambda event: self.intentar_login())

    def intentar_login(self):
        usuario = self.entry_usuario.get().strip()
        password = self.entry_pass.get().strip()

        if not usuario or not password:
            self.lbl_mensaje.configure(
                text="Por favor, completa todos los campos.",
                text_color=self.color_error
            )
            return

        if validar_credenciales(usuario, password):
            self.lbl_mensaje.configure(
                text="¡Acceso concedido!", 
                text_color="#2E7D32"
            )
            self.usuario_autenticado = usuario
            self.quit()
            self.destroy()
        else:
            self.lbl_mensaje.configure(
                text="Usuario o contraseña incorrectos.", 
                text_color=self.color_error
            )

    def accion_ayuda_cuenta(self):
        messagebox.showinfo(
            "Acceso y Seguridad",
            "Por políticas de seguridad del comercio:\n\n"
            "• Para restablecer tu contraseña o solicitar una cuenta nueva, "
            "comunícate con el Administrador del sistema.\n"
            "• Las altas y modificaciones se gestionan únicamente desde el "
            "panel interno de Configuración."
        )

if __name__ == "__main__":
    app = LoginView()
    app.mainloop()