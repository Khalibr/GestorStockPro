from models.database import inicializar_base_de_datos
from views.login_view import LoginView
from views.main_view import MainView

def main():
    inicializar_base_de_datos()

    while True:
        login = LoginView()
        login.mainloop()

        usuario = getattr(login, "usuario_autenticado", None)
        if not usuario:
            break  # Si cerró la ventana con la 'X', termina el programa

        app = MainView(usuario_activo=usuario)
        app.mainloop()

        # Si en MainView no se presionó cerrar sesión, salir del ciclo
        if not getattr(app, "sesion_reiniciada", False):
            break

if __name__ == "__main__":
    main()