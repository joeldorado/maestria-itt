from abc import ABC,abstractmethod

#Interface contetable
class Iconectable(ABC):

 	@abstractmethod
 	def Conectar(self):
 	  pass

 	@abstractmethod
 	def Desconectar(self):
	  pass
#Interface Almacenamiento
class IAlmacenamiento(ABC):
	@abstractmethod
	def Guardar(datos):
	  pass

	@abstractmethod
	def LeerTodo(self):
	  pass

class MemoriaUSB(Iconectable, IAlmacenamiento):
	def __init__(self):
	  self.data =[]

	#Implementndo interface Conectable
	def Conectar(self):
	  print("Conectado")

	def Desconectar(self):
	  print("Desconectado.")

	def Guardar(self, datos):
	  print("Guardando datos...")
	  self.data = datos
	  print("Datos guardados")
	
	def LeerTodo(self):
	  print("Leyendo datos")
	  for dato in self.data:
	    print("-----------")
	    print(f"Nombre: {dato.name} Tipo: {dato.type} Tamano: {dato.size}.")
	    print("------------")


class Dato:
	def __init__(self,name, type, size):
	  self.name =name
	  self.type = type
	  self.size = size


class Nube():
	def __init__(self):
	  self.data = []
	  self.loggedIn = False,
	  self.user =""
	
	def Login(self, username, password)->boolean:
	  user= 'joeldorado'
	  password = 12345
	  if user == username and password == password:
	    self.loggedIn = True
	    self.user = username
	    print(f"bienvenido!! {user}")
	    return True
	  else:
	    print("Credenciales incorrectas!!!")
            
	  return False

	def Conectar(self):
	  if self.loggedIn == True:
	    print("Conectado al drive A...")
	  else:
	    print("Porfavor Inicia sesion.")
	
	def Desconectar(self):
	  print("Descnectado del drive A")
	def Guardar(self, datos):
	  print("Preparando para guardar...")
	  self.data = datos
	  print("Datos guardados en drive A")
	def LeerTodo(self):
	  print("----{self.user} Tus datos del drive A son:-----")
	  for dato in self.data:
	    print(f"Nombre: {dato.name} Tipo: {dato.type} Tamano: {dato.size}")
	
	  	 

def main():
  print("Opciones de guardado:")
  print("1. USB")
  print("2. Nube") 
  tipoGuardado = input("Ingrea 1 para  elegir USB o 2 para Nube: ")
  datos = [
	  Dato("Poo 101", "PDF", "100mb"),
	  Dato("Interfaces", "VIdeo", "500mb"),
	  Dato("Tareas","Documento", "300mb")
	  ]
  if tipoGuardado == "1": 
    usb = MemoriaUSB()
    usb.Conectar()
    usb.Guardar(datos)
    usb.LeerTodo()
    usb.Desconectar()
  elif tipoGuardado == "2":
    nube = Nube()
    nube.Conectar()
    user = input("Ingresa tu Usuario: ")
    password = input("Ingresa tu password: ")
    logedIn = nube.Login(user, password)
    if logedIn == True:
      nube.Conectar()
      nube.Guardar(datos)
      nube.LeerTodo()
      nube.Desconectar
      logout = input("Quieres Cerrar Sesion? yes/no: ")
      if logout =="yes":
        print("Has cerrado sesion correctamente!!!") 
      elif logout =="no":
        print(f"Ok {user}")
      else:
        print("valor incorrecto")
  else:
    print("Valores incorrectos!!")


if __name__ == "__main__":
	main()	
		
