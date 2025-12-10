import argparse, os
import ezdxf.filemanagement

from geometry import Line, Vector2D, polygonize

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

import matplotlib.pyplot as plt

fig, ax = plt.subplots()
for pg in polygons:
    pg.calculate_normals()
    ax.plot([p.x for p in pg.points], [p.y for p in pg.points])
    ax.scatter([n.x for n in pg.edgeNormals], [n.y for n in pg.edgeNormals])
plt.show(block=True)


