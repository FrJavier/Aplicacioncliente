"""
controlador para el panel de administracion
"""

from PyQt5.QtWidgets import QDialog, QLineEdit, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QMessageBox
from PyQt5 import uic
from controllers.datos_controller import (
    obtener_ruta_vista, crear_usuario, eliminar_usuario, cambiar_rol_usuario,
    crear_proyecto, eliminar_proyecto, asignar_usuario_proyecto,
    desasignar_usuario_proyecto
)


class DialogoCrearUsuario(QDialog):
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
        self.entrada_nombre = QLineEdit()
        self.entrada_nombre.setPlaceholderText("Nombre completo")
        self.entrada_nombre.setMinimumHeight(35)
        self.entrada_nombre.setStyleSheet(self.estilo_entrada())
        layout.addWidget(self.entrada_nombre)

        # usuario
        layout.addWidget(QLabel("Usuario:"))
        self.entrada_usuario = QLineEdit()
        self.entrada_usuario.setPlaceholderText("Nombre de usuario")
        self.entrada_usuario.setMinimumHeight(35)
        self.entrada_usuario.setStyleSheet(self.estilo_entrada())
        layout.addWidget(self.entrada_usuario)

        # contrasena
        layout.addWidget(QLabel("Contrasena:"))
        self.entrada_contrasena = QLineEdit()
        self.entrada_contrasena.setPlaceholderText("Contrasena")
        self.entrada_contrasena.setEchoMode(QLineEdit.Password)
        self.entrada_contrasena.setMinimumHeight(35)
        self.entrada_contrasena.setStyleSheet(self.estilo_entrada())
        layout.addWidget(self.entrada_contrasena)

        # botones
        layout_botones = QHBoxLayout()
        boton_cancelar = QPushButton("Cancelar")
        boton_cancelar.setMinimumHeight(35)
        boton_cancelar.clicked.connect(self.reject)

        boton_crear = QPushButton("Crear")
        boton_crear.setMinimumHeight(35)
        boton_crear.setStyleSheet("""
            QPushButton {
                background-color: #D81B60;
                color: white;
                border-radius: 17px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #C2185B; }
        """)
        boton_crear.clicked.connect(self.accept)

        layout_botones.addWidget(boton_cancelar)
        layout_botones.addWidget(boton_crear)
        layout.addLayout(layout_botones)

    def estilo_entrada(self):
        """devuelve el estilo para los campos de texto"""
        return """
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding-left: 10px;
                background-color: white;
            }
        """

    def obtener_datos(self):
        """devuelve nombre, usuario y contrasena"""
        nombre = self.entrada_nombre.text().strip()
        usuario = self.entrada_usuario.text().strip()
        contrasena = self.entrada_contrasena.text()
        return nombre, usuario, contrasena


class DialogoCrearProyecto(QDialog):
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
        self.entrada_nombre = QLineEdit()
        self.entrada_nombre.setPlaceholderText("Nombre del proyecto")
        self.entrada_nombre.setMinimumHeight(35)
        self.entrada_nombre.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding-left: 10px;
                background-color: white;
            }
        """)
        layout.addWidget(self.entrada_nombre)

        # descripcion
        layout.addWidget(QLabel("Descripcion (opcional):"))
        self.entrada_descripcion = QLineEdit()
        self.entrada_descripcion.setPlaceholderText("Descripcion breve")
        self.entrada_descripcion.setMinimumHeight(35)
        self.entrada_descripcion.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding-left: 10px;
                background-color: white;
            }
        """)
        layout.addWidget(self.entrada_descripcion)

        # botones
        layout_botones = QHBoxLayout()
        boton_cancelar = QPushButton("Cancelar")
        boton_cancelar.setMinimumHeight(35)
        boton_cancelar.clicked.connect(self.reject)

        boton_crear = QPushButton("Crear")
        boton_crear.setMinimumHeight(35)
        boton_crear.setStyleSheet("""
            QPushButton {
                background-color: #D81B60;
                color: white;
                border-radius: 17px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #C2185B; }
        """)
        boton_crear.clicked.connect(self.accept)

        layout_botones.addWidget(boton_cancelar)
        layout_botones.addWidget(boton_crear)
        layout.addLayout(layout_botones)

    def obtener_datos(self):
        """devuelve nombre y descripcion"""
        nombre = self.entrada_nombre.text().strip()
        descripcion = self.entrada_descripcion.text().strip()
        return nombre, descripcion


class ControladorAdmin(QDialog):
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
        for usuario in self.datos["usuarios"]:
            info = self.datos["usuarios"][usuario]
            if info["rol"] == "admin":
                rol = "Admin"
            else:
                rol = "Usuario"
            texto = info["nombre"] + " (" + usuario + ") - " + rol
            self.listaUsuarios.addItem(texto)

    def cargar_proyectos(self):
        """carga la lista de proyectos"""
        self.listaProyectos.clear()
        for proyecto in self.datos["proyectos"]:
            participantes = proyecto.get("participantes", [])
            num_participantes = len(participantes)
            texto = proyecto["nombre"] + " (" + str(num_participantes) + " participantes)"
            self.listaProyectos.addItem(texto)

    def cargar_combos(self):
        """carga los combos de asignacion"""
        # combo de proyectos
        self.comboProyecto.clear()
        for proyecto in self.datos["proyectos"]:
            self.comboProyecto.addItem(proyecto["nombre"], proyecto["id"])

        # combo de usuarios
        self.comboUsuario.clear()
        for usuario in self.datos["usuarios"]:
            info = self.datos["usuarios"][usuario]
            texto = info["nombre"] + " (" + usuario + ")"
            self.comboUsuario.addItem(texto, usuario)

        self.mostrar_participantes()

    def mostrar_participantes(self):
        """muestra los participantes del proyecto seleccionado"""
        self.listaParticipantes.clear()
        indice = self.comboProyecto.currentIndex()
        
        if indice >= 0 and indice < len(self.datos["proyectos"]):
            proyecto = self.datos["proyectos"][indice]
            participantes = proyecto.get("participantes", [])
            
            for usuario in participantes:
                if usuario in self.datos["usuarios"]:
                    nombre = self.datos["usuarios"][usuario]["nombre"]
                    texto = nombre + " (" + usuario + ")"
                    self.listaParticipantes.addItem(texto)

    def nuevo_usuario(self):
        """crea un nuevo usuario"""
        dialogo = DialogoCrearUsuario()
        if dialogo.exec_() == QDialog.Accepted:
            nombre, usuario, contrasena = dialogo.obtener_datos()
            
            if nombre != "" and usuario != "" and contrasena != "":
                if crear_usuario(self.datos, usuario, contrasena, nombre):
                    self.cargar_usuarios()
                    self.cargar_combos()
                else:
                    QMessageBox.warning(self, "Error", "El usuario ya existe")
            else:
                QMessageBox.warning(self, "Error", "Completa todos los campos")

    def borrar_usuario(self):
        """elimina el usuario seleccionado"""
        fila = self.listaUsuarios.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona un usuario")
            return

        # obtiene el nombre de usuario de la lista
        lista_usuarios = list(self.datos["usuarios"].keys())
        if fila < len(lista_usuarios):
            usuario = lista_usuarios[fila]
            
            if usuario == "admin":
                QMessageBox.warning(self, "Error", "No se puede eliminar al admin")
                return

            respuesta = QMessageBox.question(
                self, "Confirmar",
                "Eliminar usuario '" + usuario + "'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if respuesta == QMessageBox.Yes:
                eliminar_usuario(self.datos, usuario)
                self.cargar_usuarios()
                self.cargar_combos()

    def cambiar_rol(self):
        """cambia el rol del usuario seleccionado"""
        fila = self.listaUsuarios.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona un usuario")
            return

        lista_usuarios = list(self.datos["usuarios"].keys())
        if fila < len(lista_usuarios):
            usuario = lista_usuarios[fila]
            
            if usuario == "admin":
                QMessageBox.warning(self, "Error", "No se puede cambiar el rol del admin principal")
                return

            # obtiene rol actual y lo cambia
            rol_actual = self.datos["usuarios"][usuario]["rol"]
            if rol_actual == "admin":
                nuevo_rol = "user"
                rol_texto = "Usuario"
            else:
                nuevo_rol = "admin"
                rol_texto = "Admin"

            respuesta = QMessageBox.question(
                self, "Confirmar",
                "Cambiar rol de '" + usuario + "' a " + rol_texto + "?",
                QMessageBox.Yes | QMessageBox.No
            )
            if respuesta == QMessageBox.Yes:
                cambiar_rol_usuario(self.datos, usuario, nuevo_rol)
                self.cargar_usuarios()

    def nuevo_proyecto(self):
        """crea un nuevo proyecto"""
        dialogo = DialogoCrearProyecto()
        if dialogo.exec_() == QDialog.Accepted:
            nombre, descripcion = dialogo.obtener_datos()
            
            if nombre != "":
                crear_proyecto(self.datos, nombre, descripcion)
                self.cargar_proyectos()
                self.cargar_combos()
            else:
                QMessageBox.warning(self, "Error", "El nombre es obligatorio")

    def borrar_proyecto(self):
        """elimina el proyecto seleccionado"""
        fila = self.listaProyectos.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona un proyecto")
            return

        if fila < len(self.datos["proyectos"]):
            proyecto = self.datos["proyectos"][fila]
            respuesta = QMessageBox.question(
                self, "Confirmar",
                "Eliminar proyecto '" + proyecto["nombre"] + "'?\nSe eliminaran todas sus tareas.",
                QMessageBox.Yes | QMessageBox.No
            )
            if respuesta == QMessageBox.Yes:
                eliminar_proyecto(self.datos, proyecto["id"])
                self.cargar_proyectos()
                self.cargar_combos()

    def asignar(self):
        """asigna un usuario al proyecto seleccionado"""
        proyecto_id = self.comboProyecto.currentData()
        usuario = self.comboUsuario.currentData()

        if proyecto_id is not None and usuario is not None:
            if asignar_usuario_proyecto(self.datos, usuario, proyecto_id):
                self.mostrar_participantes()
                self.cargar_proyectos()
            else:
                QMessageBox.information(self, "Info", "El usuario ya esta asignado")

    def desasignar(self):
        """quita un usuario del proyecto seleccionado"""
        proyecto_id = self.comboProyecto.currentData()
        usuario = self.comboUsuario.currentData()

        if proyecto_id is not None and usuario is not None:
            if desasignar_usuario_proyecto(self.datos, usuario, proyecto_id):
                self.mostrar_participantes()
                self.cargar_proyectos()
