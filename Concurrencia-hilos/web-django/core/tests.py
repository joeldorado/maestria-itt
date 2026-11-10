import shutil
import tempfile
from io import BytesIO, StringIO

from django.test import TestCase, override_settings
from openpyxl import load_workbook

from core.models import Corrida
from core.services.algoritmo_genetico import ejecutar_algoritmo
from core.services.funciones import FUNCIONES, configurar, optimo_en_dominio

MEDIA_TEMPORAL = tempfile.mkdtemp(prefix="ga-tests-")
RAPIDO = {"poblacion": 20, "generaciones": 12, "semilla": 7}


class ConfigurarDimensionesTests(TestCase):
    def test_trid_en_tres_dimensiones(self):
        funcion, limites, minimo = configurar("Trid", 3)
        self.assertEqual(limites, [(-9, 9)] * 3)
        self.assertEqual(minimo, -7.0)
        # El óptimo teórico x_i = i(d + 1 - i) da exactamente el mínimo.
        self.assertAlmostEqual(funcion([3, 4, 3]), -7.0)

    def test_zakharov_escala_y_conserva_minimo_cero(self):
        funcion, limites, minimo = configurar("Zakharov", 6)
        self.assertEqual(len(limites), 6)
        self.assertEqual(minimo, 0.0)
        self.assertEqual(funcion([0] * 6), 0)

    def test_funciones_no_escalables_quedan_en_dos_dimensiones(self):
        _, limites, minimo = configurar("Beale", 8)
        self.assertEqual(limites, FUNCIONES["Beale"]["limites"])
        self.assertEqual(minimo, FUNCIONES["Beale"]["minimo_conocido"])

    def test_dos_dimensiones_es_la_configuracion_original(self):
        for nombre, config in FUNCIONES.items():
            funcion, limites, minimo = configurar(nombre, 2)
            self.assertIs(funcion, config["funcion"])
            self.assertEqual(limites, config["limites"])
            self.assertEqual(minimo, config["minimo_conocido"])

    def test_misma_semilla_mismo_resultado_y_tamano_correcto(self):
        a = ejecutar_algoritmo("Trid", poblacion_tam=20, generaciones=10, semilla=3, dimensiones=4)
        b = ejecutar_algoritmo("Trid", poblacion_tam=20, generaciones=10, semilla=3, dimensiones=4)
        self.assertEqual(a[0], b[0])
        self.assertEqual(len(a[0]), 4)
        self.assertEqual(len(a[3]), 10)


class DominioTests(TestCase):
    def test_dominio_personalizado_aplica_a_todas_las_variables(self):
        _, limites, minimo = configurar("Zakharov", 3, dominio=(-1, 1))
        self.assertEqual(limites, [(-1, 1)] * 3)
        self.assertEqual(minimo, 0.0)
        _, limites, _ = configurar("Six-Hump Camel", 2, dominio=(-1, 1))
        self.assertEqual(limites, [(-1, 1), (-1, 1)])

    def test_dominio_estandar_explicito_da_el_mismo_resultado(self):
        normal = ejecutar_algoritmo("Zakharov", poblacion_tam=20, generaciones=10, semilla=5, dimensiones=3)
        explicito = ejecutar_algoritmo(
            "Zakharov", poblacion_tam=20, generaciones=10, semilla=5, dimensiones=3, dominio=(-5, 10)
        )
        self.assertEqual(normal[0], explicito[0])

    def test_solucion_respeta_el_dominio(self):
        mejor, *_ = ejecutar_algoritmo("Trid", poblacion_tam=20, generaciones=10, semilla=1, dimensiones=4, dominio=(0, 2))
        self.assertTrue(all(0 <= x <= 2 for x in mejor))

    def test_optimo_dentro_o_fuera_del_dominio(self):
        casos = [
            ("Zakharov", 4, (-5, 10), True), ("Zakharov", 4, (1, 10), False),
            ("Trid", 5, (-25, 25), True), ("Trid", 5, (-5, 5), False),
            ("Shubert", 2, (-10, 10), True), ("Shubert", 2, (-2, 0), True), ("Shubert", 2, (0, 1), False),
            ("Beale", 2, (-4.5, 4.5), True), ("Beale", 2, (-1, 1), False),
            ("Six-Hump Camel", 2, (-1, 1), True), ("Six-Hump Camel", 2, (0.5, 3), False),
        ]
        for nombre, d, dominio, esperado in casos:
            self.assertEqual(optimo_en_dominio(nombre, d, dominio), esperado, (nombre, dominio))


class EstudioVariantesTests(TestCase):
    def test_comando_genera_reportes_sin_tocar_la_bd(self):
        from django.core.management import call_command

        salida = tempfile.mkdtemp(prefix="estudio-")
        self.addCleanup(shutil.rmtree, salida, ignore_errors=True)
        call_command("estudiar_variantes", corridas=2, bloques=["dominio_trid"], procesos=1, salida=salida, stdout=StringIO())

        libro = load_workbook(f"{salida}/estudio_variantes.xlsx")
        self.assertEqual(libro["Resumen"]["B2"].value, "[-10, 10]")
        self.assertEqual(libro["Resumen"]["K2"].value, 2)  # corridas por variante
        self.assertEqual(libro["Corridas"].max_row, 1 + 3 * 2)
        with open(f"{salida}/estudio_variantes.md", encoding="utf-8") as archivo:
            self.assertIn("## Dominio · Trid d=5", archivo.read())
        self.assertFalse(Corrida.objects.exists())


@override_settings(MEDIA_ROOT=MEDIA_TEMPORAL)
class VistasTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEMPORAL, ignore_errors=True)

    def ejecutar(self, **extra):
        return self.client.get("/probar-algoritmo/", {**RAPIDO, **extra})

    def test_guarda_dimensiones_semilla_y_convergencia(self):
        respuesta = self.ejecutar(funcion="Trid", dimensiones=5)
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertEqual(datos["dimensiones"], 5)
        self.assertEqual(len(datos["mejor_solucion"]), 5)
        self.assertEqual(len(datos["convergencia"]), RAPIDO["generaciones"])
        self.assertEqual(datos["minimo_conocido"], -30.0)

        corrida = Corrida.objects.get(id=datos["id"])
        self.assertEqual(corrida.semilla, 7)
        self.assertEqual(corrida.convergencia, datos["convergencia"])

    def test_funcion_no_escalable_se_guarda_en_2d(self):
        datos = self.ejecutar(funcion="Beale", dimensiones=6).json()
        self.assertEqual(datos["dimensiones"], 2)
        self.assertEqual(len(datos["mejor_solucion"]), 2)

    def test_sin_dimensiones_usa_2(self):
        datos = self.ejecutar(funcion="Zakharov").json()
        self.assertEqual(datos["dimensiones"], 2)

    def test_dimension_fuera_de_rango_es_400(self):
        for valor in (1, 31, "abc"):
            respuesta = self.ejecutar(funcion="Trid", dimensiones=valor)
            self.assertEqual(respuesta.status_code, 400, valor)
        self.assertFalse(Corrida.objects.exists())

    def test_dominio_estandar_si_no_se_envia(self):
        datos = self.ejecutar(funcion="Zakharov", dimensiones=3).json()
        self.assertIsNone(datos["limite_inferior"])
        self.assertIsNone(datos["limite_superior"])
        self.assertEqual(datos["limites"], [[-5, 10]] * 3)
        self.assertTrue(datos["optimo_en_dominio"])

    def test_guarda_dominio_personalizado(self):
        datos = self.ejecutar(funcion="Zakharov", dimensiones=3, limite_inferior=-1, limite_superior=1).json()
        self.assertEqual((datos["limite_inferior"], datos["limite_superior"]), (-1.0, 1.0))
        self.assertTrue(all(-1 <= x <= 1 for x in datos["mejor_solucion"]))
        corrida = Corrida.objects.get(id=datos["id"])
        self.assertEqual((corrida.limite_inferior, corrida.limite_superior), (-1.0, 1.0))

    def test_avisa_si_el_optimo_queda_fuera(self):
        datos = self.ejecutar(funcion="Zakharov", limite_inferior=1, limite_superior=10).json()
        self.assertFalse(datos["optimo_en_dominio"])

    def test_dominio_invalido_es_400(self):
        casos = [
            {"limite_inferior": 1},  # falta el superior
            {"limite_inferior": 5, "limite_superior": 5},
            {"limite_inferior": 6, "limite_superior": 5},
            {"limite_inferior": "a", "limite_superior": 5},
            {"limite_inferior": -1e7, "limite_superior": 5},
        ]
        for extra in casos:
            self.assertEqual(self.ejecutar(funcion="Trid", **extra).status_code, 400, extra)
        self.assertFalse(Corrida.objects.exists())

    def test_historial_no_incluye_la_curva(self):
        self.ejecutar(funcion="Trid")
        corrida = self.client.get("/historial-json/").json()["corridas"][0]
        self.assertNotIn("convergencia", corrida)
        self.assertTrue(corrida["tiene_convergencia"])

    def test_convergencias_json(self):
        a = self.ejecutar(funcion="Trid").json()["id"]
        b = self.ejecutar(funcion="Trid", probabilidad_mutacion=0.3).json()["id"]
        datos = self.client.get("/convergencias-json/", {"ids": f"{a},{b}"}).json()
        self.assertEqual([c["id"] for c in datos["corridas"]], [a, b])
        self.assertEqual(len(datos["corridas"][1]["convergencia"]), RAPIDO["generaciones"])

        self.assertEqual(self.client.get("/convergencias-json/").status_code, 400)
        self.assertEqual(
            self.client.get("/convergencias-json/", {"ids": "1,x"}).status_code, 400
        )


@override_settings(MEDIA_ROOT=MEDIA_TEMPORAL)
class ExportarExcelTests(TestCase):
    def setUp(self):
        base = {
            "mejor_solucion": [1.0, 2.0],
            "valor_obtenido": -1.5,
            "minimo_conocido": -2.0,
            "tiempo_segundos": 0.01,
        }
        self.trid = Corrida.objects.create(
            funcion="Trid", dimensiones=3, semilla=42, convergencia=[3.0, 1.0, -1.5], **base
        )
        self.beale = Corrida.objects.create(
            funcion="Beale", convergencia=[2.0, 0.5], **base
        )
        # Corrida vieja: sin semilla ni convergencia.
        self.vieja = Corrida.objects.create(funcion="Trid", **base)

    def libro(self, **params):
        respuesta = self.client.get("/exportar-excel/", params)
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("attachment", respuesta["Content-Disposition"])
        self.assertIn(".xlsx", respuesta["Content-Disposition"])
        return load_workbook(BytesIO(respuesta.content))

    def test_exporta_todas_con_resultados_y_convergencia(self):
        libro = self.libro()
        self.assertEqual(libro.sheetnames, ["Resultados", "Convergencia"])

        resultados = libro["Resultados"]
        self.assertEqual(resultados.max_row, 4)
        encabezados = [c.value for c in resultados[1]]
        self.assertIn("Dimensiones", encabezados)
        self.assertIn("Error absoluto", encabezados)

        convergencia = libro["Convergencia"]
        generaciones = [c.value for c in convergencia["A"][1:] if c.value is not None]
        self.assertEqual(generaciones, [1, 2, 3])
        # Más reciente primero: B = Beale (2 generaciones), C = Trid (3).
        self.assertIn("Beale", convergencia["B1"].value)
        self.assertIsNone(convergencia["B4"].value)
        self.assertEqual(convergencia["C4"].value, -1.5)
        self.assertEqual(len(convergencia._charts), 1)
        notas = [c.value for fila in convergencia.iter_rows() for c in fila if c.value]
        self.assertTrue(any(f"#{self.vieja.id}" in str(n) for n in notas))

    def test_exporta_solo_ids_pedidos(self):
        libro = self.libro(ids=f"{self.trid.id}")
        resultados = libro["Resultados"]
        self.assertEqual(resultados.max_row, 2)
        self.assertEqual(resultados["D2"].value, 3)
        self.assertEqual(resultados["L2"].value, 42)

    def test_filtra_por_funcion(self):
        libro = self.libro(funcion="Beale")
        self.assertEqual(libro["Resultados"].max_row, 2)
        self.assertEqual(libro["Resultados"]["C2"].value, "Beale")

    def test_corrida_sin_curva_queda_anotada(self):
        libro = self.libro(ids=f"{self.vieja.id}")
        self.assertEqual(libro["Resultados"]["L2"].value, "no registrada")
        self.assertIn("Ninguna", libro["Convergencia"]["A1"].value)

    def test_columna_dominio(self):
        self.trid.limite_inferior, self.trid.limite_superior = -2.0, 3.5
        self.trid.save()
        resultados = self.libro()["Resultados"]
        encabezados = [c.value for c in resultados[1]]
        columna = encabezados.index("Dominio")
        valores = {fila[0].value: fila[columna].value for fila in resultados.iter_rows(min_row=2)}
        self.assertEqual(valores[self.trid.id], "[-2, 3.5]")
        self.assertEqual(valores[self.beale.id], "estándar")

    def test_parametros_invalidos(self):
        self.assertEqual(self.client.get("/exportar-excel/", {"ids": "a"}).status_code, 400)
        self.assertEqual(
            self.client.get("/exportar-excel/", {"funcion": "Nada"}).status_code, 400
        )
