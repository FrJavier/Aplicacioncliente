"""
controlador para la ventana principal
"""

from PyQt5.QtWidgets import (
    QMainWindow, QDialog, QWidget, QFrame, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QListWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5 import uic
from controllers.datos_controller import (
    obtener_ruta_vista, es_admin, obtener_proyectos_usuario,
    obtener_tareas_usuario, obtener_proyecto, recuperar_tarea,
    eliminar_tarea_permanente, vaciar_papelera
)
from controllers.proyecto_controller import ControladorProyecto
from controllers.admin_controller import ControladorAdmin


class ControladorAjustes(QDialog):
    """dialogo de ajustes con cierre de sesion"""

    def __init__(self, usuario, datos):
        super().__init__()
        uic.loadUi(obtener_ruta_vista("ajustes.ui"), self)
        self.usuario = usuario
        self.datos = datos
        self.cerrar_sesion = False

        # muestra info del usuario
        info = self.datos["usuarios"][usuario]
        if info["rol"] == "admin":
            rol = "Administrador"
        else:
            rol = "Usuario"
        self.lbl_usuario_actual.setText("Usuario: " + usuario)
        self.lbl_rol.setText("Rol: " + rol)

        # conecta botones
        self.btn_cerrar_sesion.clicked.connect(self.hacer_logout)
        self.btn_volver.clicked.connect(self.reject)

    def hacer_logout(self):
        """marca cierre de sesion"""
        self.cerrar_sesion = True
        self.accept()


class ControladorPapelera(QWidget):
    """maneja la vista de papelera"""

    def __init__(self, datos, funcion_volver):
        super().__init__()
        uic.loadUi(obtener_ruta_vista("papeleradereciclaje.ui"), self)
        self.datos = datos
        self.funcion_volver = funcion_volver

        # conecta botones
        self.btnExit.clicked.connect(self.volver)
        self.btnRecover.clicked.connect(self.recuperar)
        self.btnDeleteForever.clicked.connect(self.eliminar)
        self.btnEmptyTrash.clicked.connect(self.vaciar)

        self.cargar_papelera()

    def volver(self):
        """vuelve a la pantalla principal"""
        self.funcion_volver()

    def cargar_papelera(self):
        """carga las tareas eliminadas"""
        self.listDeletedTasks.clear()
        for tarea in self.datos["papelera"]:
            titulo = tarea.get("titulo", "Sin titulo")
            proyecto = tarea.get("proyecto_nombre", "")
            texto = titulo + " - " + proyecto
            self.listDeletedTasks.addItem(texto)
        
        cantidad = len(self.datos["papelera"])
        self.lblStatus.setText(str(cantidad) + " tareas en papelera")

    def recuperar(self):
        """recupera tarea seleccionada"""
        fila = self.listDeletedTasks.currentRow()
        if fila >= 0:
            if recuperar_tarea(self.datos, fila):
                self.cargar_papelera()
            else:
                QMessageBox.warning(
                    self, "No se puede recuperar",
                    "El proyecto de esta tarea fue eliminado.\nLa tarea no puede ser recuperada."
                )
                self.cargar_papelera()

    def eliminar(self):
        """elimina permanentemente"""
        fila = self.listDeletedTasks.currentRow()
        if fila >= 0:
            eliminar_tarea_permanente(self.datos, fila)
            self.cargar_papelera()

    def vaciar(self):
        """vacia la papelera"""
        if len(self.datos["papelera"]) > 0:
            respuesta = QMessageBox.question(
                self, "Confirmar", "Vaciar papelera?",
                QMessageBox.Yes | QMessageBox.No
            )
            if respuesta == QMessageBox.Yes:
                vaciar_papelera(self.datos)
                self.cargar_papelera()


class ControladorPrincipal(QMainWindow):
    """maneja la ventana principal"""

    def __init__(self, usuario, datos, funcion_logout):
        super().__init__()
        uic.loadUi(obtener_ruta_vista("pantallaprincipal.ui"), self)
        self.usuario = usuario
        self.datos = datos
        self.funcion_logout = funcion_logout
        self.vista_actual = None
        self.es_admin = es_admin(datos, usuario)

        # oculta boton admin si no es admin
        if not self.es_admin:
            self.btn_calendar.hide()

        # saludo
        nombre = self.datos["usuarios"][usuario].get("nombre", usuario)
        self.label_welcome.setText("Hola, <b>" + nombre + "</b>")

        # conecta botones sidebar
        self.btn_home.clicked.connect(self.mostrar_inicio)
        self.btn_board.clicked.connect(self.mostrar_proyectos)
        self.btn_calendar.clicked.connect(self.mostrar_admin)
        self.btn_settings.clicked.connect(self.mostrar_papelera)
        self.btn_ajustes.clicked.connect(self.mostrar_ajustes)
        self.btnAdd.clicked.connect(self.ir_a_proyectos)

        # carga tareas
        self.cargar_tareas_inicio()

    def cargar_tareas_inicio(self):
        """carga las tareas del usuario en inicio"""
        layout = self.scrollAreaWidgetContents.layout()

        # limpia widgets existentes
        while layout.count() > 1:
            item = layout.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()

        # obtiene tareas del usuario
        todas_tareas = obtener_tareas_usuario(self.datos, self.usuario)

        # filtra solo pendientes y en curso
        tareas = []
        for tarea in todas_tareas:
            if tarea.get("estado") != "completada":
                tareas.append(tarea)

        if len(tareas) == 0:
            etiqueta = QLabel("No tienes tareas pendientes")
            etiqueta.setStyleSheet("color: #666; font-size: 14px;")
            etiqueta.setAlignment(Qt.AlignCenter)
            layout.insertWidget(0, etiqueta)
        else:
            for tarea in tareas:
                widget = self.crear_widget_tarea(tarea)
                layout.insertWidget(layout.count() - 1, widget)

    def crear_widget_tarea(self, tarea):
        """crea widget de tarea para inicio"""
        colores = {"alta": "#FF5252", "media": "#FFD740", "baja": "#69F0AE"}
        etiquetas = {
            "alta": ("ALTA", "#FFEBEE", "#D32F2F"),
            "media": ("MEDIA", "#FFF8E1", "#FBC02D"),
            "baja": ("BAJA", "#E8F5E9", "#388E3C")
        }

        prioridad = tarea.get("prioridad", "media")
        color = colores.get(prioridad, "#FFD740")
        etiqueta_info = etiquetas.get(prioridad, etiquetas["media"])

        frame = QFrame()
        frame.setMinimumHeight(80)
        frame.setCursor(Qt.PointingHandCursor)
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border-left: 8px solid """ + color + """;
                border-right: 1px solid #FCE4EC;
                border-top: 1px solid #FCE4EC;
                border-bottom: 1px solid #FCE4EC;
            }
            QFrame:hover { background-color: #FFF5F7; }
        """)

        # guarda el id del proyecto para usarlo al hacer click
        proyecto_id = tarea.get("proyecto_id")
        frame.mousePressEvent = self.crear_funcion_abrir_proyecto(proyecto_id)

        layout = QHBoxLayout(frame)

        layout_vertical = QVBoxLayout()
        etiqueta_titulo = QLabel(tarea.get("titulo", "Sin titulo"))
        etiqueta_titulo.setStyleSheet("border: none; background: transparent; color: #333; font-weight: bold;")

        etiqueta_proyecto = QLabel("Proyecto: " + tarea.get("proyecto_nombre", ""))
        etiqueta_proyecto.setStyleSheet("border: none; background: transparent; color: #888;")

        layout_vertical.addWidget(etiqueta_titulo)
        layout_vertical.addWidget(etiqueta_proyecto)

        etiqueta_prioridad = QLabel(etiqueta_info[0])
        etiqueta_prioridad.setMaximumSize(80, 30)
        etiqueta_prioridad.setStyleSheet("""
            background-color: """ + etiqueta_info[1] + """;
            color: """ + etiqueta_info[2] + """;
            border: none;
            border-radius: 5px;
            padding: 5px;
            font-weight: bold;
        """)
        etiqueta_prioridad.setAlignment(Qt.AlignCenter)

        layout.addLayout(layout_vertical)
        layout.addWidget(etiqueta_prioridad)

        return frame

    def crear_funcion_abrir_proyecto(self, proyecto_id):
        """crea una funcion para abrir un proyecto"""
        def funcion(evento):
            self.abrir_proyecto(proyecto_id)
        return funcion

    def abrir_proyecto(self, proyecto_id):
        """abre la vista de un proyecto"""
        proyecto = obtener_proyecto(self.datos, proyecto_id)
        if proyecto is not None:
            self.mostrar_vista_proyecto(proyecto)

    def mostrar_inicio(self):
        """muestra pantalla de inicio"""
        self.resaltar_boton(self.btn_home)
        if self.vista_actual is not None:
            self.vista_actual.hide()
            self.vista_actual.deleteLater()
            self.vista_actual = None
        self.scrollAreaTasks.show()
        self.label_welcome.show()
        self.label_subtitle.show()
        self.bottomBar.show()
        self.cargar_tareas_inicio()

    def mostrar_proyectos(self):
        """muestra lista de proyectos del usuario"""
        self.resaltar_boton(self.btn_board)

        # obtiene proyectos del usuario
        proyectos = obtener_proyectos_usuario(self.datos, self.usuario)

        if len(proyectos) == 0:
            QMessageBox.information(
                self, "Sin proyectos",
                "No estas asignado a ningun proyecto.\nContacta al administrador."
            )
            return

        # dialogo para seleccionar proyecto
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

        for proyecto in proyectos:
            lista.addItem(proyecto["nombre"])

        layout.addWidget(lista)

        boton_abrir = QPushButton("Abrir Proyecto")
        boton_abrir.setMinimumHeight(40)
        boton_abrir.setStyleSheet("""
            QPushButton {
                background-color: #D81B60;
                color: white;
                border-radius: 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #C2185B; }
        """)

        # guardamos referencia a self para usar en la funcion
        controlador = self

        def abrir():
            fila = lista.currentRow()
            if fila >= 0 and fila < len(proyectos):
                dialogo.accept()
                controlador.mostrar_vista_proyecto(proyectos[fila])

        boton_abrir.clicked.connect(abrir)
        lista.itemDoubleClicked.connect(abrir)
        layout.addWidget(boton_abrir)

        dialogo.exec_()

    def mostrar_vista_proyecto(self, proyecto):
        """muestra el tablero kanban de un proyecto"""
        self.scrollAreaTasks.hide()
        self.label_welcome.hide()
        self.label_subtitle.hide()
        self.bottomBar.hide()

        if self.vista_actual is not None:
            self.vista_actual.deleteLater()

        self.vista_actual = ControladorProyecto(proyecto, self.datos, self.mostrar_inicio)
        self.centralwidget.layout().addWidget(self.vista_actual)

    def mostrar_admin(self):
        """muestra panel de administracion (solo admin)"""
        if not self.es_admin:
            return
        self.resaltar_boton(self.btn_calendar)
        dialogo = ControladorAdmin(self.datos)
        dialogo.exec_()
        self.cargar_tareas_inicio()

    def mostrar_papelera(self):
        """muestra la papelera"""
        self.resaltar_boton(self.btn_settings)
        self.scrollAreaTasks.hide()
        self.label_welcome.hide()
        self.label_subtitle.hide()
        self.bottomBar.hide()

        if self.vista_actual is not None:
            self.vista_actual.deleteLater()

        self.vista_actual = ControladorPapelera(self.datos, self.mostrar_inicio)
        self.centralwidget.layout().addWidget(self.vista_actual)

    def mostrar_ajustes(self):
        """muestra ajustes"""
        dialogo = ControladorAjustes(self.usuario, self.datos)
        if dialogo.exec_() == QDialog.Accepted:
            if dialogo.cerrar_sesion:
                self.close()
                self.funcion_logout()

    def ir_a_proyectos(self):
        """va a la seccion de proyectos"""
        self.mostrar_proyectos()

    def resaltar_boton(self, activo):
        """resalta el boton activo"""
        botones = [self.btn_home, self.btn_board, self.btn_calendar, self.btn_settings]
        for boton in botones:
            if boton == activo:
                boton.setStyleSheet("""
                    background-color: #FCE4EC;
                    color: #D81B60;
                    border-radius: 10px;
                    text-align: left;
                    padding-left: 15px;
                    border: none;
                    font-weight: bold;
                """)
            else:
                boton.setStyleSheet("""
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
