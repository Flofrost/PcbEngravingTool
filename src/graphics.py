from typing import Sequence
from matplotlib import colormaps
import matplotlib.pyplot as plt

from geometry import Geometry, Line, Polygon 

plt.style.use("dark_background")
fig, ax = plt.subplots()
ax.axis("equal")
normalScaleFactor = 1/15

def plotGeometries(geometries: Sequence[Geometry], color = None, format="-"):
    for g in geometries:
        if isinstance(g, Polygon):
            ax.plot(
                [p.x for p in g.points + [g.points[0]]],
                [p.y for p in g.points + [g.points[0]]],
                format,
                color = color
            )
        if isinstance(g, Line):
            ax.plot(
                [g.start.x, g.end.x],
                [g.start.y, g.end.y],
                format,
                color = color
            )

def plotEdgeNormals(polygons: Sequence[Polygon], color = None):
    for p in polygons:
        for p, n in zip(p.points, p.edgeNormals):
            ax.plot(
                [p.x, p.x + n.x * normalScaleFactor],
                [p.y, p.y + n.y * normalScaleFactor],
                color = color
            )

def plotVertexNormals(polygons: Sequence[Polygon], color = None):
    for p in polygons:
        for p, n in zip(p.points, p.vertexNormals):
            ax.plot(
                [p.x, p.x + n.x * normalScaleFactor],
                [p.y, p.y + n.y * normalScaleFactor],
                color = color
            )

def plotLinesRainbow(lines: list[Line]):
    for i, l in enumerate(lines):
        ax.plot(
            [l.start.x, l.end.x],
            [l.start.y, l.end.y],
            color=colormaps["hsv"](5*i/len(lines)%1)
        )

def show(): plt.show(block=True)
def clear(): ax.clear()

