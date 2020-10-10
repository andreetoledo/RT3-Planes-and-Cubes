#Andreé Toledo 18439
#DR3 Gráficas

from raytracing import Raytracer
from raytracing import Material
from raytracing import Light
from raytracing import Sphere
from raytracing import Color
from raytracing import V3

# Colors & Materials
WHITE = Color(248, 248, 248)
GRAY = Color(200, 200, 200)
BLACK = Color(0, 0, 0)
GREEN = Color(154, 255, 52)
RED = Color(255, 52, 52)
BROWN = Color(200, 94, 38)
LIGHT_BROWN = Color(245, 180, 150)

earth = Material(diffuse=BROWN, albedo=(0.92, 0.92, 0.1, 0), spec=30)
sand = Material(diffuse=LIGHT_BROWN, albedo=(0.92, 0.82, 0.1, 0), spec=30)
black = Material(diffuse=BLACK, albedo=(0.64, 0.36, 0.1, 0), spec=5)
green = Material(diffuse=GREEN, albedo=(0.64, 0.36, 0.1, 0), spec=15)
red = Material(diffuse=RED, albedo=(0.64, 0.36, 0.1, 0), spec=15)
metal = Material(diffuse=GRAY, albedo=(1, 1, 0.1, 0), spec=30)
snow = Material(diffuse=WHITE, albedo=(0.86, 0.86, 0.1, 0), spec=30)


# Render
render = Raytracer(1280, 720)
render.light = Light(position=V3(0, 20, 40), intensity=1.5)
render.background_color = BLACK
render.scene = [

    # Cuerpo
    #Sphere(V3(0, 1.8, -6), 0.76, nieve),
    Sphere(V3(0, 0.4, -6), 0.94, snow),
    Sphere(V3(0, -1.74, -8), 1.8, snow),

    # Cabeza
    Sphere(V3(0.24, 2.08, -6), 0.06, black),
    Sphere(V3(-0.24, 2.08, -6), 0.06, black),
    Sphere(V3(0.24, 2.08, -6), 0.14, metal),
    Sphere(V3(-0.24, 2.08, -6), 0.14, metal), 
    Sphere(V3(0, 1.82, -6), 0.16, red),
    Sphere(V3(-0.3, 1.62, -6), 0.06, black),
    Sphere(V3(-0.14, 1.48, -6), 0.06, black),
    Sphere(V3(0.14, 1.48, -6), 0.06, black),
    Sphere(V3(0.3, 1.62, -6), 0.06, black),
   
    # Complementos de Cuerpo

    Sphere(V3(0, 0.9, -6), 0.08, black),
    Sphere(V3(0, 0.2, -6), 0.16, black),
    Sphere(V3(0, -1.42, -6), 0.24, black),
]

render.render_stereogram()
render.finish()