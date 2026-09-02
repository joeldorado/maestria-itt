#Acticidad 2: POO
#Aurhor: Joel Dorado Aguilus
from abc import ABC, abstractmethod

#Clase abstracta Animal que está destinada a ser la clase base para 
# todas las clases de animales. Define los atributos y métodos comunes que todos los animales deben tener.
class Animal(ABC):
# constructor que inicializa los atributos de la clase Animal.
    def __init__(self, name, dob, type, gender, type_of_diet,food):
        self.name = name
        self.dob = dob
        self.type = type
        self.gender = gender
        self.type_of_diet = type_of_diet
        self.food = food
#metodo abstracto que debe ser implementado por todas las subclases de Animal.
    @abstractmethod
    def sound(self):
        pass
    
#metodo publico que devuelve una cadena que indica que el animal está comiendo su comida favorita.
    def eat(self):
        return f"{self.name} is eating {self.food}."
    
#clase Bird que hereda de la clase Animal y representa a un ave. Define atributos y métodos específicos para aves, como la velocidad de vuelo, la altitud máxima y si puede volar o no.
class Bird(Animal):
    def __init__(self, name, dob, type, gender, type_of_diet,food, fly_speed, max_altitude, it_fly):
        super().__init__(name, dob, type, gender, type_of_diet,food)
        self.fly_speed = fly_speed
        self.max_altitude = max_altitude
        self.it_fly = it_fly
#aqui usamos el metodo abstracto sound que debe ser implementado por todas las subclases de Animal.
    def sound(self, sound ):
        return f"The {self.type} makes a sound: {sound} and it is named {self.name}."
#aqui usamos el metodo eat que debe ser implementado por todas las subclases de Animal. 
# que devuelve una cadena que indica que el ave está comiendo su comida favorita.
    def eat(self):
        pass
#metodo propio de la clase Bird que devuelve una cadena que indica si el ave puede volar o no, y si puede volar, también indica su velocidad de vuelo y su altitud máxima.
    def fly(self):
        if self.it_fly:
            return f"{self.name} can fly at a speed of {self.fly_speed} km/h and reach a maximum altitude of {self.max_altitude} meters."
        else:
            return f"{self.name} cannot fly."
        
#clase Feline que hereda de la clase Animal y representa a un felino. Define atributos y métodos específicos para felinos, como el número de garras, la velocidad y si cazan en manadas o no.
class Feline(Animal):
    def __init__(self, name, dob, type, gender, type_of_diet,food, number_of_claws, speed, hunts_in_packs):
        super().__init__(name, dob, type, gender, type_of_diet,food)
        self.number_of_claws = number_of_claws
        self.speed = speed
        self.hunts_in_packs = hunts_in_packs

    def sound(self, sound):
        return f"The {self.type} makes a sound: {sound} and it is named {self.name}."

    def eat(self):
        pass

    def hunt(self):
        if self.hunts_in_packs:
            return f"{self.name} hunts in packs."
        else:
            return f"{self.name} hunts alone."
class Marine(Animal):
    def __init__(self, name, dob, type, gender, type_of_diet,food, swim_speed    , max_depth, it_swim):
        super().__init__(name, dob, type, gender, type_of_diet,food)
        self.swim_speed = swim_speed    
        self.max_depth = max_depth
        self.it_swim = it_swim

    def sound(self, sound):
        return f"The {self.type} makes a sound: {sound} and it is named {self.name}."

    def eat(self):
        pass

    def swim(self):
        if self.it_swim:
            return f"{self.name} can swim at a speed of {self.swim_speed} km/h and reach a maximum depth of {self.max_depth} meters."
        else:
            return f"{self.name} cannot swim."
#instancia de la clase Feline que representa a un león. Se le pasan los valores de los atributos al constructor de la clase Feline.
leon = Feline("Leo", "2018-05-10", "Leon", "Male", "Carnivore", "Meat", 18, 60, True)
#aqui usamos el metodo sound que debe ser implementado por todas las subclases de Animal.
print("1) ",leon.sound("Roar"))
#aqui usamos el metodo hunt que devuelve una cadena que indica si
print(leon.hunt())  
# aqui usamos el metodo eat que devuelve una cadena que indica que el león está comiendo su comida favorita.
print(leon.eat(),"\n\n")

#De esta manera se crean instancias de las clases Feline, Marine y Bird, 
# y se llaman a sus métodos para mostrar información sobre los animales y sus comportamientos.


cat = Feline("Whiskers", "2020-03-15", "Cat", "Female", "Carnivore", "Fish", 18, 30, False)
print("2) ", cat.sound("Meow"))
print(cat.hunt())   
print(cat.eat(),"\n\n")

shark = Marine("Shark", "2019-08-20", "Shark", "Male", "Carnivore","Meat" ,40, 100, True)

print("3) ",shark.sound("Splash"))
print(shark.swim())
print(shark.eat(),"\n\n")

tourtle = Marine("Turtle", "2015-06-12", "Turtle", "Female", "Herbivore", "Seaweed",   5, 20, False)
print("4) ",tourtle.sound("Splash"))
print(tourtle.swim())
print(tourtle.eat(),"\n\n")



eagle = Bird("Eagle", "2017-09-05", "Eagle", "Male", "Carnivore", "Fish", 160, 3000, True)
print("5) ",   eagle.sound("Screech"))
print(eagle.fly())     
print(eagle.eat(),"\n\n")

parrot = Bird("Parrot", "2021-02-18", "Parrot", "Female", "Herbivore","Seeds" ,24, 1000, False)
print("6) ",   parrot.sound("Squawk"))
print(parrot.fly())
print(parrot.eat(),"\n\n")




