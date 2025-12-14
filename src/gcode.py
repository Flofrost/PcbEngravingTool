from dataclasses import dataclass
from typing import Sequence
from geometry import Geometry, Line, Polygon, Vector2D

@dataclass
class GCodeSettings:
    depth: float
    feed: float
    plunge: float
    rapid: float
    safe: float
    spindle: int

def generateGCode(geometries: Sequence[Geometry], settings: GCodeSettings):
    gcode: list[str] = [
        "G90",
        f"M3 S{settings.spindle}",
        "",
        f"G0 Z{settings.rapid}"
    ]

    for g in geometries:
        if isinstance(g, Vector2D):
            gcode += [
                f"G0 X{g.x:6.2f} Y{g.y:6.2f}",
                f"G0 Z{settings.safe}",
                f"G1 F{settings.plunge} Z-{settings.depth}",
                f"G0 Z{settings.rapid}",
                ""
            ]
        elif isinstance(g, Line):
            gcode += [
                f"G0 X{g.start.x:6.2f} Y{g.start.y:6.2f}",
                f"G0 Z{settings.safe}",
                f"G1 F{settings.plunge} Z-{settings.depth}",
                f"G1 F{settings.feed} X{g.end.x:6.2f} Y{g.end.y:6.2f}",
                f"G0 Z{settings.rapid}",
                ""
            ]
        elif isinstance(g, Polygon):
            gcode += [
                f"G0 X{g.points[-1].x:6.2f} Y{g.points[-1].y:6.2f}",
                f"G0 Z{settings.safe}",
                f"G1 F{settings.plunge} Z-{settings.depth}",
                f"G1 F{settings.feed}"
            ]

            for p in g.points:
                gcode.append(f"G1 X{p.x:6.2f} Y{p.y:6.2f}")

            gcode += [
                f"G0 Z{settings.rapid}",
                ""
            ]

    gcode.append("M5\n")

    return "\n".join(gcode)

