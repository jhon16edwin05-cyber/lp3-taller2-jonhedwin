"""
Módulo de utilidades para la aplicación.
Contiene funciones auxiliares utilizadas en diferentes partes de la aplicación.
"""
import re
from datetime import datetime


def validar_correo(correo):
    """Valida que un correo electrónico tenga un formato válido."""
    if not isinstance(correo, str):
        return False

    patron = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.fullmatch(patron, correo.strip()))


def formatear_duracion(minutos):
    """Convierte una duración en minutos a formato hh:mm."""
    try:
        minutos = int(minutos)
    except (TypeError, ValueError):
        return "00:00"

    if minutos < 0:
        return "00:00"

    horas, minutos_restantes = divmod(minutos, 60)
    return f"{horas:02d}:{minutos_restantes:02d}"


def generar_slug(texto):
    """Genera un slug a partir de un texto."""
    if not texto:
        return ""

    slug = texto.strip().lower()
    slug = slug.replace(" ", "-")
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug


def obtener_año_actual():
    """Obtiene el año actual."""
    return datetime.now().year


def validar_año(año):
    """Valida que un año sea válido (no futuro y no muy antiguo)."""
    try:
        año = int(año)
    except (TypeError, ValueError):
        return False

    año_actual = obtener_año_actual()
    return 1900 <= año <= año_actual

