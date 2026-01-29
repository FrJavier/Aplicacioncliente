"""
controller para el panel de administracion
"""

from PyQt5.QtWidgets import QDialog, QLineEdit, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QMessageBox
from PyQt5 import uic
from controllers.datos_controller import (
    obtener_ruta_vista, crear_usuario, eliminar_usuario, cambiar_rol_usuario,
    crear_proyecto, eliminar_proyecto, asignar_usuario_proyecto,
    desasignar_usuario_proyecto, guardar_datos
)


class CrearUsuarioDialog(QDialog):
    """dialogo simple para crear usuario"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nuevo Usuario")
        self.setFixedSize(320, 250)
        self.setStyleSheet("background-color: #FFF0F5;")

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # nombre
        layout.addWidget(QLabel("Nombre:"))
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre completo")
        self.input_nombre.setMinimumHeight(35)
        self.input_nombre.setStyleSheet(self.estilo_input())
        layout.addWidget(self.input_nombre)

        # usuario
        layout.addWidget(QLabel("Usuario:"))
        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Nombre de usuario")
        self.input_usuario.setMinimumHeight(35)
        self.input_usuario.setStyleSheet(self.estilo_input())
        layout.addWidget(self.input_usuario)

        # password
        layout.addWidget(QLabel("Contrasena:"))
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Contrasena")
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setMinimumHeight(35)
        self.input_password.setStyleSheet(self.estilo_input())
        layout.addWidget(self.input_password)

        # botones
        btn_layout = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setMinimumHeight(35)
        btn_cancelar.clicked.connect(self.reject)

        btn_crear = QPushButton("Crear")
        btn_crear.setMinimumHeight(35)
        btn_crear.setStyleSheet("""
            QPushButton {
                background-color: #D81B60;
                color: white;
                border-radius: 17px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #C2185B; }
        """)
        btn_crear.clicked.connect(self.accept)

        btn_layout.addWidget(btn_cancelar)
        btn_layout.addWidget(btn_crear)
        layout.addLayout(btn_layout)

    def estilo_input(self):
        return """
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding-left: 10px;
                background-color: white;
            }
        """

    def obtener_datos(self):
        """retorna nombre, usuario y password"""
        return (
            self.input_nombre.text().strip(),
            self.input_usuario.text().strip(),
            self.input_password.text()
        )


class CrearProyectoDialog(QDialog):
    """dialogo simple para crear proyecto"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nuevo Proyecto")
        self.setFixedSize(320, 180)
        self.setStyleSheet("background-color: #FFF0F5;")

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # nombre
        layout.addWidget(QLabel("Nombre del proyecto:"))
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre del proyecto")
        self.input_nombre.setMinimumHeight(35)
        self.input_nombre.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding-left: 10px;
                background-color: white;
            }
        """)
        layout.addWidget(self.input_nombre)

        # descripcion
        layout.addWidget(QLabel("Descripcion (opcional):"))
        self.input_desc = QLineEdit()
        self.input_desc.setPlaceholderText("Descripcion breve")
        self.input_desc.setMinimumHeight(35)
        self.input_desc.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding-left: 10px;
                background-color: white;
            }
        """)
        layout.addWidget(self.input_desc)

        # botones
        btn_layout = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setMinimumHeight(35)
        btn_cancelar.clicked.connect(self.reject)

        btn_crear = QPushButton("Crear")
        btn_crear.setMinimumHeight(35)
        btn_crear.setStyleSheet("""
            QPushButton {
                background-color: #D81B60;
                color: white;
                border-radius: 17px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #C2185B; }
        """)
        btn_crear.clicked.connect(self.accept)

        btn_layout.addWidget(btn_cancelar)
        btn_layout.addWidget(btn_crear)
        layout.addLayout(btn_layout)

    def obtener_datos(self):
        """retorna nombre y descripcion"""
        return self.input_nombre.text().strip(), self.input_desc.text().strip()


class AdminController(QDialog):
    """maneja el panel de administracion"""

    def __init__(self, datos):
        super().__init__()
        uic.loadUi(obtener_ruta_vista("admin.ui"), self)
        self.datos = datos

        # conecta botones de usuarios
        self.btnNuevoUsuario.clicked.connect(self.nuevo_usuario)
        self.btnEliminarUsuario.clicked.connect(self.borrar_usuario)
        self.btnHacerAdmin.clicked.connect(self.cambiar_rol)

        # conecta botones de proyectos
        self.btnNuevoProyecto.clicked.connect(self.nuevo_proyecto)
        self.btnEliminarProyecto.clicked.connect(self.borrar_proyecto)

        # conecta botones de asignacion
        self.btnAsignar.clicked.connect(self.asignar)
        self.btnDesasignar.clicked.connect(self.desasignar)
        self.comboProyecto.currentIndexChanged.connect(self.mostrar_participantes)

        # carga datos iniciales
        self.cargar_usuarios()
        self.cargar_proyectos()
        self.cargar_combos()

    def cargar_usuarios(self):
        """carga la lista de usuarios"""
        self.listaUsuarios.clear()
        for usuario, info in self.datos["usuarios"].items():
            rol = "Admin" if info["rol"] == "admin" else "Usuario"
            self.listaUsuarios.addItem(f"{info['nombre']} ({usuario}) - {rol}")

    def cargar_proyectos(self):
        """carga la lista de proyectos"""
        self.listaProyectos.clear()
        for proyecto in self.datos["proyectos"]:
            num_part = len(proyecto.get("participantes", []))
            self.listaProyectos.addItem(f"{proyecto['nombre']} ({num_part} participantes)")

    def cargar_combos(self):
        """carga los combos de asignacion"""
        # combo de proyectos
        self.comboProyecto.clear()
        for proyecto in self.datos["proyectos"]:
            self.comboProyecto.addItem(proyecto["nombre"], proyecto["id"])

        # combo de usuarios
        self.comboUsuario.clear()
        for usuario, info in self.datos["usuarios"].items():
            self.comboUsuario.addItem(f"{info['nombre']} ({usuario})", usuario)

        self.mostrar_participantes()

    def mostrar_participantes(self):
        """muestra los participantes del proyecto seleccionado"""
        self.listaParticipantes.clear()
        idx = self.comboProyecto.currentIndex()
        if idx >= 0 and idx < len(self.datos["proyectos"]):
            proyecto = self.datos["proyectos"][idx]
            for usuario in proyecto.get("participantes", []):
                if usuario in self.datos["usuarios"]:
                    nombre = self.datos["usuarios"][usuario]["nombre"]
                    self.listaParticipantes.addItem(f"{nombre} ({usuario})")

    def nuevo_usuario(self):
        """crea un nuevo usuario"""
        dialogo = CrearUsuarioDialog()
        if dialogo.exec_() == QDialog.Accepted:
            nombre, usuario, password = dialogo.obtener_datos()
            if nombre and usuario and password:
                if crear_usuario(self.datos, usuario, password, nombre):
                    self.cargar_usuarios()
                    self.cargar_combos()
                else:
                    QMessageBox.warning(self, "Error", "El usuario ya existe")
            else:
                QMessageBox.warning(self, "Error", "Completa todos los campos")

    def borrar_usuario(self):
        """elimina el usuario seleccionado"""
        row = self.listaUsuarios.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Selecciona un usuario")
            return

        # obtiene el nombre de usuario de la lista
        usuarios = list(self.datos["usuarios"].keys())
        if row < len(usuarios):
            usuario = usuarios[row]
            if usuario == "admin":
                QMessageBox.warning(self, "Error", "No se puede eliminar al admin")
                return

            resp = QMessageBox.question(
                self, "Confirmar",
                f"Eliminar usuario '{usuario}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if resp == QMessageBox.Yes:
                eliminar_usuario(self.datos, usuario)
                self.cargar_usuarios()
                self.cargar_combos()

    def cambiar_rol(self):
        """cambia el rol del usuario seleccionado"""
        row = self.listaUsuarios.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Selecciona un usuario")
            return

        usuarios = list(self.datos["usuarios"].keys())
        if row < len(usuarios):
            usuario = usuarios[row]
            if usuario == "admin":
                QMessageBox.warning(self, "Error", "No se puede cambiar el rol del admin principal")
                return

            # obtiene rol actual y lo cambia
            rol_actual = self.datos["usuarios"][usuario]["rol"]
            nuevo_rol = "user" if rol_actual == "admin" else "admin"
            rol_texto = "Admin" if nuevo_rol == "admin" else "Usuario"

            resp = QMessageBox.question(
                self, "Confirmar",
                f"Cambiar rol de '{usuario}' a {rol_texto}?",
                QMessageBox.Yes | QMessageBox.No
            )
            if resp == QMessageBox.Yes:
                cambiar_rol_usuario(self.datos, usuario, nuevo_rol)
                self.cargar_usuarios()

    def nuevo_proyecto(self):
        """crea un nuevo proyecto"""
        dialogo = CrearProyectoDialog()
        if dialogo.exec_() == QDialog.Accepted:
            nombre, desc = dialogo.obtener_datos()
            if nombre:
                crear_proyecto(self.datos, nombre, desc)
                self.cargar_proyectos()
                self.cargar_combos()
            else:
                QMessageBox.warning(self, "Error", "El nombre es obligatorio")

    def borrar_proyecto(self):
        """elimina el proyecto seleccionado"""
        row = self.listaProyectos.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Selecciona un proyecto")
            return

        if row < len(self.datos["proyectos"]):
            proyecto = self.datos["proyectos"][row]
            resp = QMessageBox.question(
                self, "Confirmar",
                f"Eliminar proyecto '{proyecto['nombre']}'?\nSe eliminaran todas sus tareas.",
                QMessageBox.Yes | QMessageBox.No
            )
            if resp == QMessageBox.Yes:
                eliminar_proyecto(self.datos, proyecto["id"])
                self.cargar_proyectos()
                self.cargar_combos()

    def asignar(self):
        """asigna un usuario al proyecto seleccionado"""
        proyecto_id = self.comboProyecto.currentData()
        usuario = self.comboUsuario.currentData()

        if proyecto_id and usuario:
            if asignar_usuario_proyecto(self.datos, usuario, proyecto_id):
                self.mostrar_participantes()
                self.cargar_proyectos()
            else:
                QMessageBox.information(self, "Info", "El usuario ya esta asignado")

    def desasignar(self):
        """quita un usuario del proyecto seleccionado"""
        proyecto_id = self.comboProyecto.currentData()
        usuario = self.comboUsuario.currentData()

        if proyecto_id and usuario:
            if desasignar_usuario_proyecto(self.datos, usuario, proyecto_id):
                self.mostrar_participantes()
                self.cargar_proyectos()
