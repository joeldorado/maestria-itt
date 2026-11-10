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
