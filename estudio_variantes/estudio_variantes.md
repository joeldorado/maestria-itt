# Estudio de variantes del GA

Cada variante se corrió **100 veces** (semillas 1 a 100); en cada bloque cambia un solo parámetro y el resto queda en los valores de referencia: población 100, 200 generaciones, cruza 0.85, mutación 0.10, elitismo 2, torneo 3, 4 hilos y dominio estándar. **Éxito** = error |f(x) − f*| < 0.01. Los tiempos se midieron con varias corridas en paralelo (procesos), así que sirven para comparar entre sí, no como tiempo absoluto.

## Conclusiones

1. **El dominio controla el tamaño de la mutación.** La mutación da saltos del 10 % del ancho del dominio.
   - En Zakharov d=10, angostar el dominio a [-1, 1] sube el éxito del 19 % al 100 % y baja la mediana del error de 0.021 a 0.00017.
   - Ensancharlo lo arruina: con [-50, 100] la mediana es 13 y con [-500, 1000] es 11 097. En ninguno de los dos casos llega una sola corrida al óptimo.
2. **Más angosto no siempre es mejor.** En Trid d=5, el dominio estándar [-25, 25] da 44 % de éxito y [-10, 10] solo 14 %.
   - El óptimo x* = (5, 8, 9, 8, 5) queda junto al borde del dominio angosto (x₃ = 9 contra 10), y el recorte en el límite estorba.
   - Un dominio enorme, [-250, 250], también empeora: 11 % de éxito.
   - Por eso el dominio estándar se define para contener el óptimo con margen.
3. **Si el óptimo queda fuera, todas las corridas dan lo mismo.** Con Zakharov en [1, 10], las 100 semillas terminan en x = (1, …, 1) con error 572 680; la desviación estándar es prácticamente 0. El GA hace bien su trabajo, pero el problema está mal planteado.
4. **La dimensión es lo que más pesa.**
   - Trid pasa de 100 % de éxito en d=2 a 44 % en d=5 y a 0 % en d=10 y d=20.
   - Zakharov aguanta hasta d=5 con 100 % de éxito, cae a 19 % en d=10 y llega a 0 % en d=20.
5. **Si sobra presupuesto, conviene gastarlo en generaciones.** En Trid d=10:
   - De 100 a 1000 generaciones, la mediana del error baja de 63.6 a 0.56, unas 113 veces.
   - De 30 a 300 individuos, solo baja de 54 a 22.5, unas 2.4 veces.
   - Las dos opciones multiplican el tiempo por unas 10.
6. **La mutación tiene un punto medio.** Con 0.01 la búsqueda se estanca: mediana 0.56. Con 0.50 destruye las buenas soluciones: mediana 0.17 y 0 % de éxito. Entre 0.10 y 0.30 está lo mejor, cada una con su ventaja:
   - 0.10 logra más éxitos (34 %).
   - 0.30 tiene una mediana un poco menor (0.018 contra 0.022) y menos dispersión (desviación 0.020 contra 0.054).
7. **La cruza casi no cambia el resultado.** Entre 0.5, 0.85 y 1.0, las medianas de Zakharov d=10 van de 0.021 a 0.026 y sus rangos intercuartílicos se enciman.
   - Con solo 10 semillas había parecido que 0.5 era la mejor. Con 100, la mejor es 0.85.
   - Lección: con pocas semillas, el azar puede hacer que una variante parezca mejor sin serlo.

**Nota.** «Gen. éxito» es la mediana de la generación en que se cruzó el umbral, contando solo las corridas que lo lograron.

## Dominio · Zakharov d=10

| Variante | % éxito | Mediana | Media | Desv. est. | P25 – P75 | Mejor | Peor | Gen. éxito | Tiempo (s) |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| [-1, 1] **← mejor** | 100 % | 1.72e-04 | 2.15e-04 | 1.41e-04 | 1.12e-04 – 2.73e-04 | 3.61e-05 | 7.96e-04 | 32 | 0.209 |
| estándar | 19 % | 0.02079 | 0.02735 | 0.02091 | 0.01176 – 0.03602 | 0.003421 | 0.1036 | 185 | 0.210 |
| [-50, 100] | 0 % | 13.17 | 18.33 | 16.82 | 5.66 – 25.46 | 0.8156 | 90.51 | — | 0.206 |
| [-500, 1000] | 0 % | 11,096.72 | 13,340.75 | 10,928.33 | 5,190.67 – 17,248.78 | 525.12 | 63,342.96 | — | 0.205 |
| [1, 10] ⚠️ óptimo fuera | 0 % | 5.73e+05 | 5.73e+05 | 7.02e-05 | 5.73e+05 – 5.73e+05 | 5.73e+05 | 5.73e+05 | — | 0.209 |

## Dominio · Trid d=5

| Variante | % éxito | Mediana | Media | Desv. est. | P25 – P75 | Mejor | Peor | Gen. éxito | Tiempo (s) |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| [-10, 10] | 14 % | 0.01941 | 0.02071 | 0.009806 | 0.01368 – 0.02536 | 0.003846 | 0.0469 | 182 | 0.188 |
| estándar **← mejor** | 44 % | 0.01112 | 0.01954 | 0.02384 | 0.002405 – 0.02859 | 9.50e-08 | 0.1247 | 70 | 0.178 |
| [-250, 250] | 11 % | 0.1909 | 0.6771 | 1.09 | 0.04339 – 0.7807 | 8.96e-05 | 5.38 | 78 | 0.181 |

## Dimensiones · Trid y Zakharov

| Variante | % éxito | Mediana | Media | Desv. est. | P25 – P75 | Mejor | Peor | Gen. éxito | Tiempo (s) |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| Trid d=2 **← mejor** | 100 % | 0 | 4.59e-08 | 3.09e-07 | 0 – 1.46e-12 | 0 | 2.98e-06 | 3 | 0.152 |
| Trid d=5 | 44 % | 0.01112 | 0.01954 | 0.02384 | 0.002405 – 0.02859 | 9.50e-08 | 0.1247 | 70 | 0.185 |
| Trid d=10 | 0 % | 29.66 | 34.96 | 25.16 | 16.79 – 45.63 | 0.3784 | 115.86 | — | 0.213 |
| Trid d=20 | 0 % | 1,613.48 | 1,666.53 | 625.82 | 1,290.54 – 2,020.88 | 463.81 | 5,065.01 | — | 0.259 |
| Zakharov d=2 | 100 % | 1.22e-24 | 6.97e-08 | 6.24e-07 | 6.15e-41 – 1.21e-14 | 3.36e-111 | 6.28e-06 | 5 | 0.163 |
| Zakharov d=5 | 100 % | 9.90e-05 | 2.91e-04 | 5.24e-04 | 1.94e-05 – 2.92e-04 | 1.81e-07 | 0.003859 | 46 | 0.229 |
| Zakharov d=10 | 19 % | 0.02079 | 0.02735 | 0.02091 | 0.01176 – 0.03602 | 0.003421 | 0.1036 | 185 | 0.225 |
| Zakharov d=20 | 0 % | 2.63 | 2.69 | 0.9383 | 2.02 – 3.22 | 0.8867 | 6.24 | — | 0.260 |

## Mutación · Trid d=5, población 60

| Variante | % éxito | Mediana | Media | Desv. est. | P25 – P75 | Mejor | Peor | Gen. éxito | Tiempo (s) |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| mutación 0.01 | 11 % | 0.5632 | 0.7921 | 0.8716 | 0.09182 – 1.22 | 1.11e-05 | 4.42 | 15 | 0.130 |
| mutación 0.05 | 12 % | 0.1325 | 0.1789 | 0.1682 | 0.03619 – 0.2708 | 7.57e-06 | 0.7175 | 55 | 0.142 |
| mutación 0.10 | 34 % | 0.02213 | 0.04633 | 0.05443 | 0.004752 – 0.07355 | 1.47e-06 | 0.3192 | 62 | 0.151 |
| mutación 0.30 **← mejor** | 21 % | 0.0183 | 0.02445 | 0.01951 | 0.01188 – 0.0316 | 9.10e-04 | 0.103 | 131 | 0.142 |
| mutación 0.50 | 0 % | 0.1664 | 0.2045 | 0.1358 | 0.1126 – 0.2597 | 0.03483 | 0.6277 | — | 0.132 |

## Generaciones · Trid d=10

| Variante | % éxito | Mediana | Media | Desv. est. | P25 – P75 | Mejor | Peor | Gen. éxito | Tiempo (s) |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| 100 generaciones | 0 % | 63.62 | 68.81 | 49.47 | 32.60 – 89.67 | 0.8671 | 212.68 | — | 0.104 |
| 200 generaciones | 0 % | 29.66 | 34.96 | 25.16 | 16.79 – 45.63 | 0.3784 | 115.86 | — | 0.220 |
| 500 generaciones | 0 % | 5.43 | 5.76 | 3.94 | 2.67 – 7.39 | 0.1944 | 16.25 | — | 0.527 |
| 1000 generaciones **← mejor** | 0 % | 0.5641 | 0.6867 | 0.4238 | 0.4091 – 0.8211 | 0.1564 | 2.51 | — | 1.035 |

## Población · Trid d=10

| Variante | % éxito | Mediana | Media | Desv. est. | P25 – P75 | Mejor | Peor | Gen. éxito | Tiempo (s) |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| población 30 | 0 % | 54.07 | 64.27 | 49.59 | 23.59 – 90.99 | 0.1734 | 230.98 | — | 0.087 |
| población 100 | 0 % | 29.66 | 34.96 | 25.16 | 16.79 – 45.63 | 0.3784 | 115.86 | — | 0.209 |
| población 300 **← mejor** | 0 % | 22.53 | 25.71 | 12.75 | 16.53 – 32.47 | 6.21 | 63.65 | — | 0.598 |

## Cruza · Zakharov d=10

| Variante | % éxito | Mediana | Media | Desv. est. | P25 – P75 | Mejor | Peor | Gen. éxito | Tiempo (s) |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| cruza 0.50 | 9 % | 0.02612 | 0.03613 | 0.03095 | 0.01575 – 0.04864 | 0.001712 | 0.1877 | 160 | 0.207 |
| cruza 0.85 **← mejor** | 19 % | 0.02079 | 0.02735 | 0.02091 | 0.01176 – 0.03602 | 0.003421 | 0.1036 | 185 | 0.215 |
| cruza 1.00 | 16 % | 0.02243 | 0.02738 | 0.01914 | 0.01279 – 0.037 | 0.004093 | 0.1069 | 184 | 0.206 |

## Cómo repetirlo

```bash
cd web-django
python manage.py estudiar_variantes --corridas 100 --salida ../../estudio_variantes
python manage.py estudiar_variantes --bloques dominio_zakharov mutacion --corridas 30
```

Bloques disponibles: `dominio_zakharov`, `dominio_trid`, `dimensiones`, `mutacion`, `generaciones`, `poblacion`, `cruza`. No escribe en la base de datos.
