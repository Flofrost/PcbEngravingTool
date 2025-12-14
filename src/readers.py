from dataclasses import dataclass
import os
from typing import Callable, Sequence, TextIO
from geometry import Geometry, Line, Vector2D, Polygon
import re


@dataclass
class File:
    outputPath: str
    originalGeometries: Sequence[Geometry]
    transformedGeometries: Sequence[Geometry]

def extractGeometryDXF(inputFile: TextIO, outputFileName: str, tolerance: float = 0.05) -> Sequence[File]:
    import ezdxf.filemanagement as dxf

    dxffile = dxf.read(inputFile)

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

    return [File(outputFileName, polygons, [])]

def extractGeometryDRL(inputFile: TextIO, outputFileName: str, _) -> Sequence[File]:
    files: list[File] = []
    selectedFile = 0

    while line := inputFile.readline():

        if re.match(r"^;", line):
            continue

        if matches := re.findall(r"^T\d+C(\d+(?:\.\d+)?)", line):
            basename, ext = os.path.splitext(outputFileName)
            files.append(File(
                basename + f"_{float(matches[0])}" + ext,
                [], []
            ))
            continue

        if matches := re.findall(r"^T(\d+)", line):
            selectedFile = int(matches[0]) - 1
            continue

        if matches := re.findall(r"^X(-?\d+(?:\.\d+)?)Y(-?\d+(?:\.\d+)?)", line):
            files[selectedFile].originalGeometries.__getattribute__("append")(Vector2D(
                float(matches[0][0]),
                float(matches[0][1])
            ))
            continue

    return files

extractors: dict[str, Callable[[TextIO, str, float], Sequence[File]]] = {
    "dxf": extractGeometryDXF,
    "drl": extractGeometryDRL
}

