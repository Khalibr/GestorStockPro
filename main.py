import customtkinter as ctk
from models.database import inicializar_base_de_datos
from views.login_view import LoginView

def main():
    # Asegura que SQLite tenga todas las tablas listas
    inicializar_base_de_datos()

    # Inicia el flujo visual con el Login
    app = LoginView()
    app.mainloop()

if __name__ == "__main__":
    main()