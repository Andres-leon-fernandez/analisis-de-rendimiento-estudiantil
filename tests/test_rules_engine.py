import pytest
from src.rules_engine import evaluar_reglas_riesgo, generar_recomendacion


class TestEvaluarReglasRiesgo:
    def test_riesgo_alto_por_promedio_y_asistencia(self):
        assert evaluar_reglas_riesgo("T001", 9.0, 60.0, 50.0) == "Alto"

    def test_riesgo_alto_por_promedio_y_compromiso(self):
        assert evaluar_reglas_riesgo("T002", 8.0, 85.0, 40.0) == "Alto"

    def test_riesgo_medio_por_promedio_y_asistencia(self):
        assert evaluar_reglas_riesgo("T003", 12.0, 75.0, 70.0) == "Medio"

    def test_riesgo_medio_por_compromiso_bajo(self):
        assert evaluar_reglas_riesgo("T004", 15.0, 90.0, 50.0) == "Medio"

    def test_riesgo_bajo(self):
        assert evaluar_reglas_riesgo("T005", 16.0, 95.0, 80.0) == "Bajo"

    def test_ids_diferentes_no_colisionan(self):
        r1 = evaluar_reglas_riesgo("X001", 9.0, 60.0, 50.0)
        r2 = evaluar_reglas_riesgo("X002", 16.0, 95.0, 80.0)
        assert r1 == "Alto"
        assert r2 == "Bajo"

    def test_limite_exacto_promedio_10_5(self):
        resultado = evaluar_reglas_riesgo("T006", 10.5, 90.0, 80.0)
        assert resultado == "Medio"

    def test_limite_exacto_asistencia_80(self):
        resultado = evaluar_reglas_riesgo("T007", 14.0, 80.0, 70.0)
        assert resultado == "Bajo"


class TestGenerarRecomendacion:
    def test_alto_menciona_tutoria(self):
        rec = generar_recomendacion("Alto")
        assert "tutoria" in rec.lower()

    def test_medio_menciona_reforzar(self):
        rec = generar_recomendacion("Medio")
        assert "reforzar" in rec.lower()

    def test_bajo_menciona_mantener(self):
        rec = generar_recomendacion("Bajo")
        assert "mantener" in rec.lower()

    def test_nivel_desconocido(self):
        rec = generar_recomendacion("Inexistente")
        assert "recomendacion" in rec.lower() or "disponible" in rec.lower()
