"""
==================================================================
 GENERACION DE REPORTES PDF
 Genera un reporte profesional con resumen, graficos y tabla
 de resultados usando fpdf2.
==================================================================
"""

import os
from fpdf import FPDF


class ReportePDF(FPDF):
    """Clase personalizada para el reporte de rendimiento estudiantil."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Analisis de Rendimiento Academico Estudiantil", align="L")
        self.ln(4)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def titulo(self, texto: str):
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(44, 62, 80)
        self.cell(0, 15, texto, align="C")
        self.ln(12)

    def subtitulo(self, texto: str):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(52, 73, 94)
        self.cell(0, 10, texto)
        self.ln(8)

    def texto(self, texto: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, texto)
        self.ln(3)

    def linea_separadora(self):
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)


def generar_reporte_pdf(
    evaluador,
    ruta_salida: str,
    ruta_graficos: list[str],
    config_notas: dict,
) -> str:
    """
    Genera un reporte PDF completo con:
    - Portada con titulo y resumen
    - Graficos estadisticos
    - Tabla de resultados

    Retorna la ruta del archivo generado.
    """
    pdf = ReportePDF()
    pdf.alias_nb_pages()

    # ── Pagina 1: Portada y resumen ──
    pdf.add_page()
    pdf.titulo("Reporte de Analisis\nde Rendimiento Academico")
    pdf.ln(5)
    pdf.linea_separadora()

    pdf.subtitulo("Resumen Ejecutivo")
    resumen = evaluador.resumen_por_nivel()
    total = sum(resumen.values())
    pdf.texto(f"Total de estudiantes evaluados: {total}")
    pdf.ln(2)

    for nivel, cantidad in resumen.items():
        pct = (cantidad / total * 100) if total else 0
        pdf.set_font("Helvetica", "B", 10)
        colores = {"Alto": (231, 76, 60), "Medio": (243, 156, 18), "Bajo": (39, 174, 96)}
        r, g, b = colores.get(nivel, (50, 50, 50))
        pdf.set_text_color(r, g, b)
        pdf.cell(0, 7, f"  Riesgo {nivel}: {cantidad} estudiantes ({pct:.1f}%)")
        pdf.ln(7)

    pdf.set_text_color(50, 50, 50)
    pdf.ln(5)

    # Columnas detectadas
    cols = ", ".join(config_notas.get("columnas_nota", []))
    pdf.texto(f"Columnas de nota detectadas: {cols}")

    tiene_cursos = config_notas.get("tiene_cursos", False)
    if tiene_cursos:
        pdf.texto(f"Columna de curso: {config_notas.get('curso_col', 'curso')}")
    else:
        pdf.texto("Columna de curso: No detectada (todos como 'General')")

    pdf.ln(5)
    pdf.linea_separadora()

    # Resumen por curso si existe
    if tiene_cursos:
        resumen_curso = evaluador.resumen_por_curso()
        if not resumen_curso.empty:
            pdf.subtitulo("Estadisticas por Curso")
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_fill_color(52, 73, 94)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(60, 7, "Curso", border=1, fill=True, align="C")
            pdf.cell(35, 7, "Promedio", border=1, fill=True, align="C")
            pdf.cell(35, 7, "Asistencia", border=1, fill=True, align="C")
            pdf.cell(30, 7, "Total", border=1, fill=True, align="C")
            pdf.ln()

            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(50, 50, 50)
            for idx, row in resumen_curso.iterrows():
                fill = pdf.page_no() % 2 == 0
                pdf.set_fill_color(245, 245, 245)
                pdf.cell(60, 6, str(idx), border=1, fill=fill, align="C")
                pdf.cell(35, 6, f"{row['promedio_curso']:.2f}", border=1, fill=fill, align="C")
                pdf.cell(35, 6, f"{row['asistencia_promedio']:.1f}%", border=1, fill=fill, align="C")
                pdf.cell(30, 6, str(int(row['total_estudiantes'])), border=1, fill=fill, align="C")
                pdf.ln()
            pdf.ln(5)

    # ── Pagina de graficos ──
    if ruta_graficos:
        pdf.add_page()
        pdf.subtitulo("Graficos Estadisticos")
        pdf.ln(3)

        for i, ruta in enumerate(ruta_graficos):
            if not ruta or not os.path.exists(ruta):
                continue

            if pdf.get_y() > 180:
                pdf.add_page()

            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(100, 100, 100)
            nombres = [
                "Distribucion de Riesgo Academico",
                "Promedio de Notas por Curso",
                "Relacion Asistencia vs Promedio",
                "Composicion del Riesgo por Curso",
            ]
            nombre = nombres[i] if i < len(nombres) else f"Grafico {i+1}"
            pdf.cell(0, 6, nombre)
            pdf.ln(6)

            pdf.image(ruta, x=15, w=180)
            pdf.ln(8)

    # ── Tabla de resultados ──
    pdf.add_page()
    pdf.subtitulo("Detalle de Estudiantes")
    pdf.ln(2)

    datos = evaluador.obtener_datos_tabla()

    # Encabezados de tabla
    col_widths = [15, 32, 30, 18, 18, 18, 16, 43]
    encabezados = ["ID", "Nombre", "Curso", "Prom.", "Asist.", "Comp.", "Riesgo", "Recomendacion"]

    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(52, 73, 94)
    pdf.set_text_color(255, 255, 255)
    for texto, width in zip(encabezados, col_widths):
        pdf.cell(width, 6, texto, border=1, fill=True, align="C")
    pdf.ln()

    # Filas
    colores_riesgo = {
        "Alto": (255, 230, 230),
        "Medio": (255, 248, 230),
        "Bajo": (230, 255, 240),
    }

    pdf.set_font("Helvetica", "", 6.5)
    for i, est in enumerate(datos):
        if pdf.get_y() > 270:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 7)
            pdf.set_fill_color(52, 73, 94)
            pdf.set_text_color(255, 255, 255)
            for texto, width in zip(encabezados, col_widths):
                pdf.cell(width, 6, texto, border=1, fill=True, align="C")
            pdf.ln()
            pdf.set_font("Helvetica", "", 6.5)

        r, g, b = colores_riesgo.get(est["riesgo"], (255, 255, 255))
        pdf.set_fill_color(r, g, b)
        pdf.set_text_color(50, 50, 50)

        recom_texto = est["recomendacion"][:40] + "..." if len(est["recomendacion"]) > 40 else est["recomendacion"]

        valores = [
            str(est["id"]),
            str(est["nombre"])[:18],
            str(est["curso"])[:18],
            f"{est['promedio']:.1f}",
            f"{est['asistencia']:.0f}%",
            f"{est['compromiso']:.0f}",
            est["riesgo"],
            recom_texto,
        ]
        for valor, width in zip(valores, col_widths):
            pdf.cell(width, 5.5, valor, border=1, fill=True, align="C")
        pdf.ln()

    # Guardar
    pdf.output(ruta_salida)
    return ruta_salida
