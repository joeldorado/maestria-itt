
import os
import numpy as np
import matplotlib.pyplot as plt

from funciones import FUNCIONES

CARPETA = "graficas"
os.makedirs(CARPETA, exist_ok=True)

# Minimos globales conocidos para las funciones de 2 dimensiones.
MINIMOS = {
    "Shubert": [
        (-7.0835, 4.8580),
    ],
    "Trid": [
        (2.0, 2.0),
    ],
    "Zakharov": [
        (0.0, 0.0),
    ],
    "Beale": [
        (3.0, 0.5),
    ],
    "Six-Hump Camel": [
        (0.0898, -0.7126),
        (-0.0898, 0.7126),
    ],
}

for nombre, config in FUNCIONES.items():
    funcion = config["funcion"]
    limites = config["limites"]

    # Crear la malla del dominio de busqueda.
    x1 = np.linspace(limites[0][0], limites[0][1], 150)
    x2 = np.linspace(limites[1][0], limites[1][1], 150)
    X1, X2 = np.meshgrid(x1, x2)

    # Evaluar la funcion en cada punto de la malla.
    Z = np.zeros_like(X1)

    for i in range(X1.shape[0]):
        for j in range(X1.shape[1]):
            Z[i, j] = funcion([X1[i, j], X2[i, j]])

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")

    superficie = ax.plot_surface(
        X1,
        X2,
        Z,
        cmap="viridis",
        linewidth=0,
        antialiased=True,
    )

    # Marcar los minimos globales conocidos.
    puntos_z = []

    for px, py in MINIMOS[nombre]:
        pz = funcion([px, py])
        puntos_z.append(pz)

        ax.scatter(
            px,
            py,
            pz,
            color="red",
            edgecolor="black",
            s=75,
            depthshade=False,
        )

    # Ajustar la escala vertical para mejorar la lectura.
    if nombre == "Shubert":
        ax.set_zlim(min(puntos_z) - 10, np.percentile(Z, 98))
    elif nombre == "Beale":
        ax.set_zlim(min(puntos_z) - 1, np.percentile(Z, 90))

    ax.set_title(f"Funcion {nombre} y sus minimos globales")
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    ax.set_zlabel("f(x1, x2)")

    fig.colorbar(superficie, ax=ax, shrink=0.65, pad=0.12)
    fig.tight_layout()

    nombre_archivo = nombre.lower().replace(" ", "_")
    ruta = os.path.join(CARPETA, f"{nombre_archivo}_minimo.png")

    fig.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"Grafica guardada: {ruta}")

print("\nSe generaron las cinco graficas.")
