"""
controlador para la vista de proyecto (tablero kanban)
"""

from PyQt5.QtWidgets import QWidget, QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5 import uic
from controllers.datos_controller import (
    obtener_ruta_vista, obtener_tareas_proyecto, crear_tarea,
    cambiar_estado_tarea, eliminar_tarea
)


class ControladorNuevaTarea(QDialog):
    """dialogo para crear nueva tarea con prioridad"""

    def __init__(self):
        super().__init__()
        uic.loadUi(obtener_ruta_vista("nuevatarea.ui"), self)
        # pone media como default
        self.comboPrioridad.setCurrentIndex(1)

    def obtener_datos(self):
        """devuelve titulo y prioridad seleccionados"""
        titulo = self.inputTitulo.text().strip()
        prioridad = self.comboPrioridad.currentText().lower()
        return titulo, prioridad


class ControladorProyecto(QWidget):
    """maneja el tablero kanban de un proyecto"""

    def __init__(self, proyecto, datos, funcion_volver):
        super().__init__()
        uic.loadUi(obtener_ruta_vista("proyecto.ui"), self)
        self.proyecto = proyecto
        self.datos = datos
        self.funcion_volver = funcion_volver

        # actualiza titulo
        self.lblProjectTitle.setText("Proyecto: " + proyecto["nombre"])

        # conecta botones
        self.btnExit.clicked.connect(self.volver)
        self.btnAddTodo.clicked.connect(self.agregar_tarea)

        # carga tareas
        self.cargar_tareas()

    def volver(self):
        """vuelve a la pantalla principal"""
        self.funcion_volver()

    def cargar_tareas(self):
        """carga las tareas en las columnas"""
        # limpia columnas - elimina solo los QFrame (tareas)
        self.limpiar_columna(self.vLayoutTodo)
        self.limpiar_columna(self.vLayoutDoing)
        self.limpiar_columna(self.vLayoutDone)

        # obtiene tareas del proyecto
        tareas = obtener_tareas_proyecto(self.datos, self.proyecto.get("id"))

        for tarea in tareas:
            widget = self.crear_widget_tarea(tarea)
            estado = tarea.get("estado", "pendiente")

            if estado == "pendiente":
                self.vLayoutTodo.insertWidget(1, widget)
            elif estado == "en_curso":
                self.vLayoutDoing.insertWidget(1, widget)
            else:
                self.vLayoutDone.insertWidget(1, widget)

    def limpiar_columna(self, layout):
        """elimina solo los widgets QFrame (tareas) de la columna, no los titulos"""
        # recorre de atras hacia adelante para evitar problemas de indices
        i = layout.count() - 1
        while i >= 0:
            item = layout.itemAt(i)
            if item is not None and item.widget() is not None:
                widget = item.widget()
                # solo elimina si es un QFrame y no es una columna principal
                nombre = widget.objectName()
                es_columna = nombre in ["colTodo", "colDoing", "colDone"]
                if isinstance(widget, QFrame) and not es_columna:
                    layout.takeAt(i)
                    widget.deleteLater()
            i = i - 1

    def crear_widget_tarea(self, tarea):
        """crea widget visual para una tarea"""
        # guarda el id
        tarea_id = tarea.get("id")

        # colores segun prioridad
        colores = {"alta": "#FF5252", "media": "#FFD740", "baja": "#69F0AE"}
        prioridad = tarea.get("prioridad", "media")
        color = colores.get(prioridad, "#FFD740")

        frame = QFrame()
        frame.setMinimumHeight(70)
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border-left: 5px solid """ + color + """;
                border-right: 1px solid #FCE4EC;
                border-top: 1px solid #FCE4EC;
                border-bottom: 1px solid #FCE4EC;
            }
            QFrame:hover { background-color: #FFF5F7; }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)

        # titulo
        etiqueta_titulo = QLabel(tarea.get("titulo", "Sin titulo"))
        etiqueta_titulo.setStyleSheet("font-weight: bold; color: #333;")
        etiqueta_titulo.setWordWrap(True)

        # botones
        layout_botones = QHBoxLayout()
        estado = tarea.get("estado", "pendiente")

        if estado == "pendiente":
            boton_accion = QPushButton("Iniciar")
            boton_accion.clicked.connect(self.crear_funcion_mover(tarea_id, "en_curso"))
        elif estado == "en_curso":
            boton_accion = QPushButton("Completar")
            boton_accion.clicked.connect(self.crear_funcion_mover(tarea_id, "completada"))
        else:
            boton_accion = None

        if boton_accion is not None:
            boton_accion.setStyleSheet("""
                QPushButton {
                    background-color: #D81B60;
                    color: white;
                    border-radius: 10px;
                    padding: 5px 10px;
                    font-size: 10px;
                }
                QPushButton:hover { background-color: #C2185B; }
            """)
            layout_botones.addWidget(boton_accion)

        boton_eliminar = QPushButton("Eliminar")
        boton_eliminar.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #999;
                border-radius: 10px;
                padding: 5px 10px;
                font-size: 10px;
            }
            QPushButton:hover { color: #D32F2F; }
        """)
        boton_eliminar.clicked.connect(self.crear_funcion_borrar(tarea_id))

        layout_botones.addWidget(boton_eliminar)
        layout_botones.addStretch()

        layout.addWidget(etiqueta_titulo)
        layout.addLayout(layout_botones)

        return frame

    def crear_funcion_mover(self, tarea_id, nuevo_estado):
        """crea una funcion para mover una tarea a un estado"""
        def funcion():
            self.mover_tarea(tarea_id, nuevo_estado)
        return funcion

    def crear_funcion_borrar(self, tarea_id):
        """crea una funcion para borrar una tarea"""
        def funcion():
            self.borrar_tarea(tarea_id)
        return funcion

    def mover_tarea(self, tarea_id, nuevo_estado):
        """cambia el estado de una tarea"""
        cambiar_estado_tarea(self.datos, tarea_id, nuevo_estado)
        self.cargar_tareas()

    def borrar_tarea(self, tarea_id):
        """elimina una tarea (la manda a papelera)"""
        eliminar_tarea(self.datos, tarea_id)
        self.cargar_tareas()

    def agregar_tarea(self):
        """abre dialogo para crear tarea"""
        dialogo = ControladorNuevaTarea()
        if dialogo.exec_() == QDialog.Accepted:
            titulo, prioridad = dialogo.obtener_datos()
            if titulo != "":
                crear_tarea(self.datos, titulo, self.proyecto.get("id"), prioridad)
                self.cargar_tareas()
