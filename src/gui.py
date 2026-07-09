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

        self.lbl_riesgo_alto = ttk.Label(
            frame_resumen, text="Riesgo Alto: —", foreground=self.COLORES_RIESGO["Alto"]
        )
        self.lbl_riesgo_alto.pack(anchor="w")

        self.lbl_riesgo_medio = ttk.Label(
            frame_resumen, text="Riesgo Medio: —", foreground=self.COLORES_RIESGO["Medio"]
        )
        self.lbl_riesgo_medio.pack(anchor="w")

        self.lbl_riesgo_bajo = ttk.Label(
            frame_resumen, text="Riesgo Bajo: —", foreground=self.COLORES_RIESGO["Bajo"]
        )
        self.lbl_riesgo_bajo.pack(anchor="w")

        self.lbl_notas = ttk.Label(frame_resumen, text="Columnas de nota detectadas: —")
        self.lbl_notas.pack(anchor="w")

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

        columnas = ("id", "nombre", "curso", "promedio", "asistencia", "compromiso", "riesgo")
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
        }
        for col, texto in encabezados.items():
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=100, minwidth=80)

        self.tabla.column("id", width=70)
        self.tabla.column("nombre", width=160)
        self.tabla.column("curso", width=160)
        self.tabla.column("promedio", width=90)
        self.tabla.column("asistencia", width=90)
        self.tabla.column("compromiso", width=100)
        self.tabla.column("riesgo", width=90)

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

        # ── Panel de botones ──
        self._frame_botones = ttk.Frame(self.root, padding=10)
        self._frame_botones.pack(fill="x", padx=10, pady=(0, 10))

        self._btn_exportar = ttk.Button(
            self._frame_botones, text="Exportar CSV", command=self._exportar_csv
        )
        self._btn_exportar.pack(side="left", padx=(0, 10))
        self._btn_exportar.state(["disabled"])

        # "Ver Gráficos" se crea y muestra solo cuando hay datos cargados

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
            )
            item_id = self.tabla.insert("", "end", values=valores)

            if est["riesgo"] == "Alto":
                self.tabla.item(item_id, tags=("alto",))
            elif est["riesgo"] == "Medio":
                self.tabla.item(item_id, tags=("medio",))
            elif est["riesgo"] == "Bajo":
                self.tabla.item(item_id, tags=("bajo",))

        self._lbl_mostrando.config(text=f"{len(datos)} de {len(self._datos_completos)}")

    def _actualizar_resumen(self, config_notas: dict) -> None:
        """Actualiza las etiquetas de resumen con los resultados."""
        resumen = self.evaluador.resumen_por_nivel()
        total = sum(resumen.values())

        self.lbl_total.config(text=f"Total estudiantes: {total}")

        alto_pct = (resumen["Alto"] / total * 100) if total else 0
        medio_pct = (resumen["Medio"] / total * 100) if total else 0
        bajo_pct = (resumen["Bajo"] / total * 100) if total else 0

        self.lbl_riesgo_alto.config(
            text=f"Riesgo Alto: {resumen['Alto']} ({alto_pct:.1f}%)"
        )
        self.lbl_riesgo_medio.config(
            text=f"Riesgo Medio: {resumen['Medio']} ({medio_pct:.1f}%)"
        )
        self.lbl_riesgo_bajo.config(
            text=f"Riesgo Bajo: {resumen['Bajo']} ({bajo_pct:.1f}%)"
        )

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
