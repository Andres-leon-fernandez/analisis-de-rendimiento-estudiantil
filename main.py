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
  - PARADIGMA LÓGICO: un motor de reglas en Prolog (reglas_riesgo.pl)
    consultado desde Python via pyswip, que clasifica el riesgo
    académico a partir de hechos y reglas sobre asistencia,
    notas y participación.
  - PARADIGMA ORIENTADO A OBJETOS: clases que modelan Estudiante,
    Curso y el Evaluador de riesgo, organizando el estado y el
    comportamiento del sistema.

Características:
  - Interfaz gráfica (Tkinter) para seleccionar archivos CSV/Excel
  - Detección automática del sistema de notas por prefijos de columna
  - Pesos iguales para todas las notas detectadas
  - Exportación de resultados a CSV
  - Generación de gráficos estadísticos

Autor: [Tu nombre aquí]
==================================================================
"""

import ttkbootstrap as ttk
from src.gui import VentanaPrincipal


def main() -> None:
    root = ttk.Window(themename="flatly")
    app = VentanaPrincipal(root)
    root.mainloop()


if __name__ == "__main__":
    main()
