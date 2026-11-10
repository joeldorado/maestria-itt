# GA Lab: algoritmo genético con hilos y benchmarks

Interfaz web en Django para manipular los parámetros de un algoritmo genético y optimizar las funciones benchmark del trabajo de hilos:

- Shubert, Trid, Zakharov, Beale y Six-Hump Camel.
- La gráfica de convergencia de cada corrida.
- Exportación de los resultados a Excel.

## Cómo correrlo

Requiere Python 3.12 o superior.

```bash
cd web-django
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001
```

Abre <http://localhost:8001/historial-html/>.

## Uso

1. **Experimento:** elige la función y ajusta los parámetros, luego pulsa **Ejecutar experimento**.
   - Parámetros: dimensiones (d), población, generaciones, cruza, mutación, elitismo, torneo, hilos y semilla.
   - El campo d acepta de 2 a 30 y solo se habilita en Trid y Zakharov; las otras tres funciones son 2D por definición.
   - **Dominio (opcional):** déjalo vacío para usar el dominio estándar de la función. Si escribes [inferior, superior], se aplica a todas las variables.
     - La mutación da saltos del 10 % del ancho del dominio, así que el dominio también cambia el tamaño de la mutación.
     - La interfaz avisa si el óptimo conocido queda fuera del dominio.
   - El resultado muestra el óptimo, el valor obtenido, el error y la gráfica de convergencia. La gráfica tiene dos vistas: «Mejor valor» y «Error vs óptimo (log)».
   - El botón **Exportar esta corrida a Excel** descarga solo esa corrida.
2. **Historial:** todas las corridas guardadas en SQLite.
   - Marca de 2 a 8 y pulsa **Comparar variantes** para ver sus curvas encimadas y los parámetros que cambian resaltados.
   - **Exportar seleccionadas** descarga las corridas marcadas.
   - **Exportar a Excel** descarga todo, o solo la función filtrada.
3. **Comparativo:** ejecución secuencial contra paralela (hilos).

El Excel trae dos hojas:
- **Resultados:** una fila por corrida, con todos los parámetros, el valor, el error y el tiempo.
- **Convergencia:** el mejor valor por generación de cada corrida, con una gráfica de líneas nativa de Excel.

## Estudio de variantes (muchas corridas)

```bash
python manage.py estudiar_variantes --corridas 100 --salida ../../estudio_variantes
```

Corre cada variante con las semillas 1 a N y no escribe en la base de datos. Las variantes están en `core/services/estudio.py`:
- dominio;
- dimensiones;
- mutación;
- generaciones;
- población;
- cruza.

Genera tres archivos:
- **`estudio_variantes.xlsx`:** hojas de conclusiones, resumen por variante, todas las corridas, curvas medianas y gráficas.
- **`estudio_variantes.md`:** las mismas tablas como reporte.
- **`resumen.json`:** el resumen en formato de datos.

Con `--bloques` corres solo algunos bloques y con `--procesos` eliges cuántos procesos en paralelo usar.

## Estructura

| Ruta | Qué hay |
|---|---|
| `core/services/algoritmo_genetico.py` | GA: torneo, cruza aritmética, mutación gaussiana y elitismo; evalúa la población con `ThreadPoolExecutor` |
| `core/services/funciones.py` | Benchmarks y `configurar(nombre, d)` para Trid y Zakharov en d dimensiones |
| `core/services/exportar_excel.py` | Genera el `.xlsx` con openpyxl |
| `core/views.py`, `core/urls.py` | Endpoints: `/probar-algoritmo/`, `/historial-json/`, `/convergencias-json/` y `/exportar-excel/` |
| `templates/historial.html`, `core/static/core/variantes.js` | Interfaz: Materialize, Chart.js y MathJax |
| `core/tests.py` | Pruebas: `python manage.py test core` |
