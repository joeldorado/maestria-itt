from core.services.algoritmo_genetico import ejecutar_algoritmo
from core.services.funciones import FUNCIONES


def comparar_funcion(nombre, **parametros):
    """Corre la misma configuracion en secuencial (1 hilo) y paralelo."""
    num_hilos = parametros.pop("num_hilos", 4)

    mejor_seq, valor_seq, tiempo_seq, _ = ejecutar_algoritmo(
        nombre, usar_hilos=False, **parametros
    )
    mejor_par, valor_par, tiempo_par, _ = ejecutar_algoritmo(
        nombre, usar_hilos=True, num_hilos=num_hilos, **parametros
    )

    aceleracion = tiempo_seq / tiempo_par if tiempo_par > 0 else 0.0

    return {
        "funcion": nombre,
        "tiempo_secuencial": tiempo_seq,
        "tiempo_paralelo": tiempo_par,
        "aceleracion": aceleracion,
        "valor_secuencial": valor_seq,
        "valor_paralelo": valor_par,
        "mejor_secuencial": mejor_seq,
        "mejor_paralelo": mejor_par,
    }


if __name__ == "__main__":
    print("COMPARACION: SECUENCIAL VS PARALELO")
    print("=" * 85)
    for nombre in FUNCIONES:
        r = comparar_funcion(nombre)
        print(f"\nFuncion: {nombre}")
        print(f"Secuencial: {r['tiempo_secuencial']:.6f} segundos")
        print(f"Paralelo:   {r['tiempo_paralelo']:.6f} segundos")
        print(f"Aceleracion: {r['aceleracion']:.3f}x")
    print("\n" + "=" * 85)
