import pytest
import pandas as pd
from src.models import Estudiante, EvaluadorRiesgo


class TestEstudiante:
    def _make_estudiante(self, notas=None, pesos=None):
        return Estudiante(
            id_estudiante="E001",
            nombre="Test",
            curso="Curso A",
            notas=notas or [14.0, 12.0, 16.0],
            pesos=pesos or [0.3333, 0.3333, 0.3334],
            asistencia_pct=90.0,
            horas_estudio_semanal=3.0,
            tareas_entregadas_pct=80.0,
            participacion=4,
        )

    def test_calcular_metricas(self):
        est = self._make_estudiante()
        est.calcular_metricas()
        assert est.promedio > 0
        assert est.indice_compromiso > 0

    def test_evaluar_riesgo_bajo(self):
        est = self._make_estudiante(
            notas=[16.0, 17.0, 15.0],
            pesos=[0.3333, 0.3333, 0.3334],
        )
        est.asistencia_pct = 95.0
        est.tareas_entregadas_pct = 90.0
        est.participacion = 5
        est.calcular_metricas()
        est.evaluar_riesgo()
        assert est.nivel_riesgo == "Bajo"
        assert "mantener" in est.recomendacion.lower()

    def test_evaluar_riesgo_alto(self):
        est = self._make_estudiante(
            notas=[5.0, 4.0, 6.0],
            pesos=[0.3333, 0.3333, 0.3334],
        )
        est.asistencia_pct = 40.0
        est.tareas_entregadas_pct = 30.0
        est.participacion = 1
        est.calcular_metricas()
        est.evaluar_riesgo()
        assert est.nivel_riesgo == "Alto"

    def test_str_repr(self):
        est = self._make_estudiante()
        est.calcular_metricas()
        est.evaluar_riesgo()
        texto = str(est)
        assert "E001" in texto
        assert "Test" in texto


class TestEvaluadorRiesgo:
    def _make_evaluador(self):
        df = pd.DataFrame({
            "id_estudiante": ["E001", "E002", "E003"],
            "nombre": ["Ana", "Luis", "María"],
            "curso": ["A", "A", "B"],
            "asistencia_pct": [95.0, 50.0, 80.0],
            "horas_estudio_semanal": [3.0, 1.0, 2.5],
            "tareas_entregadas_pct": [90.0, 40.0, 70.0],
            "participacion": [5, 1, 3],
            "nota_ep1": [16.0, 8.0, 14.0],
            "nota_ep2": [15.0, 7.0, 13.0],
            "nota_final": [17.0, 9.0, 15.0],
        })
        config = {
            "columnas_nota": ["nota_ep1", "nota_ep2", "nota_final"],
            "pesos": [0.3333, 0.3333, 0.3334],
            "tiene_cursos": True,
            "curso_col": "curso",
        }
        return EvaluadorRiesgo(df, config)

    def test_construir_estudiantes(self):
        ev = self._make_evaluador()
        ev.construir_estudiantes()
        assert len(ev.estudiantes) == 3

    def test_evaluar_todos(self):
        ev = self._make_evaluador()
        ev.construir_estudiantes()
        ev.evaluar_todos()
        for est in ev.estudiantes:
            assert est.nivel_riesgo in ("Alto", "Medio", "Bajo")
            assert est.recomendacion != ""

    def test_resumen_por_nivel(self):
        ev = self._make_evaluador()
        ev.construir_estudiantes()
        ev.evaluar_todos()
        resumen = ev.resumen_por_nivel()
        assert sum(resumen.values()) == 3

    def test_estudiantes_en_riesgo_alto(self):
        ev = self._make_evaluador()
        ev.construir_estudiantes()
        ev.evaluar_todos()
        alto = ev.estudiantes_en_riesgo("Alto")
        assert all(e.nivel_riesgo == "Alto" for e in alto)

    def test_resumen_por_curso(self):
        ev = self._make_evaluador()
        ev.construir_estudiantes()
        ev.evaluar_todos()
        resumen = ev.resumen_por_curso()
        assert "A" in resumen.index
        assert "B" in resumen.index

    def test_obtener_datos_tabla(self):
        ev = self._make_evaluador()
        ev.construir_estudiantes()
        ev.evaluar_todos()
        datos = ev.obtener_datos_tabla()
        assert len(datos) == 3
        assert "recomendacion" in datos[0]
