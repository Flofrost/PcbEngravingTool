from typing import Sequence
from geometry import Geometry, Line, Vector2D, Polygon



def extractGeometryDxf(filename: str, tolerance: float) -> Sequence[Geometry]:
    import ezdxf.filemanagement as dxf
    dxffile = dxf.readfile(filename)

    rawGeometries: list[Geometry] = []

    for entity in dxffile.entities:
        entityType = entity.dxftype()

        if entityType == "LINE":
            rawGeometries.append(Line(
                Vector2D(*entity.get_dxf_attrib("start").vec2),
                Vector2D(*entity.get_dxf_attrib("end").vec2)
            ))

    lines = [g for g in rawGeometries if isinstance(g, Line)]
    polygons = [Polygon([lines[0].start])]
    previousLine = lines[0]

    for line in lines[1:]:
        if line.start.distanceTo(previousLine.end) < tolerance:
            polygons[-1].points.append(line.start)
        else:
            polygons.append(Polygon([line.start]))
        previousLine = line

    return polygons
