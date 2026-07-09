"""
==================================================================
 VISUALIZACIONES (matplotlib)
 Genera los 4 gráficos de análisis y los guarda como PNG
 en una carpeta personalizada por archivo de datos.
==================================================================
"""

import os
import matplotlib
matplotlib.use("Agg")  # backend sin interfaz gráfica
import matplotlib.pyplot as plt
import pandas as pd
from src.models import EvaluadorRiesgo


def _preparar_carpeta(carpeta: str) -> str:
    """Crea la carpeta de salida de gráficos si no existe."""
    os.makedirs(carpeta, exist_ok=True)
    return carpeta


def graficar_distribucion_riesgo(evaluador: EvaluadorRiesgo, carpeta: str) -> str:
    """Gráfico de barras: cantidad de estudiantes por nivel de riesgo."""
    resumen = evaluador.resumen_por_nivel()
    niveles = list(resumen.keys())
    cantidades = list(resumen.values())
    colores = {"Alto": "#e74c3c", "Medio": "#f39c12", "Bajo": "#27ae60"}

    fig, ax = plt.subplots(figsize=(7, 5))
    barras = ax.bar(
        niveles, cantidades, color=[colores[n] for n in niveles]
    )
    ax.set_title(
        "Distribución de Estudiantes por Nivel de Riesgo Académico",
        fontsize=13, fontweight="bold",
    )
    ax.set_xlabel("Nivel de Riesgo")
    ax.set_ylabel("Cantidad de Estudiantes")

    for barra, cantidad in zip(barras, cantidades):
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height() + 1,
            str(cantidad),
            ha="center",
            fontweight="bold",
        )

    fig.tight_layout()
    ruta = os.path.join(carpeta, "distribucion_riesgo.png")
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    return ruta


def graficar_promedio_por_curso(evaluador: EvaluadorRiesgo, carpeta: str) -> str:
    """Gráfico de barras horizontales: promedio de notas por curso."""
    resumen_curso = evaluador.resumen_por_curso()
    if resumen_curso.empty:
        return ""

    resumen_curso = resumen_curso.reset_index()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(resumen_curso["curso"], resumen_curso["promedio_curso"], color="#3498db")
    ax.set_title("Promedio de Notas por Curso", fontsize=13, fontweight="bold")
    ax.set_xlabel("Promedio (escala 0-20)")
    ax.set_xlim(0, 20)

    for i, valor in enumerate(resumen_curso["promedio_curso"]):
        ax.text(valor + 0.2, i, f"{valor:.1f}", va="center")

    fig.tight_layout()
    ruta = os.path.join(carpeta, "promedio_por_curso.png")
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    return ruta


def graficar_asistencia_vs_promedio(evaluador: EvaluadorRiesgo, carpeta: str) -> str:
    """Diagrama de dispersión: relación entre asistencia y promedio, coloreado por riesgo."""
    colores = {"Alto": "#e74c3c", "Medio": "#f39c12", "Bajo": "#27ae60"}

    fig, ax = plt.subplots(figsize=(8, 6))
    for nivel, color in colores.items():
        estudiantes_nivel = evaluador.estudiantes_en_riesgo(nivel)
        x = [e.asistencia_pct for e in estudiantes_nivel]
        y = [e.promedio for e in estudiantes_nivel]
        ax.scatter(
            x, y, c=color, label=f"Riesgo {nivel}",
            alpha=0.7, edgecolors="white",
        )

    ax.set_title(
        "Relación entre Asistencia y Promedio Académico",
        fontsize=13, fontweight="bold",
    )
    ax.set_xlabel("Asistencia (%)")
    ax.set_ylabel("Promedio (escala 0-20)")
    ax.legend()
    ax.grid(alpha=0.3)

    fig.tight_layout()
    ruta = os.path.join(carpeta, "asistencia_vs_promedio.png")
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    return ruta


def graficar_riesgo_por_curso(evaluador: EvaluadorRiesgo, carpeta: str) -> str:
    """Gráfico de barras apiladas: composición de niveles de riesgo por curso."""
    if not evaluador.config_notas.get("tiene_cursos"):
        return ""

    datos = [
        {"curso": e.curso, "riesgo": e.nivel_riesgo}
        for e in evaluador.estudiantes
    ]
    df_temp = pd.DataFrame(datos)
    tabla = pd.crosstab(df_temp["curso"], df_temp["riesgo"])
    tabla = tabla.reindex(columns=["Bajo", "Medio", "Alto"], fill_value=0)

    colores = {"Alto": "#e74c3c", "Medio": "#f39c12", "Bajo": "#27ae60"}
    fig, ax = plt.subplots(figsize=(9, 6))
    tabla.plot(
        kind="bar", stacked=True, ax=ax,
        color=[colores[c] for c in tabla.columns],
    )
    ax.set_title(
        "Composición del Riesgo Académico por Curso",
        fontsize=13, fontweight="bold",
    )
    ax.set_xlabel("Curso")
    ax.set_ylabel("Cantidad de Estudiantes")
    ax.legend(title="Nivel de Riesgo")
    plt.xticks(rotation=25, ha="right")

    fig.tight_layout()
    ruta = os.path.join(carpeta, "riesgo_por_curso.png")
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    return ruta


def generar_todos_los_graficos(
    evaluador: EvaluadorRiesgo,
    carpeta: str = "graficos",
) -> list[str]:
    """
    Genera y guarda todos los gráficos del análisis en la carpeta
    especificada (por defecto 'graficos/').
    Retorna una lista de rutas de los archivos generados.
    """
    _preparar_carpeta(carpeta)
    rutas = [
        graficar_distribucion_riesgo(evaluador, carpeta),
        graficar_promedio_por_curso(evaluador, carpeta),
        graficar_asistencia_vs_promedio(evaluador, carpeta),
        graficar_riesgo_por_curso(evaluador, carpeta),
    ]
    return [r for r in rutas if r]
