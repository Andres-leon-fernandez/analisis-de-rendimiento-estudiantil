"""
==================================================================
 GESTION DE CONFIGURACION
 Maneja la carga y guardado de umbrales de riesgo y pesos de
 notas en config.json.
==================================================================
"""

import json
import os

_RUTA_CONFIG = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

UMBRALES_PREDETERMINADOS = {
    "umbral_promedio_alto": 10.5,
    "umbral_promedio_medio": 13.0,
    "umbral_asistencia_alto": 70.0,
    "umbral_asistencia_medio": 80.0,
    "umbral_compromiso_alto": 60.0,
    "umbral_compromiso_medio": 65.0,
}


def _leer_config() -> dict:
    """Lee todo el archivo config.json. Retorna dict vacio si no existe."""
    if os.path.exists(_RUTA_CONFIG):
        try:
            with open(_RUTA_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, KeyError):
            pass
    return {}


def _escribir_config(datos: dict) -> None:
    """Escribe el dict completo en config.json."""
    with open(_RUTA_CONFIG, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


# ── Umbrales de riesgo ──

def cargar_umbrales() -> dict:
    """Carga los umbrales desde config.json. Si no existe, retorna valores predeterminados."""
    datos = _leer_config()
    umbrales = UMBRALES_PREDETERMINADOS.copy()
    umbrales.update(datos.get("umbrales_riesgo", {}))
    return umbrales


def guardar_umbrales(umbrales: dict) -> None:
    """Guarda los umbrales en config.json."""
    datos = _leer_config()
    datos["umbrales_riesgo"] = umbrales
    _escribir_config(datos)


def restablecer_umbrales() -> dict:
    """Restablece los umbrales a los valores predeterminados y los guarda."""
    guardar_umbrales(UMBRALES_PREDETERMINADOS)
    return UMBRALES_PREDETERMINADOS.copy()


# ── Pesos de notas ──

def cargar_pesos() -> dict:
    """Carga los pesos guardados. Retorna {columna: peso} o dict vacio."""
    datos = _leer_config()
    return datos.get("pesos_notas", {})


def guardar_pesos(pesos: dict) -> None:
    """Guarda los pesos de notas en config.json. Ej: {'nota_ep1': 0.20, ...}"""
    datos = _leer_config()
    datos["pesos_notas"] = pesos
    _escribir_config(datos)


def restablecer_pesos(columnas: list[str]) -> dict:
    """Restablece pesos a 1/n para las columnas dadas y los guarda."""
    n = len(columnas)
    pesos = {col: round(1.0 / n, 4) for col in columnas}
    pesos[columnas[-1]] = round(1.0 - sum(pesos[c] for c in columnas[:-1]), 4)
    guardar_pesos(pesos)
    return pesos
