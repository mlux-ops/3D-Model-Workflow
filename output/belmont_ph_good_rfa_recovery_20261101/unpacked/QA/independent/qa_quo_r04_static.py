"""Independent CPython preflight for Quorum 858-59 R04 script geometry.

No Revit process, mutations, or source file replacement.
"""
import ast
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "build_quo_858_59_r04.py"


def main():
    code = SCRIPT.read_text(encoding="utf-8")
    module = ast.parse(code, filename=str(SCRIPT))
    values = {}
    for node in module.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in ("PROFILE_DOWN", "CANOPY_H", "STEM_H", "BODY_H", "SHADE_H", "GLASS_WALL"):
                values[node.targets[0].id] = ast.literal_eval(node.value)
    profile = values["PROFILE_DOWN"]
    assert len(profile) >= 8
    assert profile[0][0] == 0.0
    assert abs(profile[-1][0] - 11.25) < 1e-8
    assert all(profile[i][0] < profile[i+1][0] for i in range(len(profile)-1))
    assert abs(2*max(r for z, r in profile) - 11.0) < 1e-8
    assert profile[0][1] < max(r for z,r in profile)
    assert profile[-1][1] < max(r for z,r in profile)
    assert profile[-1][1] > profile[0][1]
    assert min(r for z,r in profile) > values["GLASS_WALL"]
    assert values["CANOPY_H"] == 0.75
    assert values["STEM_H"] == 24.0
    assert values["BODY_H"] == 19.0
    assert values["SHADE_H"] == 11.25
    assert "R04_PHOTO_DERIVED_UNAPPROVED" in code
    assert "NOT PROVIDED" in code
    assert "CreateRevolvedGeometry" in code
    assert "f.text('Retailer SKU'" not in code
    print("PASS: profile, dimensions, open annular section, finish and source status")
    print("Glass profile: %d stations, OD 11in, H 11.25in, neck %.2fin radius, base %.2fin radius" %
          (len(profile), profile[0][1], profile[-1][1]))
    print("Installed exemplar drop: %.2fin" % (values["CANOPY_H"]+values["STEM_H"]+values["BODY_H"]))


if __name__ == "__main__":
    main()
