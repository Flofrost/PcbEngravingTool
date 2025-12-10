from __future__ import annotations
from dataclasses import dataclass, field
from math import sqrt

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

    # Calculate euclidian distance
    def distanceTo(self, other: Vector2D) -> float:
        diff = self - other
        return sqrt(diff.x ** 2 + diff.y ** 2)

    def modulus(self):
        return sqrt(self.x ** 2 + self.y ** 2)

    def scale(self, scalar: float):
        self.x *= scalar
        self.y *= scalar


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

        for i in range(len(self.points)):
            p1, p2 = self.points[i-1], self.points[i]
            diff = p1 - p2
            mod = diff.modulus()
            diff.scale(1/mod)
            diff.scale(1/100)
            diff.x, diff.y = diff.y, -diff.x
            avg = p1 + p2
            avg.scale(1/2)
            self.edgeNormals[i] = diff + avg



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
