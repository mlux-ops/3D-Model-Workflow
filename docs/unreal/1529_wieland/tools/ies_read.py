"""Read the facts of photometric files in the IES format (IESNA LM-63). Runs outside the editor.

    python -I -B ies_read.py FILE [FILE ...]      prints one JSON object per file

For each file: the header lines, the number of lamps, the lumens per lamp the file states (-1 means the
file gives absolute candela values and no lamp lumens), the candela multiplier, input watts, the largest
candela value, and the light output worked out from the candela table itself (the sum over the sphere),
which is the number to trust when the header says -1.

The files are data from outside; nothing in them is run. Run this with python -I from another folder
and pass the paths.
"""
import json
import math
import sys


def read(path):
    with open(path, "r", encoding="latin-1") as handle:
        lines = handle.read().replace("\r", "\n").split("\n")
    lines = [line.strip() for line in lines if line.strip()]
    header = []
    index = 0
    while index < len(lines) and not lines[index].upper().startswith("TILT"):
        header.append(lines[index])
        index += 1
    if index >= len(lines):
        return {"file": path, "error": "no TILT line"}
    tilt = lines[index]
    index += 1
    numbers = []
    for line in lines[index:]:
        for token in line.replace(",", " ").split():
            try:
                numbers.append(float(token))
            except ValueError:
                pass
    if tilt.upper().replace(" ", "") == "TILT=INCLUDE":
        # lamp-to-luminaire geometry, number of pairs, then that many angles and factors
        pairs = int(numbers[1])
        numbers = numbers[2 + 2 * pairs:]
    lamps, lumens_per_lamp, multiplier = int(numbers[0]), numbers[1], numbers[2]
    n_vertical, n_horizontal = int(numbers[3]), int(numbers[4])
    photometric_type, units = int(numbers[5]), int(numbers[6])
    width, length, height = numbers[7], numbers[8], numbers[9]
    ballast, _future, watts = numbers[10], numbers[11], numbers[12]
    rest = numbers[13:]
    vertical = rest[:n_vertical]
    horizontal = rest[n_vertical:n_vertical + n_horizontal]
    table = rest[n_vertical + n_horizontal:]
    if len(table) < n_vertical * n_horizontal:
        return {"file": path, "error": "candela table is short: %d of %d" % (len(table), n_vertical * n_horizontal)}
    scale = multiplier * ballast
    candela = [[table[h * n_vertical + v] * scale for v in range(n_vertical)] for h in range(n_horizontal)]
    # Light output: integrate over the vertical angles (zonal constants), average over the horizontal planes
    # weighted by the angle each plane stands for. Type C photometry only (type 1); others are reported as is.
    total = None
    if photometric_type == 1:
        if n_horizontal == 1:
            weights = [1.0]
        else:
            span = horizontal[-1] - horizontal[0]
            weights = []
            for h in range(n_horizontal):
                lower = horizontal[h - 1] if h > 0 else horizontal[h]
                upper = horizontal[h + 1] if h < n_horizontal - 1 else horizontal[h]
                weights.append((upper - lower) / 2.0 / span)
        total = 0.0
        for h in range(n_horizontal):
            plane = 0.0
            for v in range(n_vertical - 1):
                a, b = math.radians(vertical[v]), math.radians(vertical[v + 1])
                mean = (candela[h][v] + candela[h][v + 1]) / 2.0
                plane += mean * 2.0 * math.pi * (math.cos(a) - math.cos(b))
            total += plane * weights[h]
    peak = max(max(row) for row in candela)
    return {"file": path, "header": header[:12], "lamps": lamps, "lumens_per_lamp": lumens_per_lamp, "multiplier": multiplier,
            "ballast_factor": ballast, "vertical_angles": [vertical[0], vertical[-1], n_vertical],
            "horizontal_angles": [horizontal[0], horizontal[-1], n_horizontal], "photometric_type": photometric_type,
            "units_1_feet_2_metres": units, "width_length_height": [width, length, height], "input_watts": watts,
            "peak_candela": round(peak, 1), "lumens_from_table": None if total is None else round(total, 1)}


if __name__ == "__main__":
    for name in sys.argv[1:]:
        try:
            print(json.dumps(read(name)))
        except Exception as error:  # a file that does not follow the format
            print(json.dumps({"file": name, "error": repr(error)}))
