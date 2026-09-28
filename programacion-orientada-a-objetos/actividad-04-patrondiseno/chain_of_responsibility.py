from abc import ABC, abstractmethod

#Handler
class Idispensador(ABC):
    
    @abstractmethod
    def establacerSiguiente(self, dispensador):
        pass
    @abstractmethod
    def dispensar(self, solicitud):
        pass
#BaseHandler
class Dispensador(Idispensador):
    def __init__(self):
        self.siguiente = None

    def establacerSiguiente(self, dispensador):
        self.siguiente = dispensador

    def dispensar(self, solicitud):
        if self.siguiente:
            return self.siguiente.dispensar(solicitud)
        return None
#ConcreteHandlers
class Dispensador200(Dispensador):
    def dispensar(self, solicitud):
       
        cantidad = solicitud // 200
        restante = solicitud % 200
        print(f"Dispensando {cantidad} billetes de 200")
        if restante > 0:
            return super().dispensar(restante)
        
      
class Dispensador100(Dispensador):
    def dispensar(self, solicitud):
        
        if solicitud >= 100:
          
            cantidad = solicitud // 100
            restante = solicitud % 100
            print(f"Dispensando {cantidad} billetes de 100")
            if restante > 0:
                return super().dispensar(restante)
            return
        return super().dispensar(solicitud)
class Dispensador50(Dispensador):
    def dispensar(self, solicitud):
        if solicitud >= 50:
            cantidad = solicitud // 50
            restante = solicitud % 50
            print(f"Dispensando {cantidad} billetes de 50")
            if restante > 0:
                return super().dispensar(restante)
            return
        return super().dispensar(solicitud)
class Dispensador20(Dispensador):
    def dispensar(self, solicitud):
        if solicitud >= 20:
            cantidad = solicitud // 20
            restante = solicitud % 20
            print(f"Dispensando {cantidad} billetes de 20")
            if restante > 0:
                return super().dispensar(restante)
            return
        return super().dispensar(solicitud)
        
    
#Cliente
class CajeroAutomatico:
    def __init__(self):
        self.dispensador200 = Dispensador200()
        self.dispensador100 = Dispensador100()
        self.dispensador50 = Dispensador50()
        self.dispensador20 = Dispensador20()

        self.dispensador200.establacerSiguiente(self.dispensador100)
        self.dispensador100.establacerSiguiente(self.dispensador50)
        self.dispensador50.establacerSiguiente(self.dispensador20)

    def dispensar(self, solicitud):
        print(f"Solicitud de {solicitud} recibida.")
        self.dispensador200.dispensar(solicitud)
        
        
if __name__ == "__main__":
    cajero = CajeroAutomatico()
    cajero.dispensar(370)
    print("\n")
    # cajero.dispensar(90)
    # print("\n")
    # cajero.dispensar(15)