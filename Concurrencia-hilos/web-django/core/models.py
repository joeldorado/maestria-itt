from django.db import models


class Corrida(models.Model):
    funcion = models.CharField(max_length=50)
    poblacion = models.PositiveIntegerField(default=100)
    generaciones = models.PositiveIntegerField(default=200)
    probabilidad_cruza = models.FloatField(default=0.85)
    probabilidad_mutacion = models.FloatField(default=0.10)
    elitismo = models.PositiveIntegerField(default=2)
    torneo = models.PositiveIntegerField(default=3)
    num_hilos = models.PositiveIntegerField(default=4)
    dimensiones = models.PositiveIntegerField(default=2)
    # Null en las corridas guardadas antes de registrar la semilla.
    semilla = models.IntegerField(null=True, blank=True)
    # Dominio de busqueda elegido por el usuario; null = dominio estandar.
    limite_inferior = models.FloatField(null=True, blank=True)
    limite_superior = models.FloatField(null=True, blank=True)

    mejor_solucion = models.JSONField()
    valor_obtenido = models.FloatField()
    minimo_conocido = models.FloatField()
    tiempo_segundos = models.FloatField()
    # Mejor valor por generación; vacío en corridas anteriores a este campo.
    convergencia = models.JSONField(default=list, blank=True)

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.funcion} d={self.dimensiones} - {self.fecha:%Y-%m-%d %H:%M}"

class Comparacion(models.Model):
    funcion = models.CharField(max_length=50)
    poblacion = models.PositiveIntegerField(default=100)
    generaciones = models.PositiveIntegerField(default=200)
    num_hilos = models.PositiveIntegerField(default=4)

    tiempo_secuencial = models.FloatField()
    tiempo_paralelo = models.FloatField()
    aceleracion = models.FloatField()

    valor_secuencial = models.FloatField()
    valor_paralelo = models.FloatField()
    mejor_secuencial = models.JSONField()
    mejor_paralelo = models.JSONField()

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.funcion} {self.aceleracion:.3f}x - {self.fecha:%Y-%m-%d %H:%M}"
