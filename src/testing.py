from dataclasses import dataclass
from typing import Callable
from geometry import Intersection, Line, LineWithIndex, Polygon, Vector2D, Vector2DWithIndex, getBounds, sweepingLineIntersection
from readers import extractGeometryDXF
import graphics

polygons = [
    Polygon([
        Vector2D(186, 363),
        Vector2D(415, 509),
        Vector2D(523, 316),
        Vector2D(409, 148),
        Vector2D(211, 180),
    ]),
    Polygon([
        Vector2D(400, 200),
        Vector2D(400, 400),
        Vector2D(300, 200),
    ]),
    Polygon([
        Vector2D(734, 152),
        Vector2D(586, 23),
        Vector2D(479, 102),
        Vector2D(608, 180),
    ]),
    Polygon([
        Vector2D(654, 276),
        Vector2D(771, 353),
        Vector2D(560, 437),
        Vector2D(652, 656),
        Vector2D(738, 491),
        Vector2D(968, 316),
        Vector2D(830, 215),
    ]),
    Polygon([
        Vector2D(828, 510),
        Vector2D(726, 579),
        Vector2D(805, 704),
    ]),
    Polygon([
        Vector2D(97, 349),
        Vector2D(134, 194),
        Vector2D(253, 73),
        Vector2D(103, 58),
        Vector2D(44, 451),
        Vector2D(316, 677),
        Vector2D(220, 474)
    ])
]
# with open("./testschema/test-F_Cu.dxf") as f:
#     polygons = [p for p in extractGeometryDXF(f, "ya")[0].originalGeometries if isinstance(p, Polygon)]
for p in polygons: p.calculate_normals()

boundsBottomLeft, boundsTopRight = getBounds(polygons, 20)
boundingBox = Polygon([
    boundsTopRight,
    Vector2D(boundsTopRight.x, boundsBottomLeft.y),
    boundsBottomLeft,
    Vector2D(boundsBottomLeft.x, boundsTopRight.y)
])
boundLength = boundsBottomLeft.distanceTo(boundsTopRight)


def rasterPolygonsAlongAxis(
    polygons: list[Polygon],
    bounds: tuple[Vector2D, Vector2D],
    axis: Callable[[Vector2D], float],
    step: float
) -> list[list[Vector2DWithIndex]]:

    linesBucket = [
        LineWithIndex(l, i)
        if axis(l.start) < axis(l.end) else
        LineWithIndex(Line(l.end, l.start), i)
        for i, p in enumerate(polygons)
        for l in p.breakAppart()
    ]
    linesBucket.sort(key = lambda l: axis(l.line.start))

    allIntersections: list[list[Vector2DWithIndex]] = []
    compareBucket: list[LineWithIndex] = []
    sweepingLineIndex = 0
    judgmentIndex = axis(bounds[0])
    while judgmentIndex < axis(bounds[1]):
        while sweepingLineIndex < len(linesBucket) and axis((l := linesBucket[sweepingLineIndex]).line.start) < judgmentIndex:
            compareBucket.append(l)
            sweepingLineIndex += 1

        if axis(Vector2D(0, 1)):
            judgmentLine = Line(
                Vector2D(bounds[0].x, judgmentIndex),
                Vector2D(bounds[1].x, judgmentIndex)
            )
        else:
            judgmentLine = Line(
                Vector2D(judgmentIndex, bounds[0].y),
                Vector2D(judgmentIndex, bounds[1].y)
            )

        thisjudgmentIntersections: list[Vector2DWithIndex] = [
            Vector2DWithIndex(intersection, l.index) 
            for l in compareBucket
            if (intersection := judgmentLine.intersects(l.line))
        ]
        thisjudgmentIntersections.sort(key = lambda v: v.point.x if axis(v.point) is v.point.y else v.point.y)


        graphics.plotGeometries([i.point for i in thisjudgmentIntersections], color="yellow")
        # graphics.plotGeometries([l.line for l in compareBucket], color="white")
        # graphics.plotGeometries([judgmentLine], color="#555522")
        # graphics.plt.pause(0.05)

        allIntersections.append(thisjudgmentIntersections)
        judgmentIndex += step

        linesToRemove = [l for l in compareBucket if axis(l.line.end) < judgmentIndex]
        for l in linesToRemove: compareBucket.remove(l)

    return allIntersections

def rasterVoronoiBounds(polygons: list[Polygon], bounds: tuple[Vector2D, Vector2D], step: float = 0.05):
    fullRaster = rasterPolygonsAlongAxis(polygons, bounds, lambda p: p.x, step) +\
        rasterPolygonsAlongAxis(polygons, bounds, lambda p: p.y, step)

    for rasterLine in fullRaster:
        if len(rasterLine) < 2: continue

        previousIntersection = rasterLine[0]
        for intersection in rasterLine[1:]:
            if intersection.index != previousIntersection.index:
                voronoiEdgePoint = (intersection.point + previousIntersection.point) / 2
                graphics.plotGeometries([voronoiEdgePoint], color="red")
            previousIntersection = intersection

def lerp(p1: Vector2D, p2: Vector2D, t: float) -> Vector2D:
    return p1 * t + p2 * (1-t)

def createPorcupine(polygon: Polygon, length: float) -> list[LineWithIndex]:
    polygon.calculate_normals()
    quills: list[LineWithIndex] = []

    for i in range(len(polygon.points)):
        currentEdge = Line(polygon.points[i-1], polygon.points[i])
        distance = 0

        while distance < currentEdge.length():
            startPoint = lerp(currentEdge.start, currentEdge.end, distance/currentEdge.length())
            distance += 0.05
            quills.append(LineWithIndex(
                Line(startPoint, startPoint - polygon.edgeNormals[i-1] * length),
                i
            ))

    return quills

def createBisector(p1: Vector2D, p2: Vector2D, length: float) -> Line:
    midPoint = (p1 + p2) / 2
    vector = p2 - p1
    vector /= vector.modulus()
    vector = Vector2D(vector.y, -vector.x)
    return Line(
        midPoint - vector * length / 2,
        midPoint + vector * length / 2
    )

def voronoi(points: list[Vector2D], bounds: Polygon, maxLength: float) -> list[Line]:
    @dataclass
    class VoronoiEdge:
        line: Line
        bisects: tuple[int, int]


    if len(points) < 2: return []
    if len(points) == 2: return [createBisector(points[0], points[1], maxLength), ]

    edges: list[VoronoiEdge] = [VoronoiEdge(
        createBisector(points[0], points[1], maxLength),
        (0, 1)
    )]

    sites: list[Vector2D] = points[:2]
    # verticies: set[Vector2D] = set()

    graphics.clear()
    graphics.plotGeometries(sites, color="white")
    graphics.plotGeometries([e.line for e in edges], color="red")
    graphics.plt.waitforbuttonpress()

    for i, p in enumerate(points):
        if i < 2: continue

        otherPoint = min(range(len(sites)), key=lambda idx: sites[idx].distanceTo(p))
        sites.append(p)

        exploredSites: set[int] = {i}
        intersectedSites: set[int] = set()
        unexploredSites: set[int] = set()

        while True:
            newEdge = createBisector(points[otherPoint], p, maxLength)
            otherPointEdges = [e for e in edges if otherPoint in e.bisects]
            verticies = set([e.line.start for e in otherPointEdges] + [e.line.end for e in otherPointEdges])
            
            intersections = [
                Vector2DWithIndex(inter, idx)
                for idx, edge in enumerate(edges)
                if (otherPoint in edge.bisects) and (inter := edge.line.intersects(newEdge))
            ] + [
                Vector2DWithIndex(v, -1)
                for v in verticies
                if newEdge.pointOnLine(v)
            ]
            print()
            print(intersections)

            # graphics.clear()
            # graphics.plotGeometries(sites, color="white")
            # graphics.plotGeometries([e.line for e in edges], color="red")
            # graphics.plotGeometries([inter.point for inter in intersections], color="yellow")
            # graphics.plotGeometries([newEdge], color="orange")
            # graphics.plotGeometries([e.line for e in otherPointEdges], color="green")
            # graphics.plotGeometries(list(verticies), color="lime")
            # graphics.plt.waitforbuttonpress()

            if not intersections:
                if not unexploredSites: break
                otherPoint = unexploredSites.pop()
                continue
            if len(intersections) == 1:
                newEdge.trim(
                    intersections[0].point,
                    [e.line for e in otherPointEdges],
                    points[otherPoint]
                )
                if intersections[0].index >= 0:
                    edges[intersections[0].index].line.trim(
                        intersections[0].point,
                        [newEdge],
                        points[otherPoint]
                    )
            else:
                newEdge.start = intersections[0].point
                newEdge.end = intersections[1].point

                if intersections[0].index >= 0:
                    edges[intersections[0].index].line.trim(
                        intersections[0].point,
                        [e.line for e in otherPointEdges] + [newEdge],
                        points[otherPoint]
                    )
                if intersections[1].index >= 0:
                    edges[intersections[1].index].line.trim(
                        intersections[1].point,
                        [e.line for e in otherPointEdges] + [newEdge],
                        points[otherPoint] 
                    )

                newEdgeMid = (newEdge.end + newEdge.start) / 2
                projectionVector = newEdge.vector()
                projectionVector /= projectionVector.modulus()
                projectionVector = Vector2D(-projectionVector.y, projectionVector.x)
                if projectionVector.dot(p - newEdgeMid) > 0:
                    projectionVector *= -1

                for e in otherPointEdges:
                    if  projectionVector.dot(e.line.start - newEdgeMid) < 0 and\
                        projectionVector.dot(e.line.end - newEdgeMid) < 0:
                        edges.remove(e)

            edges.append(VoronoiEdge(newEdge, (i, otherPoint)))
            exploredSites.add(otherPoint)

            for b in [ b for inter in intersections if inter.index >= 0 for b in edges[inter.index].bisects ]:
                intersectedSites.add(b)
            unexploredSites = intersectedSites - exploredSites

            # graphics.clear()
            # graphics.plotGeometries(sites, color="white")
            # graphics.plotGeometries([e.line for e in edges], color="red")
            # graphics.plt.waitforbuttonpress()

            if not unexploredSites: break
            otherPoint = unexploredSites.pop()




    return [e.line for e in edges]
    





graphics.plt.ion()
pointsBucket = [p for pl in polygons for p in pl.points]
voronoiEdges = voronoi(pointsBucket, boundingBox, boundLength * 2)
graphics.clear()
graphics.plotGeometries([boundingBox], color="gray", format="--")
graphics.plotGeometries(pointsBucket, color="white")
graphics.plotGeometries(voronoiEdges, color="red")
# graphics.plotGeometries(bigPoly, color="green")
# graphics.normalScaleFactor = 1/2
# graphics.plotVertexNormals(polygons, color="pink")
# graphics.plotGeometries([l.line for p in porcupines for l in p], color="red")
graphics.show()
