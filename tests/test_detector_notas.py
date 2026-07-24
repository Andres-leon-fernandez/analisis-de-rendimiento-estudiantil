import pytest
import pandas as pd
from src.detector_notas import detectar_columnas_notas


class TestDetectarColumnasNotas:
    def _make_df(self, columns):
        return pd.DataFrame(columns=columns)

    def test_detecta_nota_ep(self):
        df = self._make_df(["id_estudiante", "nombre", "nota_ep1", "nota_ep2"])
        config = detectar_columnas_notas(df)
        assert "nota_ep1" in config["columnas_nota"]
        assert "nota_ep2" in config["columnas_nota"]

    def test_detecta_examen_final(self):
        df = self._make_df(["id_estudiante", "examen_final", "examen_practico"])
        config = detectar_columnas_notas(df)
        assert len(config["columnas_nota"]) == 2

    def test_pesos_suman_uno(self):
        df = self._make_df(["id", "nota_1", "nota_2", "nota_3"])
        config = detectar_columnas_notas(df)
        assert pytest.approx(sum(config["pesos"]), abs=0.001) == 1.0

    def test_no_detecta_columnas_metadata(self):
        df = self._make_df(["id_estudiante", "nombre", "curso", "asistencia_pct"])
        with pytest.raises(ValueError):
            detectar_columnas_notas(df)

    def test_detecta_columna_curso(self):
        df = self._make_df(["id", "curso", "nota_1"])
        config = detectar_columnas_notas(df)
        assert config["tiene_cursos"] is True
        assert config["curso_col"] == "curso"

    def test_no_hay_columna_curso(self):
        df = self._make_df(["id", "nota_1"])
        config = detectar_columnas_notas(df)
        assert config["tiene_cursos"] is False
        assert config["curso_col"] is None

    def test_prefijo_ep_sin_numero(self):
        df = self._make_df(["id", "ep", "nota_final"])
        config = detectar_columnas_notas(df)
        assert "ep" in config["columnas_nota"]
        assert "nota_final" in config["columnas_nota"]
