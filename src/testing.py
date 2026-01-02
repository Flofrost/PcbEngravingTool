from dataclasses import dataclass
from geometry import  Line,  Polygon, Vector2D, Vector2DWithIndex, getBounds, nearZero_precise, nearZero_tolerance, sweepingLineIntersection, tolerance
from readers import extractGeometryDXF
from array import array
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
# with open("../Karaoke/schematic/Karaoke-F_Cu.dxf") as f:
with open("./testschema/test-F_Cu.dxf") as f:
    polygons = [p for p in extractGeometryDXF(f, "ya")[0].originalGeometries if isinstance(p, Polygon)]
# polygons = polygons[:1]
for p in polygons: p.calculate_normals()

boundsBottomLeft, boundsTopRight = getBounds(polygons, 0.20)
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
        midPoint - vector * length,
        midPoint + vector * length
    )

def noiseUp(points: list[Vector2D], amount: float) -> list[Vector2D]:
    from random import random
    return [
        Vector2D(
            p.x + random() * amount - amount / 2,
            p.y + random() * amount - amount / 2
        )
        for p in points
    ]

def voronoi_insert(points: list[Vector2D], bounds: Polygon) -> list[Line]:
    @dataclass
    class VoronoiEdge:
        line: Line
        bisects: tuple[int, int]

    bisectorLength = bounds.longestDiagonal() * 2

    if len(points) < 2: return []
    if len(points) == 2: return [createBisector(points[0], points[1], bisectorLength)] + bounds.breakAppart()

    edges: list[VoronoiEdge] = [VoronoiEdge(
        createBisector(points[0], points[1], bisectorLength),
        (0, 1)
    )]
    sites: list[Vector2D] = points[:2]
    iter_img = 0

    def snip_1inter(intersection: Vector2DWithIndex):
        newEdge.trim(
            intersection.point,
            [e.line for e in otherPointEdges],
            points[otherPoint]
        )
        edges[intersection.index].line.trim(
            intersection.point,
            [newEdge],
            points[otherPoint]
        )

    def snip_2inter(intersections: list[Vector2DWithIndex]):
        newEdge.start = intersections[0].point
        newEdge.end = intersections[1].point

        if intersections[0].index >= 0:
            edges[intersections[0].index].line.trim(
                intersections[0].point,
                [newEdge],
                points[otherPoint]
            )
        if intersections[1].index >= 0:
            edges[intersections[1].index].line.trim(
                intersections[1].point,
                [newEdge],
                points[otherPoint]
            )

    for i, p in enumerate(points):
        if i < 2: continue

        otherPoint = min(range(len(sites)), key=lambda idx: sites[idx].distanceTo(p))
        sites.append(p)

        exploredSites: set[int] = {i}
        intersectedSites: set[int] = set()
        unexploredSites: set[int] = set()
        print(i, len(points))

        while True:
            newEdge = createBisector(points[otherPoint], p, bisectorLength)
            otherPointEdges = [e for e in edges if otherPoint in e.bisects]
            # verticies = set([e.line.start for e in otherPointEdges] + [e.line.end for e in otherPointEdges])
            
            intersections = [
                Vector2DWithIndex(inter, idx)
                for idx, edge in enumerate(edges)
                if (otherPoint in edge.bisects) and (inter := edge.line.intersects(newEdge))
            ]
            # print()
            print(len(intersections))

            graphics.clear()
            graphics.plotGeometries(sites, color="white")
            graphics.plotGeometries([e.line for e in edges], color="red")
            graphics.plotGeometries([inter.point for inter in intersections], color="yellow")
            graphics.plotGeometries([newEdge], color="orange")
            graphics.plotGeometries([e.line for e in otherPointEdges], color="green")
            graphics.plotGeometries([p], color="orange")
            graphics.plotGeometries([points[otherPoint]], color="lime")
            # graphics.plt.savefig(f"debug/{iter_img}_{i}_a_inter.svg")
            graphics.pause()

            if not intersections:
                if not unexploredSites: break
                otherPoint = unexploredSites.pop()
                continue
            if len(intersections) == 1:
                snip_1inter(intersections[0])
            else:
                if nearZero_precise((intersections[0].point - intersections[1].point).modulus()):
                    snip_1inter(intersections[0])
                else:
                    snip_2inter(intersections)

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

            graphics.clear()
            graphics.plotGeometries(sites, color="white")
            graphics.plotGeometries([e.line for e in edges], color="red")
            graphics.plotGeometries([newEdge], color="orange")
            graphics.plotGeometries([p], color="orange")
            graphics.plotGeometries([points[otherPoint]], color="lime")
            graphics.plotGeometries([e.line for e in otherPointEdges], color="green")
            graphics.plotGeometries([Line(newEdgeMid, newEdgeMid+projectionVector*0.2)], color="cyan")

            for e in otherPointEdges:
                if  projectionVector.dot(e.line.start - newEdgeMid) < 0 and\
                    projectionVector.dot(e.line.end - newEdgeMid) < 0:
                    edges.remove(e)
                    intersectedSites.add(e.bisects[0])
                    intersectedSites.add(e.bisects[1])
                    graphics.plotGeometries([e.line], color="pink")

            # graphics.plt.savefig(f"debug/{iter_img}_{i}_b_cull.svg")
            graphics.pause()
            iter_img += 1

            unexploredSites = intersectedSites - exploredSites
            if not unexploredSites: break
            otherPoint = unexploredSites.pop()

        graphics.clear()
        graphics.plotGeometries(sites, color="white")
        graphics.plotGeometries([e.line for e in edges], color="red")
        print("Site Done")
        graphics.pause()


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
    
def voronoi_raster(points: list[Vector2D], bounds: Polygon, precision: int = 200) -> list[Line]:
    boundsBL, boundsTR = getBounds([bounds])

    xspan = boundsTR.x - boundsBL.x
    yspan = boundsTR.y - boundsBL.y

    quantum = min(xspan, yspan) / precision

    xlen = int(xspan / quantum)
    ylen = int(yspan / quantum)

    pixmap = array("I", [0 for _ in range(xlen * ylen)])

    def coord2pixspace(point: Vector2D) -> int:
        xIndex = int((point.x - boundsBL.x) / xspan * xlen)
        yIndex = int((point.y - boundsBL.y) / yspan * ylen)
        return yIndex * xlen + xIndex

    def pixspace2coord(index: int) -> Vector2D:
        xIndex = index % xlen
        xIndex /= xlen
        xIndex *= xspan
        xIndex += boundsBL.x

        yIndex = index // ylen
        yIndex /= ylen
        yIndex *= yspan
        yIndex += boundsBL.y

        return Vector2D(xIndex, yIndex)

    for i in range(len(pixmap)):
        print(f"\r{i}/{len(pixmap)}", end="")
        distances = [(pixspace2coord(i).distanceTo(point), idx) for idx, point in enumerate(points)]
        closestPoint = min(distances, key=lambda d: d[0])
        pixmap[i] = closestPoint[1]

    graphics.ax.clear()
    graphics.ax.imshow(
        [[pixmap[y*xlen+x] for x in range(xlen)] for y in range(ylen)],
        aspect=xspan/yspan,
        origin="lower",
        cmap=graphics.colormaps["prism"]
    )
    graphics.pause()


    return []


graphics.plt.ion()
graphics.plt.show()
graphics.xlim = (boundsBottomLeft.x, boundsTopRight.x)
graphics.ylim = (boundsBottomLeft.y, boundsTopRight.y)
pointsBucket = [p for pl in polygons for p in pl.points] 
# pointsBucket = noiseUp([p for pl in polygons for p in pl.points], 0.02)
# voronoiEdges = voronoi_insert(pointsBucket, boundingBox)
voronoiEdges = voronoi_raster(pointsBucket, boundingBox)
graphics.clear()
graphics.plotGeometries(pointsBucket, color="white")
graphics.plotGeometries(voronoiEdges, color="red")
# graphics.plotGeometries(bigPoly, color="green")
# graphics.normalScaleFactor = 1/2
# graphics.plotVertexNormals(polygons, color="pink")
# graphics.plotGeometries([l.line for p in porcupines for l in p], color="red")
graphics.show()
