from dataclasses import dataclass
from typing import Callable
from geometry import Line, LineWithOriginIndex, Polygon, Vector2D, getBounds
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
for p in polygons: p.calculate_normals()

boundsBottomLeft, boundsTopRight = getBounds(polygons, 0.5)
boundingBox = Polygon([
    boundsTopRight,
    Vector2D(boundsTopRight.x, boundsBottomLeft.y),
    boundsBottomLeft,
    Vector2D(boundsBottomLeft.x, boundsTopRight.y)
])

@dataclass
class Vector2DWithOriginIndex:
    point: Vector2D
    index: int

def rasterPolygonsAlongAxis(
    polygons: list[Polygon],
    bounds: tuple[Vector2D, Vector2D],
    axis: Callable[[Vector2D], float],
    step: float
) -> list[list[Vector2DWithOriginIndex]]:

    linesBucket = [
        LineWithOriginIndex(l, i)
        if axis(l.start) < axis(l.end) else
        LineWithOriginIndex(Line(l.end, l.start), i)
        for i, p in enumerate(polygons)
        for l in p.breakAppart()
    ]
    linesBucket.sort(key = lambda l: axis(l.line.start))

    allIntersections: list[list[Vector2DWithOriginIndex]] = []
    compareBucket: list[LineWithOriginIndex] = []
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

        thisjudgmentIntersections: list[Vector2DWithOriginIndex] = [
            Vector2DWithOriginIndex(intersection, l.index) 
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









graphics.plt.ion()
graphics.plotGeometries([boundingBox], color="gray", format="--")
# rasterVoronoiBounds(
#     polygons,
#     (boundsBottomLeft, boundsTopRight),
#     (boundsTopRight.x - boundsBottomLeft.x) / 20
# )
graphics.plotGeometries(polygons, color="white")
graphics.normalScaleFactor = 20
graphics.plotVertexNormals(polygons, color="pink")
graphics.show()
