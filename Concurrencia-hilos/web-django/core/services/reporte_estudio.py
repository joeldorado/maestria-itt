"""Escribe el resultado del estudio de variantes: Excel + reporte Markdown."""

from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.chart.axis import ChartLines
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from core.services.estudio import BLOQUES, UMBRAL_EXITO, curva_mediana

VERDE = "0F766E"
MEJOR = "D1FAE5"
FUERA = "FEF3C7"

COLUMNAS_RESUMEN = [
    ("Bloque", "bloque_titulo", 30, None),
    ("Variante", "variante", 20, None),
    ("Función", "funcion", 11, None),
    ("d", "d", 5, None),
    ("Población", "poblacion", 10, None),
    ("Generaciones", "generaciones", 12, None),
    ("Cruza", "cruza", 7, "0.00"),
    ("Mutación", "mutacion", 9, "0.00"),
    ("Dominio", "dominio", 14, None),
    ("Óptimo dentro", "optimo_dentro", 9, None),
    ("Corridas", "n", 9, None),
    ("% éxito (error < 0.01)", "exito_pct", 11, "0"),
    ("Error medio", "media", 13, "0.000E+00"),
    ("Error mediana", "mediana", 13, "0.000E+00"),
    ("Desv. estándar", "desv", 13, "0.000E+00"),
    ("P25", "p25", 12, "0.000E+00"),
    ("P75", "p75", 12, "0.000E+00"),
    ("Mejor error", "minimo_err", 12, "0.000E+00"),
    ("Peor error", "maximo_err", 12, "0.000E+00"),
    ("Gen. de éxito (mediana)", "gen_exito_mediana", 11, "0"),
    ("Tiempo medio (s)", "tiempo_medio", 11, "0.000"),
]


def _encabezado(hoja, titulos):
    for col, titulo in enumerate(titulos, start=1):
        celda = hoja.cell(row=1, column=col, value=titulo)
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor=VERDE)
        celda.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    hoja.row_dimensions[1].height = 42
    hoja.freeze_panes = "C2"


def _mejores_por_bloque(filas):
    mejores = {}
    for f in filas:
        if f["bloque"] not in mejores or f["mediana"] < mejores[f["bloque"]]["mediana"]:
            mejores[f["bloque"]] = f
    return {id(f) for f in mejores.values()}


def _hoja_resumen(libro, filas):
    hoja = libro.active
    hoja.title = "Resumen"
    _encabezado(hoja, [c[0] for c in COLUMNAS_RESUMEN])
    mejores = _mejores_por_bloque(filas)
    for f in filas:
        hoja.append([
            ("sí" if f[clave] else "no") if clave == "optimo_dentro" else f[clave]
            for _, clave, _, _ in COLUMNAS_RESUMEN
        ])
        fila = hoja.max_row
        relleno = MEJOR if id(f) in mejores else (FUERA if not f["optimo_dentro"] else None)
        if relleno:
            for col in range(1, len(COLUMNAS_RESUMEN) + 1):
                hoja.cell(row=fila, column=col).fill = PatternFill("solid", fgColor=relleno)
    for i, (_, _, ancho, formato) in enumerate(COLUMNAS_RESUMEN, start=1):
        hoja.column_dimensions[get_column_letter(i)].width = ancho
        if formato:
            for (celda,) in hoja.iter_rows(min_row=2, min_col=i, max_col=i):
                celda.number_format = formato
    hoja.auto_filter.ref = hoja.dimensions
    nota = hoja.max_row + 2
    hoja.cell(row=nota, column=1, value="Verde: mejor mediana del bloque. Amarillo: el óptimo queda fuera del dominio.")
    hoja.cell(row=nota + 1, column=1, value=f"Éxito = error < {UMBRAL_EXITO}. Semillas 1..N; una sola variable cambia por bloque.")


def _hoja_corridas(libro, resultados):
    hoja = libro.create_sheet("Corridas")
    titulos = ["Bloque", "Variante", "Función", "Semilla", "Valor", "Mínimo", "Error", "Gen. de éxito", "Tiempo (s)", "Mejor solución"]
    _encabezado(hoja, titulos)
    for r in resultados:
        hoja.append([
            BLOQUES[r["bloque"]][0], r["variante"], r["funcion"], r["semilla"], r["valor"],
            r["minimo"], r["error"], r["generacion_exito"], r["tiempo"],
            "[" + ", ".join(f"{x:.5f}" for x in r["mejor"]) + "]",
        ])
    for i, ancho in enumerate([30, 20, 11, 8, 14, 12, 12, 10, 10, 60], start=1):
        hoja.column_dimensions[get_column_letter(i)].width = ancho
    for (celda,) in hoja.iter_rows(min_row=2, min_col=7, max_col=7):
        celda.number_format = "0.000E+00"
    hoja.auto_filter.ref = hoja.dimensions


def _hoja_curvas(libro, filas, resultados):
    """Curva mediana del error por bloque, con una gráfica log por bloque."""
    hoja = libro.create_sheet("Curvas medianas")
    graficas = libro.create_sheet("Gráficas")  # una gráfica por bloque, una debajo de otra
    columna = 1
    fila_grafica = 1
    for bloque in dict.fromkeys(f["bloque"] for f in filas):
        del_bloque = [f for f in filas if f["bloque"] == bloque]
        curvas = [curva_mediana(resultados, bloque, f["variante"]) for f in del_bloque]
        largo = max(len(c) for c in curvas)
        hoja.cell(row=1, column=columna, value=f"{BLOQUES[bloque][0]} · generación").font = Font(bold=True)
        for g in range(largo):
            hoja.cell(row=g + 2, column=columna, value=g + 1)
        for k, (f, curva) in enumerate(zip(del_bloque, curvas), start=1):
            hoja.cell(row=1, column=columna + k, value=f["variante"]).font = Font(bold=True)
            for g, valor in enumerate(curva):
                hoja.cell(row=g + 2, column=columna + k, value=max(valor, 1e-12))
        grafica = LineChart()
        grafica.title = f"{BLOQUES[bloque][0]} · mediana del error"
        grafica.y_axis.title = "Error (log)"
        grafica.x_axis.title = "Generación"
        grafica.y_axis.scaling.logBase = 10
        grafica.y_axis.majorGridlines = ChartLines()
        grafica.height, grafica.width = 9, 18
        datos = Reference(hoja, min_col=columna + 1, max_col=columna + len(del_bloque), min_row=1, max_row=largo + 1)
        grafica.add_data(datos, titles_from_data=True)
        grafica.set_categories(Reference(hoja, min_col=columna, min_row=2, max_row=largo + 1))
        for serie in grafica.series:
            serie.smooth = False
            serie.graphicalProperties.line.width = 20000
        graficas.add_chart(grafica, f"A{fila_grafica}")
        fila_grafica += 20
        columna += len(del_bloque) + 2


def _hoja_conclusiones(libro, conclusiones):
    hoja = libro.create_sheet("Conclusiones", 0)
    hoja.column_dimensions["A"].width = 140
    hoja["A1"] = "Conclusiones del estudio de variantes"
    hoja["A1"].font = Font(bold=True, size=14)
    for i, linea in enumerate(l for l in conclusiones.splitlines() if l.strip()):
        celda = hoja.cell(row=i + 3, column=1, value=linea.replace("**", ""))
        celda.alignment = Alignment(wrap_text=True, vertical="top")


def generar_excel(filas, resultados, ruta, conclusiones=""):
    libro = Workbook()
    _hoja_resumen(libro, filas)
    if conclusiones:
        _hoja_conclusiones(libro, conclusiones)
    _hoja_corridas(libro, resultados)
    _hoja_curvas(libro, filas, resultados)
    libro.save(ruta)


def _num(v):
    if v is None:
        return "—"
    if v == 0:
        return "0"
    if abs(v) < 1e-3 or abs(v) >= 1e5:
        return f"{v:.2e}"
    return f"{v:.4g}" if abs(v) < 1 else f"{v:,.2f}"


def generar_markdown(filas, corridas, ruta, conclusiones=""):
    lineas = [
        "# Estudio de variantes del GA",
        "",
        f"Cada variante se corrió **{corridas} veces** (semillas 1 a {corridas}); en cada bloque cambia un solo parámetro "
        "y el resto queda en los valores de referencia: población 100, 200 generaciones, cruza 0.85, mutación 0.10, "
        f"elitismo 2, torneo 3, 4 hilos y dominio estándar. **Éxito** = error |f(x) − f*| < {UMBRAL_EXITO}. "
        "Los tiempos se midieron con varias corridas en paralelo (procesos), así que sirven para comparar entre sí, "
        "no como tiempo absoluto.",
        "",
    ]
    if conclusiones:
        lineas += ["## Conclusiones", "", conclusiones.strip(), ""]
    mejores = _mejores_por_bloque(filas)
    for bloque in dict.fromkeys(f["bloque"] for f in filas):
        del_bloque = [f for f in filas if f["bloque"] == bloque]
        lineas += [
            f"## {BLOQUES[bloque][0]}",
            "",
            "| Variante | % éxito | Mediana | Media | Desv. est. | P25 – P75 | Mejor | Peor | Gen. éxito | Tiempo (s) |",
            "|---|---:|---:|---:|---:|---|---:|---:|---:|---:|",
        ]
        for f in del_bloque:
            nombre = f["variante"] + (" **← mejor**" if id(f) in mejores else "") + ("" if f["optimo_dentro"] else " ⚠️ óptimo fuera")
            lineas.append(
                f"| {nombre} | {f['exito_pct']:.0f} % | {_num(f['mediana'])} | {_num(f['media'])} | {_num(f['desv'])} | "
                f"{_num(f['p25'])} – {_num(f['p75'])} | {_num(f['minimo_err'])} | {_num(f['maximo_err'])} | "
                f"{'—' if f['gen_exito_mediana'] is None else int(f['gen_exito_mediana'])} | {f['tiempo_medio']:.3f} |"
            )
        lineas.append("")
    lineas += [
        "## Cómo repetirlo",
        "",
        "```bash",
        "cd web-django",
        "python manage.py estudiar_variantes --corridas 100 --salida ../../estudio_variantes",
        "python manage.py estudiar_variantes --bloques dominio_zakharov mutacion --corridas 30",
        "```",
        "",
        f"Bloques disponibles: {', '.join(f'`{b}`' for b in BLOQUES)}. No escribe en la base de datos.",
        "",
    ]
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(lineas))
