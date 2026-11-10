
import os

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


def generar_grafica_convergencia(
    historial,
    corrida_id,
    media_root
):
    carpeta = os.path.join(
        media_root,
        "corridas",
        str(corrida_id)
    )

    os.makedirs(carpeta, exist_ok=True)

    ruta = os.path.join(
        carpeta,
        "convergencia.png"
    )

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        range(1, len(historial) + 1),
        historial,
        linewidth=2,
        color="#0f766e",
        label="Mejor valor"
    )

    ax.set_title("Convergencia del algoritmo genético")
    ax.set_xlabel("Generación")
    ax.set_ylabel("Mejor valor de la función")
    ax.grid(True, alpha=0.3)
    ax.legend()

    fig.tight_layout()
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return ruta
