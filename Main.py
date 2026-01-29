"""
MyPlanner - Aplicacion de gestion de tareas estilo Trello

Credenciales admin:
    Usuario: admin
    Contrasena: admin123
"""

import sys
from PyQt5.QtWidgets import QApplication, QDialog
from controllers.datos_controller import cargar_datos
from controllers.login_controller import LoginController
from controllers.principal_controller import PrincipalController


class App:
    """clase principal de la aplicacion"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")
        self.ventana = None

    def iniciar(self):
        """inicia la aplicacion mostrando login"""
        datos = cargar_datos()

        login = LoginController(datos)
        if login.exec_() == QDialog.Accepted:
            self.ventana = PrincipalController(
                login.usuario_logueado,
                datos,
                self.reiniciar
            )
            self.ventana.show()
            return True
        return False

    def reiniciar(self):
        """reinicia la app para volver al login"""
        self.iniciar()

    def ejecutar(self):
        """ejecuta el loop principal"""
        if self.iniciar():
            sys.exit(self.app.exec_())
        else:
            sys.exit(0)


if __name__ == "__main__":
    aplicacion = App()
    aplicacion.ejecutar()
