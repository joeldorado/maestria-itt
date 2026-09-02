from abc import ABC, abstractmethod
#Acticidad 2: POO

class Animal(ABC):
    def __init__(self, name, dob, type, gender, type_of_diet,food):
        self.name = name
        self.dob = dob
        self.type = type
        self.gender = gender
        self.type_of_diet = type_of_diet
        self.food = food
    @abstractmethod
    def sound(self):
        pass
    
    
    def eat(self):
        return f"{self.name} is eating {self.food}."
    
class bird(Animal):
    def __init__(self, name, dob, type, gender, type_of_diet,food, fly_speed, max_altitude, it_fly):
        super().__init__(name, dob, type, gender, type_of_diet,food)
        self.fly_speed = fly_speed
        self.max_altitude = max_altitude
        self.it_fly = it_fly
    
    def sound(self, sound ):
        return f"The {self.type} makes a sound: {sound} and it is named {self.name}."

    def eat(self):
        pass
    
    def fly(self):
        if self.it_fly:
            return f"{self.name} can fly at a speed of {self.fly_speed} km/h and reach a maximum altitude of {self.max_altitude} meters."
        else:
            return f"{self.name} cannot fly."
class feline(Animal):
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
class marine(Animal):
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
        
leon = feline("Leo", "2018-05-10", "Leon", "Male", "Carnivore", "Meat", 18, 60, True)
print("1) ",leon.sound("Roar"))
print(leon.hunt())  
print(leon.eat(),"\n\n")

cat = feline("Whiskers", "2020-03-15", "Cat", "Female", "Carnivore", "Fish", 18, 30, False)
print("2) ", cat.sound("Meow"))
print(cat.hunt())   
print(cat.eat(),"\n\n")

shark = marine("Shark", "2019-08-20", "Shark", "Male", "Carnivore","Meat" ,40, 100, True)

print("3) ",shark.sound("Splash"))
print(shark.swim())
print(shark.eat(),"\n\n")

tourtle = marine("Turtle", "2015-06-12", "Turtle", "Female", "Herbivore", "Seaweed",   5, 20, False)
print("4) ",tourtle.sound("Splash"))
print(tourtle.swim())
print(tourtle.eat(),"\n\n")



eagle = bird("Eagle", "2017-09-05", "Eagle", "Male", "Carnivore", "Fish", 160, 3000, True)
print("5) ",   eagle.sound("Screech"))
print(eagle.fly())     
print(eagle.eat(),"\n\n")

parrot = bird("Parrot", "2021-02-18", "Parrot", "Female", "Herbivore","Seeds" ,24, 1000, False)
print("6) ",   parrot.sound("Squawk"))
print(parrot.fly())
print(parrot.eat(),"\n\n")




