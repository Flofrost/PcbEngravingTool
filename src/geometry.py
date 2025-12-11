from __future__ import annotations
from dataclasses import dataclass, field
from math import cos, pi, sin, sqrt, atan

@dataclass
class Vector2D:
    x: float
    y: float

    def __getitem__(self, key):
        if not isinstance(key, int): raise Exception("An integer should be used to index in a Point")
        if key > 1: raise Exception("Index out of range")

        if key: return self.y
        return self.x

    def __setitem__(self, key, value):
        if not isinstance(key, int): raise Exception("An integer should be used to index in a Point")
        if key > 1: raise Exception("Index out of range")
        if not isinstance(value, float): raise Exception("Value assigned to Point should be a float")

        if key: self.y = value
        self.x = value

    def __add__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, other: float) -> Vector2D:
        return Vector2D(self.x * other, self.y * other)

    def __truediv__(self, other: float) -> Vector2D:
        return Vector2D(self.x / other, self.y / other)

    # Calculate euclidian distance
    def distanceTo(self, other: Vector2D) -> float:
        diff = self - other
        return sqrt(diff.x ** 2 + diff.y ** 2)

    def modulus(self) -> float:
        return sqrt(self.x ** 2 + self.y ** 2)

    def angle(self) -> float:
        if abs(self.x) < 0.00000000000001: return 0
        angle = atan(self.y / self.x)
        return angle + pi if self.x < 0 else angle


@dataclass
class Line:
    start: Vector2D
    end: Vector2D

    def __getitem__(self, key):
        if not isinstance(key, int): raise Exception("An integer should be used to index in a Point")
        if key > 1: raise Exception("Index out of range")

        if key: return self.start
        return self.end

    def __setitem__(self, key, value):
        if not isinstance(key, int): raise Exception("An integer should be used to index in a Point")
        if key > 1: raise Exception("Index out of range")
        if not isinstance(value, Vector2D): raise Exception("Value assigned to Point should be a float")

        if key: self.y = value
        self.x = value

@dataclass
class Polygon:
    points: list[Vector2D]
    edgeNormals: list[Vector2D] = field(default_factory=lambda: [])
    vertexNormals: list[Vector2D] = field(default_factory=lambda: []) 

    def calculate_normals(self):
        if not len(self.edgeNormals): self.edgeNormals = [Vector2D(0,0) for _ in self.points]
        if not len(self.vertexNormals): self.vertexNormals = [Vector2D(0,0) for _ in self.points]

        # Calculating Edge Normals
        for i in range(len(self.points)):
            p1, p2 = self.points[i-1], self.points[i]
            diff = p1 - p2                    # Take Difference
            diff /= diff.modulus()            # Normalize
            diff.x, diff.y = diff.y, -diff.x  # Rotate by 90deg
            self.edgeNormals[i] = diff

        # Calculating Vertex Normals
        for i in range(len(self.points)):
            p1, p2 = self.edgeNormals[i-1], self.edgeNormals[i]
            self.vertexNormals[i-1] = (p1 + p2) / 2



@dataclass
class Circle:
    center: Vector2D
    radius: float


def polygonize(lines: list[Line]) -> list[Polygon]:
    polygons = [Polygon([lines[0].start])]
    previousLine = lines[0]

    for line in lines[1:]:
        if line.start.distanceTo(previousLine.end) < 0.001:
            polygons[-1].points.append(line.start)
        else:
            polygons.append(Polygon([line.start]))
        previousLine = line

    return polygons

def inflate(polygon: Polygon, amount_mm: float) -> Polygon:
    if not len(polygon.vertexNormals): raise Exception("Polygon's normals have not been calculated")

    return Polygon([
        point + normal * amount_mm
        for point, normal in zip(polygon.points, polygon.vertexNormals)
    ])
    
