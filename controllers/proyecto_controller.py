"""
controller para la vista de proyecto (tablero kanban)
"""

from PyQt5.QtWidgets import QWidget, QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5 import uic
from controllers.datos_controller import (
    obtener_ruta_vista, obtener_tareas_proyecto, crear_tarea,
    cambiar_estado_tarea, eliminar_tarea, guardar_datos
)


class NuevaTareaController(QDialog):
    """dialogo para crear nueva tarea con prioridad"""

    def __init__(self):
        super().__init__()
        uic.loadUi(obtener_ruta_vista("nuevatarea.ui"), self)
        # pone media como default
        self.comboPrioridad.setCurrentIndex(1)

    def obtener_datos(self):
        """retorna titulo y prioridad seleccionados"""
        titulo = self.inputTitulo.text().strip()
        prioridad = self.comboPrioridad.currentText().lower()
        return titulo, prioridad


class ProyectoController(QWidget):
    """maneja el tablero kanban de un proyecto"""

    def __init__(self, proyecto, datos, on_volver):
        super().__init__()
        uic.loadUi(obtener_ruta_vista("proyecto.ui"), self)
        self.proyecto = proyecto
        self.datos = datos
        self.on_volver = on_volver

        # actualiza titulo
        self.lblProjectTitle.setText(f"✨ {proyecto['nombre']}")

        # conecta botones
        self.btnExit.clicked.connect(self.volver)
        self.btnAddTodo.clicked.connect(self.agregar_tarea)

        # carga tareas
        self.cargar_tareas()

    def volver(self):
        """vuelve a la pantalla principal"""
        self.on_volver()

    def cargar_tareas(self):
        """carga las tareas en las columnas"""
        # limpia columnas
        self.limpiar_columna(self.vLayoutTodo, 2)
        self.limpiar_columna(self.vLayoutDoing, 1)
        self.limpiar_columna(self.vLayoutDone, 1)

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

    def limpiar_columna(self, layout, desde):
        """elimina widgets de tarea de la columna"""
        while layout.count() > desde + 1:
            item = layout.takeAt(desde)
            if item.widget():
                item.widget().deleteLater()

    def crear_widget_tarea(self, tarea):
        """crea widget visual para una tarea"""
        # guarda el id para evitar problemas con lambda
        tarea_id = tarea.get("id")

        # colores segun prioridad
        colores = {"alta": "#FF5252", "media": "#FFD740", "baja": "#69F0AE"}
        color = colores.get(tarea.get("prioridad", "media"), "#FFD740")

        frame = QFrame()
        frame.setMinimumHeight(70)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                border-left: 5px solid {color};
                border-right: 1px solid #FCE4EC;
                border-top: 1px solid #FCE4EC;
                border-bottom: 1px solid #FCE4EC;
            }}
            QFrame:hover {{ background-color: #FFF5F7; }}
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)

        # titulo
        lbl_titulo = QLabel(tarea.get("titulo", "Sin titulo"))
        lbl_titulo.setStyleSheet("font-weight: bold; color: #333;")
        lbl_titulo.setWordWrap(True)

        # botones
        btn_layout = QHBoxLayout()
        estado = tarea.get("estado", "pendiente")

        if estado == "pendiente":
            btn_accion = QPushButton("Iniciar")
            btn_accion.clicked.connect(lambda checked, tid=tarea_id: self.mover_tarea(tid, "en_curso"))
        elif estado == "en_curso":
            btn_accion = QPushButton("Completar")
            btn_accion.clicked.connect(lambda checked, tid=tarea_id: self.mover_tarea(tid, "completada"))
        else:
            btn_accion = None

        if btn_accion:
            btn_accion.setStyleSheet("""
                QPushButton {
                    background-color: #D81B60;
                    color: white;
                    border-radius: 10px;
                    padding: 5px 10px;
                    font-size: 10px;
                }
                QPushButton:hover { background-color: #C2185B; }
            """)
            btn_layout.addWidget(btn_accion)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #999;
                border-radius: 10px;
                padding: 5px 10px;
                font-size: 10px;
            }
            QPushButton:hover { color: #D32F2F; }
        """)
        btn_eliminar.clicked.connect(lambda checked, tid=tarea_id: self.borrar_tarea(tid))

        btn_layout.addWidget(btn_eliminar)
        btn_layout.addStretch()

        layout.addWidget(lbl_titulo)
        layout.addLayout(btn_layout)

        return frame

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
        dialogo = NuevaTareaController()
        if dialogo.exec_() == QDialog.Accepted:
            titulo, prioridad = dialogo.obtener_datos()
            if titulo:
                crear_tarea(self.datos, titulo, self.proyecto.get("id"), prioridad)
                self.cargar_tareas()
