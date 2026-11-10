import json
import os
import platform
import shutil
import threading
import time

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from core.models import Comparacion, Corrida
from core.services.algoritmo_genetico import (
    DIMENSIONES,
    ELITISMO,
    GENERACIONES,
    NUM_HILOS,
    POBLACION,
    PROBABILIDAD_CRUZA,
    PROBABILIDAD_MUTACION,
    SEMILLA,
    TORNEO,
    ejecutar_algoritmo,
)
from core.services.comparar_rendimiento import comparar_funcion
from core.services.exportar_excel import generar_excel
from core.services.funciones import (
    DIMENSIONES_MAX,
    DIMENSIONES_MIN,
    FUNCIONES,
    configurar,
    dimensiones_efectivas,
    optimo_en_dominio,
)

# Cota de seguridad para el dominio que elige el usuario.
LIMITE_DOMINIO = 1e6
from core.services.graficas import generar_grafica_convergencia


def hello(request):
    return render(request, 'hello.html', {'name': 'Joel'})


def listar_productos(request):
    productos = [
        {"id": 1, "nombre": "Teclado", "precio": 350},
        {"id": 2, "nombre": "Mouse", "precio": 200},
        {"id": 3, "nombre": "Monitor", "precio": 2500},
    ]
    print("Sistema:", platform.system())
    print("Procesadores lógicos:", os.cpu_count())
    return JsonResponse({"productos": productos})


def tarea(nombre):
    for i in range(1, 6):
        print(f"[{nombre}] Iteración {i}")
        time.sleep(1)


def probar_hilos(request):
    hilo1 = threading.Thread(target=tarea, args=("Hilo A",))
    hilo2 = threading.Thread(target=tarea, args=("Hilo B",))
    hilo1.start()
    hilo2.start()
    return JsonResponse({"mensaje": "Se iniciaron los dos hilos"})


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def _leer_parametros(datos):
    """Lee y valida los parametros del algoritmo desde un dict (GET o JSON).

    Devuelve (parametros, error). Si error no es None, parametros es None.
    """
    try:
        parametros = {
            "poblacion_tam": int(datos.get("poblacion", POBLACION)),
            "generaciones": int(datos.get("generaciones", GENERACIONES)),
            "probabilidad_cruza": float(
                datos.get("probabilidad_cruza", PROBABILIDAD_CRUZA)
            ),
            "probabilidad_mutacion": float(
                datos.get("probabilidad_mutacion", PROBABILIDAD_MUTACION)
            ),
            "elitismo": int(datos.get("elitismo", ELITISMO)),
            "torneo": int(datos.get("torneo", TORNEO)),
            "num_hilos": int(datos.get("num_hilos", NUM_HILOS)),
            "semilla": int(datos.get("semilla", SEMILLA)),
            "dimensiones": int(datos.get("dimensiones") or DIMENSIONES),
        }
    except (ValueError, TypeError):
        return None, "Los parametros deben tener valores numericos validos"

    p = parametros
    if (
        p["poblacion_tam"] < 2
        or p["generaciones"] < 1
        or not 0 <= p["probabilidad_cruza"] <= 1
        or not 0 <= p["probabilidad_mutacion"] <= 1
        or not 1 <= p["elitismo"] < p["poblacion_tam"]
        or not 2 <= p["torneo"] <= p["poblacion_tam"]
        or not 1 <= p["num_hilos"] <= 64
        or not DIMENSIONES_MIN <= p["dimensiones"] <= DIMENSIONES_MAX
    ):
        return None, "Uno o mas parametros estan fuera de rango"

    dominio, error = _leer_dominio(datos)
    if error:
        return None, error
    parametros["dominio"] = dominio
    return parametros, None


def _leer_dominio(datos):
    """Dominio opcional: ambos limites o ninguno (ninguno = dominio estandar).

    Devuelve ((inferior, superior) o None, error).
    """
    crudos = [datos.get("limite_inferior"), datos.get("limite_superior")]
    vacios = [v is None or str(v).strip() == "" for v in crudos]
    if all(vacios):
        return None, None
    if any(vacios):
        return None, "Escribe ambos limites del dominio o deja los dos vacios"
    try:
        inferior, superior = (float(v) for v in crudos)
    except (ValueError, TypeError):
        return None, "Los limites del dominio deben ser numericos"
    if not -LIMITE_DOMINIO <= inferior < superior <= LIMITE_DOMINIO:
        return None, (
            "El limite inferior debe ser menor que el superior y ambos "
            f"estar entre {-LIMITE_DOMINIO:g} y {LIMITE_DOMINIO:g}"
        )
    return (inferior, superior), None


def _leer_json(request):
    try:
        return json.loads(request.body or b"{}"), None
    except json.JSONDecodeError:
        return None, "El cuerpo de la peticion debe ser JSON valido"


def _url_grafica(corrida_id):
    ruta = os.path.join(
        settings.MEDIA_ROOT, "corridas", str(corrida_id), "convergencia.png"
    )
    if not os.path.exists(ruta):
        return None
    return f"{settings.MEDIA_URL}corridas/{corrida_id}/convergencia.png"


def _serializar_corrida(corrida):
    return {
        "id": corrida.id,
        "funcion": corrida.funcion,
        "poblacion": corrida.poblacion,
        "generaciones": corrida.generaciones,
        "probabilidad_cruza": corrida.probabilidad_cruza,
        "probabilidad_mutacion": corrida.probabilidad_mutacion,
        "elitismo": corrida.elitismo,
        "torneo": corrida.torneo,
        "num_hilos": corrida.num_hilos,
        "dimensiones": corrida.dimensiones,
        "semilla": corrida.semilla,
        "limite_inferior": corrida.limite_inferior,
        "limite_superior": corrida.limite_superior,
        "tiene_convergencia": bool(corrida.convergencia),
        "mejor_solucion": corrida.mejor_solucion,
        "valor_obtenido": corrida.valor_obtenido,
        "minimo_conocido": corrida.minimo_conocido,
        "tiempo_segundos": corrida.tiempo_segundos,
        "fecha": corrida.fecha.isoformat(),
        "grafica_convergencia": _url_grafica(corrida.id),
    }


def _serializar_comparacion(c):
    return {
        "id": c.id,
        "funcion": c.funcion,
        "poblacion": c.poblacion,
        "generaciones": c.generaciones,
        "num_hilos": c.num_hilos,
        "tiempo_secuencial": c.tiempo_secuencial,
        "tiempo_paralelo": c.tiempo_paralelo,
        "aceleracion": c.aceleracion,
        "valor_secuencial": c.valor_secuencial,
        "valor_paralelo": c.valor_paralelo,
        "mejor_secuencial": c.mejor_secuencial,
        "mejor_paralelo": c.mejor_paralelo,
        "fecha": c.fecha.isoformat(),
    }


# ---------------------------------------------------------------------------
# Experimento individual
# ---------------------------------------------------------------------------

def probar_algoritmo(request):
    nombre = request.GET.get("funcion", "Trid")
    if nombre not in FUNCIONES:
        return JsonResponse({"error": "Funcion no valida"}, status=400)

    parametros, error = _leer_parametros(request.GET)
    if error:
        return JsonResponse({"error": error}, status=400)
    parametros["dimensiones"] = dimensiones_efectivas(
        nombre, parametros["dimensiones"]
    )
    dominio = parametros["dominio"]
    _, limites, minimo_conocido = configurar(
        nombre, parametros["dimensiones"], dominio
    )

    mejor, valor, tiempo, historial = ejecutar_algoritmo(
        nombre, usar_hilos=True, **parametros
    )

    corrida = Corrida.objects.create(
        funcion=nombre,
        poblacion=parametros["poblacion_tam"],
        generaciones=parametros["generaciones"],
        probabilidad_cruza=parametros["probabilidad_cruza"],
        probabilidad_mutacion=parametros["probabilidad_mutacion"],
        elitismo=parametros["elitismo"],
        torneo=parametros["torneo"],
        num_hilos=parametros["num_hilos"],
        dimensiones=parametros["dimensiones"],
        semilla=parametros["semilla"],
        limite_inferior=dominio[0] if dominio else None,
        limite_superior=dominio[1] if dominio else None,
        mejor_solucion=mejor,
        valor_obtenido=valor,
        minimo_conocido=minimo_conocido,
        tiempo_segundos=tiempo,
        convergencia=historial,
    )
    generar_grafica_convergencia(
        historial=historial,
        corrida_id=corrida.id,
        media_root=settings.MEDIA_ROOT,
    )

    respuesta = _serializar_corrida(corrida)
    respuesta["parametros"] = {
        "poblacion": parametros["poblacion_tam"],
        **{k: v for k, v in parametros.items() if k != "poblacion_tam"},
    }
    respuesta["limites"] = [list(par) for par in limites]
    # El dominio estandar siempre contiene el optimo conocido.
    respuesta["optimo_en_dominio"] = (
        optimo_en_dominio(nombre, parametros["dimensiones"], dominio)
        if dominio else True
    )
    respuesta["guardado"] = True
    respuesta["generaciones_registradas"] = len(historial)
    respuesta["convergencia"] = historial
    return JsonResponse(respuesta)


# ---------------------------------------------------------------------------
# Historial
# ---------------------------------------------------------------------------

def historial_corridas(request):
    corridas = Corrida.objects.order_by("-fecha")
    return JsonResponse({
        "corridas": [_serializar_corrida(c) for c in corridas],
    })


def pagina_historial(request):
    return render(
        request,
        "historial.html",
        {
            "corridas": Corrida.objects.order_by("-fecha"),
            "funciones": FUNCIONES.keys(),
            "escalables": [n for n, f in FUNCIONES.items() if f["escalable"]],
            "dimensiones_max": DIMENSIONES_MAX,
        },
    )


MAX_IDS = 500


def _leer_ids(texto):
    """Convierte "1,2,3" en [1, 2, 3]. Devuelve (ids, error)."""
    partes = [p for p in (texto or "").split(",") if p.strip()]
    try:
        ids = [int(p) for p in partes]
    except ValueError:
        return None, "Los ids deben ser enteros separados por coma"
    if len(ids) > MAX_IDS:
        return None, f"Se pueden pedir como maximo {MAX_IDS} corridas"
    return ids, None


@require_GET
def convergencias_json(request):
    ids, error = _leer_ids(request.GET.get("ids"))
    if error or not ids:
        return JsonResponse(
            {"error": error or "No se recibieron ids"}, status=400
        )
    corridas = Corrida.objects.filter(id__in=ids).order_by("id")
    return JsonResponse({
        "corridas": [
            {**_serializar_corrida(c), "convergencia": c.convergencia}
            for c in corridas
        ],
    })


@require_GET
def exportar_excel(request):
    """Excel de las corridas pedidas: ?ids=1,2 o ?funcion=Trid o todas."""
    corridas = Corrida.objects.order_by("-fecha", "-id")
    ids, error = _leer_ids(request.GET.get("ids"))
    if error:
        return JsonResponse({"error": error}, status=400)
    if ids:
        corridas = corridas.filter(id__in=ids)
    funcion = request.GET.get("funcion")
    if funcion:
        if funcion not in FUNCIONES:
            return JsonResponse({"error": "Funcion no valida"}, status=400)
        corridas = corridas.filter(funcion=funcion)

    contenido = generar_excel(corridas)
    nombre = f"ga_resultados_{timezone.localtime():%Y%m%d_%H%M}.xlsx"
    respuesta = HttpResponse(
        contenido,
        content_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )
    respuesta["Content-Disposition"] = f'attachment; filename="{nombre}"'
    return respuesta


@require_POST
def eliminar_corridas(request):
    datos, error = _leer_json(request)
    if error:
        return JsonResponse({"ok": False, "error": error}, status=400)

    try:
        ids = [int(i) for i in datos.get("ids", [])]
    except (ValueError, TypeError):
        return JsonResponse(
            {"ok": False, "error": "Los ids deben ser enteros"}, status=400
        )
    if not ids:
        return JsonResponse(
            {"ok": False, "error": "No se recibieron ids"}, status=400
        )

    eliminadas, _ = Corrida.objects.filter(id__in=ids).delete()
    for corrida_id in ids:
        shutil.rmtree(
            os.path.join(settings.MEDIA_ROOT, "corridas", str(corrida_id)),
            ignore_errors=True,
        )

    return JsonResponse({
        "ok": True,
        "eliminadas": eliminadas,
        "mensaje": f"{eliminadas} corrida(s) eliminada(s).",
    })


# ---------------------------------------------------------------------------
# Comparativo secuencial vs paralelo
# ---------------------------------------------------------------------------

@require_POST
def comparar_rendimiento(request):
    datos, error = _leer_json(request)
    if error:
        return JsonResponse({"ok": False, "error": error}, status=400)

    funciones = datos.get("funciones") or list(FUNCIONES.keys())
    invalidas = [f for f in funciones if f not in FUNCIONES]
    if invalidas:
        return JsonResponse(
            {"ok": False, "error": f"Funciones no validas: {invalidas}"},
            status=400,
        )

    parametros, error = _leer_parametros(datos)
    if error:
        return JsonResponse({"ok": False, "error": error}, status=400)

    resultados = []
    for nombre in funciones:
        r = comparar_funcion(nombre, **dict(parametros))
        comparacion = Comparacion.objects.create(
            funcion=nombre,
            poblacion=parametros["poblacion_tam"],
            generaciones=parametros["generaciones"],
            num_hilos=parametros["num_hilos"],
            tiempo_secuencial=r["tiempo_secuencial"],
            tiempo_paralelo=r["tiempo_paralelo"],
            aceleracion=r["aceleracion"],
            valor_secuencial=r["valor_secuencial"],
            valor_paralelo=r["valor_paralelo"],
            mejor_secuencial=r["mejor_secuencial"],
            mejor_paralelo=r["mejor_paralelo"],
        )
        resultados.append(_serializar_comparacion(comparacion))

    return JsonResponse({"ok": True, "resultados": resultados})


def comparaciones_json(request):
    todas = [
        _serializar_comparacion(c)
        for c in Comparacion.objects.order_by("-fecha", "-id")
    ]
    ultimas = {}
    for c in todas:
        ultimas.setdefault(c["funcion"], c)
    orden = list(FUNCIONES.keys())
    resumen = [ultimas[f] for f in orden if f in ultimas]
    return JsonResponse({"resumen": resumen, "comparaciones": todas})


@require_POST
def limpiar_comparaciones(request):
    eliminadas, _ = Comparacion.objects.all().delete()
    return JsonResponse({
        "ok": True,
        "eliminadas": eliminadas,
        "mensaje": "Comparaciones limpiadas.",
    })
