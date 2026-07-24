% =================================================================
%  REGLAS DE CLASIFICACION DE RIESGO ACADEMICO
%  Motor de inferencia en Prolog para el sistema de evaluacion
%  de rendimiento estudiantil.
%
%  Curso: Lenguajes de Programacion (100000SI68)
%  UMRALES CONFIGURABLES: Se cargan desde Python via hechos dinamicos
% =================================================================

% --- Hechos dinamicos (se cargan desde Python via pyswip) ---
:- dynamic estudiante_promedio/2.
:- dynamic estudiante_asistencia/2.
:- dynamic estudiante_compromiso/2.

% --- Hechos dinamicos para umbrales de riesgo ---
:- dynamic umbral_promedio_alto/1.
:- dynamic umbral_promedio_medio/1.
:- dynamic umbral_asistencia_alto/1.
:- dynamic umbral_asistencia_medio/1.
:- dynamic umbral_compromiso_alto/1.
:- dynamic umbral_compromiso_medio/1.

% --- Regla: Riesgo Alto ---
riesgo_alto(ID) :-
    estudiante_promedio(ID, P),
    umbral_promedio_alto(UmbralP),
    P < UmbralP,
    estudiante_asistencia(ID, A),
    umbral_asistencia_alto(UmbralA),
    A < UmbralA.

riesgo_alto(ID) :-
    estudiante_promedio(ID, P),
    umbral_promedio_alto(UmbralP),
    P < UmbralP,
    estudiante_compromiso(ID, C),
    umbral_compromiso_alto(UmbralC),
    C < UmbralC.

% --- Regla: Riesgo Medio ---
riesgo_medio(ID) :-
    estudiante_promedio(ID, P),
    umbral_promedio_medio(UmbralP),
    P < UmbralP,
    estudiante_asistencia(ID, A),
    umbral_asistencia_medio(UmbralA),
    A < UmbralA.

riesgo_medio(ID) :-
    estudiante_compromiso(ID, C),
    umbral_compromiso_medio(UmbralC),
    C < UmbralC.

% --- Regla: Riesgo Bajo ---
riesgo_bajo(ID) :-
    estudiante_promedio(ID, P),
    umbral_promedio_medio(UmbralP),
    P >= UmbralP,
    estudiante_asistencia(ID, A),
    umbral_asistencia_medio(UmbralA),
    A >= UmbralA,
    estudiante_compromiso(ID, C),
    umbral_compromiso_medio(UmbralC),
    C >= UmbralC.
