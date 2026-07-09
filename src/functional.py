"""
==================================================================
 PARADIGMA FUNCIONAL
 Funciones puras para el cálculo de métricas académicas.
 Utiliza map, filter y reduce sin efectos secundarios.
==================================================================
"""

from functools import reduce
from typing import Callable
import numpy as np


def calcular_promedio_notas(notas: list[float], pesos: list[float]) -> float:
    """
    Función pura: calcula el promedio ponderado de N notas con N pesos.

    >>> calcular_promedio_notas([14.0, 12.0, 16.0], [0.3, 0.3, 0.4])
    14.2
    """
    return float(np.dot(np.array(notas), np.array(pesos)))


def calcular_indice_compromiso(
    asistencia: float, tareas: float, participacion: int
) -> float:
    """
    Función pura: combina asistencia, entrega de tareas y participación
    en un único índice de 0 a 100 usando programación funcional (reduce).

    La participación (escala 1-5) se normaliza multiplicando por 20.
    """
    indicadores = [
        asistencia,
        tareas,
        participacion * 20.0,  # normalización a 0-100
    ]
    return reduce(lambda acc, x: acc + x, indicadores) / len(indicadores)


def aplicar_a_todos(func: Callable, valores: list) -> list:
    """Aplica una función pura a una lista de valores (estilo map)."""
    return list(map(func, valores))


def filtrar_por_condicion(estudiantes: list, condicion: Callable) -> list:
    """Filtra estudiantes que cumplen una condición (estilo filter)."""
    return list(filter(condicion, estudiantes))
