"""Estudio de variantes: muchas corridas por configuración y su resumen.

Cada variante cambia un solo parámetro respecto a una base; se corre con las
semillas 1..N y se resume el error |f(x) - f*| contra el óptimo conocido.
No escribe en la base de datos.
"""

import statistics
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field

from core.services.algoritmo_genetico import ejecutar_algoritmo
from core.services.funciones import configurar, optimo_en_dominio

UMBRAL_EXITO = 1e-2  # error con el que una corrida "llega al óptimo"


@dataclass(frozen=True)
class Variante:
    bloque: str
    etiqueta: str
    funcion: str
    parametros: dict = field(hash=False)


def _variantes(bloque, funcion, base, campo, valores, etiqueta):
    return [
        Variante(bloque, etiqueta(v), funcion, {**base, campo: v})
        for v in valores
    ]


def _dom(r):
    return "estándar" if r is None else f"[{r[0]:g}, {r[1]:g}]"


BLOQUES = {
    "dominio_zakharov": (
        "Dominio · Zakharov d=10",
        lambda: _variantes(
            "dominio_zakharov", "Zakharov", {"dimensiones": 10}, "dominio",
            [(-1, 1), None, (-50, 100), (-500, 1000), (1, 10)], _dom,
        ),
    ),
    "dominio_trid": (
        "Dominio · Trid d=5",
        lambda: _variantes(
            "dominio_trid", "Trid", {"dimensiones": 5}, "dominio",
            [(-10, 10), None, (-250, 250)], _dom,
        ),
    ),
    "dimensiones": (
        "Dimensiones · Trid y Zakharov",
        lambda: [
            Variante("dimensiones", f"{f} d={d}", f, {"dimensiones": d})
            for f in ("Trid", "Zakharov") for d in (2, 5, 10, 20)
        ],
    ),
    "mutacion": (
        "Mutación · Trid d=5, población 60",
        lambda: _variantes(
            "mutacion", "Trid", {"dimensiones": 5, "poblacion_tam": 60},
            "probabilidad_mutacion", [0.01, 0.05, 0.10, 0.30, 0.50],
            lambda v: f"mutación {v:.2f}",
        ),
    ),
    "generaciones": (
        "Generaciones · Trid d=10",
        lambda: _variantes(
            "generaciones", "Trid", {"dimensiones": 10}, "generaciones",
            [100, 200, 500, 1000], lambda v: f"{v} generaciones",
        ),
    ),
    "poblacion": (
        "Población · Trid d=10",
        lambda: _variantes(
            "poblacion", "Trid", {"dimensiones": 10}, "poblacion_tam",
            [30, 100, 300], lambda v: f"población {v}",
        ),
    ),
    "cruza": (
        "Cruza · Zakharov d=10",
        lambda: _variantes(
            "cruza", "Zakharov", {"dimensiones": 10}, "probabilidad_cruza",
            [0.5, 0.85, 1.0], lambda v: f"cruza {v:.2f}",
        ),
    ),
}


def variantes(bloques=None):
    nombres = bloques or list(BLOQUES)
    desconocidos = [b for b in nombres if b not in BLOQUES]
    if desconocidos:
        raise ValueError(f"Bloques desconocidos: {desconocidos}")
    return [v for b in nombres for v in BLOQUES[b][1]()]


def _primera_generacion_exitosa(curva, minimo):
    for i, valor in enumerate(curva, start=1):
        if abs(valor - minimo) < UMBRAL_EXITO:
            return i
    return None


def correr_una(tarea):
    """Una corrida (se ejecuta en un proceso aparte)."""
    variante, semilla = tarea
    p = variante.parametros
    _, _, minimo = configurar(variante.funcion, p.get("dimensiones", 2), p.get("dominio"))
    mejor, valor, tiempo, curva = ejecutar_algoritmo(variante.funcion, semilla=semilla, **p)
    return {
        "bloque": variante.bloque,
        "variante": variante.etiqueta,
        "funcion": variante.funcion,
        "semilla": semilla,
        "valor": valor,
        "minimo": minimo,
        "error": abs(valor - minimo),
        "tiempo": tiempo,
        "generacion_exito": _primera_generacion_exitosa(curva, minimo),
        "mejor": mejor,
        "curva": curva,
    }


def ejecutar_estudio(lista, corridas, procesos, al_avanzar=None):
    tareas = [(v, s) for v in lista for s in range(1, corridas + 1)]
    resultados = []
    with ProcessPoolExecutor(max_workers=procesos) as pool:
        for i, r in enumerate(pool.map(correr_una, tareas, chunksize=4), start=1):
            resultados.append(r)
            if al_avanzar:
                al_avanzar(i, len(tareas))
    return resultados


def _percentil(ordenados, q):
    k = (len(ordenados) - 1) * q
    abajo, arriba = int(k), min(int(k) + 1, len(ordenados) - 1)
    return ordenados[abajo] + (ordenados[arriba] - ordenados[abajo]) * (k - abajo)


def resumir(lista, resultados):
    """Una fila por variante, en el orden de `lista`."""
    por_variante = {}
    for r in resultados:
        por_variante.setdefault((r["bloque"], r["variante"]), []).append(r)
    filas = []
    for v in lista:
        grupo = por_variante.get((v.bloque, v.etiqueta), [])
        if not grupo:
            continue
        errores = sorted(r["error"] for r in grupo)
        exitos = [r["generacion_exito"] for r in grupo if r["generacion_exito"]]
        p = v.parametros
        dominio = p.get("dominio")
        filas.append({
            "bloque": v.bloque,
            "bloque_titulo": BLOQUES[v.bloque][0],
            "variante": v.etiqueta,
            "funcion": v.funcion,
            "d": p.get("dimensiones", 2),
            "poblacion": p.get("poblacion_tam", 100),
            "generaciones": p.get("generaciones", 200),
            "cruza": p.get("probabilidad_cruza", 0.85),
            "mutacion": p.get("probabilidad_mutacion", 0.10),
            "dominio": _dom(dominio),
            "optimo_dentro": True if dominio is None else optimo_en_dominio(v.funcion, p.get("dimensiones", 2), dominio),
            "n": len(grupo),
            "exito_pct": 100 * sum(e < UMBRAL_EXITO for e in errores) / len(errores),
            "media": statistics.fmean(errores),
            "mediana": statistics.median(errores),
            "desv": statistics.pstdev(errores),
            "p25": _percentil(errores, 0.25),
            "p75": _percentil(errores, 0.75),
            "minimo_err": errores[0],
            "maximo_err": errores[-1],
            "gen_exito_mediana": statistics.median(exitos) if exitos else None,
            "tiempo_medio": statistics.fmean(r["tiempo"] for r in grupo),
        })
    return filas


def curva_mediana(resultados, bloque, variante):
    """Mediana del error por generación entre todas las semillas de la variante."""
    curvas = [
        [abs(x - r["minimo"]) for x in r["curva"]]
        for r in resultados if r["bloque"] == bloque and r["variante"] == variante
    ]
    if not curvas:
        return []
    return [statistics.median(col) for col in zip(*curvas)]
