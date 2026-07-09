"""
==================================================================
 PARADIGMA LÓGICO
 Motor de reglas "si-entonces" para clasificar el riesgo académico.
 Inspirado en sistemas expertos basados en reglas.
==================================================================
"""


def evaluar_reglas_riesgo(
    promedio: float, asistencia: float, compromiso: float
) -> str:
    """
    Motor de inferencia basado en reglas lógicas (si-entonces).
    Evalúa condiciones en orden de severidad y retorna el nivel
    de riesgo académico: "Alto", "Medio" o "Bajo".
    """
    # Regla 1: riesgo alto
    if promedio < 10.5 and asistencia < 70:
        return "Alto"
    if promedio < 10.5 and compromiso < 60:
        return "Alto"

    # Regla 2: riesgo medio
    if promedio < 13 and asistencia < 80:
        return "Medio"
    if compromiso < 65:
        return "Medio"

    # Regla 3: riesgo bajo (condición por defecto)
    if promedio >= 13 and asistencia >= 80 and compromiso >= 65:
        return "Bajo"

    # Regla de respaldo
    return "Medio"


def generar_recomendacion(nivel_riesgo: str) -> str:
    """Regla lógica adicional: recomendación según nivel de riesgo."""
    reglas_recomendacion = {
        "Alto": "Requiere tutoría académica inmediata y seguimiento semanal.",
        "Medio": "Se recomienda reforzar hábitos de estudio y asistencia.",
        "Bajo": "Mantener el desempeño actual; sin acciones urgentes.",
    }
    return reglas_recomendacion.get(nivel_riesgo, "Sin recomendación disponible.")
