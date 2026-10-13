
from algoritmo_genetico import ejecutar_algoritmo, FUNCIONES

print("COMPARACION: SECUENCIAL VS PARALELO")
print("=" * 85)

for nombre in FUNCIONES:
    # Ejecucion secuencial: un solo hilo
    mejor_seq, valor_seq, tiempo_seq = ejecutar_algoritmo(
        nombre,
        usar_hilos=False
    )

    # Ejecucion paralela: cuatro hilos
    mejor_par, valor_par, tiempo_par = ejecutar_algoritmo(
        nombre,
        usar_hilos=True
    )

    # Calcular aceleracion
    if tiempo_par > 0:
        aceleracion = tiempo_seq / tiempo_par
    else:
        aceleracion = 0

    print(f"\nFuncion: {nombre}")
    print(f"Secuencial: {tiempo_seq:.6f} segundos")
    print(f"Paralelo:   {tiempo_par:.6f} segundos")
    print(f"Aceleracion: {aceleracion:.3f}x")
    print(f"Mejor valor secuencial: {valor_seq:.6f}")
    print(f"Mejor valor paralelo:   {valor_par:.6f}")

    if aceleracion > 1:
        print("Resultado: la ejecucion paralela fue mas rapida.")
    elif aceleracion < 1:
        print("Resultado: la ejecucion secuencial fue mas rapida.")
    else:
        print("Resultado: ambos tiempos fueron iguales.")

print("\n" + "=" * 85)
print("Comparacion terminada.")
