"""
==================================================================
 CARGA Y VALIDACIÓN DE DATOS
 Soporta archivos CSV y Excel (.xlsx, .xls)
==================================================================
"""

import pandas as pd


def cargar_archivo(ruta: str) -> pd.DataFrame:
    """
    Carga un archivo CSV o Excel y retorna un DataFrame.
    Detecta automáticamente el formato según la extensión.
    Lanza ValueError si el archivo no existe o el formato no es soportado.
    """
    import os
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    if ruta.endswith((".xlsx", ".xls")):
        df = pd.read_excel(ruta)
    elif ruta.endswith(".csv"):
        df = pd.read_csv(ruta)
    else:
        raise ValueError("Formato no soportado. Usa archivos .csv, .xlsx o .xls")

    if df.empty:
        raise ValueError("El archivo está vacío.")

    return df


def limpiar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia los datos: rellena valores nulos con la mediana de cada
    columna numérica identificada automáticamente.
    """
    columnas_numericas = df.select_dtypes(include=["float64", "int64"]).columns
    for col in columnas_numericas:
        if df[col].isna().any():
            mediana = df[col].median()
            df[col] = df[col].fillna(mediana)
    return df
