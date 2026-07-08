"""
==================================================================
 ANÁLISIS INTELIGENTE DE RENDIMIENTO ACADÉMICO ESTUDIANTIL
 usando Programación Multiparadigma
==================================================================

Curso: Lenguajes de Programación (100000SI68)

Este sistema evalúa el nivel de riesgo académico de cada estudiante
combinando tres paradigmas de programación:

  - PARADIGMA FUNCIONAL: funciones puras, map/filter/reduce para
    calcular promedios, tendencias y agregados sin efectos secundarios.
  - PARADIGMA LÓGICO: un motor de reglas tipo "si-entonces" que
    clasifica el riesgo académico a partir de condiciones sobre
    asistencia, notas y participación.
  - PARADIGMA ORIENTADO A OBJETOS: clases que modelan Estudiante,
    Curso y el Evaluador de riesgo, organizando el estado y el
    comportamiento del sistema.

Autor: [Tu nombre aquí]
==================================================================
"""

from __future__ import annotations
from dataclasses import dataclass, field
from functools import reduce
from typing import Callable
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # backend sin interfaz gráfica, genera archivos directamente
import matplotlib.pyplot as plt


# ==================================================================
# 1. CARGA Y LIMPIEZA DE DATOS (pandas / numpy)
# ==================================================================

RUTA_CSV = "rendimiento_estudiantil.csv"


def cargar_datos(ruta: str) -> pd.DataFrame:
    """Carga el CSV y realiza limpieza básica de datos faltantes."""
    df = pd.read_csv(ruta)

    # Tratamiento de datos: rellenar valores nulos con la mediana de
    # la columna (más robusta que la media ante valores atípicos)
    columnas_numericas = [
        "asistencia_pct", "horas_estudio_semanal",
        "tareas_entregadas_pct", "nota_ep1", "nota_ep2", "nota_final",
    ]
    for col in columnas_numericas:
        if df[col].isna().any():
            mediana = df[col].median()
            df[col] = df[col].fillna(mediana)

    return df


# ==================================================================
# 2. PARADIGMA FUNCIONAL: funciones puras de cálculo
# ==================================================================

def calcular_promedio_notas(nota_ep1: float, nota_ep2: float, nota_final: float) -> float:
    """Función pura: calcula el promedio ponderado de las 3 notas."""
    notas = np.array([nota_ep1, nota_ep2, nota_final])
    pesos = np.array([0.3, 0.3, 0.4])
    return float(np.dot(notas, pesos))


def calcular_indice_compromiso(asistencia: float, tareas: float, participacion: int) -> float:
    """
    Función pura: combina asistencia, entrega de tareas y participación
    en un único índice de 0 a 100 usando programación funcional (reduce).
    """
    indicadores = [asistencia, tareas, participacion * 20]  # participación normalizada a 0-100
    return reduce(lambda acc, x: acc + x, indicadores) / len(indicadores)


def aplicar_a_todos(func: Callable, valores: list) -> list:
    """Aplica una función pura a una lista de valores (estilo map)."""
    return list(map(func, valores))


def filtrar_por_condicion(estudiantes: list, condicion: Callable) -> list:
    """Filtra estudiantes que cumplen una condición (estilo filter)."""
    return list(filter(condicion, estudiantes))


# ==================================================================
# 3. PARADIGMA LÓGICO: motor de reglas para clasificar el riesgo
# ==================================================================

def evaluar_reglas_riesgo(promedio: float, asistencia: float, compromiso: float) -> str:
    """
    Motor de inferencia basado en reglas lógicas (si-entonces),
    inspirado en sistemas expertos. Evalúa condiciones en orden de
    severidad y retorna el nivel de riesgo académico.
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

    # Regla 3: riesgo bajo (condición por defecto si no cumple reglas anteriores)
    if promedio >= 13 and asistencia >= 80 and compromiso >= 65:
        return "Bajo"

    # Regla de respaldo por si ningún caso anterior aplicó exactamente
    return "Medio"


def generar_recomendacion(nivel_riesgo: str) -> str:
    """Regla lógica adicional: recomendación según nivel de riesgo."""
    reglas_recomendacion = {
        "Alto": "Requiere tutoría académica inmediata y seguimiento semanal.",
        "Medio": "Se recomienda reforzar hábitos de estudio y asistencia.",
        "Bajo": "Mantener el desempeño actual; sin acciones urgentes.",
    }
    return reglas_recomendacion.get(nivel_riesgo, "Sin recomendación disponible.")


# ==================================================================
# 4. PARADIGMA ORIENTADO A OBJETOS: modelado del dominio
# ==================================================================

@dataclass
class Estudiante:
    """Representa a un estudiante con su información académica."""
    id_estudiante: str
    nombre: str
    curso: str
    ciclo: str
    asistencia_pct: float
    horas_estudio_semanal: float
    tareas_entregadas_pct: float
    participacion: int
    nota_ep1: float
    nota_ep2: float
    nota_final: float

    # Campos calculados, se completan luego de la evaluación
    promedio: float = field(default=0.0, init=False)
    indice_compromiso: float = field(default=0.0, init=False)
    nivel_riesgo: str = field(default="", init=False)
    recomendacion: str = field(default="", init=False)

    def calcular_metricas(self) -> None:
        """Calcula promedio e índice de compromiso usando las funciones puras."""
        self.promedio = calcular_promedio_notas(self.nota_ep1, self.nota_ep2, self.nota_final)
        self.indice_compromiso = calcular_indice_compromiso(
            self.asistencia_pct, self.tareas_entregadas_pct, self.participacion
        )

    def evaluar_riesgo(self) -> None:
        """Aplica el motor de reglas lógicas para determinar el riesgo."""
        self.nivel_riesgo = evaluar_reglas_riesgo(
            self.promedio, self.asistencia_pct, self.indice_compromiso
        )
        self.recomendacion = generar_recomendacion(self.nivel_riesgo)

    def __str__(self) -> str:
        return (f"[{self.id_estudiante}] {self.nombre} ({self.curso}) | "
                f"Promedio: {self.promedio:.1f} | Riesgo: {self.nivel_riesgo}")


class EvaluadorRiesgo:
    """
    Clase orquestadora: administra la colección de estudiantes,
    ejecuta la evaluación completa y genera reportes agregados.
    """

    def __init__(self, dataframe: pd.DataFrame):
        self._df = dataframe
        self.estudiantes: list[Estudiante] = []

    def construir_estudiantes(self) -> None:
        """Convierte cada fila del DataFrame en un objeto Estudiante."""
        for _, fila in self._df.iterrows():
            est = Estudiante(
                id_estudiante=fila["id_estudiante"],
                nombre=fila["nombre"],
                curso=fila["curso"],
                ciclo=fila["ciclo"],
                asistencia_pct=fila["asistencia_pct"],
                horas_estudio_semanal=fila["horas_estudio_semanal"],
                tareas_entregadas_pct=fila["tareas_entregadas_pct"],
                participacion=int(fila["participacion"]),
                nota_ep1=fila["nota_ep1"],
                nota_ep2=fila["nota_ep2"],
                nota_final=fila["nota_final"],
            )
            self.estudiantes.append(est)

    def evaluar_todos(self) -> None:
        """Ejecuta el cálculo de métricas y la evaluación de riesgo para todos."""
        for est in self.estudiantes:
            est.calcular_metricas()
            est.evaluar_riesgo()

    def estudiantes_en_riesgo(self, nivel: str = "Alto") -> list[Estudiante]:
        """Usa el paradigma funcional (filter) para obtener estudiantes por nivel."""
        return filtrar_por_condicion(self.estudiantes, lambda e: e.nivel_riesgo == nivel)

    def resumen_por_nivel(self) -> dict:
        """Cuenta cuántos estudiantes hay en cada nivel de riesgo."""
        resumen = {"Alto": 0, "Medio": 0, "Bajo": 0}
        for est in self.estudiantes:
            resumen[est.nivel_riesgo] += 1
        return resumen

    def resumen_por_curso(self) -> pd.DataFrame:
        """Genera estadísticas agregadas por curso usando pandas/NumPy."""
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
        return df_temp.groupby("curso").agg(
            promedio_curso=("promedio", "mean"),
            asistencia_promedio=("asistencia", "mean"),
            total_estudiantes=("curso", "count"),
        ).round(2)

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
        print(f"\n✅ Resultados exportados a: {ruta_salida}")


# ==================================================================
# 5. REPORTES Y VISUALIZACIÓN EN CONSOLA
# ==================================================================

def imprimir_reporte(evaluador: EvaluadorRiesgo) -> None:
    """Imprime un reporte legible en consola con los resultados clave."""
    print("=" * 70)
    print(" REPORTE DE RIESGO ACADÉMICO ESTUDIANTIL")
    print("=" * 70)

    resumen = evaluador.resumen_por_nivel()
    total = sum(resumen.values())
    print(f"\nTotal de estudiantes evaluados: {total}\n")
    for nivel, cantidad in resumen.items():
        porcentaje = (cantidad / total) * 100 if total else 0
        print(f"  Riesgo {nivel:<6}: {cantidad:>3} estudiantes ({porcentaje:5.1f}%)")

    print("\n" + "-" * 70)
    print(" ESTUDIANTES EN RIESGO ALTO (requieren atención inmediata)")
    print("-" * 70)
    en_riesgo_alto = evaluador.estudiantes_en_riesgo("Alto")
    for est in en_riesgo_alto[:10]:  # se muestran los primeros 10
        print(f"  {est}")
        print(f"      → {est.recomendacion}")
    if len(en_riesgo_alto) > 10:
        print(f"  ... y {len(en_riesgo_alto) - 10} estudiantes más en riesgo alto.")

    print("\n" + "-" * 70)
    print(" ESTADÍSTICAS POR CURSO")
    print("-" * 70)
    print(evaluador.resumen_por_curso().to_string())
    print("=" * 70)


# ==================================================================
# 6. VISUALIZACIONES (matplotlib)
# ==================================================================

CARPETA_GRAFICOS = "graficos"


def _preparar_carpeta_graficos() -> None:
    """Crea la carpeta de salida de gráficos si no existe."""
    import os
    os.makedirs(CARPETA_GRAFICOS, exist_ok=True)


def graficar_distribucion_riesgo(evaluador: EvaluadorRiesgo) -> None:
    """Gráfico de barras: cantidad de estudiantes por nivel de riesgo."""
    resumen = evaluador.resumen_por_nivel()
    niveles = list(resumen.keys())
    cantidades = list(resumen.values())
    colores = {"Alto": "#e74c3c", "Medio": "#f39c12", "Bajo": "#27ae60"}

    fig, ax = plt.subplots(figsize=(7, 5))
    barras = ax.bar(niveles, cantidades, color=[colores[n] for n in niveles])
    ax.set_title("Distribución de Estudiantes por Nivel de Riesgo Académico", fontsize=13, fontweight="bold")
    ax.set_xlabel("Nivel de Riesgo")
    ax.set_ylabel("Cantidad de Estudiantes")

    for barra, cantidad in zip(barras, cantidades):
        ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height() + 1,
                 str(cantidad), ha="center", fontweight="bold")

    fig.tight_layout()
    fig.savefig(f"{CARPETA_GRAFICOS}/distribucion_riesgo.png", dpi=150)
    plt.close(fig)


def graficar_promedio_por_curso(evaluador: EvaluadorRiesgo) -> None:
    """Gráfico de barras horizontales: promedio de notas por curso."""
    resumen_curso = evaluador.resumen_por_curso().reset_index()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(resumen_curso["curso"], resumen_curso["promedio_curso"], color="#3498db")
    ax.set_title("Promedio de Notas por Curso", fontsize=13, fontweight="bold")
    ax.set_xlabel("Promedio (escala 0-20)")
    ax.set_xlim(0, 20)

    for i, valor in enumerate(resumen_curso["promedio_curso"]):
        ax.text(valor + 0.2, i, f"{valor:.1f}", va="center")

    fig.tight_layout()
    fig.savefig(f"{CARPETA_GRAFICOS}/promedio_por_curso.png", dpi=150)
    plt.close(fig)


def graficar_asistencia_vs_promedio(evaluador: EvaluadorRiesgo) -> None:
    """Diagrama de dispersión: relación entre asistencia y promedio, coloreado por riesgo."""
    colores = {"Alto": "#e74c3c", "Medio": "#f39c12", "Bajo": "#27ae60"}

    fig, ax = plt.subplots(figsize=(8, 6))
    for nivel, color in colores.items():
        estudiantes_nivel = evaluador.estudiantes_en_riesgo(nivel)
        x = [e.asistencia_pct for e in estudiantes_nivel]
        y = [e.promedio for e in estudiantes_nivel]
        ax.scatter(x, y, c=color, label=f"Riesgo {nivel}", alpha=0.7, edgecolors="white")

    ax.set_title("Relación entre Asistencia y Promedio Académico", fontsize=13, fontweight="bold")
    ax.set_xlabel("Asistencia (%)")
    ax.set_ylabel("Promedio (escala 0-20)")
    ax.legend()
    ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(f"{CARPETA_GRAFICOS}/asistencia_vs_promedio.png", dpi=150)
    plt.close(fig)


def graficar_riesgo_por_curso(evaluador: EvaluadorRiesgo) -> None:
    """Gráfico de barras apiladas: composición de niveles de riesgo por curso."""
    datos = [{"curso": e.curso, "riesgo": e.nivel_riesgo} for e in evaluador.estudiantes]
    df_temp = pd.DataFrame(datos)
    tabla = pd.crosstab(df_temp["curso"], df_temp["riesgo"])
    tabla = tabla.reindex(columns=["Bajo", "Medio", "Alto"], fill_value=0)

    colores = {"Alto": "#e74c3c", "Medio": "#f39c12", "Bajo": "#27ae60"}
    fig, ax = plt.subplots(figsize=(9, 6))
    tabla.plot(kind="bar", stacked=True, ax=ax, color=[colores[c] for c in tabla.columns])
    ax.set_title("Composición del Riesgo Académico por Curso", fontsize=13, fontweight="bold")
    ax.set_xlabel("Curso")
    ax.set_ylabel("Cantidad de Estudiantes")
    ax.legend(title="Nivel de Riesgo")
    plt.xticks(rotation=25, ha="right")

    fig.tight_layout()
    fig.savefig(f"{CARPETA_GRAFICOS}/riesgo_por_curso.png", dpi=150)
    plt.close(fig)


def generar_todos_los_graficos(evaluador: EvaluadorRiesgo) -> None:
    """Genera y guarda todos los gráficos del análisis en la carpeta 'graficos/'."""
    _preparar_carpeta_graficos()
    graficar_distribucion_riesgo(evaluador)
    graficar_promedio_por_curso(evaluador)
    graficar_asistencia_vs_promedio(evaluador)
    graficar_riesgo_por_curso(evaluador)
    print(f"\n📊 Gráficos guardados en la carpeta '{CARPETA_GRAFICOS}/':")
    print("   - distribucion_riesgo.png")
    print("   - promedio_por_curso.png")
    print("   - asistencia_vs_promedio.png")
    print("   - riesgo_por_curso.png")


# ==================================================================
# 7. PROGRAMA PRINCIPAL
# ==================================================================

def main() -> None:
    print("Cargando datos desde:", RUTA_CSV, "...")
    df = cargar_datos(RUTA_CSV)
    print(f"Se cargaron {len(df)} registros.\n")

    evaluador = EvaluadorRiesgo(df)
    evaluador.construir_estudiantes()
    evaluador.evaluar_todos()

    imprimir_reporte(evaluador)
    evaluador.exportar_resultados("resultados_riesgo.csv")
    generar_todos_los_graficos(evaluador)


if __name__ == "__main__":
    main()
