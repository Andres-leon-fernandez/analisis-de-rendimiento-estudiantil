# Análisis Inteligente de Rendimiento Académico Estudiantil

**Curso:** Lenguajes de Programación (100000SI68)

Documentación técnica completa del proyecto: qué hace, cómo está organizado, cómo funciona internamente cada módulo y cómo ejecutarlo de principio a fin.

---

## 1. Propósito del sistema

La aplicación toma un archivo de notas de estudiantes (CSV o Excel), calcula el rendimiento académico de cada uno y **clasifica automáticamente su nivel de riesgo académico** (Alto, Medio o Bajo) combinando promedio de notas, asistencia y compromiso (tareas + participación). El resultado se muestra en una interfaz gráfica de escritorio (Tkinter), se puede exportar a CSV y se visualiza mediante 4 gráficos estadísticos generados con matplotlib.

El proyecto es también un ejercicio académico: demuestra tres paradigmas de programación trabajando juntos sobre el mismo dominio.

| Paradigma | Dónde vive | Qué resuelve |
|---|---|---|
| **Funcional** | [`src/functional.py`](../functional.py) | Cálculo de promedio ponderado y compromiso mediante funciones puras (`map`/`filter`/`reduce`), sin efectos secundarios. |
| **Lógico** | [`src/rules_engine.py`](../rules_engine.py) | Motor de reglas "si-entonces" tipo sistema experto que clasifica el riesgo. |
| **Orientado a objetos** | [`src/models.py`](../models.py) | Clases `Estudiante` y `EvaluadorRiesgo` que modelan el dominio y orquestan el flujo. |

---

## 2. Estructura del proyecto

```
analisis-de-rendimiento-estudiantil/
├── main.py                                # Punto de entrada de la aplicación
├── requirements.txt                       # Dependencias (pandas, numpy, matplotlib, openpyxl)
├── rendimiento_estudiantil.csv            # Dataset de ejemplo (entrada)
├── rendimiento_estudiantil_26.csv         # Otro dataset de ejemplo
├── rendimiento_estudiantil_resultados.csv # Salida generada automáticamente
├── rendimiento_estudiantil-img/           # Gráficos PNG generados automáticamente
│   ├── distribucion_riesgo.png
│   ├── promedio_por_curso.png
│   ├── asistencia_vs_promedio.png
│   └── riesgo_por_curso.png
└── src/
    ├── __init__.py
    ├── carga.py            # Carga y limpieza de datos (pandas)
    ├── detector_notas.py   # Detección automática de columnas de notas
    ├── functional.py       # Paradigma funcional: cálculos puros
    ├── rules_engine.py     # Paradigma lógico: motor de reglas
    ├── models.py            # Paradigma OOP: Estudiante y EvaluadorRiesgo
    ├── graficos.py          # Generación de visualizaciones (matplotlib)
    ├── gui.py               # Interfaz gráfica (Tkinter)
    └── docs/                # Esta documentación
```

---

## 3. Flujo de ejecución de principio a fin

```
1. python main.py
2. Se abre la ventana principal (VentanaPrincipal) → tk.Tk() + mainloop()
3. Usuario pulsa "Examinar..." y elige un CSV/Excel
        │
        ▼
4. carga.cargar_archivo(ruta)          → lee el archivo a un DataFrame
        │
        ▼
5. detector_notas.detectar_columnas_notas(df)
        → identifica columnas de nota por prefijo (nota_, examen_, eval_, ...)
        → calcula pesos iguales normalizados a 1.0
        → detecta si existe columna "curso"
        │
        ▼
6. models.EvaluadorRiesgo(df, config_notas)
        → limpia datos (carga.limpiar_datos: rellena NaN con la mediana)
        │
        ▼
7. evaluador.construir_estudiantes()
        → convierte cada fila del DataFrame en un objeto Estudiante
        │
        ▼
8. evaluador.evaluar_todos()
        → por cada Estudiante:
            a) calcular_metricas()   [functional.py: promedio ponderado + índice de compromiso]
            b) evaluar_riesgo()      [rules_engine.py: motor de reglas → nivel_riesgo + recomendación]
        │
        ▼
9. GUI se actualiza:
        - Panel de resumen (totales por nivel de riesgo)
        - Tabla de estudiantes (Treeview, coloreada por riesgo)
        - Combo de cursos poblado dinámicamente
        │
        ▼
10. graficos.generar_todos_los_graficos(evaluador, carpeta)
        → genera 4 PNG en "<nombre_archivo>-img/"
        │
        ▼
11. Exportación automática a "<nombre_archivo>_resultados.csv"
        │
        ▼
12. Se abre automáticamente VentanaGraficos con los 4 gráficos en pestañas
        │
        ▼
13. Usuario puede filtrar (riesgo/curso/estado/búsqueda), exportar
    manualmente a otro CSV, o reabrir la ventana de gráficos.
```

---

## 4. Formato de datos de entrada

El archivo de notas (CSV o Excel) debe tener, como mínimo, columnas de nota reconocibles por prefijo. Ejemplo real usado en el proyecto (`rendimiento_estudiantil.csv`):

```
id_estudiante,nombre,curso,ciclo,asistencia_pct,horas_estudio_semanal,tareas_entregadas_pct,participacion,nota_ep1,nota_ep2,nota_final
E0001,María Aguilar,Matemática Discreta,2025-2,93.8,1.6,66.5,4,14.1,13.1,16.2
```

### Columnas reconocidas explícitamente (metadata, nunca se tratan como nota)

`id_estudiante`, `nombre`, `curso`, `ciclo`, `asistencia_pct`, `horas_estudio_semanal`, `tareas_entregadas_pct`, `participacion`

### Columnas de nota (detectadas automáticamente por prefijo)

Cualquier columna cuyo nombre (en minúsculas) empiece con:

`nota_`, `examen_`, `eval_`, `parcial_`, `final_`, `practico_`, `lab_`, `ep`

Ejemplos válidos: `nota_ep1`, `examen_final`, `parcial_1`, `ep2`. El sistema **no limita cuántas** columnas de nota puede haber: se detectan todas y a cada una se le asigna un peso igual (`1/N`), ajustando el último peso para que la suma sea exactamente `1.0`.

Si no se detecta ninguna columna de nota, se lanza un `ValueError` explicativo.

Si no existe columna `curso`, todos los estudiantes se agrupan bajo el curso `"General"`.

Los valores nulos en columnas numéricas se rellenan automáticamente con la **mediana** de esa columna (`carga.limpiar_datos`).

---

## 5. Módulos en detalle

### 5.1 `main.py` — Punto de entrada

Crea la ventana raíz de Tkinter, instancia `VentanaPrincipal` y arranca el bucle de eventos (`root.mainloop()`). No contiene lógica de negocio.

### 5.2 `src/carga.py` — Carga y limpieza de datos

- `cargar_archivo(ruta)`: detecta el formato por extensión (`.csv`, `.xlsx`, `.xls`), lee con pandas y valida que el archivo exista y no esté vacío. Lanza `FileNotFoundError` o `ValueError` según el caso.
- `limpiar_datos(df)`: para cada columna numérica (`float64`/`int64`) con valores nulos, los reemplaza por la **mediana** de esa columna.

### 5.3 `src/detector_notas.py` — Detección automática del sistema de notas

- `PREFIJOS_NOTA`: lista de prefijos reconocidos como columnas de evaluación.
- `COLUMNAS_EXCLUIDAS`: set de columnas que jamás se consideran nota, aunque coincidan con un prefijo.
- `detectar_columnas_notas(df)`: recorre las columnas, aplica la exclusión y el filtro por prefijo, calcula pesos iguales normalizados, y detecta si existe columna `curso`. Retorna un diccionario:
  ```python
  {
      "columnas_nota": [...],
      "pesos": [...],
      "tiene_cursos": bool,
      "curso_col": "curso" | None,
  }
  ```

### 5.4 `src/functional.py` — Paradigma funcional

Funciones **puras** (sin efectos secundarios, mismo input → mismo output):

- `calcular_promedio_notas(notas, pesos)`: producto punto (`np.dot`) entre notas y pesos → promedio ponderado.
- `calcular_indice_compromiso(asistencia, tareas, participacion)`: combina asistencia, % de tareas entregadas y participación (escala 1-5, normalizada ×20) usando `reduce` para sumarlos y dividir entre 3 → índice de 0 a 100.
- `aplicar_a_todos(func, valores)`: envoltorio sobre `map`.
- `filtrar_por_condicion(estudiantes, condicion)`: envoltorio sobre `filter`, usado por `EvaluadorRiesgo.estudiantes_en_riesgo`.

### 5.5 `src/rules_engine.py` — Paradigma lógico (sistema experto)

`evaluar_reglas_riesgo(promedio, asistencia, compromiso)` aplica reglas "si-entonces" **en orden de severidad**:

| Orden | Condición | Resultado |
|---|---|---|
| 1 | `promedio < 10.5` y `asistencia < 70` | **Alto** |
| 2 | `promedio < 10.5` y `compromiso < 60` | **Alto** |
| 3 | `promedio < 13` y `asistencia < 80` | **Medio** |
| 4 | `compromiso < 65` | **Medio** |
| 5 | `promedio >= 13` y `asistencia >= 80` y `compromiso >= 65` | **Bajo** |
| — | cualquier otro caso no cubierto | **Medio** (regla de respaldo) |

`generar_recomendacion(nivel_riesgo)` mapea cada nivel a un mensaje de acción:

- **Alto** → "Requiere tutoría académica inmediata y seguimiento semanal."
- **Medio** → "Se recomienda reforzar hábitos de estudio y asistencia."
- **Bajo** → "Mantener el desempeño actual; sin acciones urgentes."

### 5.6 `src/models.py` — Paradigma orientado a objetos

**`Estudiante`** (`@dataclass`): almacena los datos crudos de una fila (`id_estudiante`, `nombre`, `curso`, `notas`, `pesos`, `asistencia_pct`, `horas_estudio_semanal`, `tareas_entregadas_pct`, `participacion`) y campos calculados (`promedio`, `indice_compromiso`, `nivel_riesgo`, `recomendacion`, inicializados vacíos con `init=False`).

- `calcular_metricas()`: delega en `functional.py` para llenar `promedio` e `indice_compromiso`.
- `evaluar_riesgo()`: delega en `rules_engine.py` para llenar `nivel_riesgo` y `recomendacion`.

**`EvaluadorRiesgo`**: clase orquestadora que administra la colección completa de estudiantes.

- `__init__(dataframe, config_notas)`: limpia el DataFrame (`limpiar_datos`) y guarda la configuración de notas.
- `construir_estudiantes()`: itera el DataFrame fila por fila y crea un objeto `Estudiante` por cada una.
- `evaluar_todos()`: llama `calcular_metricas()` y `evaluar_riesgo()` en cada estudiante.
- `estudiantes_en_riesgo(nivel)`: filtra usando `functional.filtrar_por_condicion`.
- `resumen_por_nivel()`: cuenta estudiantes por nivel de riesgo → `{"Alto": n, "Medio": n, "Bajo": n}`.
- `resumen_por_curso()`: agrega con pandas (`groupby`) promedio, asistencia y total de estudiantes por curso.
- `exportar_resultados(ruta_salida)`: escribe el reporte final a CSV (UTF-8 con BOM, `utf-8-sig`).
- `obtener_datos_tabla()`: retorna una lista de diccionarios lista para poblar la tabla de la GUI.

### 5.7 `src/graficos.py` — Visualizaciones

Usa matplotlib con backend `Agg` (sin ventana propia, solo genera archivos). Todas las funciones reciben un `EvaluadorRiesgo` ya evaluado y una carpeta de salida:

1. **`graficar_distribucion_riesgo`** — barras verticales: cantidad de estudiantes por nivel de riesgo (rojo/naranja/verde).
2. **`graficar_promedio_por_curso`** — barras horizontales: promedio de notas por curso (escala 0-20). Vacío si no hay columna curso.
3. **`graficar_asistencia_vs_promedio`** — dispersión (scatter): asistencia (%) vs. promedio, coloreado por nivel de riesgo.
4. **`graficar_riesgo_por_curso`** — barras apiladas: composición de niveles de riesgo dentro de cada curso (usa `pd.crosstab`). Solo se genera si el dataset tiene columna curso.

`generar_todos_los_graficos(evaluador, carpeta)` crea la carpeta si no existe, ejecuta las 4 funciones y devuelve solo las rutas de los gráficos efectivamente generados (descarta cadenas vacías).

La carpeta de salida se nombra dinámicamente como `<nombre_del_archivo_cargado>-img/` (ver `gui.py`).

### 5.8 `src/gui.py` — Interfaz gráfica (Tkinter)

**`VentanaPrincipal`**: ventana principal (1100×750, mínimo 900×600) con:

- **Panel "Cargar archivo"**: botón "Examinar..." que abre un diálogo de selección de CSV/Excel.
- **Panel "Resumen"**: totales de estudiantes y desglose por nivel de riesgo (con color), columnas de nota detectadas y si existe columna curso.
- **Panel "Filtrar resultados"**: combos de Riesgo (Todos/Alto/Medio/Bajo), Curso (poblado dinámicamente) y Estado (Todos/Aprobado ≥10.5/Desaprobado <10.5), más un campo de búsqueda por nombre o ID. Los filtros se combinan entre sí (AND) y se aplican en memoria sobre `_datos_completos` sin volver a tocar el DataFrame.
- **Tabla de estudiantes** (`ttk.Treeview`): columnas ID, Nombre, Curso, Promedio, Asistencia, Compromiso, Riesgo — con scroll vertical y horizontal, y filas coloreadas según el nivel de riesgo mediante tags.
- **Botones**: "Exportar CSV" (habilitado tras cargar datos) y "Ver Gráficos" (aparece solo si se generaron gráficos).

Flujo al seleccionar archivo (`_seleccionar_archivo`): carga → detecta notas → construye y evalúa estudiantes → actualiza resumen → puebla combo de cursos → aplica filtros → habilita exportar → **genera gráficos automáticamente** → **exporta CSV automáticamente** (`<nombre>_resultados.csv`) → **abre automáticamente la ventana de gráficos**. Maneja errores de archivo no encontrado / formato inválido con `messagebox.showerror`, y cualquier otra excepción como "error inesperado".

**`VentanaGraficos`**: ventana emergente (`Toplevel`, 900×700) con un `ttk.Notebook` (pestañas), una por cada gráfico generado: "Distribución de Riesgo", "Promedio por Curso", "Asistencia vs Promedio", "Riesgo por Curso". Cada imagen se abre con Pillow (`PIL.Image`/`ImageTk`) y se redimensiona a un ancho máximo de 850px manteniendo proporción.

> **Nota de dependencia:** `gui.py` usa `PIL` (Pillow) para mostrar las imágenes en las pestañas, pero **Pillow no figura en `requirements.txt`**. Debe instalarse aparte (`pip install Pillow`) o agregarse al archivo de requisitos.

---

## 6. Cómo ejecutar el proyecto

### 6.1 Requisitos previos

- Python 3.10+ (el proyecto usa sintaxis moderna de tipos como `list[float]` y `X | None`).
- Dependencias de `requirements.txt`: `pandas`, `numpy`, `matplotlib`, `openpyxl`.
- **Pillow** (no listado en requirements.txt, pero requerido por `gui.py` para mostrar gráficos).
- Tkinter (incluido en la instalación estándar de Python en Windows; en Linux puede requerir el paquete `python3-tk`).

### 6.2 Instalación

```powershell
pip install -r requirements.txt
pip install Pillow
```

### 6.3 Ejecución

Desde la carpeta raíz del proyecto (`analisis-de-rendimiento-estudiantil/`):

```powershell
python main.py
```

Se abrirá la ventana principal. Pulsar "Examinar...", elegir `rendimiento_estudiantil.csv` (o cualquier CSV/Excel con el formato descrito en la sección 4) y el sistema procesará todo automáticamente: tabla, resumen, gráficos y exportación.

### 6.4 Salidas generadas

Al procesar `nombre_archivo.csv`, el sistema genera junto al proyecto:

- `nombre_archivo-img/` con los 4 PNG de gráficos.
- `nombre_archivo_resultados.csv` con el reporte final (id, nombre, curso, promedio, asistencia, índice de compromiso, nivel de riesgo, recomendación).

También se puede exportar manualmente a cualquier ruta con el botón "Exportar CSV".

---

## 7. Resumen de reglas de negocio clave

- **Promedio**: suma ponderada de todas las notas detectadas, con pesos iguales que suman exactamente 1.0.
- **Índice de compromiso**: promedio simple de `asistencia_pct`, `tareas_entregadas_pct` y `participacion × 20` (normalizada a escala 0-100).
- **Aprobación** (solo para el filtro de la GUI, no afecta el nivel de riesgo): promedio ≥ 10.5 = Aprobado.
- **Nivel de riesgo**: ver tabla de reglas en la sección 5.5.
- **Datos faltantes**: se imputan con la mediana de la columna correspondiente antes de cualquier cálculo.
