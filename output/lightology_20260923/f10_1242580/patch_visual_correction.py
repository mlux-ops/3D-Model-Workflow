from pathlib import Path
p = Path(r"output\lightology_20260923\f10_1242580\build_covet.py")
s = p.read_text(encoding="utf-8-sig")
s = s.replace(
"""        gloss=.22, transparency=.10, reflectivity=.12,
        emission=55, cct=2700, material_class='Stone')""",
"""        gloss=.20, transparency=.02, reflectivity=.10,
        emission=350, cct=2700, material_class='Stone')""")
s = s.replace(
"""    stone = loft_square(0.50, 8.75, 2.75, 9.125)
    f.add('Tapered alabaster body', stone, alabaster)

    clip_w = 2.60
    z0, z1 = 1.35, 2.62
    f.box('East brass prong', 8.91,-clip_w/2,z0, 9.13,clip_w/2,z1, brass, rounding=.04)
    f.box('West brass prong', -9.13,-clip_w/2,z0, -8.91,clip_w/2,z1, brass, rounding=.04)
    f.box('North brass prong', -clip_w/2,8.91,z0, clip_w/2,9.13,z1, brass, rounding=.04)
    f.box('South brass prong', -clip_w/2,-9.13,z0, clip_w/2,-8.91,z1, brass, rounding=.04)""",
"""    # Exact option imagery and manufacturer-reference bounds show the ceiling-side stone edge
    # is the widest portion, with a narrower exposed underside.
    stone = loft_square(0.50, 9.125, 2.75, 8.75)
    f.add('Tapered alabaster body', stone, alabaster)

    # Two large opposite-side brass retainers. Manufacturer reference RFA contains two
    # solids approximately 1.60 in x 3.02 in x 11.01 in; the exact option photo shows
    # these as the two prominent side retainers. They seat into/overlap the stone body.
    retainer_w = 1.60
    retainer_len = 11.00
    f.box('East brass retainer', 7.525,-retainer_len/2,0.50, 9.125,retainer_len/2,2.75, brass, rounding=.04)
    f.box('West brass retainer', -9.125,-retainer_len/2,0.50, -7.525,retainer_len/2,2.75, brass, rounding=.04)""")
s = s.replace(
"Stone side taper and brass prong sizes/positions are photo/drawing-derived approximations.",
"Stone taper direction is photo/drawing-derived; two brass retainer dimensions are informed by native manufacturer-reference solid bounds and exact option photography.")
p.write_text(s, encoding="utf-8")
