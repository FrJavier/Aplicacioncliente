"""
controlador para la pantalla de login
"""

from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
from controllers.datos_controller import obtener_ruta_vista


class ControladorLogin(QDialog):
    """maneja la logica del login"""

    def __init__(self, datos):
        super().__init__()
        uic.loadUi(obtener_ruta_vista("login.ui"), self)
        self.datos = datos
        self.usuario_logueado = None

        # conecta eventos
        self.btn_login.clicked.connect(self.intentar_login)
        self.input_password.returnPressed.connect(self.intentar_login)

    def intentar_login(self):
        """valida las credenciales del usuario"""
        usuario = self.input_usuario.text().strip()
        password = self.input_password.text()

        if usuario == "" or password == "":
            self.lbl_error.setText("Completa todos los campos")
            return

        if usuario in self.datos["usuarios"]:
            if self.datos["usuarios"][usuario]["password"] == password:
                self.usuario_logueado = usuario
                self.accept()
            else:
                self.lbl_error.setText("Contrasena incorrecta")
        else:
            self.lbl_error.setText("Usuario no encontrado")
