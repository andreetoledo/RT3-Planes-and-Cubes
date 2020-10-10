#Andreé Toledo 18439
#DR3 Gráficas

from collections import namedtuple
import struct
from math import tan
from math import pi

V2 = namedtuple("Vertex2", ["x", "y"])
V3 = namedtuple("Vertex3", ["x", "y", "z"])


def sum(v0, v1):
    return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)


def sub(v0, v1):
    return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)


def mul(v0, k):
    return V3(v0.x * k, v0.y * k, v0.z * k)


def dot(v0, v1):
    return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z


def length(v0):
    return (v0.x ** 2 + v0.y ** 2 + v0.z ** 2) ** 0.5


def norm(v0):
    v0length = length(v0)

    if not v0length:
        return V3(0, 0, 0)

    return V3(v0.x / v0length, v0.y / v0length, v0.z / v0length)


def bbox(*vertices):
    xs = [vertex.x for vertex in vertices]
    ys = [vertex.y for vertex in vertices]

    xs.sort()
    ys.sort()

    xmin = xs[0]
    xmax = xs[-1]
    ymin = ys[0]
    ymax = ys[-1]

    return xmin, xmax, ymin, ymax


def cross(v1, v2):
    return V3(
        v1.y * v2.z - v1.z * v2.y, v1.z * v2.x - v1.x * v2.z, v1.x * v2.y - v1.y * v2.x,
    )


def barycentric(A, B, C, P):
    cx, cy, cz = cross(
        V3(B.x - A.x, C.x - A.x, A.x - P.x), V3(B.y - A.y, C.y - A.y, A.y - P.y),
    )

    if abs(cz) < 1:
        return -1, -1, -1

    u = cx / cz
    v = cy / cz
    w = 1 - (cx + cy) / cz

    return w, v, u


def reflect(I, N):
    Lm = mul(I, -1)
    n = mul(N, 2 * dot(Lm, N))
    return norm(sub(Lm, n))
#Lay de Snell implementada
def refract(I, N, refractive_index):  
    cosi = -max(-1, min(1, dot(I, N)))
    etai = 1
    etat = refractive_index
# Se corrige el resultado si se encuentra adentro del objeto
    if cosi < 0:  
        cosi = -cosi
        etai, etat = etat, etai
        N = mul(N, -1)

    eta = etai/etat
    k = 1 - eta**2 * (1 - cosi**2)
    if k < 0:
        return V3(1, 0, 0)

    return norm(sum(
        mul(I, eta),
        mul(N, (eta * cosi - k**(1/2)))
    ))



def char(c):
    return struct.pack("=c", c.encode("ascii"))


def word(w):
    return struct.pack("=h", w)


def dword(d):
    return struct.pack("=l", d)


class Color(object):
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __add__(self, offset_color):
        r = self.r + offset_color.r
        g = self.g + offset_color.g
        b = self.b + offset_color.b

        return Color(r, g, b)

    def __mul__(self, other):
        r = self.r * other
        g = self.g * other
        b = self.b * other
        return Color(r, g, b)

    def __truediv__(self, other):
        r = self.r / other
        g = self.g / other
        b = self.b / other
        return Color(r, g, b)
    
    def __eq__(self, other):
        if other is None or not isinstance(other, Color):
            return False

        return (self.r, self.g, self.b) == (other.r, other.r, other.r)

    def toBytes(self):
        self.r = int(max(min(self.r, 255), 0))
        self.g = int(max(min(self.g, 255), 0))
        self.b = int(max(min(self.b, 255), 0))
        return bytes([self.b, self.g, self.r])


    __rmul__ = __mul__
    __rtruediv__ = __truediv__


def writebmp(filename, width, height, pixels):
    f = open(filename, "bw")

    # File header (14 bytes)
    f.write(char("B"))
    f.write(char("M"))
    f.write(dword(14 + 40 + width * height * 3))
    f.write(dword(0))
    f.write(dword(14 + 40))

    # Image header (40 bytes)
    f.write(dword(40))
    f.write(dword(width))
    f.write(dword(height))
    f.write(word(1))
    f.write(word(24))
    f.write(dword(0))
    f.write(dword(width * height * 3))
    f.write(dword(0))
    f.write(dword(0))
    f.write(dword(0))
    f.write(dword(0))

    # Pixel data (width x height x 3 pixels)
    for x in range(height):
        for y in range(width):
            f.write(pixels[x][y].toBytes())
    f.close()


WHITE = Color(255, 255, 255)


class Light(object):
    def __init__(self, position=V3(0, 0, 0), intensity=1):
        self.position = position
        self.intensity = intensity


class Material(object):
    def __init__(self, diffuse=WHITE, albedo=(1, 0, 0, 0), spec=0, refractive_index=1):
        self.diffuse = diffuse
        self.albedo = albedo
        self.spec = spec
        self.refractive_index = refractive_index


class Intersect(object):
    def __init__(self, distance, point, normal):
        self.distance = distance
        self.point = point
        self.normal = normal

MAX_RECURSION_DEPTH = 3
GREY = Color(54, 69, 79)
BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
RED = Color(100, 0, 0)
BLUE = Color(0, 0, 100)

class Raytracer(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.background_color = GREY
        self.scene = []
        self.light = None
        self.clear()

    def clear(self):
        self.pixels = [
            [self.background_color for x in range(self.width)]
            for y in range(self.height)
        ]

    def write(self, filename):
        writebmp(filename, self.width, self.height, self.pixels)

    def finish(self, filename="output.bmp"):
        self.write(filename)

    def point(self, x, y, c=None):
        try:
            self.pixels[y][x] = c or self.current_color
        except:
            pass

    def cast_ray(self, orig, direction, recursion=0):
        material, intersect = self.scene_intersect(orig, direction)

        if (
            material is None or recursion >= MAX_RECURSION_DEPTH
        ):  
            return self.background_color

        offset_normal = mul(intersect.normal, 1.1)

        if material.albedo[2] > 0:
            reverse_direction = mul(direction, -1)
            reflect_dir = reflect(reverse_direction, intersect.normal)
            reflect_orig = (
                sub(intersect.point, offset_normal)
                if dot(reflect_dir, intersect.normal) < 0
                else sum(intersect.point, offset_normal)
            )
            reflect_color = self.cast_ray(reflect_orig, reflect_dir, recursion + 1)
        else:
            reflect_color = BLACK

        if material.albedo[3] > 0:
            refract_dir = refract(
                direction, intersect.normal, material.refractive_index
            )
            refract_orig = (
                sub(intersect.point, offset_normal)
                if dot(refract_dir, intersect.normal) < 0
                else sum(intersect.point, offset_normal)
            )
            refract_color = self.cast_ray(refract_orig, refract_dir, recursion + 1)
        else:
            refract_color = BLACK

        light_dir = norm(sub(self.light.position, intersect.point))
        light_distance = length(sub(self.light.position, intersect.point))

        shadow_orig = (
            sub(intersect.point, offset_normal)
            if dot(light_dir, intersect.normal) < 0
            else sum(intersect.point, offset_normal)
        )
        shadow_material, shadow_intersect = self.scene_intersect(shadow_orig, light_dir)
        shadow_intensity = 0

        if (
            shadow_material
            and length(sub(shadow_intersect.point, shadow_orig)) < light_distance
        ):
            shadow_intensity = 0.9

        intensity = (
            self.light.intensity
            * max(0, dot(light_dir, intersect.normal))
            * (1 - shadow_intensity)
        )

        reflection = reflect(light_dir, intersect.normal)
        specular_intensity = self.light.intensity * (
            max(0, -dot(reflection, direction)) ** material.spec
        )

        diffuse = material.diffuse * intensity * material.albedo[0]
        specular = WHITE * specular_intensity * material.albedo[1]
        reflection = reflect_color * material.albedo[2]
        refraction = refract_color * material.albedo[3]

        return diffuse + specular + reflection + refraction

    def scene_intersect(self, orig, direction):
        zbuffer = float("inf")

        material = None
        intersect = None

        for obj in self.scene:
            hit = obj.ray_intersect(orig, direction)
            if hit is not None:
                if hit.distance < zbuffer:
                    zbuffer = hit.distance
                    material = obj.material
                    intersect = hit

        return material, intersect

    def render_stereogram(self):
        print("Rendering...")
        fov = int(pi / 2)
        for y in range(self.height):
            for x in range(self.width):
                i = (
                    (2 * (x + 0.5) / self.width - 1)
                    * tan(fov / 2)
                    * self.width
                    / self.height
                )
                j = (2 * (y + 0.5) / self.height - 1) * tan(fov / 2)
                direction = norm(V3(i, j, -1))

                first_offset = self.cast_ray(V3(0.25, 0.5, 0), direction)
                first_camera = (first_offset / 2 + RED) if first_offset != self.background_color else first_offset

                second_offset = self.cast_ray(V3(-0.25, 0.5, 0), direction)
                second_camera = (second_offset / 2 + BLUE) if second_offset != self.background_color else second_offset

                camera_offset = first_camera + second_camera
                self.pixels[y][x] = camera_offset




class Sphere(object):
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material

    def ray_intersect(self, orig, direction):
        L = sub(self.center, orig)
        tca = dot(L, direction)
        l = length(L)
        d2 = l ** 2 - tca ** 2
        if d2 > self.radius ** 2:
            return None
        thc = (self.radius ** 2 - d2) ** 1 / 2
        t0 = tca - thc
        t1 = tca + thc
        if t0 < 0:
            t0 = t1
        if t0 < 0:
            return None

        hit = sum(orig, mul(direction, t0))
        normal = norm(sub(hit, self.center))

        return Intersect(distance=t0, point=hit, normal=normal)