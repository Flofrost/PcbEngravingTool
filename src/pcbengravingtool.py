import argparse, os
import ezdxf.filemanagement

from geometry import Line, Vector2D, inflate, polygonize

parser = argparse.ArgumentParser(
    prog="PCB Engraving Tool",
    description="A tool to process dxf files and transform them to be suited for CNC engraving PCBs"
)

parser.add_argument(
    "filename",
    type=str,
    help="Input file to process, can be dxf or drl file"
)
parser.add_argument(
    "-o", "--output",
    type=str,
    default="",
    help="Name of output file, defaults to filename.gcode"
)
parser.add_argument

args = parser.parse_args()

if not os.path.isfile(args.filename):
    print(f"File {args.filename} not found")
    exit(1)



dxffile = ezdxf.filemanagement.readfile(args.filename)

geometry: list[Line] = []

for entity in dxffile.entities:
    entityType = entity.dxftype()

    if entityType == "LINE":
        geometry.append(Line(
            Vector2D(*entity.get_dxf_attrib("start").vec2),
            Vector2D(*entity.get_dxf_attrib("end").vec2)
        ))

polygons = polygonize(geometry)
for p in polygons: 
    p.calculate_normals()
biggerPolygons = [inflate(p, 0.2) for p in polygons]

import matplotlib.pyplot as plt

fig, ax = plt.subplots()
for pg, ipg in zip(polygons, biggerPolygons):
    ax.plot([p.x for p in pg.points + [pg.points[0]]], [p.y for p in pg.points + [pg.points[0]]])
    # ax.plot([p.x for p in ipg.points + [ipg.points[0]]], [p.y for p in ipg.points + [ipg.points[0]]])
    ax.scatter([n.x/20+p.x for p,n in zip(pg.points, pg.edgeNormals)], [n.y/20+p.y for p,n in zip(pg.points, pg.edgeNormals)], marker="x")
    ax.scatter([n.x/20+p.x for p,n in zip(pg.points, pg.vertexNormals)], [n.y/20+p.y for p,n in zip(pg.points, pg.vertexNormals)], marker=".")
plt.show(block=True)


