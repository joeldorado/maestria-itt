"""python manage.py estudiar_variantes --corridas 100 --salida <carpeta>

Corre cada variante de core/services/estudio.py con las semillas 1..N y deja
estudio_variantes.xlsx, estudio_variantes.md y resumen.json en la carpeta.
No escribe en la base de datos.
"""

import json
import os
import time

from django.core.management.base import BaseCommand, CommandError

from core.services.estudio import BLOQUES, ejecutar_estudio, resumir, variantes
from core.services.reporte_estudio import generar_excel, generar_markdown


class Command(BaseCommand):
    help = "Corre muchas semillas por variante y genera Excel + reporte Markdown."

    def add_arguments(self, parser):
        parser.add_argument("--corridas", type=int, default=100)
        parser.add_argument("--salida", default="estudio_variantes")
        parser.add_argument("--bloques", nargs="*", choices=list(BLOQUES))
        parser.add_argument("--procesos", type=int, default=max(1, (os.cpu_count() or 2) - 2))
        parser.add_argument("--conclusiones", help="Archivo .md con conclusiones para el reporte")

    def handle(self, *args, **opciones):
        if not 1 <= opciones["corridas"] <= 1000:
            raise CommandError("--corridas debe estar entre 1 y 1000")
        lista = variantes(opciones["bloques"])
        total = len(lista) * opciones["corridas"]
        self.stdout.write(f"{len(lista)} variantes × {opciones['corridas']} corridas = {total} corridas, {opciones['procesos']} procesos")

        inicio = time.perf_counter()
        paso = max(1, total // 20)

        def avance(hechas, total_):
            if hechas % paso == 0 or hechas == total_:
                self.stdout.write(f"  {hechas}/{total_} ({time.perf_counter() - inicio:.0f} s)")

        resultados = ejecutar_estudio(lista, opciones["corridas"], opciones["procesos"], avance)
        filas = resumir(lista, resultados)

        salida = opciones["salida"]
        os.makedirs(salida, exist_ok=True)
        conclusiones = ""
        if opciones["conclusiones"]:
            with open(opciones["conclusiones"], encoding="utf-8") as archivo:
                conclusiones = archivo.read()
        generar_excel(filas, resultados, os.path.join(salida, "estudio_variantes.xlsx"), conclusiones)
        generar_markdown(filas, opciones["corridas"], os.path.join(salida, "estudio_variantes.md"), conclusiones)
        with open(os.path.join(salida, "resumen.json"), "w", encoding="utf-8") as archivo:
            json.dump(filas, archivo, ensure_ascii=False, indent=1)
        self.stdout.write(self.style.SUCCESS(f"Listo en {time.perf_counter() - inicio:.0f} s → {os.path.abspath(salida)}"))
