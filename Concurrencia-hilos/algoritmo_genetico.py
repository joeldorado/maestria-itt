
import random
import time
from concurrent.futures import ThreadPoolExecutor

from funciones import FUNCIONES


# Parametros del algoritmo genetico
POBLACION = 100
GENERACIONES = 200
PROBABILIDAD_CRUZA = 0.85
PROBABILIDAD_MUTACION = 0.10
ELITISMO = 2
TORNEO = 3
NUM_HILOS = 4
SEMILLA = 42


def crear_individuo(limites):
    """Genera una solucion aleatoria dentro del dominio."""
    return [
        random.uniform(minimo, maximo)
        for minimo, maximo in limites
    ]


def evaluar_individuo(argumentos):
    """Evalua un individuo con la funcion seleccionada."""
    funcion, individuo = argumentos
    return funcion(individuo)


def seleccionar_torneo(poblacion, resultados):
    """Selecciona un individuo mediante torneo."""
    indices = random.sample(
        range(len(poblacion)),
        TORNEO
    )

    mejor_indice = min(
        indices,
        key=lambda i: resultados[i]
    )

    return poblacion[mejor_indice][:]


def cruzar(padre1, padre2):
    """Cruza aritmetica para generar dos hijos."""
    if random.random() > PROBABILIDAD_CRUZA:
        return padre1[:], padre2[:]

    hijo1 = []
    hijo2 = []

    for a, b in zip(padre1, padre2):
        alpha = random.random()

        hijo1.append(alpha * a + (1 - alpha) * b)
        hijo2.append(alpha * b + (1 - alpha) * a)

    return hijo1, hijo2


def mutar(individuo, limites):
    """Aplica mutacion gaussiana respetando los limites."""
    for i, (minimo, maximo) in enumerate(limites):
        if random.random() < PROBABILIDAD_MUTACION:
            desviacion = (maximo - minimo) * 0.10

            individuo[i] += random.gauss(0, desviacion)

            individuo[i] = max(
                minimo,
                min(maximo, individuo[i])
            )

    return individuo


def ejecutar_algoritmo(nombre, usar_hilos=True):
    configuracion = FUNCIONES[nombre]
    funcion = configuracion["funcion"]
    limites = configuracion["limites"]

    # Cada ejecucion empieza con la misma semilla.
    random.seed(SEMILLA)

    poblacion = [
        crear_individuo(limites)
        for _ in range(POBLACION)
    ]

    inicio = time.perf_counter()

    # El executor distribuye las evaluaciones entre los hilos.
    with ThreadPoolExecutor(
        max_workers=NUM_HILOS if usar_hilos else 1
    ) as executor:

        for generacion in range(GENERACIONES):
            resultados = list(
                executor.map(
                    evaluar_individuo,
                    [(funcion, individuo) for individuo in poblacion]
                )
            )

            # Ordenar de menor a mayor: buscamos minimizar.
            orden = sorted(
                range(len(poblacion)),
                key=lambda i: resultados[i]
            )

            mejor_indice = orden[0]
            mejor_valor = resultados[mejor_indice]
            mejor_individuo = poblacion[mejor_indice][:]

            nueva_poblacion = [
                poblacion[i][:]
                for i in orden[:ELITISMO]
            ]

            while len(nueva_poblacion) < POBLACION:
                padre1 = seleccionar_torneo(
                    poblacion, resultados
                )
                padre2 = seleccionar_torneo(
                    poblacion, resultados
                )

                hijo1, hijo2 = cruzar(padre1, padre2)

                nueva_poblacion.append(
                    mutar(hijo1, limites)
                )

                if len(nueva_poblacion) < POBLACION:
                    nueva_poblacion.append(
                        mutar(hijo2, limites)
                    )

            poblacion = nueva_poblacion

        # Evaluar la poblacion final para obtener el resultado final.
        resultados = list(
            executor.map(
                evaluar_individuo,
                [(funcion, individuo) for individuo in poblacion]
            )
        )

        mejor_indice = min(
            range(len(poblacion)),
            key=lambda i: resultados[i]
        )

        mejor_individuo = poblacion[mejor_indice][:]
        mejor_valor = resultados[mejor_indice]

    tiempo = time.perf_counter() - inicio

    return mejor_individuo, mejor_valor, tiempo


if __name__ == "__main__":
    print("ALGORITMO GENETICO: CINCO FUNCIONES")
    print("=" * 76)
    print(
        f"Poblacion: {POBLACION} | "
        f"Generaciones: {GENERACIONES} | "
        f"Cruza: {PROBABILIDAD_CRUZA} | "
        f"Mutacion: {PROBABILIDAD_MUTACION} | "
        f"Hilos: {NUM_HILOS}"
    )
    print("=" * 76)

    for nombre, configuracion in FUNCIONES.items():
        mejor, valor, tiempo = ejecutar_algoritmo(
            nombre,
            usar_hilos=True
        )

        conocido = configuracion["minimo_conocido"]

        print(f"\nFuncion: {nombre}")
        print(f"Mejor solucion encontrada: {mejor}")
        print(f"Valor obtenido: {valor:.6f}")
        print(f"Minimo global conocido: {conocido:.6f}")
        print(f"Tiempo: {tiempo:.4f} segundos")
