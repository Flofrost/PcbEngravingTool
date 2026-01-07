from __future__ import annotations
from dataclasses import dataclass, field
from array import array
from math import cos, pi, sin, sqrt, atan
from typing import Literal, Sequence


nearZero = 1e-10
tolerance = 1e-4
def nearZero_tolerance(x: float) -> bool: return abs(x) < tolerance
def nearZero_precise(x: float) -> bool: return abs(x) < nearZero

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

    def __radd__(self, other) -> Vector2D:
        return self.__add__(other) if isinstance(other, Vector2D) else self

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

    def cross(self, other: Vector2D) -> float:
        """ Calculate cross product"""
        return self.x * other.y - self.y * other.x

    def modulus(self) -> float:
        return sqrt(self.x ** 2 + self.y ** 2)

    def angle(self) -> float:
        if nearZero_precise(self.x): return pi/2 if self.y > 0 else -pi/2
        angle = atan(self.y / self.x)
        return angle + pi if self.x < 0 else angle

@dataclass
class Vector2DWithIndex:
    point: Vector2D
    index: int

    def __hash__(self) -> int:
        return hash(self.point.__hash__() + self.index.__hash__())

@dataclass
class Line:
    start: Vector2D
    end: Vector2D

    def __hash__(self) -> int:
        return hash(hash(self.start) + hash(self.end))

    def lerp(self, distance: float) -> LerpLine:
        return LerpLine(self, distance)

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

    def pointOnLine(self, point: Vector2D) -> bool:
        projectionVector = self.vector()
        projectionVector /= self.length()
        projectionVector = Vector2D(projectionVector.y, -projectionVector.x)
        return nearZero_precise(abs((point - self.start).dot(projectionVector)))

    def intersects(self, other: Line, rejectIntersectionsEnds: bool = False) -> Vector2D | None:
        selfVect = self.vector()
        otherVect = other.vector()

        derterminent = selfVect.cross(otherVect)
        if nearZero_precise(derterminent):
            if self.pointOnLine(other.start): return other.start
            if self.pointOnLine(other.end): return other.end
            if other.pointOnLine(self.start): return self.start
            if other.pointOnLine(self.end): return self.end
            return

        coefficientVector = Vector2D(
            (other.start - self.start).cross(selfVect) / derterminent,
            (other.start - self.start).cross(otherVect) / derterminent
        )

        if not (
            0 - nearZero < coefficientVector.x < 1 + nearZero and\
            0 - nearZero < coefficientVector.y < 1 + nearZero
        ): return

        intersection = self.start + selfVect * coefficientVector.y

        if rejectIntersectionsEnds:
            if nearZero_tolerance(intersection.distanceTo(self.start)): return
            if nearZero_tolerance(intersection.distanceTo(self.end)): return
            if nearZero_tolerance(intersection.distanceTo(other.start)): return
            if nearZero_tolerance(intersection.distanceTo(other.end)): return

        return intersection

    def trim(self, trimPoint: Vector2D, compareAgainst: list[Line], referencePoint: Vector2D):
        intersections = [i for l in compareAgainst if (i := Line(referencePoint, self.start).intersects(l))]
        if intersections:
            self.start = trimPoint
        else:
            self.end = trimPoint

@dataclass
class LineWithIndex:
    line: Line
    index: int

@dataclass
class Polygon:
    points: list[Vector2D]
    edgeNormals: list[Vector2D] = field(default_factory=lambda: [])
    vertexNormals: list[Vector2D] = field(default_factory=lambda: []) 
    bounds: Polygon | None = None

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
            # p1, p2, p3 = self.points[i-2], self.points[i-1], self.points[i]
            # v1 = p3 - p2
            # v2 = p1 - p2
            # a = (v1.angle() + v2.angle()) / 2
            # n = Vector2D(cos(a), sin(a))
            e1, e2 = self.edgeNormals[i-1], self.edgeNormals[i]
            a = (e1.angle() + e2.angle()) / 2
            n = Vector2D(cos(a), sin(a))
            if n.dot(self.edgeNormals[i-1]) < 0:
                n *= -1
            self.vertexNormals[i] = n

    def perimeter(self) -> float:
        perimeter = 0
        for i in range(len(self.points)):
            perimeter += self.points[i-1].distanceTo(self.points[i])
        return perimeter

    def longestDiagonal(self) -> float:
        return max([
            p1.distanceTo(p2)
            for i, p1 in enumerate(self.points[:-1])
            for p2 in self.points[i+1:]
        ])

    def removeSmallSegments(self) -> Polygon:
        newPolygon = Polygon([])

        for i in range(len(self.points)):
            if self.points[i-1].distanceTo(self.points[i]) > tolerance:
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

        for i in range(len(newLines)):
            lineVect = newLines[i].end - newLines[i].start
            lineVect /= lineVect.modulus()

            if (d := self.vertexNormals[i-1].dot(lineVect)) < 0:
                newLines[i].start += lineVect * d * amount

            if (d := self.vertexNormals[i].dot(lineVect)) > 0:
                newLines[i].end += lineVect * d * amount

        index = 0
        while index < len(newLines):
            p1 = newLines[index - 1].end
            p2 = newLines[index].start
            if p1.distanceTo(p2) < tolerance:
                mid = (p1 + p2) / 2
                newLines[index - 1].end = mid
                newLines[index].start = mid
            else:
                newLines.insert(index, Line(p1, p2))
            index += 1

        # import graphics
        # graphics.plotLinesRainbow(newLines)

        intersections = list(sweepingLineIntersection(newLines))
        # Sorting such that intersectionsbetween the closest and furthest vertext come earlier
        intersections.sort(key=lambda i: i.between[1], reverse=True)
        intersections.sort(key=lambda i: i.between[0])


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

class PixelMap:
    origin: Vector2D
    xspan: float
    yspan: float
    xlen: int
    ylen: int
    map: array[int]

    def __init__(self, boundBottomLeft: Vector2D, boundTopRight: Vector2D, numberSidePixels: int = 200) -> None:
        self.origin = boundBottomLeft
        self.xspan = boundTopRight.x - boundBottomLeft.x
        self.yspan = boundTopRight.y - boundBottomLeft.y

        quantum = min(self.xspan, self.yspan) / numberSidePixels

        self.xlen = int(self.xspan / quantum)
        self.ylen = int(self.yspan / quantum)

        self.map = array("I", b"\x00\x00\x00\x00" * self.xlen * self.ylen)

    def __getitem__(self, key: int | tuple[int, int] | Vector2D) -> int:
        if isinstance(key, int):
            return self.map[key]
        
        if isinstance(key, tuple) :
            if not list(map(type, key)) == [int, int]:
                raise Exception("Accessing pixmaps can only be done using indices (int), pair or indicies (int, int), or a point (Vector2D)")

            return self.map[key[1] * self.xlen + key[0]]

        return self.map[self.vectorToIndex(key)]

    def __setitem__(self, key: int | tuple[int, int] | Vector2D, value: int):
        if isinstance(key, int):
            self.map[key] = value
            return
        
        if isinstance(key, tuple) :
            if not list(map(type, key)) == [int, int]:
                raise Exception("Accessing pixmaps can only be done using indices (int), pair or indicies (int, int), or a point (Vector2D)")

            self.map[key[1] * self.xlen + key[0]] = value
            return

        self.map[self.vectorToIndex(key)] = value

    def __iter__(self):
        self.iterationIndex = 0
        return self

    def __next__(self):
        if self.iterationIndex < len(self.map):
            self.iterationIndex += 1
            return self.map[self.iterationIndex - 1]
        raise StopIteration

    def __repr__(self) -> str:
        s = "PixelMap=("
        s += f"origin={self.origin},"
        s += f"xspan={self.xspan},"
        s += f"yspan={self.yspan},"
        s += f"xlen={self.xlen},"
        s += f"ylen={self.ylen},"
        # s += f"map={self.map}"
        s += f"mapLength={len(self.map)},"
        return s + ")"

    def vectorToIndex(self, point: Vector2D) -> int:
        xIndex = int((point.x - self.origin.x) / self.xspan * self.xlen)
        yIndex = int((point.y - self.origin.y) / self.yspan * self.ylen)
        return yIndex * self.xlen + xIndex

    def coordsToIndex(self, x: int, y: int) -> int:
        return y * self.xlen + x

    def indexToVector(self, index: int) -> Vector2D:
        xIndex = index % self.xlen
        xIndex /= self.xlen
        xIndex *= self.xspan
        xIndex += self.origin.x

        yIndex = index // self.xlen
        yIndex /= self.ylen
        yIndex *= self.yspan
        yIndex += self.origin.y

        return Vector2D(xIndex, yIndex)

    def indexToCoords(self, index: int) -> tuple[int, int]:
        return (index % self.xlen, index // self.xlen)

Geometry =  Polygon | Line | Vector2D

@dataclass
class Intersection:
    point: Vector2D
    between: tuple[int, int]

    def __post_init__(self):
        if self.between[0] > self.between[1]:
            self.between = (self.between[1], self.between[0])
    def __hash__(self) -> int:
        return hash(self.point.__hash__() + self.between.__hash__())

class LerpLine:
    start: Vector2D
    direction: Vector2D
    step: float
    t: float = 0

    def __init__(self, line: Line, step: float) -> None:
        self.start = line.start
        self.direction = line.vector()
        self.step = step / line.length()
        pass

    def __iter__(self) -> LerpLine:
        self.t = 0
        return self

    def __next__(self) -> Vector2D:
        if self.t > 1: raise StopIteration 
        newPoint = self.start + self.direction * self.t
        self.t += self.step
        return newPoint

@dataclass
class GeometrySettigs:
    inflate: float | None
    mirror_x: bool
    mirror_y: bool
    offset_x: float | None
    offset_y: float | None
    tolerance: float


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
    class SweepedLine(LineWithIndex):
        checkedAgainst: set[int] = set()

    sortedLines: list[SweepedLine] = [
        SweepedLine(Line(line.start, line.end), i)
        if line.start.x < line.end.x else
        SweepedLine(Line(line.end, line.start), i)
        for i, line in enumerate(lines)
    ]
    sortedLines.sort(key=lambda sl: sl.line.start.x)

    intersections: set[Intersection] = set()
    evaluationBucket: list[SweepedLine] = []
    for sl in sortedLines:
        elementsToRemove = [
            e
            for e in evaluationBucket
            if e.line.end.x + tolerance < sl.line.start.x
        ]
        for e in elementsToRemove: evaluationBucket.remove(e)

        evaluationBucket.append(sl)
        for i, evaluee1 in enumerate(evaluationBucket[:-1]):
            for evaluee2 in evaluationBucket[i+1:]:
                if evaluee2.index in evaluee1.checkedAgainst: continue
                evaluee1.checkedAgainst.add(evaluee2.index)
                intersection = evaluee1.line.intersects(evaluee2.line, True)
                if intersection is None: continue
                intersections.add(Intersection(intersection, (evaluee1.index, evaluee2.index)))

    return intersections

def getBounds(geometries: Sequence[Geometry], padding: float = 0) -> tuple[Vector2D, Vector2D]:
    minimum = Vector2D(float("inf"), float("inf"))
    maximum = Vector2D(float("-inf"), float("-inf")) 

    def testPoint(p: Vector2D):
        if p.x < minimum.x: minimum.x = p.x
        if p.y < minimum.y: minimum.y = p.y
        if p.x > maximum.x: maximum.x = p.x
        if p.y > maximum.y: maximum.y = p.y

    for g in geometries:
        if isinstance(g, Vector2D):
            testPoint(g)
        elif isinstance(g, Line):
            testPoint(g.start)
            testPoint(g.end)
        else:
            for p in g.points:
                testPoint(p)

    return  minimum + Vector2D(-padding, -padding), maximum + Vector2D(padding, padding)

def lerp():
    ...

def interpolateGeometry(geo: Geometry, quantum: float = tolerance) -> list[Vector2D]:
    if isinstance(geo, Vector2D): return [geo]

    if isinstance(geo, Line): return [p for p in geo.lerp(quantum)]

    return [
        p
        for l in geo.breakAppart()
        for p in l.lerp(quantum)
    ]

