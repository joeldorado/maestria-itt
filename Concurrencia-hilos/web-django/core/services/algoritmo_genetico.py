
import random
import time
from concurrent.futures import ThreadPoolExecutor

from core.services.funciones import FUNCIONES, configurar


# Parámetros predeterminados del algoritmo genético
DIMENSIONES = 2
POBLACION = 100
GENERACIONES = 200
PROBABILIDAD_CRUZA = 0.85
PROBABILIDAD_MUTACION = 0.10
ELITISMO = 2
TORNEO = 3
NUM_HILOS = 4
SEMILLA = 42


def crear_individuo(limites):
    """Crea un individuo aleatorio respetando los límites."""
    return [
        random.uniform(minimo, maximo)
        for minimo, maximo in limites
    ]


def evaluar_individuo(argumentos):
    """Evalúa un individuo con la función seleccionada."""
    funcion, individuo = argumentos
    return funcion(individuo)


def seleccionar_torneo(poblacion, resultados, torneo=3):
    """Selecciona un individuo mediante torneo."""
    indices = random.sample(
        range(len(poblacion)),
        torneo
    )

    mejor_indice = min(
        indices,
        key=lambda i: resultados[i]
    )

    return poblacion[mejor_indice][:]


def cruzar(padre1, padre2, probabilidad_cruza=0.85):
    """Cruza aritmética para generar dos hijos."""
    if random.random() > probabilidad_cruza:
        return padre1[:], padre2[:]

    hijo1 = []
    hijo2 = []

    for a, b in zip(padre1, padre2):
        alpha = random.random()

        hijo1.append(alpha * a + (1 - alpha) * b)
        hijo2.append(alpha * b + (1 - alpha) * a)

    return hijo1, hijo2


def mutar(individuo, limites, probabilidad_mutacion=0.10):
    """Aplica mutación gaussiana respetando los límites."""
    for i, (minimo, maximo) in enumerate(limites):
        if random.random() < probabilidad_mutacion:
            desviacion = (maximo - minimo) * 0.10

            individuo[i] += random.gauss(0, desviacion)

            individuo[i] = max(
                minimo,
                min(maximo, individuo[i])
            )

    return individuo


def ejecutar_algoritmo(
    nombre,
    usar_hilos=True,
    poblacion_tam=POBLACION,
    generaciones=GENERACIONES,
    probabilidad_cruza=PROBABILIDAD_CRUZA,
    probabilidad_mutacion=PROBABILIDAD_MUTACION,
    elitismo=ELITISMO,
    torneo=TORNEO,
    num_hilos=NUM_HILOS,
    semilla=SEMILLA,
    dimensiones=DIMENSIONES,
    dominio=None,
):
    """
    Ejecuta el algoritmo genético y registra la convergencia.

    Retorna:
        mejor_individuo: mejor solución encontrada.
        mejor_valor: valor de la función objetivo.
        tiempo: duración de la ejecución en segundos.
        historial_convergencia: mejor valor de cada generación.
    """
    # dominio=None usa el dominio estandar de la funcion.
    funcion, limites, _ = configurar(nombre, dimensiones, dominio)

    # Reiniciar la semilla para permitir experimentos reproducibles.
    random.seed(semilla)

    poblacion = [
        crear_individuo(limites)
        for _ in range(poblacion_tam)
    ]

    historial_convergencia = []

    # Medir únicamente el tiempo del algoritmo.
    inicio = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=num_hilos if usar_hilos else 1
    ) as executor:

        for generacion in range(generaciones):

            resultados = list(
                executor.map(
                    evaluar_individuo,
                    [
                        (funcion, individuo)
                        for individuo in poblacion
                    ]
                )
            )

            # Registrar el mejor valor de la generación actual.
            mejor_valor_generacion = min(resultados)
            historial_convergencia.append(
                mejor_valor_generacion
            )

            # Ordenar de menor a mayor: buscamos minimizar.
            orden = sorted(
                range(len(poblacion)),
                key=lambda i: resultados[i]
            )

            # Conservar los mejores individuos.
            nueva_poblacion = [
                poblacion[i][:]
                for i in orden[:elitismo]
            ]

            # Generar el resto de la población.
            while len(nueva_poblacion) < poblacion_tam:

                padre1 = seleccionar_torneo(
                    poblacion,
                    resultados,
                    torneo
                )

                padre2 = seleccionar_torneo(
                    poblacion,
                    resultados,
                    torneo
                )

                hijo1, hijo2 = cruzar(
                    padre1,
                    padre2,
                    probabilidad_cruza
                )

                nueva_poblacion.append(
                    mutar(
                        hijo1,
                        limites,
                        probabilidad_mutacion
                    )
                )

                if len(nueva_poblacion) < poblacion_tam:
                    nueva_poblacion.append(
                        mutar(
                            hijo2,
                            limites,
                            probabilidad_mutacion
                        )
                    )

            poblacion = nueva_poblacion

        # Evaluar la población final.
        resultados = list(
            executor.map(
                evaluar_individuo,
                [
                    (funcion, individuo)
                    for individuo in poblacion
                ]
            )
        )

        mejor_indice = min(
            range(len(poblacion)),
            key=lambda i: resultados[i]
        )

        mejor_individuo = poblacion[mejor_indice][:]
        mejor_valor = resultados[mejor_indice]

    # Finalizar la medición del tiempo.
    tiempo = time.perf_counter() - inicio

    return (
        mejor_individuo,
        mejor_valor,
        tiempo,
        historial_convergencia,
    )


if __name__ == "__main__":
    print("ALGORITMO GENÉTICO: CINCO FUNCIONES")
    print("=" * 76)

    print(
        f"Población: {POBLACION} | "
        f"Generaciones: {GENERACIONES} | "
        f"Cruza: {PROBABILIDAD_CRUZA} | "
        f"Mutación: {PROBABILIDAD_MUTACION} | "
        f"Hilos: {NUM_HILOS}"
    )

    print("=" * 76)

    for nombre, configuracion in FUNCIONES.items():

        mejor, valor, tiempo, historial = ejecutar_algoritmo(
            nombre,
            usar_hilos=True
        )

        conocido = configuracion["minimo_conocido"]

        print(f"\nFunción: {nombre}")
        print(f"Mejor solución encontrada: {mejor}")
        print(f"Valor obtenido: {valor:.6f}")
        print(f"Mínimo global conocido: {conocido:.6f}")
        print(f"Tiempo: {tiempo:.4f} segundos")
        print(f"Generaciones registradas: {len(historial)}")
