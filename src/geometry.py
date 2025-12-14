from __future__ import annotations
from dataclasses import dataclass, field
from math import cos, pi, sin, sqrt, atan
from typing import Literal, Sequence


basicallyZero = 0.000000001
mergeTolerance = 0.05

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

    def __hash__(self) -> int:
        return hash(self.x.__hash__() + self.y.__hash__())

    def offset(self, offset: Vector2D):
        self += offset

    def mirror(self, axis: Literal["x", "y"]):
        if axis == "x": self.x *= -1
        else: self.y *= -1

    def distanceTo(self, other: Vector2D) -> float:
        """Calculate euclidian distance"""
        diff = self - other
        return sqrt(diff.x ** 2 + diff.y ** 2)

    def dot(self, other: Vector2D) -> float:
        """ Calculate dot product"""
        return self.x * other.x + self.y * other.y

    def modulus(self) -> float:
        return sqrt(self.x ** 2 + self.y ** 2)

    def angle(self) -> float:
        if abs(self.x) < basicallyZero: return pi/2 if self.y > 0 else -pi/2
        angle = atan(self.y / self.x)
        return angle + pi if self.x < 0 else angle

@dataclass
class Intersection:
    point: Vector2D
    between: tuple[int, int]

    def __post_init__(self):
        if self.between[0] > self.between[1]:
            self.between = (self.between[1], self.between[0])
    def __hash__(self) -> int:
        return hash(self.point.__hash__() + self.between.__hash__())

@dataclass
class Line:
    start: Vector2D
    end: Vector2D

    def length(self) -> float:
        return self.start.distanceTo(self.end)

    def vector(self) -> Vector2D:
        return self.end - self.start

    def offset(self, offset: Vector2D):
        self.start += offset
        self.end += offset

    def mirror(self, axis: Literal["x", "y"]):
        if axis == "x":
            self.start.x *= -1
            self.end.x *= -1
        else:
            self.start.y *= -1
            self.end.y *= -1

    def projectToNormal(self, other: Line) -> tuple[float, float]:
        """
        Calculates the projection of the other line on the self's normal
        The function returns two distances being the projections
        The distances are relative to the projection line's vertex
        """
        projectionVector = self.vector()
        projectionVector /= self.length()
        projectionVector = Vector2D(projectionVector.y, -projectionVector.x)

        startDistance = (other.start - self.start).dot(projectionVector)
        endDistance = (other.end - self.start).dot(projectionVector)

        return startDistance, endDistance

    def intersects(self, other: Line) -> Vector2D | None:
        (ds1, de1) = self.projectToNormal(other)
        (ds2, de2) = other.projectToNormal(self)

        # Here both lines are on the same axis
        if  abs(ds1) < basicallyZero and\
            abs(de1) < basicallyZero and\
            abs(ds2) < basicallyZero and\
            abs(de2) < basicallyZero:

            ds1 = self.start.dot(other.start - self.start)
            de1 = self.start.dot(other.end - self.start)
            ds2 = self.end.dot(other.start - self.end)
            de2 = self.end.dot(other.end - self.end)

            if ds1 * de1 > 0 and ds2 * de2 > 0:
                return
            if ds1 * de1 > 0:
                return self.end
            else: 
                return self.start

        # For either projection
        # If the projection distances have different signs
        # This means that there is an intersection in ths projection
        # Both projections must intersect for a real intersection to be present
        if ds1 * de1 > 0 or ds2 * de2 > 0:
            return

        correctionFactor = sin(self.vector().angle() - other.vector().angle())
        # if abs(correctionFactor) < basicallyZero:
        #     return other.start
        return self.start + self.vector() / self.length() * ds2 / correctionFactor

@dataclass
class Polygon:
    points: list[Vector2D]
    edgeNormals: list[Vector2D] = field(default_factory=lambda: [])
    vertexNormals: list[Vector2D] = field(default_factory=lambda: []) 

    def offset(self, offset: Vector2D):
        for i in range(len(self.points)):
            self.points[i] += offset

    def mirror(self, axis: Literal["x", "y"]):
        if axis == "x":
            for p in self.points:
                p.x *= -1
        else:
            for p in self.points:
                p.y *= -1

    def calculate_normals(self):
        if not len(self.edgeNormals): self.edgeNormals = [Vector2D(0,0) for _ in self.points]
        if not len(self.vertexNormals): self.vertexNormals = [Vector2D(0,0) for _ in self.points]

        # Calculating Edge Normals
        for i in range(len(self.points)):
            p1, p2 = self.points[i-1], self.points[i]
            diff = p1 - p2                    # Take Difference
            diff /= diff.modulus()            # Normalize
            diff.x, diff.y = diff.y, -diff.x  # Rotate by 90deg
            self.edgeNormals[i-1] = diff

        # Calculating Vertex Normals
        for i in range(len(self.points)):
            p1, p2, p3 = self.points[i-2], self.points[i-1], self.points[i]
            v1 = p3 - p2
            v2 = p1 - p2
            a = (v1.angle() + v2.angle()) / 2
            n = Vector2D(cos(a), sin(a))
            if n.dot(self.edgeNormals[i-1]) < 0:
                n *= -1
            self.vertexNormals[i-1] = n

    def perimeter(self) -> float:
        perimeter = 0
        for i in range(len(self.points)):
            perimeter += self.points[i-1].distanceTo(self.points[i])
        return perimeter

    def removeSmallSegments(self) -> Polygon:
        newPolygon = Polygon([])

        for i in range(len(self.points)):
            if self.points[i-1].distanceTo(self.points[i]) > mergeTolerance:
                newPolygon.points.append(self.points[i])

        return newPolygon

    def breakAppart(self) -> list[Line]:
        return [
            Line(self.points[i-1], self.points[i])
            for i in range(len(self.points))
        ]

    def inflate(self, amount: float, attempts: int = 3) -> Polygon:
        self.calculate_normals()
        lines = self.breakAppart()
        oldPerimeter = self.perimeter()

        newLines = [
            Line(
                line.start + self.edgeNormals[i-1] * amount,
                line.end   + self.edgeNormals[i-1] * amount,
            ) for i, line in enumerate(lines)
        ]

        index = 0
        while index < len(newLines):
            p1 = newLines[index - 1].end
            p2 = newLines[index].start
            if p1.distanceTo(p2) < mergeTolerance:
                mid = (p1 + p2) / 2
                newLines[index - 1].end = mid
                newLines[index].start = mid
            else:
                newLines.insert(index, Line(p1, p2))
            index += 1

        intersections = list(sweepingLineIntersection(newLines))
        intersections.sort(key=lambda i: i.between[1], reverse=True)
        intersections.sort(key=lambda i: i.between[0])

        # import graphics
        # graphics.plotLinesRainbow(newLines)

        minimumIndex = 0
        severedLines = []
        for i in intersections:
            # graphics.ax.scatter(i.point.x, i.point.y, color="yellow")

            if i.between[0] < minimumIndex: continue

            newLines[i.between[0]].end = i.point
            newLines[i.between[1]].start = i.point
            minimumIndex = i.between[1]
            severedLines += newLines[i.between[0] + 1 : i.between[1]]

        for severee in severedLines:
            newLines.remove(severee)

        newPolygon = Polygon([line.start for line in newLines]).removeSmallSegments()

        # If the new inflated polygon is far smaller than the previous one
        # because most of it was culled and only "inside an interception" was kept
        # try again but with the starting point shifted a little
        if attempts and newPolygon.perimeter() < oldPerimeter * 0.7:
            self.points = self.points[2:] + self.points[:2]
            return self.inflate(amount, attempts-1)

        return newPolygon

@dataclass
class GeometrySettigs:
    inflate: float | None
    mirror_x: bool
    mirror_y: bool
    offset_x: float | None
    offset_y: float | None
    tolerance: float

Geometry =  Polygon | Line | Vector2D


def transformGeometries(geometries: Sequence[Geometry], settings: GeometrySettigs) -> Sequence[Geometry]: 
    newGeometries = [g for g in geometries]

    if settings.inflate is not None:
        newGeometries = [
            g.inflate(settings.inflate)
            for g in newGeometries if isinstance(g, Polygon)
        ] + [
            g for g in newGeometries if not isinstance(g, Polygon)
        ]

    if settings.mirror_x:
        for g in newGeometries:
            g.mirror("x")

    if settings.mirror_y:
        for g in newGeometries:
            g.mirror("y")

    if settings.offset_x or settings.offset_y:
        for g in newGeometries:
            offset = Vector2D(
                settings.offset_x or 0,
                settings.offset_y or 0
            )
            g.offset(offset)

    return newGeometries

def sweepingLineIntersection(lines: Sequence[Line]) -> set[Intersection]:
    @dataclass
    class SweepingLineIntersectionStruct:
        line: Line
        index: int

    sortedLines: list[SweepingLineIntersectionStruct] = []
    for i, line in enumerate(lines):
        if line.start.x < line.end.x:
            sortedLines.append(SweepingLineIntersectionStruct(Line(line.start, line.end), i))
        else:
            sortedLines.append(SweepingLineIntersectionStruct(Line(line.end, line.start), i))
    sortedLines.sort(key=lambda sl: sl.line.start.x)

    intersections: set[Intersection] = set()
    evaluationBucket:list [SweepingLineIntersectionStruct] = []
    for sl in sortedLines:
        elementsToRemove = [e for e in evaluationBucket if e.line.end.x + mergeTolerance < sl.line.start.x]
        for e in elementsToRemove: evaluationBucket.remove(e)

        evaluationBucket.append(sl)
        for i in range(len(evaluationBucket) - 1):
            evaluee1 = evaluationBucket[i]
            for evaluee2 in evaluationBucket[i+1:]:
                intersection = evaluee1.line.intersects(evaluee2.line)
                if intersection is None: continue
                if intersection.distanceTo(evaluee1.line.start) < basicallyZero: continue
                if intersection.distanceTo(evaluee1.line.end) < basicallyZero: continue
                if intersection.distanceTo(evaluee2.line.start) < basicallyZero: continue
                if intersection.distanceTo(evaluee2.line.end) < basicallyZero: continue
                intersections.add(Intersection(intersection, (evaluee1.index, evaluee2.index)))

    return intersections

