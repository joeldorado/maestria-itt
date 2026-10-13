
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


# Configuracion para las pruebas y el algoritmo genetico
FUNCIONES = {
    "Shubert": {
        "funcion": shubert,
        "limites": [(-10, 10), (-10, 10)],
        "minimo_conocido": -186.7309,
    },
    "Trid": {
        "funcion": trid,
        "limites": [(-4, 4), (-4, 4)],
        "minimo_conocido": -2.0,
    },
    "Zakharov": {
        "funcion": zakharov,
        "limites": [(-5, 10), (-5, 10)],
        "minimo_conocido": 0.0,
    },
    "Beale": {
        "funcion": beale,
        "limites": [(-4.5, 4.5), (-4.5, 4.5)],
        "minimo_conocido": 0.0,
    },
    "Six-Hump Camel": {
        "funcion": camel6,
        "limites": [(-3, 3), (-2, 2)],
        "minimo_conocido": -1.0316,
    },
}


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
