import os
import sys

# Agrega la carpeta raíz del proyecto al path de Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import customtkinter as ctk
from PIL import Image
from views.inventario_view import InventarioFrame

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MainView(ctk.CTk):
    def __init__(self, usuario_activo="admin"):
        super().__init__()

        self.usuario_activo = usuario_activo
        self.sidebar_expandido = True

        self.title("GestorStockPro - Panel Principal")
        self.geometry("1050x650")
        self.minsize(850, 500)

        # Paleta dinámica
        self.color_bg_app = ("#F9F6F0", "#1C1C1E")
        self.color_bg_header = ("#EDE8F5", "#2C2C2E")
        self.color_bg_sidebar = ("#F3EFEA", "#252528")
        self.color_card = ("#FFFFFF", "#2A2A2D")
        self.color_texto = ("#333333", "#EBEBF5")
        self.color_subtexto = ("#7C7C7C", "#8E8E93")

        self.configure(fg_color=self.color_bg_app)

        # Grilla
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=60)
        self.grid_columnconfigure(1, weight=1)

        self.cargar_recursos()
        self.crear_header()
        self.crear_sidebar()
        self.crear_area_trabajo()

    def cargar_recursos(self):
        """Carga iconos y genera automáticamente la versión blanca para modo oscuro."""
        from PIL import ImageOps

        self.iconos = {}
        iconos_map = {
            "box": "assets/icons/treasure-chest.png",
            "chart": "assets/icons/chart-bar-columns.png",
            "dollar": "assets/icons/dollar.png",
            "settings": "assets/icons/spanner.png",
            "theme": "assets/icons/brightness-half.png",
        }

        for clave, ruta in iconos_map.items():
            if os.path.exists(ruta):
                # 1. Imagen original (negra para el tema claro)
                img_dark_mode_asset = Image.open(ruta).convert("RGBA")

                # 2. Invertir solo los canales RGB manteniendo la transparencia alfa
                r, g, b, alpha = img_dark_mode_asset.split()
                rgb_image = Image.merge("RGB", (r, g, b))
                inverted_rgb = ImageOps.invert(rgb_image)
                r2, g2, b2 = inverted_rgb.split()
                img_white = Image.merge("RGBA", (r2, g2, b2, alpha))

                # 3. Asignar versión negra a light_image y blanca a dark_image
                self.iconos[clave] = ctk.CTkImage(
                    light_image=img_dark_mode_asset,
                    dark_image=img_white,
                    size=(20, 20)
                )
            else:
                self.iconos[clave] = None

    def crear_header(self):
        self.header_frame = ctk.CTkFrame(
            self, height=55, fg_color=self.color_bg_header, corner_radius=0
        )
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="new")
        self.header_frame.grid_propagate(False)

        # Lado izquierdo
        self.btn_toggle = ctk.CTkButton(
            self.header_frame,
            text="☰",
            width=40,
            height=35,
            fg_color="transparent",
            text_color=self.color_texto,
            hover_color=("#DDD7E8", "#3A3A3C"),
            font=ctk.CTkFont(size=20),
            command=self.toggle_sidebar
        )
        self.btn_toggle.pack(side="left", padx=(10, 15))

        self.lbl_negocio = ctk.CTkLabel(
            self.header_frame,
            text="GestorStockPro | Panel de Control",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color=self.color_texto
        )
        self.lbl_negocio.pack(side="left")

        # Lado derecho: Cerrar sesión anclado al borde exterior
        self.btn_logout = ctk.CTkButton(
            self.header_frame,
            text="Cerrar Sesión",
            width=100,
            height=32,
            corner_radius=6,
            fg_color="#D9534F",
            hover_color="#B53B37",
            command=self.cerrar_sesion
        )
        self.btn_logout.pack(side="right", padx=(10, 15))

        # Usuario activo al centro del bloque derecho
        self.lbl_usuario = ctk.CTkLabel(
            self.header_frame,
            text=f"Usuario: {self.usuario_activo}",
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color=self.color_subtexto
        )
        self.lbl_usuario.pack(side="right", padx=10)

        # Botón Tema primero a la izquierda del bloque derecho
        self.btn_tema = ctk.CTkButton(
            self.header_frame,
            text=" Modo",
            image=self.iconos.get("theme"),
            width=75,
            height=30,
            fg_color="transparent",
            text_color=self.color_texto,
            hover_color=("#DDD7E8", "#3A3A3C"),
            compound="left",
            command=self.cambiar_apariencia
        )
        self.btn_tema.pack(side="right", padx=(0, 10))

    def crear_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(
            self, width=210, fg_color=self.color_bg_sidebar, corner_radius=0
        )
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        self.btn_inventario = self.crear_boton_sidebar(
            "Inventario", self.iconos.get("box"), lambda: self.cambiar_vista("Inventario")
        )
        self.btn_inventario.pack(pady=(20, 5), padx=5, fill="x")

        self.btn_stock = self.crear_boton_sidebar(
            "Carga de Stock", self.iconos.get("chart"), lambda: self.cambiar_vista("Carga de Stock")
        )
        self.btn_stock.pack(pady=5, padx=5, fill="x")

        self.btn_ventas = self.crear_boton_sidebar(
            "Ventas", self.iconos.get("dollar"), lambda: self.cambiar_vista("Ventas")
        )
        self.btn_ventas.pack(pady=5, padx=5, fill="x")

        self.btn_config = self.crear_boton_sidebar(
            "Configuración", self.iconos.get("settings"), lambda: self.cambiar_vista("Configuración")
        )
        self.btn_config.pack(side="bottom", pady=20, padx=5, fill="x")

    def crear_boton_sidebar(self, texto, icono, comando):
        btn = ctk.CTkButton(
            self.sidebar_frame,
            text=f"  {texto}",
            image=icono,
            height=38,
            corner_radius=6,
            fg_color="transparent",
            text_color=self.color_texto,
            hover_color=("#E4DFD7", "#323236"),
            anchor="w",
            compound="left",
            font=ctk.CTkFont(family="Helvetica", size=13),
            command=comando
        )
        btn.texto_completo = f"  {texto}"
        return btn

    def crear_area_trabajo(self):
        self.contenido_frame = ctk.CTkFrame(
            self, fg_color=self.color_card, corner_radius=10
        )
        self.contenido_frame.grid(row=1, column=1, sticky="nsew", padx=15, pady=15)

        self.lbl_vista_actual = ctk.CTkLabel(
            self.contenido_frame,
            text="Bienvenido a GestorStockPro",
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=self.color_texto
        )
        self.lbl_vista_actual.pack(pady=(40, 10))

        self.lbl_desc_vista = ctk.CTkLabel(
            self.contenido_frame,
            text="Selecciona una opción del menú lateral para comenzar a operar.",
            font=ctk.CTkFont(family="Helvetica", size=14),
            text_color=self.color_subtexto
        )
        self.lbl_desc_vista.pack()

    def toggle_sidebar(self):
        botones = [self.btn_inventario, self.btn_stock, self.btn_ventas, self.btn_config]
        if self.sidebar_expandido:
            self.sidebar_frame.configure(width=60)
            for b in botones:
                b.configure(text="", anchor="center")
            self.sidebar_expandido = False
        else:
            self.sidebar_frame.configure(width=210)
            for b in botones:
                b.configure(text=b.texto_completo, anchor="w")
            self.sidebar_expandido = True

    def cambiar_vista(self, modulo: str):
        """Limpia el área central y renderiza la vista solicitada."""
        for widget in self.contenido_frame.winfo_children():
            widget.destroy()

        if modulo == "Inventario":
            self.vista_inventario = InventarioFrame(self.contenido_frame)
            self.vista_inventario.pack(fill="both", expand=True, padx=10, pady=10)
        else:
            # Placeholder temporal para las demás pantallas
            lbl_vista_actual = ctk.CTkLabel(
                self.contenido_frame,
                text=f"Módulo: {modulo}",
                font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
                text_color=self.color_texto
            )
            lbl_vista_actual.pack(pady=(40, 10))

            lbl_desc = ctk.CTkLabel(
                self.contenido_frame,
                text=f"Área operativa para la gestión de {modulo.lower()}.",
                font=ctk.CTkFont(family="Helvetica", size=14),
                text_color=self.color_subtexto
            )
            lbl_desc.pack()

    def cambiar_apariencia(self):
        modo = ctk.get_appearance_mode()
        nuevo_modo = "Dark" if modo == "Light" else "Light"
        ctk.set_appearance_mode(nuevo_modo)
        
        # Si la vista de inventario está montada, refresca sus estilos al instante
        if hasattr(self, 'vista_inventario') and self.vista_inventario.winfo_exists():
            self.vista_inventario.actualizar_estilos()

    def cerrar_sesion(self):
        self.destroy()
        from views.login_view import LoginView
        login = LoginView()
        login.mainloop()

if __name__ == "__main__":
    app = MainView()
    app.mainloop()