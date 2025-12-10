from __future__ import annotations
from dataclasses import dataclass
from math import sqrt

@dataclass
class Point:
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

    # Calculate euclidian distance
    def __sub__(self, other: Point) -> float:
        xdiff = self.x - other.x
        ydiff = self.y - other.y
        return sqrt(xdiff ** 2 + ydiff ** 2)


@dataclass
class Line:
    start: Point
    end: Point
    normal: Point | None = None

    def __getitem__(self, key):
        if not isinstance(key, int): raise Exception("An integer should be used to index in a Point")
        if key > 1: raise Exception("Index out of range")

        if key: return self.start
        return self.end

    def __setitem__(self, key, value):
        if not isinstance(key, int): raise Exception("An integer should be used to index in a Point")
        if key > 1: raise Exception("Index out of range")
        if not isinstance(value, Point): raise Exception("Value assigned to Point should be a float")

        if key: self.y = value
        self.x = value

@dataclass
class Polygon:
    points: list[Point]

@dataclass
class Circle:
    center: Point
    radius: float


def polygonize(lines: list[Line]) -> list[Polygon]:
    polygons = [Polygon([lines[0].start])]
    previousLine = lines[0]

    for line in lines[1:]:
        if line.start - previousLine.end < 0.001:
            polygons[-1].points.append(line.start)
        else:
            polygons.append(Polygon([line.start]))
        previousLine = line

    return polygons
