import argparse, os
from gcode import GCodeSettings, generateGCode
from geometry import GeometrySettigs, InflatableGeometry, Vector2D, transformGeometries
from readers import extractGeometryDxf

parser = argparse.ArgumentParser(
    prog="PCB Engraving Tool",
    description="A tool to process DXF and DRL files and transform them to be suited for CNC engraving PCBs"
)

parser.add_argument(
    "filename",
    type=str,
    help="Input file to process, can be DXF or DRL file"
)
parser.add_argument(
    "-o", "--output",
    type=str,
    help="Name of output file, defaults to filename.gcode"
)
parser.add_argument(
    "-c", "--config",
    type=str,
    help="Path to a TOML config file with the same settings in the CLI, settings in the CLI will override what is specified in the config"
)

parser_geometry = parser.add_argument_group("Geometry", "Settings controlling how geometry is read and modified")
parser_geometry.add_argument(
    "-t", "--tolerance",
    type=float,
    default=0.05,
    help="Length below which points tend to be merged (default 0.05mm)"
)
parser_geometry.add_argument(
    "-i", "--inflate",
    type=float,
    help="Length to inflate all geometries by"
)
parser_geometry.add_argument(
    "-Ox", "--offset-x",
    type=float,
    help="Length to offset all geometries by in the X axis, effectively moving the origin"
)
parser_geometry.add_argument(
    "-Oy", "--offset-y",
    type=float,
    help="Length to offset all geometries by in the Y axis, effectively moving the origin"
)
parser_geometry.add_argument(
    "-mx", "--mirror-x",
    action="store_true",
    help="Mirror all geometries along X axis (horizontal flip)"
)
parser_geometry.add_argument(
    "-my", "--mirror-y",
    action="store_true",
    help="Mirror all geometries along Y axis (vertical flip)"
)

parser_gcode = parser.add_argument_group("Gcode", "Settings used during gcode generation")
parser_gcode.add_argument(
    "-f", "--feed-rate",
    type=int,
    default=400,
    help="Horizontal feed rate (default 300mm/min)"
)
parser_gcode.add_argument(
    "-p", "--plunge-rate",
    type=int,
    default=70,
    help="Plunge feed rate, used when moving the head down into the work pirce or drilling (default 70mm/min)"
)
parser_gcode.add_argument(
    "-d", "--depth",
    type=float,
    default=0.15,
    help="Carving and drilling depth in mm, should be changed when drilling (default 0.15mm)"
)
parser_gcode.add_argument(
    "-r", "--rapid-height",
    type=float,
    default=5,
    help="Height at which to perform rapid movements (default 5mm)"
)
parser_gcode.add_argument(
    "-s", "--safe-height",
    type=float,
    default=1,
    help="Height under which all movements are slow, must be lower than safe fast height (default 1mm)"
)
parser_gcode.add_argument(
    "-S", "--spindle",
    type=int,
    default=5000,
    help="Spindle speed (default 5000rpm)"
)

parser_graphics = parser.add_argument_group("Plotting", "Settings enabling display of processed geometries, these settings require matplotlib to be installed")
parser_graphics.add_argument(
    "--plot-original",
    action="store_true",
    help="Displays the original goemetries"
)
parser_graphics.add_argument(
    "--plot-result",
    action="store_true",
    help="Displays the processed geometries"
)


args = parser.parse_args()

if not os.path.isfile(args.filename):
    print(f"File {args.filename} not found")
    exit(1)

basename, extention = os.path.splitext(args.filename)
basename = str(basename)
extention = str(extention).lower()[1:]
if not extention in ["dxf", "drl"]:
    print(f"File type (extention) must be DXF or DRL")
    exit(2)

if not args.output:
    args.output = basename + ".gcode"


geometrySettings = GeometrySettigs(
    tolerance=args.tolerance,
    inflate=args.inflate,
    offset_x=args.offset_x,
    offset_y=args.offset_y,
    mirror_x=args.mirror_x,
    mirror_y=args.mirror_y
)

gcodeSettings = GCodeSettings(
    depth=args.depth,
    feed=args.feed_rate,
    plunge=args.plunge_rate,
    rapid=args.rapid_height,
    safe=args.safe_height,
    spindle=args.spindle
)


if extention == "dxf":
    geometries = extractGeometryDxf(args.filename, args.tolerance)
else:
    geometries = []

newGeometries = transformGeometries(geometries, geometrySettings)

print(generateGCode(newGeometries, gcodeSettings))

if args.plot_original or args.plot_result:
    import graphics

    if args.plot_original:
        graphics.plotGeometries(geometries, color="blue")

    if args.plot_result:
        graphics.plotGeometries(newGeometries, color="green")

    graphics.show()


