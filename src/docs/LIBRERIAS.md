# Librerías utilizadas en el proyecto

Este documento lista todas las dependencias externas del proyecto **Análisis de Rendimiento Estudiantil**, con la versión mínima requerida (ver [`requirements.txt`](../../requirements.txt)) y el comando para instalarlas.

## Instalación rápida (todas a la vez)

```bash
pip install -r requirements.txt
```

## Detalle por librería

### pandas
- **Versión mínima:** `>=1.3.0`
- **Uso en el proyecto:** carga y limpieza de datos ([`src/carga.py`](../carga.py)), detección de columnas de notas ([`src/detector_notas.py`](../detector_notas.py)), modelo de estudiante ([`src/models.py`](../models.py)), gráficos ([`src/graficos.py`](../graficos.py)).
- **Instalación:**
```bash
pip install pandas>=1.3.0
```

### numpy
- **Versión mínima:** `>=1.21.0`
- **Uso en el proyecto:** cálculos numéricos en [`src/functional.py`](../functional.py) y [`src/detector_notas.py`](../detector_notas.py).
- **Instalación:**
```bash
pip install numpy>=1.21.0
```

### matplotlib
- **Versión mínima:** `>=3.4.0`
- **Uso en el proyecto:** generación de gráficos estadísticos ([`src/graficos.py`](../graficos.py)).
- **Instalación:**
```bash
pip install matplotlib>=3.4.0
```

### openpyxl
- **Versión mínima:** `>=3.0.0`
- **Uso en el proyecto:** motor usado por pandas para leer/escribir archivos Excel (`.xlsx`) en [`src/carga.py`](../carga.py).
- **Instalación:**
```bash
pip install openpyxl>=3.0.0
```

### Pillow
- **Versión mínima:** `>=9.0.0`
- **Uso en el proyecto:** manejo de imágenes para la interfaz gráfica (`ttkbootstrap`/Tkinter) en [`src/gui.py`](../gui.py).
- **Instalación:**
```bash
pip install Pillow>=9.0.0
```

### ttkbootstrap
- **Versión mínima:** `>=1.10.1`
- **Uso en el proyecto:** temas y widgets modernos para la interfaz gráfica ([`src/gui.py`](../gui.py), [`main.py`](../../main.py)).
- **Instalación:**
```bash
pip install ttkbootstrap>=1.10.1
```

### pyswip
- **Versión mínima:** `>=0.3.3`
- **Uso en el proyecto:** puente Python↔Prolog para el motor de reglas declarativas ([`src/rules_engine.py`](../rules_engine.py) + [`reglas_riesgo.pl`](../reglas_riesgo.pl)).
- **Instalación:**
```bash
pip install pyswip>=0.3.3
```
- **Requisito adicional:** necesita **SWI-Prolog** instalado en el sistema (no es un paquete de pip). Descarga: https://www.swi-prolog.org/download/stable

### fpdf2
- **Versión mínima:** `>=2.8.0`
- **Uso en el proyecto:** generación de reportes en PDF ([`src/pdf_report.py`](../pdf_report.py)), importado como `from fpdf import FPDF`.
- **Instalación:**
```bash
pip install fpdf2>=2.8.0
```

### pytest
- **Versión mínima:** `>=7.0.0`
- **Uso en el proyecto:** framework de pruebas unitarias ([`tests/`](../../tests/)).
- **Instalación:**
```bash
pip install pytest>=7.0.0
```

## Librerías de la biblioteca estándar de Python

Estas ya vienen incluidas con Python y no requieren instalación:

| Módulo | Uso |
|---|---|
| `tkinter` | Interfaz gráfica base ([`src/gui.py`](../gui.py)). En Linux puede requerir el paquete del sistema `python3-tk`. |
| `os` | Manejo de rutas y archivos. |
| `json` | Lectura/escritura de [`config.json`](../../config.json) en [`src/config_manager.py`](../config_manager.py). |
| `dataclasses` | Definición del modelo `Estudiante` en [`src/models.py`](../models.py). |
| `functools` | Programación funcional (`reduce`) en [`src/functional.py`](../functional.py). |
| `typing` | Tipado estático (`Callable`, etc.). |
| `__future__` | Anotaciones de tipos modernas (`list[float]`, `X | None`). |

## Requisitos previos del sistema

- **Python 3.10+**
- **SWI-Prolog** (requerido por `pyswip` para el motor de reglas lógicas)
