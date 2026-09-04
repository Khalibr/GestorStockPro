from models.database import inicializar_base_de_datos
from views.login_view import LoginView
from views.main_view import MainView

def main():
    # 1. Asegurar base de datos lista
    inicializar_base_de_datos()

    # 2. Abrir Login y esperar a que el usuario se autentique
    login = LoginView()
    login.mainloop()

    # 3. Si el login fue exitoso, iniciar la aplicación principal sin conflictos
    if hasattr(login, "usuario_autenticado") and login.usuario_autenticado:
        app = MainView(usuario_activo=login.usuario_autenticado)
        app.mainloop()

if __name__ == "__main__":
    main()