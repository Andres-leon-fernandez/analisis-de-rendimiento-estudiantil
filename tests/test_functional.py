import pytest
from src.functional import (
    calcular_promedio_notas,
    calcular_indice_compromiso,
    filtrar_por_condicion,
    aplicar_a_todos,
)


class TestCalcularPromedioNotas:
    def test_pesos_iguales_tres_notas(self):
        resultado = calcular_promedio_notas([14.0, 12.0, 16.0], [0.3333, 0.3333, 0.3334])
        assert round(resultado, 2) == 14.0

    def test_un_solo_examen(self):
        assert calcular_promedio_notas([15.0], [1.0]) == 15.0

    def test_notas_cero(self):
        assert calcular_promedio_notas([0.0, 0.0], [0.5, 0.5]) == 0.0

    def test_notas_maximas(self):
        assert calcular_promedio_notas([20.0, 20.0], [0.5, 0.5]) == 20.0

    def test_pesos_desiguales(self):
        resultado = calcular_promedio_notas([10.0, 18.0], [0.3, 0.7])
        assert round(resultado, 2) == 15.6

    def test_lista_vacia_retorna_cero(self):
        assert calcular_promedio_notas([], []) == 0.0


class TestCalcularIndiceCompromiso:
    def test_compromiso_maximo(self):
        assert calcular_indice_compromiso(100.0, 100.0, 5) == 100.0

    def test_compromiso_medio(self):
        resultado = calcular_indice_compromiso(80.0, 70.0, 3)
        assert 60 < resultado < 80

    def test_compromiso_bajo(self):
        resultado = calcular_indice_compromiso(50.0, 50.0, 1)
        assert pytest.approx(resultado, abs=0.1) == 40.0

    def test_cero_en_todo(self):
        resultado = calcular_indice_compromiso(0.0, 0.0, 0)
        assert resultado == 0.0


class TestAplicarATodos:
    def test_duplicar_valores(self):
        assert aplicar_a_todos(lambda x: x * 2, [1, 2, 3]) == [2, 4, 6]

    def test_lista_vacia(self):
        assert aplicar_a_todos(lambda x: x + 1, []) == []


class TestFiltrarPorCondicion:
    class FakeEst:
        def __init__(self, riesgo):
            self.nivel_riesgo = riesgo

    def test_filtrar_alto(self):
        estudiantes = [self.FakeEst("Alto"), self.FakeEst("Bajo"), self.FakeEst("Alto")]
        resultado = filtrar_por_condicion(estudiantes, lambda e: e.nivel_riesgo == "Alto")
        assert len(resultado) == 2

    def test_filtrar_ninguno(self):
        estudiantes = [self.FakeEst("Alto"), self.FakeEst("Medio")]
        resultado = filtrar_por_condicion(estudiantes, lambda e: e.nivel_riesgo == "Bajo")
        assert len(resultado) == 0

    def test_filtrar_todos(self):
        estudiantes = [self.FakeEst("Bajo"), self.FakeEst("Bajo")]
        resultado = filtrar_por_condicion(estudiantes, lambda e: e.nivel_riesgo == "Bajo")
        assert len(resultado) == 2
