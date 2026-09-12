from abc import ABC, abstractmethod
#clase Abstracta
class Producto(ABC):
    #constructor
    def __init__(self, precioventa, costofabirca, nombreproducto):
        self.precioventa = precioventa
        self.costofabirca = costofabirca
        self.nombreproducto = nombreproducto
    
    @abstractmethod
    def imprimirDatos(self):
        pass


class Libro(Producto):
    def __init__(self, precioventa, costofabrica, nombreproducto):
        super().__init__(precioventa, costofabrica, nombreproducto)
        
    def imprimirDatos(self):
        return f"El libro {self.nombreproducto} tiene un precio de venta de ${self.precioventa} MXN y un costo de fabrica de ${self.costofabirca} MXN."
class Dvd(Producto):
    def __init__(self, precioventa, costofabrica, nombreproducto):
        super().__init__(precioventa, costofabrica, nombreproducto)
        
    def imprimirDatos(self):
        return f"El DVD {self.nombreproducto} tiene un precio de venta de ${self.precioventa} MXN y un costo de fabrica de ${self.costofabirca} MXN."

# el metodo Main en Phyton vive fuera de la clase, es el punto de entrada del programa. Se utiliza 
# para ejecutar el código principal del programa y se llama automáticamente cuando se ejecuta el archivo.
def main():
    libro = Libro(200, 100, "El Principito")
    dvd = Dvd(300, 150, "Inception")
    print(libro.imprimirDatos())
    print(dvd.imprimirDatos())
    
# Para generar el Main que se usa en C# en phyton usamos la variable especial __name__
# cuando ejecuta uno el archivo .py, la variable __name__  regresa "__main__" y si se 
# importa el archivo .py, la variable __name__ regresa el nombre del archivo .py
if __name__ == "__main__":
    main()