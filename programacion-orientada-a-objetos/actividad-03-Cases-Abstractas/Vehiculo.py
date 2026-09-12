from abc import ABC, abstractmethod

class Vehiculo(ABC):
    def __init__(self, marca, modelo, anio, combustible):
        self.marca = marca
        self.modelo = modelo
        self.anio = anio
        self.__combustible = combustible
    #getters y setters
    @property
    def getCombustible(self):
        return self.__combustible
    
    @getCombustible.setter
    def setCombustible(self, value):
        self.__combustible = value
        
    #metodos abstractos
    @abstractmethod
    def encender(self):
        pass
    
    
    @abstractmethod
    def calcular_autonomia(self):
        pass
    
class Auto(Vehiculo):
    def __init__(self, marca, modelo, anio, combustible, puertas):
        super().__init__(marca, modelo, anio, combustible)
        self.puertas = puertas
    
    def encender(self):
        return f"El auto {self.marca} {self.modelo} del año {self.anio} está encendido."
    
    def calcular_autonomia(self):
        gasto = 15 #km por litro
        return self.getCombustible * gasto # La autonomía del auto se calcula multiplicando la cantidad de combustible por el gasto de km por litro.
    
class Motocicleta(Vehiculo):
    def __init__(self, marca, modelo, anio, combustible, tipo):
        super().__init__(marca, modelo, anio, combustible)
        self.tipo = tipo
    
    def encender(self):
        return f"La motocicleta {self.marca} {self.modelo} del año {self.anio} está encendida."
    
    def calcular_autonomia(self):
        gasto = 70 #km por litro
        return self.getCombustible * gasto # La autonomía de la motocicleta se calcula multiplicando la cantidad de combustible por el gasto de km por litro.
        

class Camion(Vehiculo):
    def __init__(self,marca,modelo, anio, combustible, carga):
        super(). __init__(marca, modelo, anio, combustible)
        self.carga = carga
        
    def encender(self):
        return f"El camión {self.marca} {self.modelo} del año {self.anio} está encendido."
    
    def calcular_autonomia(self):
        gasto = 10 #km x litro
        return self.getCombustible * gasto 


toyota=Auto("Toyota", "Corolla", 2020, 0, 4)
honda= Motocicleta("Honda", "CBR500R", 2021, 0, "Deportiva")
volvo=Camion("Volvo", "FH16", 2019, 0, 20000)

toyota.setCombustible= 55
honda.setCombustible= 20
volvo.setCombustible= 115

vehiculos = [toyota, honda, volvo];

for vehiculo in vehiculos:
    print("--------------------------------")
    print(f"MArca: {vehiculo.marca}")
    print(f"Modelo: {vehiculo.modelo}")
    print(f"Año: {vehiculo.anio}")
    print(f"Combustible: {vehiculo.getCombustible} litros")

    print(vehiculo.encender())
    rendimiento = vehiculo.calcular_autonomia()
    
    print(f"Rendimiento alcanzado: {rendimiento} km")
    