import sys
import os
import customtkinter as ctk

# Ruta al modelo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.database import validar_credenciales
from views.main_view import MainView

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class LoginView(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("GestorStockPro - Iniciar Sesión")
        ancho, alto = 400, 520
        self.update_idletasks()
        pos_x = (self.winfo_screenwidth() - ancho) // 2
        pos_y = (self.winfo_screenheight() - alto) // 2
        self.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")
        self.resizable(False, False)

        # Paleta pastel
        self.bg_cremita = "#F9F6F0"
        self.color_primario = "#9B7EBD"
        self.color_primario_hover = "#8668A6"
        self.color_texto = "#333333"
        self.color_error = "#D9534F"

        self.configure(fg_color=self.bg_cremita)

        self.crear_componentes()
        self.vincular_eventos()

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
            text_color="#7C7C7C"
        )
        self.lbl_sub.pack(pady=(0, 15))

        # Etiqueta para avisos y errores
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

        self.entry_pass = ctk.CTkEntry(
            self, 
            placeholder_text="Contraseña", 
            width=280, 
            height=40,
            corner_radius=8,
            show="*"
        )
        self.entry_pass.pack(pady=8)

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
            text_color="#6A6A6A",
            hover=False,
            command=self.accion_ayuda_cuenta
        )
        self.btn_recuperar.pack(pady=(0, 10))

        self.lbl_footer = ctk.CTkLabel(
            self, 
            text="Dev Khalibr - v1.0", 
            font=ctk.CTkFont(family="Helvetica", size=11),
            text_color="#A0A0A0"
        )
        self.lbl_footer.pack(side="bottom", pady=15)

    def vincular_eventos(self):
        self.bind("<Return>", lambda event: self.intentar_login())

    def intentar_login(self):
        usuario = self.entry_usuario.get().strip()
        password = self.entry_pass.get().strip()

        # Debug en terminal para verificar captura
        print(f"Debug -> Usuario: '{usuario}' | Password: '{password}'")

        # 1. Campos obligatorios
        if not usuario or not password:
            self.lbl_mensaje.configure(
                text="Por favor, completa todos los campos.",
                text_color=self.color_error
            )
            return

        # 2. Validación en base de datos
        if validar_credenciales(usuario, password):
            self.lbl_mensaje.configure(
                text="¡Acceso concedido!", 
                text_color="#2E7D32"
            )
            # Destruye la ventana de login y abre el dashboard principal
            self.destroy()
            app_principal = MainView(usuario_activo=usuario)
            app_principal.mainloop()
        else:
            self.lbl_mensaje.configure(
                text="Usuario o contraseña incorrectos.", 
                text_color=self.color_error
            )

    def accion_ayuda_cuenta(self):
        self.lbl_mensaje.configure(
            text="Módulo de registro/recuperación en desarrollo.",
            text_color=self.color_texto
        )

if __name__ == "__main__":
    app = LoginView()
    app.mainloop()