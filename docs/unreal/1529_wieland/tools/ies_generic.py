"""Phase 8: write generic photometric files (IES, IESNA LM-63-2002, type C) for fixture kinds that have
no published file. Runs outside the editor; standard library only.

    python -I -B ies_generic.py OUTPUT_FOLDER

Each file is a plain shape that turns with the fixture's axis, scaled so that the file's own light output
is 1,000 lumens; the fixture table then scales it to the lumens of the data sheet. The header of every
file says that it is generic, made here, and not a manufacturer's measurement.

    GENERIC_downlight_60deg.ies   a recessed downlight: beam 60 degrees wide at half strength, nothing
                                  above 75 degrees from straight down
    GENERIC_diffuse_globe.ies     an opal glass shade: the same strength in every direction
    GENERIC_diffuse_down.ies      a flat lit panel or ring facing down: strength falls with the cosine of
                                  the angle from straight down, nothing upward
    GENERIC_wall_wash_updown.ies  a wall sconce that lights up and down the wall: two cosine lobes
"""
import math
import os
import sys

STEP = 2.5  # degrees between vertical angles


def shapes():
    n = math.log(0.5) / math.log(math.cos(math.radians(30.0)))
    return {
        "GENERIC_downlight_60deg": ("recessed downlight, 60 degree beam, cut off at 75 degrees",
                                    lambda t: math.cos(math.radians(t)) ** n if t < 75.0 else 0.0),
        "GENERIC_diffuse_globe": ("opal shade, equal in every direction", lambda t: 1.0),
        "GENERIC_diffuse_down": ("flat lit surface facing down, cosine", lambda t: max(0.0, math.cos(math.radians(t)))),
        "GENERIC_wall_wash_updown": ("wall sconce, cosine lobes up and down plus a weak glow sideways",
                                     lambda t: 0.15 + 0.85 * abs(math.cos(math.radians(t))) ** 2),
    }


def lumens(angles, values):
    total = 0.0
    for i in range(len(angles) - 1):
        a, b = math.radians(angles[i]), math.radians(angles[i + 1])
        total += (values[i] + values[i + 1]) / 2.0 * 2.0 * math.pi * (math.cos(a) - math.cos(b))
    return total


def write(folder, name, text, shape):
    angles = [i * STEP for i in range(int(180.0 / STEP) + 1)]
    raw = [shape(t) for t in angles]
    scale = 1000.0 / lumens(angles, raw)
    values = [v * scale for v in raw]
    lines = [
        "IESNA:LM-63-2002",
        "[TEST] none: generic shape made for the 1529 N. Wieland scene, not a measurement",
        "[TESTLAB] none",
        "[ISSUEDATE] 12-NOV-2026",
        "[MANUFAC] none (generic)",
        "[LUMCAT] " + name,
        "[LUMINAIRE] " + text,
        "[LAMP] generic, 1000 lumens",
        "[OTHER] placeholder until the owner names a product; scale to the wanted lumens",
        "TILT=NONE",
        "1 1000 1 %d 1 1 2 0 0 0" % len(angles),
        "1 1 10",
    ]
    for start in range(0, len(angles), 10):
        lines.append(" ".join("%.1f" % a for a in angles[start:start + 10]))
    lines.append("0")
    for start in range(0, len(values), 10):
        lines.append(" ".join("%.2f" % v for v in values[start:start + 10]))
    path = os.path.join(folder, name + ".ies")
    with open(path, "w", encoding="ascii", newline="\r\n") as handle:
        handle.write("\n".join(lines) + "\n")
    return path, max(values), lumens(angles, values)


def main(argv):
    folder = argv[1]
    os.makedirs(folder, exist_ok=True)
    for name, (text, shape) in shapes().items():
        path, peak, total = write(folder, name, text, shape)
        print("%s  peak %.1f cd  %.1f lm" % (path, peak, total))


if __name__ == "__main__":
    main(sys.argv)
