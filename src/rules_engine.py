"""
==================================================================
 PARADIGMA LOGICO (Prolog via pyswip)
 Motor de reglas para clasificar el riesgo academico.
 Las reglas estan definidas en reglas_riesgo.pl y se consultan
 desde Python usando el bridge pyswip <-> SWI-Prolog.
 Los umbrales de riesgo son configurables via config.json.
==================================================================
"""

import os
from pyswip import Prolog
from src.config_manager import cargar_umbrales

_RUTA_PL = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reglas_riesgo.pl")
_prolog = Prolog()
_prolog.consult(_RUTA_PL)


def _cargar_umbrales_en_prolog(umbrales: dict) -> None:
    """Carga los umbrales de riesgo como hechos en la base de conocimiento Prolog."""
    try:
        _prolog.retractall("umbral_promedio_alto(_)")
        _prolog.retractall("umbral_promedio_medio(_)")
        _prolog.retractall("umbral_asistencia_alto(_)")
        _prolog.retractall("umbral_asistencia_medio(_)")
        _prolog.retractall("umbral_compromiso_alto(_)")
        _prolog.retractall("umbral_compromiso_medio(_)")
    except Exception:
        pass

    _prolog.assertz(f"umbral_promedio_alto({umbrales['umbral_promedio_alto']})")
    _prolog.assertz(f"umbral_promedio_medio({umbrales['umbral_promedio_medio']})")
    _prolog.assertz(f"umbral_asistencia_alto({umbrales['umbral_asistencia_alto']})")
    _prolog.assertz(f"umbral_asistencia_medio({umbrales['umbral_asistencia_medio']})")
    _prolog.assertz(f"umbral_compromiso_alto({umbrales['umbral_compromiso_alto']})")
    _prolog.assertz(f"umbral_compromiso_medio({umbrales['umbral_compromiso_medio']})")


def evaluar_reglas_riesgo(
    id_estudiante: str,
    promedio: float,
    asistencia: float,
    compromiso: float,
    umbrales: dict = None,
) -> str:
    """
    Motor de inferencia basado en Prolog.
    Carga los hechos del estudiante en la base de conocimiento,
    consulta las reglas definidas en reglas_riesgo.pl y retorna
    el nivel de riesgo: "Alto", "Medio" o "Bajo".
    
    Si se proporcionan umbrales, los usa; si no, carga los predeterminados.
    """
    if umbrales is None:
        umbrales = cargar_umbrales()

    _cargar_umbrales_en_prolog(umbrales)

    eid = id_estudiante.replace("'", "\\'")
    _prolog.assertz(f"estudiante_promedio('{eid}', {promedio})")
    _prolog.assertz(f"estudiante_asistencia('{eid}', {asistencia})")
    _prolog.assertz(f"estudiante_compromiso('{eid}', {compromiso})")

    try:
        if list(_prolog.query(f"riesgo_alto('{eid}')")):
            return "Alto"
        if list(_prolog.query(f"riesgo_medio('{eid}')")):
            return "Medio"
        if list(_prolog.query(f"riesgo_bajo('{eid}')")):
            return "Bajo"
        return "Medio"
    finally:
        _prolog.retractall(f"estudiante_promedio('{eid}', _)")
        _prolog.retractall(f"estudiante_asistencia('{eid}', _)")
        _prolog.retractall(f"estudiante_compromiso('{eid}', _)")


def generar_recomendacion(nivel_riesgo: str) -> str:
    """Regla adicional: recomendacion segun nivel de riesgo."""
    reglas_recomendacion = {
        "Alto": "Requiere tutoria academica inmediata y seguimiento semanal.",
        "Medio": "Se recomienda reforzar habitos de estudio y asistencia.",
        "Bajo": "Mantener el desempeno actual; sin acciones urgentes.",
    }
    return reglas_recomendacion.get(nivel_riesgo, "Sin recomendacion disponible.")
