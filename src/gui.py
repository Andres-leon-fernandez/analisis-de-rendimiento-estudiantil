"""
==================================================================
 INTERFAZ GRÁFICA DE USUARIO (Tkinter)
 Ventana principal con selección de archivo, tabla de resultados,
 resumen estadístico, exportación y visualización de gráficos.
==================================================================
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

from src.carga import cargar_archivo
from src.detector_notas import detectar_columnas_notas
from src.models import EvaluadorRiesgo
from src.graficos import generar_todos_los_graficos


class VentanaPrincipal:
    """
    Ventana principal de la aplicación.
    Contiene: selector de archivo, resumen, tabla de datos y botones de acción.
    """

    COLORES_RIESGO = {
        "Alto": "#e74c3c",
        "Medio": "#f39c12",
        "Bajo": "#27ae60",
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Análisis de Rendimiento Estudiantil")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)

        self.evaluador: EvaluadorRiesgo | None = None
        self._datos_completos: list[dict] = []
        self._sort_col: str = ""
        self._sort_asc: bool = True
        self._construir_widgets()

    # ── Variables de control para filtros ──
    def _crear_vars_filtro(self) -> None:
        self._var_riesgo = tk.StringVar(value="Todos")
        self._var_curso = tk.StringVar(value="Todos")
        self._var_estado = tk.StringVar(value="Todos")
        self._var_buscar = tk.StringVar(value="")

    def _construir_widgets(self) -> None:
        """Construye todos los widgets de la ventana principal."""
        self._crear_vars_filtro()

        # ── Panel superior: selector de archivo ──
        frame_archivo = ttk.LabelFrame(self.root, text="Cargar archivo de notas", padding=10)
        frame_archivo.pack(fill="x", padx=10, pady=(10, 5))

        self.lbl_archivo = ttk.Label(
            frame_archivo,
            text="Selecciona un archivo CSV o Excel (.xlsx / .xls)",
        )
        self.lbl_archivo.pack(side="left", padx=(0, 10))

        btn_examinar = ttk.Button(
            frame_archivo, text="Examinar...", command=self._seleccionar_archivo
        )
        btn_examinar.pack(side="right")

        # ── Panel de resumen ──
        frame_resumen = ttk.LabelFrame(self.root, text="Resumen", padding=10)
        frame_resumen.pack(fill="x", padx=10, pady=5)

        self.lbl_total = ttk.Label(frame_resumen, text="Total estudiantes: —")
        self.lbl_total.pack(anchor="w")

        # Barras de riesgo (etiqueta + barra de color proporcional)
        self._frame_barras = ttk.Frame(frame_resumen)
        self._frame_barras.pack(fill="x", pady=(5, 0))

        self._barra_alto = self._crear_barra_riesgo(self._frame_barras, "Alto", self.COLORES_RIESGO["Alto"])
        self._barra_medio = self._crear_barra_riesgo(self._frame_barras, "Medio", self.COLORES_RIESGO["Medio"])
        self._barra_bajo = self._crear_barra_riesgo(self._frame_barras, "Bajo", self.COLORES_RIESGO["Bajo"])

        self.lbl_notas = ttk.Label(frame_resumen, text="Columnas de nota detectadas: —")
        self.lbl_notas.pack(anchor="w", pady=(5, 0))

        self.lbl_curso = ttk.Label(frame_resumen, text="Columna curso: —")
        self.lbl_curso.pack(anchor="w")

        # ── Panel de filtros ──
        frame_filtros = ttk.LabelFrame(self.root, text="Filtrar resultados", padding=8)
        frame_filtros.pack(fill="x", padx=10, pady=5)

        # Fila 1: combos
        sub_frame_combos = ttk.Frame(frame_filtros)
        sub_frame_combos.pack(fill="x", pady=(0, 5))

        ttk.Label(sub_frame_combos, text="Riesgo:").pack(side="left", padx=(0, 4))
        self._combo_riesgo = ttk.Combobox(
            sub_frame_combos, textvariable=self._var_riesgo,
            values=["Todos", "Alto", "Medio", "Bajo"],
            state="readonly", width=12,
        )
        self._combo_riesgo.pack(side="left", padx=(0, 15))
        self._combo_riesgo.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtros())

        ttk.Label(sub_frame_combos, text="Curso:").pack(side="left", padx=(0, 4))
        self._combo_curso = ttk.Combobox(
            sub_frame_combos, textvariable=self._var_curso,
            state="readonly", width=22,
        )
        self._combo_curso.pack(side="left", padx=(0, 15))
        self._combo_curso.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtros())

        ttk.Label(sub_frame_combos, text="Estado:").pack(side="left", padx=(0, 4))
        self._combo_estado = ttk.Combobox(
            sub_frame_combos, textvariable=self._var_estado,
            values=["Todos", "Aprobado", "Desaprobado"],
            state="readonly", width=14,
        )
        self._combo_estado.pack(side="left", padx=(0, 5))
        self._combo_estado.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtros())

        # Fila 2: búsqueda + botón
        sub_frame_buscar = ttk.Frame(frame_filtros)
        sub_frame_buscar.pack(fill="x")

        ttk.Label(sub_frame_buscar, text="Buscar:").pack(side="left", padx=(0, 4))
        self._entry_buscar = ttk.Entry(
            sub_frame_buscar, textvariable=self._var_buscar, width=30,
        )
        self._entry_buscar.pack(side="left", padx=(0, 8))
        self._entry_buscar.bind("<Return>", lambda e: self._aplicar_filtros())

        btn_filtrar = ttk.Button(
            sub_frame_buscar, text="Filtrar", command=self._aplicar_filtros,
        )
        btn_filtrar.pack(side="left", padx=(0, 15))

        ttk.Label(sub_frame_buscar, text="Mostrando:").pack(side="left", padx=(0, 3))
        self._lbl_mostrando = ttk.Label(sub_frame_buscar, text="—")
        self._lbl_mostrando.pack(side="left")

        # ── Panel de tabla ──
        frame_tabla = ttk.LabelFrame(self.root, text="Estudiantes evaluados", padding=5)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=5)

        columnas = ("id", "nombre", "curso", "promedio", "asistencia", "compromiso", "riesgo", "recomendacion")
        self.tabla = ttk.Treeview(
            frame_tabla, columns=columnas, show="headings",
            selectmode="browse", height=15,
        )

        encabezados = {
            "id": "ID",
            "nombre": "Nombre",
            "curso": "Curso",
            "promedio": "Promedio",
            "asistencia": "Asist. %",
            "compromiso": "Compromiso",
            "riesgo": "Riesgo",
            "recomendacion": "Recomendación",
        }
        for col, texto in encabezados.items():
            self.tabla.heading(
                col, text=texto,
                command=lambda c=col: self._ordenar_tabla(c),
            )
            self.tabla.column(col, width=100, minwidth=80)

        self.tabla.column("id", width=70)
        self.tabla.column("nombre", width=160)
        self.tabla.column("curso", width=160)
        self.tabla.column("promedio", width=90)
        self.tabla.column("asistencia", width=90)
        self.tabla.column("compromiso", width=100)
        self.tabla.column("riesgo", width=90)
        self.tabla.column("recomendacion", width=350)

        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(
            yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set
        )

        self.tabla.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

        self.tabla.bind("<Double-1>", self._mostrar_detalle_estudiante)

        # ── Panel de botones ──
        self._frame_botones = ttk.Frame(self.root, padding=10)
        self._frame_botones.pack(fill="x", padx=10, pady=(0, 10))

        self._btn_exportar = ttk.Button(
            self._frame_botones, text="Exportar CSV", command=self._exportar_csv
        )
        self._btn_exportar.pack(side="left", padx=(0, 10))
        self._btn_exportar.state(["disabled"])

        self._btn_pdf = ttk.Button(
            self._frame_botones, text="Exportar PDF", command=self._exportar_pdf
        )
        self._btn_pdf.pack(side="left", padx=(0, 10))
        self._btn_pdf.state(["disabled"])

        self._btn_config = ttk.Button(
            self._frame_botones, text="Configurar Umbrales",
            command=self._abrir_configuracion,
        )
        self._btn_config.pack(side="left", padx=(0, 10))

        self._btn_pesos = ttk.Button(
            self._frame_botones, text="Editar Pesos",
            command=self._abrir_pesos,
        )
        self._btn_pesos.pack(side="left", padx=(0, 10))
        self._btn_pesos.state(["disabled"])

        # "Ver Gráficos" se crea y muestra solo cuando hay datos cargados

    def _crear_barra_riesgo(self, parent: ttk.Frame, nivel: str, color: str) -> dict:
        """Crea una fila con etiqueta + canvas de barra proporcional para un nivel de riesgo."""
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=1)

        lbl_nombre = ttk.Label(frame, text=f"{nivel}:", width=8, anchor="w",
                               foreground=color, font=("Segoe UI", 9, "bold"))
        lbl_nombre.pack(side="left", padx=(0, 5))

        canvas = tk.Canvas(frame, height=18, highlightthickness=0, bg="#f0f0f0")
        canvas.pack(side="left", fill="x", expand=True, padx=(0, 5))

        lbl_valor = ttk.Label(frame, text="—", width=14, anchor="w")
        lbl_valor.pack(side="left")

        return {"canvas": canvas, "label": lbl_valor, "color": color, "frame": frame}

    def _dibujar_barra(self, barra: dict, cantidad: int, porcentaje: float, total: int) -> None:
        """Dibuja una barra de color proporcional al porcentaje del nivel de riesgo."""
        canvas = barra["canvas"]
        canvas.update_idletasks()
        ancho_max = canvas.winfo_width()

        canvas.delete("all")
        if total == 0:
            barra["label"].config(text="—")
            return

        ancho_barra = max(2, int(ancho_max * porcentaje / 100))
        canvas.create_rectangle(0, 0, ancho_barra, 18, fill=barra["color"], outline="")
        barra["label"].config(text=f"{cantidad} ({porcentaje:.1f}%)")

    def _seleccionar_archivo(self) -> None:
        """Abre el diálogo de selección de archivo y procesa los datos."""
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de notas",
            filetypes=[
                ("Archivos soportados", "*.csv *.xlsx *.xls"),
                ("CSV", "*.csv"),
                ("Excel", "*.xlsx *.xls"),
            ],
        )
        if not ruta:
            return

        nombre_archivo = os.path.basename(ruta)
        self.lbl_archivo.config(text=nombre_archivo)
        nombre_base = os.path.splitext(nombre_archivo)[0]
        self._carpeta_graficos = nombre_base + "-img"

        try:
            df = cargar_archivo(ruta)
            config_notas = detectar_columnas_notas(df)
            self.evaluador = EvaluadorRiesgo(df, config_notas)
            self.evaluador.construir_estudiantes()
            self.evaluador.evaluar_todos()

            self._actualizar_resumen(config_notas)
            self._poblar_cursos()
            self._datos_completos = self.evaluador.obtener_datos_tabla()
            self._aplicar_filtros()
            self._btn_exportar.state(["!disabled"])
            self._btn_pdf.state(["!disabled"])
            self._btn_pesos.state(["!disabled"])

            # Generar gráficos automáticamente y mostrar botón
            from src.graficos import generar_todos_los_graficos
            self._rutas_graficos = generar_todos_los_graficos(
                self.evaluador, self._carpeta_graficos
            )
            self._mostrar_boton_graficos()

            # Exportar CSV automáticamente
            csv_auto = f"{nombre_base}_resultados.csv"
            self.evaluador.exportar_resultados(csv_auto)

            # Abrir ventana de gráficos automáticamente
            self._mostrar_graficos()

        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("Error", str(e))
            self.lbl_archivo.config(text="Selecciona un archivo CSV o Excel")
        except Exception as e:
            messagebox.showerror(
                "Error inesperado",
                f"Ocurrió un error al procesar el archivo:\n{e}",
            )
            self.lbl_archivo.config(text="Selecciona un archivo CSV o Excel")

    def _poblar_cursos(self) -> None:
        """Llena el combo de cursos con los valores únicos del dataset."""
        if not self.evaluador:
            return
        cursos = sorted(set(e.curso for e in self.evaluador.estudiantes))
        values = ["Todos"] + cursos
        self._combo_curso["values"] = values
        self._var_curso.set("Todos")

    def _aplicar_filtros(self) -> None:
        """Filtra los datos completos según los criterios seleccionados y refresca la tabla."""
        if not self._datos_completos:
            return

        datos = list(self._datos_completos)

        # 1. Filtrar por riesgo
        riesgo = self._var_riesgo.get()
        if riesgo != "Todos":
            datos = [d for d in datos if d["riesgo"] == riesgo]

        # 2. Filtrar por curso
        curso = self._var_curso.get()
        if curso != "Todos":
            datos = [d for d in datos if d["curso"] == curso]

        # 3. Filtrar por estado (aprobado/desaprobado)
        estado = self._var_estado.get()
        if estado == "Aprobado":
            datos = [d for d in datos if d["promedio"] >= 10.5]
        elif estado == "Desaprobado":
            datos = [d for d in datos if d["promedio"] < 10.5]

        # 4. Filtrar por búsqueda de texto (nombre o ID)
        busqueda = self._var_buscar.get().strip().lower()
        if busqueda:
            datos = [
                d for d in datos
                if busqueda in d["nombre"].lower()
                or busqueda in d["id"].lower()
            ]

        self._refrescar_tabla(datos)

    def _refrescar_tabla(self, datos: list[dict]) -> None:
        """Limpia la tabla y la llena con los datos filtrados."""
        self.tabla.tag_configure("alto", foreground=self.COLORES_RIESGO["Alto"])
        self.tabla.tag_configure("medio", foreground=self.COLORES_RIESGO["Medio"])
        self.tabla.tag_configure("bajo", foreground=self.COLORES_RIESGO["Bajo"])

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        for est in datos:
            valores = (
                est["id"],
                est["nombre"],
                est["curso"],
                f"{est['promedio']:.2f}",
                f"{est['asistencia']:.1f}",
                f"{est['compromiso']:.2f}",
                est["riesgo"],
                est["recomendacion"],
            )
            item_id = self.tabla.insert("", "end", values=valores)

            if est["riesgo"] == "Alto":
                self.tabla.item(item_id, tags=("alto",))
            elif est["riesgo"] == "Medio":
                self.tabla.item(item_id, tags=("medio",))
            elif est["riesgo"] == "Bajo":
                self.tabla.item(item_id, tags=("bajo",))

        self._lbl_mostrando.config(text=f"{len(datos)} de {len(self._datos_completos)}")

    _COLUMNAS_NUMERICAS = {"id", "promedio", "asistencia", "compromiso"}

    def _ordenar_tabla(self, columna: str) -> None:
        """Ordena la tabla por la columna indicada (asc/desc al alternar clic)."""
        if self._sort_col == columna:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = columna
            self._sort_asc = True

        flecha = " \u25B2" if self._sort_asc else " \u25BC"
        for col in self.tabla["columns"]:
            texto = self.tabla.heading(col)["text"].rstrip(" \u25B2\u25BC")
            self.tabla.heading(col, text=texto)

        texto_actual = self.tabla.heading(columna)["text"]
        self.tabla.heading(columna, text=texto_actual + flecha)

        datos = list(self.tabla.get_children("",))
        datos_ordenados = sorted(
            datos,
            key=lambda iid: self._clave_ordenamiento(iid, columna),
            reverse=not self._sort_asc,
        )
        for idx, iid in enumerate(datos_ordenados):
            self.tabla.move(iid, "", idx)

    def _clave_ordenamiento(self, iid: str, columna: str) -> float | str:
        """Retorna la clave de ordenamiento para una fila y columna dada."""
        valor = self.tabla.set(iid, columna)
        if columna in self._COLUMNAS_NUMERICAS:
            try:
                return float(valor)
            except (ValueError, TypeError):
                return 0.0
        return valor.lower() if isinstance(valor, str) else ""

    def _actualizar_resumen(self, config_notas: dict) -> None:
        """Actualiza las etiquetas de resumen con los resultados."""
        resumen = self.evaluador.resumen_por_nivel()
        total = sum(resumen.values())

        self.lbl_total.config(text=f"Total estudiantes: {total}")

        alto_pct = (resumen["Alto"] / total * 100) if total else 0
        medio_pct = (resumen["Medio"] / total * 100) if total else 0
        bajo_pct = (resumen["Bajo"] / total * 100) if total else 0

        self._dibujar_barra(self._barra_alto, resumen["Alto"], alto_pct, total)
        self._dibujar_barra(self._barra_medio, resumen["Medio"], medio_pct, total)
        self._dibujar_barra(self._barra_bajo, resumen["Bajo"], bajo_pct, total)

        columnas = ", ".join(config_notas["columnas_nota"])
        self.lbl_notas.config(text=f"Columnas de nota detectadas: {columnas}")
        curso_texto = (
            f"Sí ('{config_notas['curso_col']}')"
            if config_notas["tiene_cursos"]
            else "No (todos como 'General')"
        )
        self.lbl_curso.config(text=f"Columna curso: {curso_texto}")

    def _exportar_csv(self) -> None:
        """Exporta los resultados a un archivo CSV."""
        if not self.evaluador:
            return
        ruta = filedialog.asksaveasfilename(
            title="Guardar resultados como CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="resultados_riesgo.csv",
        )
        if ruta:
            self.evaluador.exportar_resultados(ruta)
            messagebox.showinfo("Exportado", f"Resultados guardados en:\n{ruta}")

    def _exportar_pdf(self) -> None:
        """Genera un reporte PDF con resumen, graficos y tabla de resultados."""
        if not self.evaluador:
            return
        ruta = filedialog.asksaveasfilename(
            title="Guardar reporte como PDF",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile="reporte_riesgo.pdf",
        )
        if not ruta:
            return

        from src.pdf_report import generar_reporte_pdf
        try:
            rutas_graficos = getattr(self, "_rutas_graficos", [])
            generar_reporte_pdf(
                self.evaluador,
                ruta,
                rutas_graficos,
                self.evaluador.config_notas,
            )
            messagebox.showinfo("PDF generado", f"Reporte guardado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF:\n{e}")

    def _mostrar_boton_graficos(self) -> None:
        """Crea y muestra el botón 'Ver Gráficos' solo si hay gráficos generados."""
        if not self._rutas_graficos:
            return
        if hasattr(self, '_btn_graficos') and self._btn_graficos.winfo_exists():
            return
        self._btn_graficos = ttk.Button(
            self._frame_botones, text="Ver Gráficos",
            command=self._mostrar_graficos,
        )
        self._btn_graficos.pack(side="left")

    def _mostrar_graficos(self) -> None:
        """Abre una ventana con los gráficos generados."""
        if not self.evaluador or not self._rutas_graficos:
            return
        VentanaGraficos(self.root, self._rutas_graficos)

    def _abrir_configuracion(self) -> None:
        """Abre la ventana de configuración de umbrales de riesgo."""
        VentanaConfiguracion(self.root, self)

    def _abrir_pesos(self) -> None:
        """Abre la ventana de configuración de pesos de notas."""
        if not self.evaluador:
            return
        VentanaPesos(self.root, self)

    def _mostrar_detalle_estudiante(self, event: tk.Event) -> None:
        """Abre ventana de detalle al hacer doble clic en una fila de la tabla."""
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        item = self.tabla.item(seleccion[0])
        id_est = item["values"][0]

        estudiante = None
        for e in self.evaluador.estudiantes:
            if e.id_estudiante == str(id_est):
                estudiante = e
                break

        if estudiante:
            config = self.evaluador.config_notas
            VentanaDetalleEstudiante(self.root, estudiante, config)


class VentanaGraficos:
    """
    Ventana emergente que muestra los gráficos generados.
    Recibe las rutas de las imágenes ya generadas.
    """

    def __init__(self, parent: tk.Tk, rutas: list[str]):
        self._rutas = rutas
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Gráficos de Análisis")
        self.ventana.geometry("900x700")

        if not self._rutas:
            ttk.Label(
                self.ventana, text="No se pudieron generar gráficos.",
            ).pack(pady=20)
            return

        # Crear pestañas para cada gráfico
        self._notebook = ttk.Notebook(self.ventana)
        self._notebook.pack(fill="both", expand=True, padx=10, pady=10)

        nombres = [
            "Distribución de Riesgo",
            "Promedio por Curso",
            "Asistencia vs Promedio",
            "Riesgo por Curso",
        ]

        for ruta, nombre in zip(self._rutas, nombres):
            if not ruta or not os.path.exists(ruta):
                continue
            self._agregar_pestania(ruta, nombre)

    def _agregar_pestania(self, ruta_imagen: str, titulo: str) -> None:
        """Agrega una pestaña con la imagen del gráfico."""
        from PIL import Image, ImageTk

        frame = ttk.Frame(self._notebook)
        self._notebook.add(frame, text=titulo)

        imagen = Image.open(ruta_imagen)
        # Redimensionar para que encaje en la ventana
        ancho_max = 850
        proporcion = ancho_max / imagen.width
        alto_max = int(imagen.height * proporcion)
        imagen = imagen.resize((ancho_max, alto_max), Image.LANCZOS)

        foto = ImageTk.PhotoImage(imagen)

        label = ttk.Label(frame, image=foto)
        label.image = foto  # mantener referencia
        label.pack(padx=10, pady=10)


class VentanaDetalleEstudiante:
    """Ventana emergente que muestra toda la información de un estudiante."""

    COLORES_RIESGO = {
        "Alto": "#e74c3c",
        "Medio": "#f39c12",
        "Bajo": "#27ae60",
    }

    def __init__(self, parent: tk.Tk, estudiante, config_notas: dict):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title(f"Detalle — {estudiante.nombre}")
        self.ventana.geometry("520x520")
        self.ventana.resizable(False, False)

        # ── Encabezado con nombre y riesgo ──
        frame_header = ttk.Frame(self.ventana, padding=15)
        frame_header.pack(fill="x")

        ttk.Label(
            frame_header, text=estudiante.nombre,
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")

        lbl_id = ttk.Label(
            frame_header,
            text=f"ID: {estudiante.id_estudiante}  |  Curso: {estudiante.curso}",
            font=("Segoe UI", 10),
        )
        lbl_id.pack(anchor="w", pady=(2, 0))

        color = self.COLORES_RIESGO.get(estudiante.nivel_riesgo, "#333")
        ttk.Label(
            frame_header,
            text=f"Riesgo: {estudiante.nivel_riesgo}",
            font=("Segoe UI", 12, "bold"),
            foreground=color,
        ).pack(anchor="w", pady=(6, 0))

        ttk.Separator(self.ventana, orient="horizontal").pack(fill="x", padx=15)

        # ── Panel de datos ──
        frame_datos = ttk.Frame(self.ventana, padding=15)
        frame_datos.pack(fill="both", expand=True)

        # Notas individuales
        ttk.Label(
            frame_datos, text="Notas individuales",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

        col_nota = config_notas.get("columnas_nota", [])
        for i, col in enumerate(col_nota):
            nota = estudiante.notas[i] if i < len(estudiante.notas) else 0
            peso = estudiante.pesos[i] if i < len(estudiante.pesos) else 0
            ttk.Label(frame_datos, text=f"  {col}:").grid(
                row=i + 1, column=0, sticky="w", padx=(10, 0)
            )
            ttk.Label(
                frame_datos,
                text=f"{nota:.1f}  (peso: {peso:.2%})",
            ).grid(row=i + 1, column=1, sticky="w")

        # Separador
        fila_sep = len(col_nota) + 1
        ttk.Separator(frame_datos, orient="horizontal").grid(
            row=fila_sep, column=0, columnspan=2, sticky="ew", pady=8
        )

        # Métricas calculadas
        fila = fila_sep + 1
        metricas = [
            ("Promedio ponderado:", f"{estudiante.promedio:.2f}"),
            ("Índice de compromiso:", f"{estudiante.indice_compromiso:.2f}"),
            ("", ""),
            ("Asistencia:", f"{estudiante.asistencia_pct:.1f}%"),
            ("Horas de estudio/semana:", f"{estudiante.horas_estudio_semanal:.1f}"),
            ("Tareas entregadas:", f"{estudiante.tareas_entregadas_pct:.1f}%"),
            ("Participación:", f"{estudiante.participacion}/5"),
        ]
        for j, (etiqueta, valor) in enumerate(metricas):
            if not etiqueta:
                continue
            ttk.Label(frame_datos, text=etiqueta, font=("Segoe UI", 9, "bold")).grid(
                row=fila + j, column=0, sticky="w", padx=(10, 0), pady=1
            )
            ttk.Label(frame_datos, text=valor).grid(
                row=fila + j, column=1, sticky="w", pady=1
            )

        # Separador
        fila_sep2 = fila + len(metricas)
        ttk.Separator(frame_datos, orient="horizontal").grid(
            row=fila_sep2, column=0, columnspan=2, sticky="ew", pady=8
        )

        # Recomendación
        fila_rec = fila_sep2 + 1
        ttk.Label(
            frame_datos, text="Recomendación:",
            font=("Segoe UI", 9, "bold"),
        ).grid(row=fila_rec, column=0, sticky="nw", padx=(10, 0), pady=1)
        lbl_rec = ttk.Label(
            frame_datos, text=estudiante.recomendacion,
            wraplength=350, justify="left",
        )
        lbl_rec.grid(row=fila_rec, column=1, sticky="w", pady=1)

        # ── Botón cerrar ──
        frame_btn = ttk.Frame(self.ventana, padding=10)
        frame_btn.pack(fill="x")
        ttk.Button(
            frame_btn, text="Cerrar", command=self.ventana.destroy,
        ).pack(side="right")


class VentanaConfiguracion:
    """Ventana emergente para ajustar los umbrales de riesgo academico."""

    ETIQUETAS = {
        "umbral_promedio_alto": ("Promedio umbral Alto:", "Si el promedio es menor a este valor, se considera riesgo Alto."),
        "umbral_promedio_medio": ("Promedio umbral Medio:", "Si el promedio es menor a este valor (>= Alto), es riesgo Medio."),
        "umbral_asistencia_alto": ("Asistencia umbral Alto (%):", "Si la asistencia es menor a este valor, se considera riesgo Alto."),
        "umbral_asistencia_medio": ("Asistencia umbral Medio (%):", "Si la asistencia es menor a este valor (>= Alto), es riesgo Medio."),
        "umbral_compromiso_alto": ("Compromiso umbral Alto (%):", "Si el indice de compromiso es menor a este valor, es riesgo Alto."),
        "umbral_compromiso_medio": ("Compromiso umbral Medio (%):", "Si el indice de compromiso es menor a este valor (>= Alto), es riesgo Medio."),
    }

    def __init__(self, parent: tk.Tk, ventana_principal: "VentanaPrincipal"):
        from src.config_manager import cargar_umbrales, guardar_umbrales, restablecer_umbrales

        self._guardar = guardar_umbrales
        self._restablecer = restablecer_umbrales
        self._vp = ventana_principal

        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Configurar Umbrales de Riesgo")
        self.ventana.geometry("520x480")
        self.ventana.resizable(False, False)
        self.ventana.grab_set()

        umbrales = cargar_umbrales()
        self._vars: dict[str, tk.StringVar] = {}

        ttk.Label(
            self.ventana,
            text="Ajuste los umbrales de clasificacion de riesgo academico.\n"
                 "Los valores se aplicaran al re-evaluar los estudiantes.",
            justify="center",
            font=("Segoe UI", 9),
            padding=10,
        ).pack(fill="x")

        frame = ttk.Frame(self.ventana, padding=10)
        frame.pack(fill="both", expand=True)

        for i, (clave, (etiqueta, ayuda)) in enumerate(self.ETIQUETAS.items()):
            ttk.Label(frame, text=etiqueta, font=("Segoe UI", 9, "bold")).grid(
                row=i * 2, column=0, sticky="w", padx=(10, 5), pady=(8, 0),
            )
            var = tk.StringVar(value=str(umbrales.get(clave, 0)))
            self._vars[clave] = var
            ttk.Entry(frame, textvariable=var, width=10).grid(
                row=i * 2, column=1, sticky="w", padx=(0, 10), pady=(8, 0),
            )
            ttk.Label(frame, text=ayuda, foreground="gray", font=("Segoe UI", 8)).grid(
                row=i * 2 + 1, column=0, columnspan=2, sticky="w", padx=(20, 0),
            )

        # Botones
        frame_btn = ttk.Frame(self.ventana, padding=10)
        frame_btn.pack(fill="x")

        ttk.Button(
            frame_btn, text="Restablecer predeterminados",
            command=self._restablecer_valores,
        ).pack(side="left")

        ttk.Button(
            frame_btn, text="Aplicar", command=self._aplicar,
        ).pack(side="right", padx=(5, 0))

        ttk.Button(
            frame_btn, text="Cancelar", command=self.ventana.destroy,
        ).pack(side="right")

    def _restablecer_valores(self) -> None:
        """Restablece los valores a los predeterminados."""
        nuevos = self._restablecer()
        for clave, var in self._vars.items():
            var.set(str(nuevos[clave]))

    def _aplicar(self) -> None:
        """Valida, guarda los umbrales y re-evalua los estudiantes."""
        nuevos = {}
        try:
            for clave, var in self._vars.items():
                valor = float(var.get())
                if valor <= 0 or valor > 100:
                    raise ValueError(f"El valor de {clave} debe estar entre 0 y 100.")
                nuevos[clave] = valor
        except ValueError as e:
            messagebox.showerror("Valor invalido", str(e), parent=self.ventana)
            return

        self._guardar(nuevos)
        self._vp.umbrales = nuevos

        # Re-evaluar si hay datos cargados
        if self._vp.evaluador:
            self._vp.evaluador.umbrales = nuevos
            self._vp.evaluador.evaluar_todos()
            self._vp._refrescar_tabla(self._vp.evaluador.obtener_datos_tabla())
            self._vp._actualizar_resumen(self._vp.evaluador.config_notas)

        messagebox.showinfo(
            "Configuracion aplicada",
            "Umbrales actualizados y estudiantes re-evaluados.",
            parent=self.ventana,
        )
        self.ventana.destroy()


class VentanaPesos:
    """Ventana emergente para ajustar los pesos de las columnas de notas."""

    def __init__(self, parent: tk.Tk, ventana_principal: "VentanaPrincipal"):
        from src.config_manager import cargar_pesos, guardar_pesos, restablecer_pesos

        self._guardar = guardar_pesos
        self._restablecer = restablecer_pesos
        self._vp = ventana_principal

        columnas = ventana_principal.evaluador.config_notas["columnas_nota"]
        pesos_actuales = ventana_principal.evaluador.config_notas["pesos"]

        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Configurar Pesos de Notas")
        self.ventana.geometry("480x420")
        self.ventana.resizable(False, False)
        self.ventana.grab_set()

        ttk.Label(
            self.ventana,
            text="Asigne el peso (porcentaje) de cada columna de nota.\n"
                 "La suma debe ser igual a 1.0 (100%).",
            justify="center",
            font=("Segoe UI", 9),
            padding=10,
        ).pack(fill="x")

        self._columnas = columnas
        self._vars: dict[str, tk.StringVar] = {}
        self._lbl_suma: ttk.Label | None = None

        frame = ttk.Frame(self.ventana, padding=10)
        frame.pack(fill="both", expand=True)

        for i, col in enumerate(columnas):
            peso_actual = pesos_actuales[i] if i < len(pesos_actuales) else round(1.0 / len(columnas), 4)
            ttk.Label(frame, text=col + ":", font=("Segoe UI", 9, "bold")).grid(
                row=i, column=0, sticky="w", padx=(10, 5), pady=6,
            )
            var = tk.StringVar(value=str(peso_actual))
            self._vars[col] = var
            ttk.Entry(frame, textvariable=var, width=10).grid(
                row=i, column=1, sticky="w", padx=(0, 10), pady=6,
            )
            ttk.Label(frame, text=f"({peso_actual * 100:.1f}%)").grid(
                row=i, column=2, sticky="w", pady=6,
            )

        # Indicador de suma
        sep_row = len(columnas)
        ttk.Separator(frame, orient="horizontal").grid(
            row=sep_row, column=0, columnspan=3, sticky="ew", pady=8,
        )
        self._lbl_suma = ttk.Label(
            frame, text="Suma: —", font=("Segoe UI", 9, "bold"),
        )
        self._lbl_suma.grid(row=sep_row + 1, column=0, columnspan=3, sticky="w", padx=(10, 0))
        self._actualizar_suma()

        # Vincular evento de cambio en cada variable
        for var in self._vars.values():
            var.trace_add("write", lambda *_: self._actualizar_suma())

        # Botones
        frame_btn = ttk.Frame(self.ventana, padding=10)
        frame_btn.pack(fill="x")

        ttk.Button(
            frame_btn, text="Iguales (1/n)",
            command=self._restablecer_iguales,
        ).pack(side="left")

        ttk.Button(
            frame_btn, text="Aplicar", command=self._aplicar,
        ).pack(side="right", padx=(5, 0))

        ttk.Button(
            frame_btn, text="Cancelar", command=self.ventana.destroy,
        ).pack(side="right")

    def _actualizar_suma(self) -> None:
        """Actualiza el indicador de suma total."""
        total = 0.0
        valido = True
        for col in self._columnas:
            try:
                total += float(self._vars[col].get())
            except ValueError:
                valido = False
                break

        if not valido:
            self._lbl_suma.config(text="Suma: valor invalido", foreground="gray")
        elif abs(total - 1.0) < 0.001:
            self._lbl_suma.config(text=f"Suma: {total:.4f}  OK", foreground="#27ae60")
        else:
            self._lbl_suma.config(text=f"Suma: {total:.4f}  (debe ser 1.0)", foreground="#e74c3c")

    def _restablecer_iguales(self) -> None:
        """Restablece todos los pesos a 1/n."""
        n = len(self._columnas)
        iguales = round(1.0 / n, 4)
        for i, col in enumerate(self._columnas):
            if i < n - 1:
                self._vars[col].set(str(iguales))
            else:
                self._vars[col].set(str(round(1.0 - iguales * (n - 1), 4)))

    def _aplicar(self) -> None:
        """Valida, guarda los pesos y re-evalua los estudiantes."""
        pesos_nuevos = {}
        try:
            for col in self._columnas:
                valor = float(self._vars[col].get())
                if valor < 0 or valor > 1:
                    raise ValueError(f"El peso de '{col}' debe estar entre 0 y 1.")
                pesos_nuevos[col] = valor
        except ValueError as e:
            messagebox.showerror("Valor invalido", str(e), parent=self.ventana)
            return

        total = sum(pesos_nuevos.values())
        if abs(total - 1.0) > 0.01:
            messagebox.showwarning(
                "Pesos no suman 1.0",
                f"La suma actual es {total:.4f}. Debe ser 1.0 (100%).",
                parent=self.ventana,
            )
            return

        self._guardar(pesos_nuevos)

        # Actualizar pesos en el evaluador y re-evaluar
        pesos_lista = [pesos_nuevos[col] for col in self._columnas]
        self._vp.evaluador.config_notas["pesos"] = pesos_lista
        self._vp.evaluador.evaluar_todos()
        self._vp._refrescar_tabla(self._vp.evaluador.obtener_datos_tabla())
        self._vp._actualizar_resumen(self._vp.evaluador.config_notas)

        messagebox.showinfo(
            "Pesos actualizados",
            "Pesos guardados y estudiantes re-evaluados.",
            parent=self.ventana,
        )
        self.ventana.destroy()
