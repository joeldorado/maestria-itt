"""Exporta corridas del GA a un libro de Excel (.xlsx) con openpyxl."""

from io import BytesIO

from django.utils import timezone
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

COLOR_ENCABEZADO = "0F766E"
MAX_SERIES_GRAFICA = 12

COLUMNAS_RESULTADOS = [
    ("ID", 7, None),
    ("Fecha", 18, "yyyy-mm-dd hh:mm"),
    ("Función", 16, None),
    ("Dimensiones", 12, None),
    ("Población", 11, None),
    ("Generaciones", 13, None),
    ("Prob. cruza", 11, "0.00"),
    ("Prob. mutación", 14, "0.00"),
    ("Elitismo", 9, None),
    ("Torneo", 8, None),
    ("Hilos", 7, None),
    ("Semilla", 9, None),
    ("Dominio", 14, None),
    ("Valor obtenido", 16, "0.000000"),
    ("Mínimo conocido", 16, "0.000000"),
    ("Error absoluto", 14, "0.00E+00"),
    ("Tiempo (s)", 12, "0.0000"),
    ("Mejor solución", 48, None),
    ("Convergencia", 14, None),
]


def _encabezado(hoja, titulos):
    relleno = PatternFill("solid", fgColor=COLOR_ENCABEZADO)
    for columna, titulo in enumerate(titulos, start=1):
        celda = hoja.cell(row=1, column=columna, value=titulo)
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = relleno
        celda.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    hoja.freeze_panes = "A2"


def _texto_dominio(corrida):
    if corrida.limite_inferior is None:
        return "estándar"
    return f"[{corrida.limite_inferior:g}, {corrida.limite_superior:g}]"


def _fila_resultado(corrida):
    fecha = timezone.localtime(corrida.fecha).replace(tzinfo=None)
    solucion = ", ".join(f"{x:.6f}" for x in corrida.mejor_solucion or [])
    return [
        corrida.id,
        fecha,
        corrida.funcion,
        corrida.dimensiones,
        corrida.poblacion,
        corrida.generaciones,
        corrida.probabilidad_cruza,
        corrida.probabilidad_mutacion,
        corrida.elitismo,
        corrida.torneo,
        corrida.num_hilos,
        corrida.semilla if corrida.semilla is not None else "no registrada",
        _texto_dominio(corrida),
        corrida.valor_obtenido,
        corrida.minimo_conocido,
        abs(corrida.valor_obtenido - corrida.minimo_conocido),
        corrida.tiempo_segundos,
        f"[{solucion}]",
        "sí" if corrida.convergencia else "no registrada",
    ]


def _hoja_resultados(libro, corridas):
    hoja = libro.active
    hoja.title = "Resultados"
    _encabezado(hoja, [c[0] for c in COLUMNAS_RESULTADOS])
    for corrida in corridas:
        hoja.append(_fila_resultado(corrida))

    for indice, (_, ancho, formato) in enumerate(COLUMNAS_RESULTADOS, start=1):
        letra = get_column_letter(indice)
        hoja.column_dimensions[letra].width = ancho
        if formato:
            for fila in range(2, hoja.max_row + 1):
                hoja[f"{letra}{fila}"].number_format = formato
    hoja.auto_filter.ref = hoja.dimensions


def _etiqueta(corrida):
    return (
        f"#{corrida.id} {corrida.funcion} d={corrida.dimensiones} "
        f"p={corrida.poblacion} c={corrida.probabilidad_cruza} "
        f"m={corrida.probabilidad_mutacion}"
        + ("" if corrida.limite_inferior is None else f" dom={_texto_dominio(corrida)}")
    )


def _grafica_convergencia(hoja, num_series, num_generaciones):
    grafica = LineChart()
    grafica.title = "Convergencia del algoritmo genético"
    grafica.x_axis.title = "Generación"
    grafica.y_axis.title = "Mejor valor"
    grafica.height = 10
    grafica.width = 22
    series = min(num_series, MAX_SERIES_GRAFICA)
    datos = Reference(
        hoja, min_col=2, max_col=1 + series, min_row=1, max_row=1 + num_generaciones
    )
    grafica.add_data(datos, titles_from_data=True)
    grafica.set_categories(
        Reference(hoja, min_col=1, min_row=2, max_row=1 + num_generaciones)
    )
    for serie in grafica.series:
        serie.smooth = False
        serie.graphicalProperties.line.width = 20000
    hoja.add_chart(grafica, f"{get_column_letter(num_series + 3)}2")


def _hoja_convergencia(libro, corridas):
    hoja = libro.create_sheet("Convergencia")
    con_curva = [c for c in corridas if c.convergencia]
    sin_curva = [c.id for c in corridas if not c.convergencia]

    if not con_curva:
        hoja["A1"] = "Ninguna de las corridas exportadas tiene la convergencia registrada."
        hoja["A2"] = "Las corridas nuevas la guardan automáticamente."
        return

    _encabezado(hoja, ["Generación"] + [_etiqueta(c) for c in con_curva])
    hoja.row_dimensions[1].height = 45
    generaciones = max(len(c.convergencia) for c in con_curva)
    for g in range(generaciones):
        fila = [g + 1] + [
            c.convergencia[g] if g < len(c.convergencia) else None for c in con_curva
        ]
        hoja.append(fila)

    hoja.column_dimensions["A"].width = 12
    for indice in range(2, len(con_curva) + 2):
        hoja.column_dimensions[get_column_letter(indice)].width = 20

    _grafica_convergencia(hoja, len(con_curva), generaciones)

    notas = []
    if len(con_curva) > MAX_SERIES_GRAFICA:
        notas.append(
            f"La gráfica muestra las primeras {MAX_SERIES_GRAFICA} corridas; "
            "la tabla las incluye todas."
        )
    if sin_curva:
        notas.append(
            "Sin convergencia registrada (corridas anteriores): "
            + ", ".join(f"#{i}" for i in sin_curva)
        )
    fila_nota = 24
    columna_nota = len(con_curva) + 3
    for nota in notas:
        hoja.cell(row=fila_nota, column=columna_nota, value=nota).font = Font(italic=True)
        fila_nota += 1


def generar_excel(corridas):
    """Devuelve los bytes de un .xlsx con las hojas Resultados y Convergencia."""
    corridas = list(corridas)
    libro = Workbook()
    _hoja_resultados(libro, corridas)
    _hoja_convergencia(libro, corridas)
    salida = BytesIO()
    libro.save(salida)
    return salida.getvalue()
