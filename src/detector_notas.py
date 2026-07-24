"""
==================================================================
 DETECTOR AUTOMATICO DE SISTEMA DE NOTAS
 Identifica columnas de evaluacion academica basandose en
 prefijos de nombre y asigna pesos (iguales o guardados).
==================================================================
"""

import pandas as pd
import numpy as np
from src.config_manager import cargar_pesos

# Prefijos que identifican columnas de nota/evaluación
PREFIJOS_NOTA = [
    "nota_", "examen_", "eval_", "parcial_",
    "final_", "practico_", "lab_", "ep",
]

# Columnas que siempre se excluyen (metadata, no notas)
COLUMNAS_EXCLUIDAS = {
    "id_estudiante", "nombre", "curso", "ciclo",
    "asistencia_pct", "horas_estudio_semanal",
    "tareas_entregadas_pct", "participacion",
}


def detectar_columnas_notas(df: pd.DataFrame) -> dict:
    """
    Escanea las columnas del DataFrame y detecta cuáles son notas
    basándose en prefijos definidos en PREFIJOS_NOTA.

    Retorna:
    {
        "columnas_nota": list[str],   # nombres de columnas detectadas
        "pesos": list[float],          # pesos iguales normalizados
        "tiene_cursos": bool,          # si existe columna 'curso'
        "curso_col": str | None,       # nombre de la columna curso
    }
    """
    columnas = list(df.columns)
    columnas_nota = []

    for col in columnas:
        col_lower = col.lower().strip()
        if col_lower in COLUMNAS_EXCLUIDAS:
            continue
        for prefijo in PREFIJOS_NOTA:
            if col_lower.startswith(prefijo):
                columnas_nota.append(col)
                break

    if not columnas_nota:
        raise ValueError(
            "No se detectaron columnas de nota en el archivo. "
            "Asegúrate de que las columnas de evaluación empiecen "
            "con: nota_, examen_, eval_, parcial_, final_, "
            "practico_, lab_ o ep (ej: nota_ep1, examen_final, etc.)."
        )

    n = len(columnas_nota)

    # Intentar cargar pesos guardados; si no existen, asignar iguales
    pesos_guardados = cargar_pesos()
    if all(col in pesos_guardados for col in columnas_nota):
        pesos = [pesos_guardados[col] for col in columnas_nota]
    else:
        pesos = [round(1.0 / n, 4) for _ in range(n)]
        pesos[-1] = round(1.0 - sum(pesos[:-1]), 4)

    tiene_cursos = "curso" in [c.lower().strip() for c in columnas]
    curso_col = "curso" if tiene_cursos else None

    return {
        "columnas_nota": columnas_nota,
        "pesos": pesos,
        "tiene_cursos": tiene_cursos,
        "curso_col": curso_col,
    }
