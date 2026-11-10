
import math


# 1. SHUBERT
# Dominio: x1, x2 en [-10, 10]
def shubert(x):
    x1, x2 = x

    suma1 = sum(
        i * math.cos((i + 1) * x1 + i)
        for i in range(1, 6)
    )

    suma2 = sum(
        i * math.cos((i + 1) * x2 + i)
        for i in range(1, 6)
    )

    return suma1 * suma2


# 2. TRID
# Configuracion de 2 dimensiones
# Dominio: x1, x2 en [-4, 4]
def trid(x):
    x1, x2 = x

    return (x1 - 1)**2 + (x2 - 1)**2 - x1 * x2


# 3. ZAKHAROV
# Dominio: x1, x2 en [-5, 10]
def zakharov(x):
    suma_cuadrados = sum(xi**2 for xi in x)

    suma_ponderada = sum(
        0.5 * (i + 1) * xi
        for i, xi in enumerate(x)
    )

    return (
        suma_cuadrados
        + suma_ponderada**2
        + suma_ponderada**4
    )


# 4. BEALE
# Dominio: x1, x2 en [-4.5, 4.5]
def beale(x):
    x1, x2 = x

    termino1 = (1.5 - x1 + x1 * x2)**2
    termino2 = (2.25 - x1 + x1 * x2**2)**2
    termino3 = (2.625 - x1 + x1 * x2**3)**2

    return termino1 + termino2 + termino3


# 5. SIX-HUMP CAMEL
# Dominio: x1 en [-3, 3], x2 en [-2, 2]
def camel6(x):
    x1, x2 = x

    termino1 = (
        4 - 2.1 * x1**2 + x1**4 / 3
    ) * x1**2

    termino2 = x1 * x2

    termino3 = (-4 + 4 * x2**2) * x2**2

    return termino1 + termino2 + termino3


# TRID en d dimensiones
# Dominio: xi en [-d^2, d^2]; minimo -d(d+4)(d-1)/6 en xi = i(d+1-i)
def trid_d(x):
    return (
        sum((xi - 1)**2 for xi in x)
        - sum(x[i] * x[i - 1] for i in range(1, len(x)))
    )


# Configuracion para las pruebas y el algoritmo genetico.
# "escalable" indica si la funcion admite mas de 2 dimensiones.
FUNCIONES = {
    "Shubert": {
        "funcion": shubert,
        "limites": [(-10, 10), (-10, 10)],
        "minimo_conocido": -186.7309,
        "escalable": False,
    },
    "Trid": {
        "funcion": trid,
        "limites": [(-4, 4), (-4, 4)],
        "minimo_conocido": -2.0,
        "escalable": True,
    },
    "Zakharov": {
        "funcion": zakharov,
        "limites": [(-5, 10), (-5, 10)],
        "minimo_conocido": 0.0,
        "escalable": True,
    },
    "Beale": {
        "funcion": beale,
        "limites": [(-4.5, 4.5), (-4.5, 4.5)],
        "minimo_conocido": 0.0,
        "escalable": False,
    },
    "Six-Hump Camel": {
        "funcion": camel6,
        "limites": [(-3, 3), (-2, 2)],
        "minimo_conocido": -1.0316,
        "escalable": False,
    },
}

DIMENSIONES_MIN = 2
DIMENSIONES_MAX = 30


def dimensiones_efectivas(nombre, dimensiones):
    """Las funciones no escalables solo existen en 2 dimensiones."""
    return dimensiones if FUNCIONES[nombre]["escalable"] else 2


def _configuracion_estandar(nombre, d):
    config = FUNCIONES[nombre]
    if d == 2:
        return config["funcion"], config["limites"], config["minimo_conocido"]
    if nombre == "Trid":
        cota = d**2
        return trid_d, [(-cota, cota)] * d, -d * (d + 4) * (d - 1) / 6
    if nombre == "Zakharov":
        return zakharov, [(-5, 10)] * d, 0.0
    raise ValueError(f"{nombre} no admite {d} dimensiones")


def configurar(nombre, dimensiones=2, dominio=None):
    """Devuelve (funcion, limites, minimo_conocido) para la dimension pedida.

    Con dimensiones=2 y sin dominio regresa exactamente la configuracion
    original. `dominio=(inferior, superior)` reemplaza el dominio estandar y se
    aplica igual a todas las variables; el minimo conocido no cambia (es el de
    la funcion), aunque puede quedar fuera del dominio elegido.
    """
    d = dimensiones_efectivas(nombre, dimensiones)
    funcion, limites, minimo = _configuracion_estandar(nombre, d)
    if dominio is not None:
        limites = [tuple(dominio)] * d
    return funcion, limites, minimo


# Puntos donde se alcanza el minimo global, para saber si un dominio lo
# contiene. Shubert repite sus 18 minimos con periodo 2*pi en cada eje:
# una coordenada vale -1.42513 + 2*pi*k y la otra -0.80032 + 2*pi*m.
SHUBERT_BASE = (-1.42513, -0.80032)
CAMEL_OPTIMOS = [(0.0898, -0.7126), (-0.0898, 0.7126)]


def _contiene_periodico(base, inferior, superior):
    """¿Hay algun base + 2*pi*k dentro de [inferior, superior]?"""
    k = math.ceil((inferior - base) / (2 * math.pi))
    return base + 2 * math.pi * k <= superior


def optimo_en_dominio(nombre, dimensiones, dominio):
    """¿Algun minimo global de la funcion cae dentro de [inferior, superior]^d?"""
    inferior, superior = dominio
    dentro = lambda punto: all(inferior <= x <= superior for x in punto)  # noqa: E731
    d = dimensiones_efectivas(nombre, dimensiones)
    if nombre == "Shubert":
        return all(_contiene_periodico(b, inferior, superior) for b in SHUBERT_BASE)
    if nombre == "Trid":
        return dentro([i * (d + 1 - i) for i in range(1, d + 1)])
    if nombre == "Zakharov":
        return dentro([0] * d)
    if nombre == "Beale":
        return dentro([3, 0.5])
    if nombre == "Six-Hump Camel":
        return any(dentro(p) for p in CAMEL_OPTIMOS)
    raise ValueError(f"Funcion desconocida: {nombre}")


# Prueba directa de las cinco funciones
if __name__ == "__main__":
    pruebas = {
        "Shubert": [0, 0],
        "Trid": [2, 2],
        "Zakharov": [0, 0],
        "Beale": [3, 0.5],
        "Six-Hump Camel": [0.0898, -0.7126],
    }

    for nombre, punto in pruebas.items():
        funcion = FUNCIONES[nombre]["funcion"]
        resultado = funcion(punto)

        print(
            f"{nombre:16} "
            f"Entrada: {punto} "
            f"Resultado: {resultado:.6f}"
        )
