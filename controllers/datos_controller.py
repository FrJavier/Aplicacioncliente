"""
controller para manejo de datos (json)
"""

import os
import json

# rutas de archivos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VISTAS_DIR = os.path.join(BASE_DIR, "vistas")
DATA_FILE = os.path.join(BASE_DIR, "datos.json")


def obtener_ruta_vista(nombre):
    """retorna la ruta completa de un archivo .ui"""
    return os.path.join(VISTAS_DIR, nombre)


def cargar_datos():
    """carga los datos desde el archivo json"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # datos por defecto con admin
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


# funciones para usuarios

def crear_usuario(datos, usuario, password, nombre):
    """crea un nuevo usuario normal"""
    if usuario in datos["usuarios"]:
        return False
    datos["usuarios"][usuario] = {
        "password": password,
        "rol": "user",
        "nombre": nombre
    }
    guardar_datos(datos)
    return True


def eliminar_usuario(datos, usuario):
    """elimina un usuario (no permite eliminar admin)"""
    if usuario == "admin":
        return False
    if usuario in datos["usuarios"]:
        del datos["usuarios"][usuario]
        # quita al usuario de todos los proyectos
        for proyecto in datos["proyectos"]:
            if usuario in proyecto.get("participantes", []):
                proyecto["participantes"].remove(usuario)
        guardar_datos(datos)
        return True
    return False


def es_admin(datos, usuario):
    """verifica si el usuario es admin"""
    if usuario in datos["usuarios"]:
        return datos["usuarios"][usuario]["rol"] == "admin"
    return False


def cambiar_rol_usuario(datos, usuario, nuevo_rol):
    """cambia el rol de un usuario (admin o user)"""
    if usuario == "admin":
        return False  # no permite cambiar al admin principal
    if usuario in datos["usuarios"]:
        datos["usuarios"][usuario]["rol"] = nuevo_rol
        guardar_datos(datos)
        return True
    return False


# funciones para proyectos

def crear_proyecto(datos, nombre, descripcion=""):
    """crea un nuevo proyecto"""
    nuevo_id = len(datos["proyectos"]) + 1
    proyecto = {
        "id": nuevo_id,
        "nombre": nombre,
        "descripcion": descripcion,
        "participantes": []
    }
    datos["proyectos"].append(proyecto)
    guardar_datos(datos)
    return proyecto


def eliminar_proyecto(datos, proyecto_id):
    """elimina un proyecto, sus tareas y las tareas de papelera"""
    datos["proyectos"] = [p for p in datos["proyectos"] if p.get("id") != proyecto_id]
    datos["tareas"] = [t for t in datos["tareas"] if t.get("proyecto_id") != proyecto_id]
    # tambien elimina las tareas de la papelera de este proyecto
    datos["papelera"] = [t for t in datos["papelera"] if t.get("proyecto_id") != proyecto_id]
    guardar_datos(datos)


def obtener_proyecto(datos, proyecto_id):
    """obtiene un proyecto por su id"""
    for proyecto in datos["proyectos"]:
        if proyecto.get("id") == proyecto_id:
            return proyecto
    return None


def obtener_proyectos_usuario(datos, usuario):
    """obtiene los proyectos donde participa un usuario (admins ven todos)"""
    # si es admin, ve todos los proyectos
    if es_admin(datos, usuario):
        return datos["proyectos"].copy()
    
    proyectos = []
    for proyecto in datos["proyectos"]:
        if usuario in proyecto.get("participantes", []):
            proyectos.append(proyecto)
    return proyectos


def asignar_usuario_proyecto(datos, usuario, proyecto_id):
    """asigna un usuario a un proyecto"""
    for proyecto in datos["proyectos"]:
        if proyecto.get("id") == proyecto_id:
            if "participantes" not in proyecto:
                proyecto["participantes"] = []
            if usuario not in proyecto["participantes"]:
                proyecto["participantes"].append(usuario)
                guardar_datos(datos)
                return True
    return False


def desasignar_usuario_proyecto(datos, usuario, proyecto_id):
    """quita un usuario de un proyecto"""
    for proyecto in datos["proyectos"]:
        if proyecto.get("id") == proyecto_id:
            if usuario in proyecto.get("participantes", []):
                proyecto["participantes"].remove(usuario)
                guardar_datos(datos)
                return True
    return False


# funciones para tareas

def crear_tarea(datos, titulo, proyecto_id, prioridad="media"):
    """crea una nueva tarea en un proyecto"""
    proyecto = obtener_proyecto(datos, proyecto_id)
    if not proyecto:
        return None

    nuevo_id = len(datos["tareas"]) + len(datos["papelera"]) + 1
    tarea = {
        "id": nuevo_id,
        "titulo": titulo,
        "proyecto_id": proyecto_id,
        "proyecto_nombre": proyecto["nombre"],
        "estado": "pendiente",
        "prioridad": prioridad
    }
    datos["tareas"].append(tarea)
    guardar_datos(datos)
    return tarea


def obtener_tareas_proyecto(datos, proyecto_id):
    """obtiene las tareas de un proyecto"""
    return [t for t in datos["tareas"] if t.get("proyecto_id") == proyecto_id]


def obtener_tareas_usuario(datos, usuario):
    """obtiene las tareas de los proyectos donde participa el usuario (admins ven todas)"""
    # si es admin, ve todas las tareas
    if es_admin(datos, usuario):
        tareas = datos["tareas"].copy()
    else:
        proyectos_ids = []
        for proyecto in datos["proyectos"]:
            if usuario in proyecto.get("participantes", []):
                proyectos_ids.append(proyecto.get("id"))

        tareas = []
        for tarea in datos["tareas"]:
            if tarea.get("proyecto_id") in proyectos_ids:
                tareas.append(tarea)

    # ordena por prioridad
    orden = {"alta": 0, "media": 1, "baja": 2}
    tareas.sort(key=lambda t: orden.get(t.get("prioridad", "media"), 1))
    return tareas


def cambiar_estado_tarea(datos, tarea_id, nuevo_estado):
    """cambia el estado de una tarea"""
    for tarea in datos["tareas"]:
        if tarea.get("id") == tarea_id:
            tarea["estado"] = nuevo_estado
            guardar_datos(datos)
            return True
    return False


def eliminar_tarea(datos, tarea_id):
    """mueve una tarea a la papelera"""
    for i, tarea in enumerate(datos["tareas"]):
        if tarea.get("id") == tarea_id:
            tarea_eliminada = datos["tareas"].pop(i)
            datos["papelera"].append(tarea_eliminada)
            guardar_datos(datos)
            return True
    return False


def recuperar_tarea(datos, indice):
    """recupera una tarea de la papelera (solo si el proyecto existe)"""
    if 0 <= indice < len(datos["papelera"]):
        tarea = datos["papelera"][indice]
        # verifica que el proyecto aun existe
        proyecto = obtener_proyecto(datos, tarea.get("proyecto_id"))
        if proyecto is None:
            # el proyecto fue borrado, no se puede recuperar
            return False
        tarea = datos["papelera"].pop(indice)
        datos["tareas"].append(tarea)
        guardar_datos(datos)
        return True
    return False


def eliminar_tarea_permanente(datos, indice):
    """elimina una tarea permanentemente de la papelera"""
    if 0 <= indice < len(datos["papelera"]):
        datos["papelera"].pop(indice)
        guardar_datos(datos)
        return True
    return False


def vaciar_papelera(datos):
    """vacia la papelera"""
    datos["papelera"] = []
    guardar_datos(datos)
