"""
==================================================================
 PARADIGMA ORIENTADO A OBJETOS
 Modelado del dominio: Estudiante y EvaluadorRiesgo.
==================================================================
"""

from __future__ import annotations
from dataclasses import dataclass, field
import pandas as pd
from src.functional import (
    calcular_promedio_notas,
    calcular_indice_compromiso,
    filtrar_por_condicion,
)
from src.rules_engine import evaluar_reglas_riesgo, generar_recomendacion
from src.config_manager import cargar_umbrales
from src.carga import limpiar_datos


@dataclass
class Estudiante:
    """Representa a un estudiante con su información académica.

    Las notas se almacenan como una lista dinámica junto con sus
    pesos, lo que permite adaptarse a cualquier sistema de evaluación
    independientemente de la cantidad de exámenes.
    """
    id_estudiante: str
    nombre: str
    curso: str
    notas: list[float]
    pesos: list[float]
    asistencia_pct: float
    horas_estudio_semanal: float
    tareas_entregadas_pct: float
    participacion: int

    # Campos calculados, se completan tras la evaluación
    promedio: float = field(default=0.0, init=False)
    indice_compromiso: float = field(default=0.0, init=False)
    nivel_riesgo: str = field(default="", init=False)
    recomendacion: str = field(default="", init=False)

    def calcular_metricas(self) -> None:
        """Calcula promedio e índice de compromiso usando funciones puras."""
        self.promedio = calcular_promedio_notas(self.notas, self.pesos)
        self.indice_compromiso = calcular_indice_compromiso(
            self.asistencia_pct, self.tareas_entregadas_pct, self.participacion
        )

    def evaluar_riesgo(self, umbrales: dict = None) -> None:
        """Aplica el motor de reglas Prolog para determinar el riesgo."""
        self.nivel_riesgo = evaluar_reglas_riesgo(
            self.id_estudiante, self.promedio, self.asistencia_pct, self.indice_compromiso,
            umbrales=umbrales,
        )
        self.recomendacion = generar_recomendacion(self.nivel_riesgo)

    def __str__(self) -> str:
        return (
            f"[{self.id_estudiante}] {self.nombre} ({self.curso}) | "
            f"Promedio: {self.promedio:.1f} | Riesgo: {self.nivel_riesgo}"
        )


class EvaluadorRiesgo:
    """
    Clase orquestadora: administra la coleccion de estudiantes,
    ejecuta la evaluacion completa y genera reportes agregados.
    """

    def __init__(self, dataframe: pd.DataFrame, config_notas: dict):
        self._df = limpiar_datos(dataframe)
        self.config_notas = config_notas
        self.estudiantes: list[Estudiante] = []
        self._curso_col = config_notas.get("curso_col")
        self.umbrales: dict = cargar_umbrales()

    def construir_estudiantes(self) -> None:
        """Convierte cada fila del DataFrame en un objeto Estudiante."""
        cols_nota = self.config_notas["columnas_nota"]
        pesos = self.config_notas["pesos"]

        for _, fila in self._df.iterrows():
            notas = [float(fila[col]) for col in cols_nota]

            curso = (
                str(fila[self._curso_col])
                if self._curso_col
                else "General"
            )

            est = Estudiante(
                id_estudiante=str(fila.get("id_estudiante", "")),
                nombre=str(fila.get("nombre", "")),
                curso=curso,
                notas=notas,
                pesos=pesos,
                asistencia_pct=float(fila.get("asistencia_pct", 0)),
                horas_estudio_semanal=float(fila.get("horas_estudio_semanal", 0)),
                tareas_entregadas_pct=float(fila.get("tareas_entregadas_pct", 0)),
                participacion=int(fila.get("participacion", 1)),
            )
            self.estudiantes.append(est)

    def evaluar_todos(self) -> None:
        """Ejecuta el calculo de metricas y la evaluacion de riesgo para todos."""
        for est in self.estudiantes:
            est.calcular_metricas()
            est.evaluar_riesgo(umbrales=self.umbrales)

    def estudiantes_en_riesgo(self, nivel: str = "Alto") -> list[Estudiante]:
        """Usa el paradigma funcional (filter) para obtener estudiantes por nivel."""
        return filtrar_por_condicion(
            self.estudiantes, lambda e: e.nivel_riesgo == nivel
        )

    def resumen_por_nivel(self) -> dict:
        """Cuenta cuántos estudiantes hay en cada nivel de riesgo."""
        resumen = {"Alto": 0, "Medio": 0, "Bajo": 0}
        for est in self.estudiantes:
            resumen[est.nivel_riesgo] += 1
        return resumen

    def resumen_por_curso(self) -> pd.DataFrame:
        """Genera estadísticas agregadas por curso usando pandas."""
        if not self._curso_col:
            return pd.DataFrame()

        datos = [
            {
                "curso": e.curso,
                "promedio": e.promedio,
                "asistencia": e.asistencia_pct,
                "riesgo": e.nivel_riesgo,
            }
            for e in self.estudiantes
        ]
        df_temp = pd.DataFrame(datos)
        return (
            df_temp.groupby("curso")
            .agg(
                promedio_curso=("promedio", "mean"),
                asistencia_promedio=("asistencia", "mean"),
                total_estudiantes=("curso", "count"),
            )
            .round(2)
        )

    def exportar_resultados(self, ruta_salida: str = "resultados_riesgo.csv") -> None:
        """Exporta el reporte final con todos los estudiantes evaluados."""
        datos = [
            {
                "id_estudiante": e.id_estudiante,
                "nombre": e.nombre,
                "curso": e.curso,
                "promedio": round(e.promedio, 2),
                "asistencia_pct": e.asistencia_pct,
                "indice_compromiso": round(e.indice_compromiso, 2),
                "nivel_riesgo": e.nivel_riesgo,
                "recomendacion": e.recomendacion,
            }
            for e in self.estudiantes
        ]
        pd.DataFrame(datos).to_csv(ruta_salida, index=False, encoding="utf-8-sig")

    def obtener_datos_tabla(self) -> list[dict]:
        """Retorna los datos listos para mostrar en la tabla de la GUI."""
        return [
            {
                "id": e.id_estudiante,
                "nombre": e.nombre,
                "curso": e.curso,
                "promedio": round(e.promedio, 2),
                "asistencia": e.asistencia_pct,
                "compromiso": round(e.indice_compromiso, 2),
                "riesgo": e.nivel_riesgo,
                "recomendacion": e.recomendacion,
            }
            for e in self.estudiantes
        ]
