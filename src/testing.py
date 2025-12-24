from dataclasses import dataclass
from geometry import  Line,  Polygon, Vector2D, Vector2DWithIndex, getBounds, sweepingLineIntersection
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
# polygons = [polygons[0]]
for p in polygons: p.calculate_normals()

boundsBottomLeft, boundsTopRight = getBounds(polygons, 20)
boundingBox = Polygon([
    boundsTopRight,
    Vector2D(boundsTopRight.x, boundsBottomLeft.y),
    boundsBottomLeft,
    Vector2D(boundsBottomLeft.x, boundsTopRight.y)
])
boundLength = boundsBottomLeft.distanceTo(boundsTopRight)


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

    # graphics.clear()
    # graphics.plotGeometries(sites, color="white")
    # graphics.plotGeometries([e.line for e in edges], color="red")
    # graphics.pause()

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
            # print()
            # print(intersections)
            #
            # graphics.clear()
            # graphics.plotGeometries(sites, color="white")
            # graphics.plotGeometries([e.line for e in edges], color="red")
            # graphics.plotGeometries([inter.point for inter in intersections], color="yellow")
            # graphics.plotGeometries([newEdge], color="orange")
            # graphics.plotGeometries([e.line for e in otherPointEdges], color="green")
            # graphics.plotGeometries(list(verticies), color="lime")
            # graphics.pause()

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

            edges.append(VoronoiEdge(newEdge, (i, otherPoint)))
            exploredSites.add(otherPoint)

            for b in [ b for inter in intersections if inter.index >= 0 for b in edges[inter.index].bisects ]:
                intersectedSites.add(b)

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
                    intersectedSites.add(e.bisects[0])
                    intersectedSites.add(e.bisects[1])

            # graphics.clear()
            # graphics.plotGeometries(sites, color="white")
            # graphics.plotGeometries([e.line for e in edges], color="red")
            # graphics.plotGeometries([newEdge], color="orange")
            # graphics.plotGeometries([e.line for e in otherPointEdges], color="green")
            # graphics.pause()

            unexploredSites = intersectedSites - exploredSites
            if not unexploredSites: break
            otherPoint = unexploredSites.pop()

    boundsCenter = sum(bounds.points) / len(bounds.points)
    if not isinstance(boundsCenter, Vector2D):
        boundsCenter = Vector2D(0,0)
    boundEdges = bounds.breakAppart()

    boundIntersections = sweepingLineIntersection([e.line for e in edges] + boundEdges)
    for inter in boundIntersections:
        edgeIndex = min(inter.between)
        if edges[edgeIndex].line.start.distanceTo(boundsCenter) > edges[edgeIndex].line.end.distanceTo(boundsCenter):
            edges[edgeIndex].line.start = inter.point
        else:
            edges[edgeIndex].line.end = inter.point

    return [e.line for e in edges] + boundEdges
    





graphics.plt.ion()
graphics.plt.show()
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
