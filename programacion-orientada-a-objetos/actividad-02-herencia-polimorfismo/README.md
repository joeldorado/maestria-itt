# Actividad #2. POO con Herencia y polimorfismo

Modelado de una jerarquía de animales usando clases abstractas, herencia y polimorfismo en Python.

## Diseño

- `Animal` es una clase abstracta (`ABC`) con los atributos comunes: nombre, fecha de nacimiento, tipo, género, tipo de dieta y alimento.
  Declara el método abstracto `sound()` y un método concreto `eat()`.
- `Bird`, `Feline` y `Marine` heredan de `Animal`, agregan atributos propios y sobrescriben `sound()` y `eat()` (polimorfismo).
- Cada subclase agrega un comportamiento específico: `fly()`, `hunt()` y `swim()`.

```
Animal (abstracta)
├── Bird    -> fly()
├── Feline  -> hunt()
└── Marine  -> swim()
```

## Ejecución

```bash
python3 clases_y_objetos.py
```

El programa crea seis instancias (león, gato, tiburón, tortuga, águila y perico) y muestra el sonido, el comportamiento propio y la alimentación de cada una.

## Salida esperada

```
1)  The Leon makes a sound: Roar and it is named Leo.
Leo hunts in packs.
None

2)  The Cat makes a sound: Meow and it is named Whiskers.
Whiskers hunts alone.
None

3)  The Shark makes a sound: Splash and it is named Shark.
Shark can swim at a speed of 40 km/h and reach a maximum depth of 100 meters.
None

4)  The Turtle makes a sound: Splash and it is named Turtle.
Turtle cannot swim.
None

5)  The Eagle makes a sound: Screech and it is named Eagle.
Eagle can fly at a speed of 160 km/h and reach a maximum altitude of 3000 meters.
None

6)  The Parrot makes a sound: Squawk and it is named Parrot.
Parrot cannot fly.
None
```
