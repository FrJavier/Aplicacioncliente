"""
MyPlanner - Aplicacion de gestion de tareas estilo Trello
Credenciales admin: usuario=admin, contrasena=admin123
"""

import sys
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox,
    QLineEdit, QComboBox, QListWidget, QListWidgetItem, QTableWidgetItem
)
from PyQt5.QtCore import Qt, QDate
from PyQt5 import uic

# ruta base para los archivos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VISTAS_DIR = os.path.join(BASE_DIR, "vistas")
DATA_FILE = os.path.join(BASE_DIR, "datos.json")


def cargar_datos():
    """carga los datos desde el archivo json"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # datos por defecto
    return {
        "usuarios": {
            "admin": {"password": "admin123", "rol": "admin", "nombre": "Administrador"}
        },
        "proyectos": [],
        "tareas": [],
        "papelera": []
    }


def guardar_datos(datos):
    """guarda los datos en el archivo json"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


class LoginDialog(QDialog):
    """dialogo de inicio de sesion"""

    def __init__(self, datos):
        super().__init__()
        uic.loadUi(os.path.join(VISTAS_DIR, "login.ui"), self)
        self.datos = datos
        self.usuario_logueado = None

        # conecta el boton de login
        self.btn_login.clicked.connect(self.intentar_login)
        self.input_password.returnPressed.connect(self.intentar_login)

    def intentar_login(self):
        """verifica las credenciales del usuario"""
        usuario = self.input_usuario.text().strip()
        password = self.input_password.text()

        if not usuario or not password:
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


class AjustesDialog(QDialog):
    """dialogo de ajustes con opcion de cerrar sesion"""

    def __init__(self, usuario, datos):
        super().__init__()
        uic.loadUi(os.path.join(VISTAS_DIR, "ajustes.ui"), self)
        self.usuario = usuario
        self.datos = datos
        self.cerrar_sesion = False

        # muestra info del usuario actual
        info_usuario = self.datos["usuarios"][usuario]
        rol_texto = "Administrador" if info_usuario["rol"] == "admin" else "Usuario"
        self.lbl_usuario_actual.setText(f"Usuario actual: {usuario}")
        self.lbl_rol.setText(f"Rol: {rol_texto}")

        # conecta botones
        self.btn_cerrar_sesion.clicked.connect(self.hacer_logout)
        self.btn_volver.clicked.connect(self.reject)

    def hacer_logout(self):
        """marca que se debe cerrar sesion"""
        self.cerrar_sesion = True
        self.accept()


class NuevoProyectoDialog(QDialog):
    """dialogo para crear nuevo proyecto"""

    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(VISTAS_DIR, "nuevoproyecto.ui"), self)
        self.input_date.setDate(QDate.currentDate())

    def get_datos_proyecto(self):
        """retorna los datos del proyecto ingresados"""
        prioridad_texto = self.input_priority.currentText()
        # extrae solo el nivel de prioridad
        if "Alta" in prioridad_texto:
            prioridad = "alta"
        elif "Media" in prioridad_texto:
            prioridad = "media"
        else:
            prioridad = "baja"

        return {
            "nombre": self.input_name.text().strip(),
            "descripcion": self.input_desc.toPlainText().strip(),
            "fecha_limite": self.input_date.date().toString("yyyy-MM-dd"),
            "prioridad": prioridad,
            "participantes": []
        }


class RolesDialog(QDialog):
    """dialogo para gestionar usuarios y roles"""

    def __init__(self, datos, proyecto_id=None):
        super().__init__()
        uic.loadUi(os.path.join(VISTAS_DIR, "permisos.ui"), self)
        self.datos = datos
        self.proyecto_id = proyecto_id

        # cambia titulo si es gestion general
        if proyecto_id is None:
            self.label_title.setText("Gestion de Usuarios")
            self.label_subtitle.setText("Administra los usuarios del sistema:")

        # conecta boton de invitar
        self.btn_invite.clicked.connect(self.invitar_usuario)

        # carga usuarios en la tabla
        self.cargar_usuarios()

    def cargar_usuarios(self):
        """carga los usuarios en la tabla"""
        self.tableWidget.setRowCount(0)

        for usuario, info in self.datos["usuarios"].items():
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)

            self.tableWidget.setItem(row, 0, QTableWidgetItem(info.get("nombre", usuario)))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(usuario))

            # crea combobox para rol
            combo_rol = QComboBox()
            combo_rol.addItems(["Admin", "Usuario"])
            combo_rol.setCurrentText("Admin" if info["rol"] == "admin" else "Usuario")
            combo_rol.setProperty("usuario", usuario)
            self.tableWidget.setCellWidget(row, 2, combo_rol)

    def invitar_usuario(self):
        """abre dialogo para crear nuevo usuario"""
        dialogo = CrearUsuarioDialog(self.datos)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_usuarios()

    def accept(self):
        """guarda los cambios de roles"""
        for row in range(self.tableWidget.rowCount()):
            combo = self.tableWidget.cellWidget(row, 2)
            if combo:
                usuario = combo.property("usuario")
                nuevo_rol = "admin" if combo.currentText() == "Admin" else "user"
                if usuario in self.datos["usuarios"]:
                    self.datos["usuarios"][usuario]["rol"] = nuevo_rol

        guardar_datos(self.datos)
        super().accept()


class CrearUsuarioDialog(QDialog):
    """dialogo simple para crear usuario"""

    def __init__(self, datos):
        super().__init__()
        self.datos = datos
        self.setWindowTitle("Nuevo Usuario")
        self.setFixedSize(350, 300)
        self.setStyleSheet("background-color: #FFF0F5;")

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # campo nombre
        lbl_nombre = QLabel("Nombre:")
        lbl_nombre.setStyleSheet("font-weight: bold; color: #555;")
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre completo")
        self.input_nombre.setMinimumHeight(40)
        self.input_nombre.setStyleSheet(self.estilo_input())

        # campo usuario
        lbl_usuario = QLabel("Usuario:")
        lbl_usuario.setStyleSheet("font-weight: bold; color: #555;")
        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Nombre de usuario")
        self.input_usuario.setMinimumHeight(40)
        self.input_usuario.setStyleSheet(self.estilo_input())

        # campo password
        lbl_password = QLabel("Contrasena:")
        lbl_password.setStyleSheet("font-weight: bold; color: #555;")
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Contrasena")
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setMinimumHeight(40)
        self.input_password.setStyleSheet(self.estilo_input())

        # botones
        btn_layout = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setMinimumHeight(40)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                border-radius: 20px;
            }
            QPushButton:hover { background-color: #F0F0F0; }
        """)
        btn_cancelar.clicked.connect(self.reject)

        btn_crear = QPushButton("Crear Usuario")
        btn_crear.setMinimumHeight(40)
        btn_crear.setStyleSheet("""
            QPushButton {
                background-color: #D81B60;
                color: white;
                border-radius: 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #C2185B; }
        """)
        btn_crear.clicked.connect(self.crear_usuario)

        btn_layout.addWidget(btn_cancelar)
        btn_layout.addWidget(btn_crear)

        # agrega widgets al layout
        layout.addWidget(lbl_nombre)
        layout.addWidget(self.input_nombre)
        layout.addWidget(lbl_usuario)
        layout.addWidget(self.input_usuario)
        layout.addWidget(lbl_password)
        layout.addWidget(self.input_password)
        layout.addLayout(btn_layout)

    def estilo_input(self):
        """retorna el estilo para los inputs"""
        return """
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding-left: 15px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #D81B60;
            }
        """

    def crear_usuario(self):
        """crea el nuevo usuario"""
        nombre = self.input_nombre.text().strip()
        usuario = self.input_usuario.text().strip()
        password = self.input_password.text()

        if not nombre or not usuario or not password:
            QMessageBox.warning(self, "Error", "Completa todos los campos")
            return

        if usuario in self.datos["usuarios"]:
            QMessageBox.warning(self, "Error", "El usuario ya existe")
            return

        self.datos["usuarios"][usuario] = {
            "password": password,
            "rol": "user",
            "nombre": nombre
        }
        guardar_datos(self.datos)
        self.accept()


class ProyectoView(QWidget):
    """vista del tablero kanban de un proyecto"""

    def __init__(self, proyecto, datos, usuario, on_volver):
        super().__init__()
        uic.loadUi(os.path.join(VISTAS_DIR, "proyecto.ui"), self)
        self.proyecto = proyecto
        self.datos = datos
        self.usuario = usuario
        self.on_volver = on_volver

        # actualiza titulo
        self.lblProjectTitle.setText(f"✨ {proyecto['nombre']}")

        # conecta botones
        self.btnExit.clicked.connect(self.volver)
        self.btnAddTodo.clicked.connect(self.agregar_tarea)

        # carga tareas del proyecto
        self.cargar_tareas()

    def volver(self):
        """vuelve a la pantalla principal"""
        self.on_volver()

    def cargar_tareas(self):
        """carga las tareas en las columnas correspondientes"""
        # limpia columnas (excepto labels y spacers)
        self.limpiar_columna(self.vLayoutTodo, 2)
        self.limpiar_columna(self.vLayoutDoing, 1)
        self.limpiar_columna(self.vLayoutDone, 1)

        # filtra tareas de este proyecto
        tareas_proyecto = [t for t in self.datos["tareas"]
                          if t.get("proyecto_id") == self.proyecto.get("id")]

        for tarea in tareas_proyecto:
            widget_tarea = self.crear_widget_tarea(tarea)
            estado = tarea.get("estado", "pendiente")

            if estado == "pendiente":
                self.vLayoutTodo.insertWidget(1, widget_tarea)
            elif estado == "en_curso":
                self.vLayoutDoing.insertWidget(1, widget_tarea)
            else:
                self.vLayoutDone.insertWidget(1, widget_tarea)

    def limpiar_columna(self, layout, desde_index):
        """elimina widgets de tarea de una columna"""
        while layout.count() > desde_index + 1:
            item = layout.takeAt(desde_index)
            if item.widget():
                item.widget().deleteLater()

    def crear_widget_tarea(self, tarea):
        """crea un widget para mostrar una tarea"""
        frame = QFrame()
        frame.setMinimumHeight(60)
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #FCE4EC;
            }
            QFrame:hover {
                border: 1px solid #D81B60;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)

        lbl_titulo = QLabel(tarea.get("titulo", "Sin titulo"))
        lbl_titulo.setStyleSheet("font-weight: bold; color: #333;")
        lbl_titulo.setWordWrap(True)

        # botones de accion
        btn_layout = QHBoxLayout()

        estado = tarea.get("estado", "pendiente")

        if estado == "pendiente":
            btn_mover = QPushButton("Iniciar")
            btn_mover.clicked.connect(lambda: self.cambiar_estado(tarea, "en_curso"))
        elif estado == "en_curso":
            btn_mover = QPushButton("Completar")
            btn_mover.clicked.connect(lambda: self.cambiar_estado(tarea, "completada"))
        else:
            btn_mover = None

        if btn_mover:
            btn_mover.setStyleSheet("""
                QPushButton {
                    background-color: #D81B60;
                    color: white;
                    border-radius: 10px;
                    padding: 5px 10px;
                    font-size: 10px;
                }
                QPushButton:hover { background-color: #C2185B; }
            """)
            btn_layout.addWidget(btn_mover)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                border-radius: 10px;
                padding: 5px 10px;
                font-size: 10px;
            }
            QPushButton:hover { color: #D32F2F; }
        """)
        btn_eliminar.clicked.connect(lambda: self.eliminar_tarea(tarea))

        btn_layout.addWidget(btn_eliminar)
        btn_layout.addStretch()

        layout.addWidget(lbl_titulo)
        layout.addLayout(btn_layout)

        return frame

    def cambiar_estado(self, tarea, nuevo_estado):
        """cambia el estado de una tarea"""
        for t in self.datos["tareas"]:
            if t.get("id") == tarea.get("id"):
                t["estado"] = nuevo_estado
                break
        guardar_datos(self.datos)
        self.cargar_tareas()

    def eliminar_tarea(self, tarea):
        """mueve la tarea a la papelera"""
        self.datos["tareas"] = [t for t in self.datos["tareas"]
                                if t.get("id") != tarea.get("id")]
        tarea["eliminada_de"] = "proyecto"
        self.datos["papelera"].append(tarea)
        guardar_datos(self.datos)
        self.cargar_tareas()

    def agregar_tarea(self):
        """abre dialogo para agregar nueva tarea"""
        dialogo = NuevaTareaDialog()
        if dialogo.exec_() == QDialog.Accepted:
            nueva_tarea = {
                "id": len(self.datos["tareas"]) + len(self.datos["papelera"]) + 1,
                "titulo": dialogo.get_titulo(),
                "proyecto_id": self.proyecto.get("id"),
                "proyecto_nombre": self.proyecto.get("nombre"),
                "estado": "pendiente",
                "prioridad": "media"
            }
            self.datos["tareas"].append(nueva_tarea)
            guardar_datos(self.datos)
            self.cargar_tareas()


class NuevaTareaDialog(QDialog):
    """dialogo simple para crear tarea"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nueva Tarea")
        self.setFixedSize(350, 180)
        self.setStyleSheet("background-color: #FFF0F5;")

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        lbl = QLabel("Titulo de la tarea:")
        lbl.setStyleSheet("font-weight: bold; color: #555;")

        self.input_titulo = QLineEdit()
        self.input_titulo.setPlaceholderText("Escribe el titulo...")
        self.input_titulo.setMinimumHeight(40)
        self.input_titulo.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding-left: 15px;
                background-color: white;
            }
            QLineEdit:focus { border: 1px solid #D81B60; }
        """)

        btn_layout = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setMinimumHeight(40)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                border-radius: 20px;
            }
            QPushButton:hover { background-color: #F0F0F0; }
        """)
        btn_cancelar.clicked.connect(self.reject)

        btn_crear = QPushButton("Crear")
        btn_crear.setMinimumHeight(40)
        btn_crear.setStyleSheet("""
            QPushButton {
                background-color: #D81B60;
                color: white;
                border-radius: 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #C2185B; }
        """)
        btn_crear.clicked.connect(self.accept)

        btn_layout.addWidget(btn_cancelar)
        btn_layout.addWidget(btn_crear)

        layout.addWidget(lbl)
        layout.addWidget(self.input_titulo)
        layout.addLayout(btn_layout)

    def get_titulo(self):
        return self.input_titulo.text().strip()


class PapeleraView(QWidget):
    """vista de la papelera de reciclaje"""

    def __init__(self, datos, on_volver):
        super().__init__()
        uic.loadUi(os.path.join(VISTAS_DIR, "papeleradereciclaje.ui"), self)
        self.datos = datos
        self.on_volver = on_volver

        # conecta botones
        self.btnExit.clicked.connect(self.volver)
        self.btnRecover.clicked.connect(self.recuperar_tarea)
        self.btnDeleteForever.clicked.connect(self.eliminar_permanente)
        self.btnEmptyTrash.clicked.connect(self.vaciar_papelera)

        # carga tareas eliminadas
        self.cargar_papelera()

    def volver(self):
        self.on_volver()

    def cargar_papelera(self):
        """carga las tareas en la papelera"""
        self.listDeletedTasks.clear()

        for tarea in self.datos["papelera"]:
            texto = f"Tarea: {tarea.get('titulo', 'Sin titulo')}"
            if tarea.get("proyecto_nombre"):
                texto += f" (Proyecto: {tarea['proyecto_nombre']})"
            self.listDeletedTasks.addItem(texto)

        self.lblStatus.setText(f"{len(self.datos['papelera'])} tareas en la papelera")

    def recuperar_tarea(self):
        """recupera la tarea seleccionada"""
        row = self.listDeletedTasks.currentRow()
        if row >= 0 and row < len(self.datos["papelera"]):
            tarea = self.datos["papelera"].pop(row)
            tarea.pop("eliminada_de", None)
            self.datos["tareas"].append(tarea)
            guardar_datos(self.datos)
            self.cargar_papelera()

    def eliminar_permanente(self):
        """elimina permanentemente la tarea seleccionada"""
        row = self.listDeletedTasks.currentRow()
        if row >= 0 and row < len(self.datos["papelera"]):
            self.datos["papelera"].pop(row)
            guardar_datos(self.datos)
            self.cargar_papelera()

    def vaciar_papelera(self):
        """vacia toda la papelera"""
        if self.datos["papelera"]:
            resp = QMessageBox.question(
                self, "Confirmar",
                "Seguro que quieres vaciar la papelera?",
                QMessageBox.Yes | QMessageBox.No
            )
            if resp == QMessageBox.Yes:
                self.datos["papelera"] = []
                guardar_datos(self.datos)
                self.cargar_papelera()


class GestionProyectosDialog(QDialog):
    """dialogo para gestionar proyectos y participantes"""

    def __init__(self, datos, usuario):
        super().__init__()
        self.datos = datos
        self.usuario = usuario
        self.setWindowTitle("Gestion de Proyectos")
        self.setFixedSize(600, 500)
        self.setStyleSheet("background-color: #FFF0F5;")

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # titulo
        titulo = QLabel("Gestion de Proyectos")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #D81B60;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # lista de proyectos
        self.lista_proyectos = QListWidget()
        self.lista_proyectos.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #FCE4EC;
                border-radius: 10px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #FCE4EC;
            }
            QListWidget::item:selected {
                background-color: #FCE4EC;
                color: #D81B60;
            }
        """)
        self.lista_proyectos.itemClicked.connect(self.proyecto_seleccionado)
        layout.addWidget(self.lista_proyectos)

        # info participantes
        self.lbl_participantes = QLabel("Selecciona un proyecto para ver participantes")
        self.lbl_participantes.setStyleSheet("color: #666;")
        layout.addWidget(self.lbl_participantes)

        # combo para agregar participante
        h_layout = QHBoxLayout()
        self.combo_usuarios = QComboBox()
        self.combo_usuarios.setMinimumHeight(35)
        self.combo_usuarios.setStyleSheet("""
            QComboBox {
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding-left: 10px;
                background-color: white;
            }
        """)

        btn_agregar = QPushButton("Agregar")
        btn_agregar.setMinimumHeight(35)
        btn_agregar.setStyleSheet("""
            QPushButton {
                background-color: #D81B60;
                color: white;
                border-radius: 17px;
                padding: 0 15px;
            }
            QPushButton:hover { background-color: #C2185B; }
        """)
        btn_agregar.clicked.connect(self.agregar_participante)

        btn_quitar = QPushButton("Quitar")
        btn_quitar.setMinimumHeight(35)
        btn_quitar.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                border: 1px solid #CCC;
                border-radius: 17px;
                padding: 0 15px;
            }
            QPushButton:hover { color: #D32F2F; border-color: #D32F2F; }
        """)
        btn_quitar.clicked.connect(self.quitar_participante)

        h_layout.addWidget(self.combo_usuarios)
        h_layout.addWidget(btn_agregar)
        h_layout.addWidget(btn_quitar)
        layout.addLayout(h_layout)

        # botones principales
        btn_layout = QHBoxLayout()

        btn_nuevo = QPushButton("+ Nuevo Proyecto")
        btn_nuevo.setMinimumHeight(40)
        btn_nuevo.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #D81B60;
                border: 1px solid #D81B60;
                border-radius: 20px;
            }
            QPushButton:hover { background-color: #FCE4EC; }
        """)
        btn_nuevo.clicked.connect(self.crear_proyecto)

        btn_eliminar = QPushButton("Eliminar Proyecto")
        btn_eliminar.setMinimumHeight(40)
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                border-radius: 20px;
            }
            QPushButton:hover { color: #D32F2F; }
        """)
        btn_eliminar.clicked.connect(self.eliminar_proyecto)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setMinimumHeight(40)
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #D81B60;
                color: white;
                border-radius: 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #C2185B; }
        """)
        btn_cerrar.clicked.connect(self.accept)

        btn_layout.addWidget(btn_nuevo)
        btn_layout.addWidget(btn_eliminar)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cerrar)
        layout.addLayout(btn_layout)

        self.proyecto_actual = None
        self.cargar_proyectos()
        self.cargar_usuarios_combo()

    def cargar_proyectos(self):
        """carga la lista de proyectos"""
        self.lista_proyectos.clear()
        for proyecto in self.datos["proyectos"]:
            self.lista_proyectos.addItem(proyecto["nombre"])

    def cargar_usuarios_combo(self):
        """carga los usuarios en el combo"""
        self.combo_usuarios.clear()
        for usuario in self.datos["usuarios"].keys():
            self.combo_usuarios.addItem(usuario)

    def proyecto_seleccionado(self, item):
        """muestra info del proyecto seleccionado"""
        nombre = item.text()
        for proyecto in self.datos["proyectos"]:
            if proyecto["nombre"] == nombre:
                self.proyecto_actual = proyecto
                participantes = proyecto.get("participantes", [])
                if participantes:
                    self.lbl_participantes.setText(f"Participantes: {', '.join(participantes)}")
                else:
                    self.lbl_participantes.setText("Sin participantes asignados")
                break

    def agregar_participante(self):
        """agrega un participante al proyecto"""
        if not self.proyecto_actual:
            QMessageBox.warning(self, "Error", "Selecciona un proyecto primero")
            return

        usuario = self.combo_usuarios.currentText()
        if usuario:
            if "participantes" not in self.proyecto_actual:
                self.proyecto_actual["participantes"] = []

            if usuario not in self.proyecto_actual["participantes"]:
                self.proyecto_actual["participantes"].append(usuario)
                guardar_datos(self.datos)
                self.lbl_participantes.setText(
                    f"Participantes: {', '.join(self.proyecto_actual['participantes'])}"
                )

    def quitar_participante(self):
        """quita un participante del proyecto"""
        if not self.proyecto_actual:
            QMessageBox.warning(self, "Error", "Selecciona un proyecto primero")
            return

        usuario = self.combo_usuarios.currentText()
        if usuario and usuario in self.proyecto_actual.get("participantes", []):
            self.proyecto_actual["participantes"].remove(usuario)
            guardar_datos(self.datos)
            participantes = self.proyecto_actual.get("participantes", [])
            if participantes:
                self.lbl_participantes.setText(f"Participantes: {', '.join(participantes)}")
            else:
                self.lbl_participantes.setText("Sin participantes asignados")

    def crear_proyecto(self):
        """abre dialogo para crear proyecto"""
        dialogo = NuevoProyectoDialog()
        if dialogo.exec_() == QDialog.Accepted:
            datos_proyecto = dialogo.get_datos_proyecto()
            if datos_proyecto["nombre"]:
                datos_proyecto["id"] = len(self.datos["proyectos"]) + 1
                datos_proyecto["creador"] = self.usuario
                self.datos["proyectos"].append(datos_proyecto)
                guardar_datos(self.datos)
                self.cargar_proyectos()

    def eliminar_proyecto(self):
        """elimina el proyecto seleccionado"""
        if not self.proyecto_actual:
            QMessageBox.warning(self, "Error", "Selecciona un proyecto primero")
            return

        resp = QMessageBox.question(
            self, "Confirmar",
            f"Seguro que quieres eliminar '{self.proyecto_actual['nombre']}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if resp == QMessageBox.Yes:
            self.datos["proyectos"] = [
                p for p in self.datos["proyectos"]
                if p.get("id") != self.proyecto_actual.get("id")
            ]
            # elimina tareas asociadas
            self.datos["tareas"] = [
                t for t in self.datos["tareas"]
                if t.get("proyecto_id") != self.proyecto_actual.get("id")
            ]
            guardar_datos(self.datos)
            self.proyecto_actual = None
            self.lbl_participantes.setText("Selecciona un proyecto para ver participantes")
            self.cargar_proyectos()


class MainWindow(QMainWindow):
    """ventana principal de la aplicacion"""

    def __init__(self, usuario, datos):
        super().__init__()
        uic.loadUi(os.path.join(VISTAS_DIR, "pantallaprincipal.ui"), self)
        self.usuario = usuario
        self.datos = datos
        self.vista_actual = None

        # verifica si es admin
        self.es_admin = self.datos["usuarios"][usuario]["rol"] == "admin"

        # oculta boton de roles si no es admin
        if not self.es_admin:
            self.btn_calendar.hide()

        # actualiza saludo
        nombre = self.datos["usuarios"][usuario].get("nombre", usuario)
        self.label_welcome.setText(f"Hola, <b>{nombre}</b>")

        # conecta botones del sidebar
        self.btn_home.clicked.connect(self.mostrar_inicio)
        self.btn_board.clicked.connect(self.mostrar_proyectos)
        self.btn_calendar.clicked.connect(self.mostrar_roles)
        self.btn_settings.clicked.connect(self.mostrar_papelera)
        self.btn_ajustes.clicked.connect(self.mostrar_ajustes)
        self.btnAdd.clicked.connect(self.nueva_tarea_rapida)

        # carga tareas del usuario
        self.cargar_tareas_inicio()

    def cargar_tareas_inicio(self):
        """carga las tareas pendientes del usuario en el inicio"""
        # limpia el contenedor de tareas
        layout = self.scrollAreaWidgetContents.layout()

        # elimina widgets existentes excepto el spacer
        while layout.count() > 1:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # filtra tareas del usuario
        tareas_usuario = []
        for tarea in self.datos["tareas"]:
            proyecto_id = tarea.get("proyecto_id")
            # busca el proyecto
            for proyecto in self.datos["proyectos"]:
                if proyecto.get("id") == proyecto_id:
                    # verifica si el usuario es participante o creador
                    if (self.usuario in proyecto.get("participantes", []) or
                        proyecto.get("creador") == self.usuario or
                        self.es_admin):
                        tareas_usuario.append(tarea)
                    break

        # ordena por prioridad
        orden_prioridad = {"alta": 0, "media": 1, "baja": 2}
        tareas_usuario.sort(key=lambda t: orden_prioridad.get(t.get("prioridad", "media"), 1))

        # crea widgets para cada tarea
        for tarea in tareas_usuario:
            if tarea.get("estado") != "completada":
                widget = self.crear_widget_tarea_inicio(tarea)
                layout.insertWidget(layout.count() - 1, widget)

        if not tareas_usuario or all(t.get("estado") == "completada" for t in tareas_usuario):
            lbl = QLabel("No tienes tareas pendientes")
            lbl.setStyleSheet("color: #666; font-size: 14px;")
            lbl.setAlignment(Qt.AlignCenter)
            layout.insertWidget(0, lbl)

    def crear_widget_tarea_inicio(self, tarea):
        """crea un widget de tarea para la pantalla de inicio"""
        # colores segun prioridad
        colores = {
            "alta": "#FF5252",
            "media": "#FFD740",
            "baja": "#69F0AE"
        }
        etiquetas = {
            "alta": ("ALTA", "#FFEBEE", "#D32F2F"),
            "media": ("MEDIA", "#FFF8E1", "#FBC02D"),
            "baja": ("BAJA", "#E8F5E9", "#388E3C")
        }

        prioridad = tarea.get("prioridad", "media")
        color_borde = colores.get(prioridad, "#FFD740")
        etiqueta_info = etiquetas.get(prioridad, etiquetas["media"])

        frame = QFrame()
        frame.setMinimumHeight(80)
        frame.setCursor(Qt.PointingHandCursor)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border-left: 8px solid {color_borde};
                border-right: 1px solid #FCE4EC;
                border-top: 1px solid #FCE4EC;
                border-bottom: 1px solid #FCE4EC;
            }}
            QFrame:hover {{
                background-color: #FFF5F7;
            }}
        """)

        # guarda el id de la tarea para el click
        frame.setProperty("tarea_id", tarea.get("id"))
        frame.setProperty("proyecto_id", tarea.get("proyecto_id"))

        # hace clickeable el frame
        frame.mousePressEvent = lambda e: self.abrir_proyecto_tarea(tarea)

        layout = QHBoxLayout(frame)

        # contenido izquierdo
        v_layout = QVBoxLayout()

        lbl_titulo = QLabel(tarea.get("titulo", "Sin titulo"))
        lbl_titulo.setStyleSheet("""
            border: none;
            background: transparent;
            color: #333;
            font-weight: bold;
            font-size: 11px;
        """)

        # muestra el nombre del proyecto
        proyecto_nombre = tarea.get("proyecto_nombre", "")
        lbl_proyecto = QLabel(f"Proyecto: {proyecto_nombre}")
        lbl_proyecto.setStyleSheet("border: none; background: transparent; color: #888;")

        v_layout.addWidget(lbl_titulo)
        v_layout.addWidget(lbl_proyecto)

        # etiqueta de prioridad
        lbl_tag = QLabel(etiqueta_info[0])
        lbl_tag.setMaximumSize(80, 30)
        lbl_tag.setStyleSheet(f"""
            background-color: {etiqueta_info[1]};
            color: {etiqueta_info[2]};
            border: none;
            border-radius: 5px;
            padding: 5px;
            font-weight: bold;
        """)
        lbl_tag.setAlignment(Qt.AlignCenter)

        layout.addLayout(v_layout)
        layout.addWidget(lbl_tag)

        return frame

    def abrir_proyecto_tarea(self, tarea):
        """abre la vista del proyecto de una tarea"""
        proyecto_id = tarea.get("proyecto_id")
        for proyecto in self.datos["proyectos"]:
            if proyecto.get("id") == proyecto_id:
                self.mostrar_vista_proyecto(proyecto)
                break

    def mostrar_inicio(self):
        """muestra la pantalla de inicio"""
        self.resaltar_boton(self.btn_home)
        if self.vista_actual:
            self.vista_actual.hide()
            self.vista_actual.deleteLater()
            self.vista_actual = None
        self.scrollAreaTasks.show()
        self.label_welcome.show()
        self.label_subtitle.show()
        self.bottomBar.show()
        self.cargar_tareas_inicio()

    def mostrar_proyectos(self):
        """muestra dialogo de seleccion de proyectos"""
        self.resaltar_boton(self.btn_board)

        # si es admin, muestra gestion completa
        if self.es_admin:
            dialogo = GestionProyectosDialog(self.datos, self.usuario)
            dialogo.exec_()
            self.cargar_tareas_inicio()
        else:
            # muestra solo proyectos donde participa
            self.mostrar_lista_proyectos_usuario()

    def mostrar_lista_proyectos_usuario(self):
        """muestra lista de proyectos para usuario normal"""
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Mis Proyectos")
        dialogo.setFixedSize(400, 350)
        dialogo.setStyleSheet("background-color: #FFF0F5;")

        layout = QVBoxLayout(dialogo)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        titulo = QLabel("Mis Proyectos")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #D81B60;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        lista = QListWidget()
        lista.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #FCE4EC;
                border-radius: 10px;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #FCE4EC;
            }
            QListWidget::item:selected {
                background-color: #FCE4EC;
                color: #D81B60;
            }
        """)

        # filtra proyectos donde el usuario participa
        proyectos_usuario = []
        for proyecto in self.datos["proyectos"]:
            if (self.usuario in proyecto.get("participantes", []) or
                proyecto.get("creador") == self.usuario):
                proyectos_usuario.append(proyecto)
                lista.addItem(proyecto["nombre"])

        layout.addWidget(lista)

        btn_abrir = QPushButton("Abrir Proyecto")
        btn_abrir.setMinimumHeight(40)
        btn_abrir.setStyleSheet("""
            QPushButton {
                background-color: #D81B60;
                color: white;
                border-radius: 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #C2185B; }
        """)

        def abrir_seleccionado():
            row = lista.currentRow()
            if row >= 0 and row < len(proyectos_usuario):
                dialogo.accept()
                self.mostrar_vista_proyecto(proyectos_usuario[row])

        btn_abrir.clicked.connect(abrir_seleccionado)
        lista.itemDoubleClicked.connect(lambda: abrir_seleccionado())
        layout.addWidget(btn_abrir)

        dialogo.exec_()

    def mostrar_vista_proyecto(self, proyecto):
        """muestra la vista kanban de un proyecto"""
        self.scrollAreaTasks.hide()
        self.label_welcome.hide()
        self.label_subtitle.hide()
        self.bottomBar.hide()

        if self.vista_actual:
            self.vista_actual.deleteLater()

        self.vista_actual = ProyectoView(
            proyecto, self.datos, self.usuario, self.mostrar_inicio
        )
        self.centralwidget.layout().addWidget(self.vista_actual)

    def mostrar_roles(self):
        """muestra dialogo de gestion de roles (solo admin)"""
        if not self.es_admin:
            return

        self.resaltar_boton(self.btn_calendar)
        dialogo = RolesDialog(self.datos)
        dialogo.exec_()

    def mostrar_papelera(self):
        """muestra la papelera de reciclaje"""
        self.resaltar_boton(self.btn_settings)
        self.scrollAreaTasks.hide()
        self.label_welcome.hide()
        self.label_subtitle.hide()
        self.bottomBar.hide()

        if self.vista_actual:
            self.vista_actual.deleteLater()

        self.vista_actual = PapeleraView(self.datos, self.mostrar_inicio)
        self.centralwidget.layout().addWidget(self.vista_actual)

    def mostrar_ajustes(self):
        """muestra dialogo de ajustes"""
        dialogo = AjustesDialog(self.usuario, self.datos)
        if dialogo.exec_() == QDialog.Accepted:
            if dialogo.cerrar_sesion:
                self.close()
                # reinicia la app para mostrar login
                iniciar_app()

    def nueva_tarea_rapida(self):
        """crea una nueva tarea rapidamente"""
        # primero selecciona proyecto
        proyectos_usuario = []
        for proyecto in self.datos["proyectos"]:
            if (self.usuario in proyecto.get("participantes", []) or
                proyecto.get("creador") == self.usuario or
                self.es_admin):
                proyectos_usuario.append(proyecto)

        if not proyectos_usuario:
            QMessageBox.information(
                self, "Sin Proyectos",
                "No hay proyectos disponibles. Contacta al administrador."
            )
            return

        # dialogo para seleccionar proyecto y crear tarea
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Nueva Tarea")
        dialogo.setFixedSize(350, 250)
        dialogo.setStyleSheet("background-color: #FFF0F5;")

        layout = QVBoxLayout(dialogo)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        lbl_proyecto = QLabel("Proyecto:")
        lbl_proyecto.setStyleSheet("font-weight: bold; color: #555;")

        combo_proyecto = QComboBox()
        combo_proyecto.setMinimumHeight(35)
        combo_proyecto.setStyleSheet("""
            QComboBox {
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding-left: 10px;
                background-color: white;
            }
        """)
        for p in proyectos_usuario:
            combo_proyecto.addItem(p["nombre"])

        lbl_titulo = QLabel("Titulo:")
        lbl_titulo.setStyleSheet("font-weight: bold; color: #555;")

        input_titulo = QLineEdit()
        input_titulo.setPlaceholderText("Titulo de la tarea")
        input_titulo.setMinimumHeight(40)
        input_titulo.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding-left: 15px;
                background-color: white;
            }
            QLineEdit:focus { border: 1px solid #D81B60; }
        """)

        btn_crear = QPushButton("Crear Tarea")
        btn_crear.setMinimumHeight(40)
        btn_crear.setStyleSheet("""
            QPushButton {
                background-color: #D81B60;
                color: white;
                border-radius: 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #C2185B; }
        """)

        def crear():
            titulo = input_titulo.text().strip()
            if not titulo:
                return

            idx = combo_proyecto.currentIndex()
            proyecto = proyectos_usuario[idx]

            nueva_tarea = {
                "id": len(self.datos["tareas"]) + len(self.datos["papelera"]) + 1,
                "titulo": titulo,
                "proyecto_id": proyecto["id"],
                "proyecto_nombre": proyecto["nombre"],
                "estado": "pendiente",
                "prioridad": "media"
            }
            self.datos["tareas"].append(nueva_tarea)
            guardar_datos(self.datos)
            dialogo.accept()
            self.cargar_tareas_inicio()

        btn_crear.clicked.connect(crear)

        layout.addWidget(lbl_proyecto)
        layout.addWidget(combo_proyecto)
        layout.addWidget(lbl_titulo)
        layout.addWidget(input_titulo)
        layout.addWidget(btn_crear)

        dialogo.exec_()

    def resaltar_boton(self, boton_activo):
        """resalta el boton activo en el sidebar"""
        botones = [self.btn_home, self.btn_board, self.btn_calendar, self.btn_settings]

        for btn in botones:
            if btn == boton_activo:
                btn.setStyleSheet("""
                    background-color: #FCE4EC;
                    color: #D81B60;
                    border-radius: 10px;
                    text-align: left;
                    padding-left: 15px;
                    border: none;
                    font-weight: bold;
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #666;
                        border-radius: 10px;
                        text-align: left;
                        padding-left: 15px;
                    }
                    QPushButton:hover {
                        background-color: #F5F5F5;
                        color: #D81B60;
                    }
                """)


def iniciar_app():
    """inicia la aplicacion mostrando el login"""
    datos = cargar_datos()

    login = LoginDialog(datos)
    if login.exec_() == QDialog.Accepted:
        ventana = MainWindow(login.usuario_logueado, datos)
        ventana.show()
        return ventana
    return None


def main():
    """funcion principal"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    ventana = iniciar_app()

    if ventana:
        sys.exit(app.exec_())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
