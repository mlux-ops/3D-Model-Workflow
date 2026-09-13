# PolyTerra adaptation of your SHB process

Import both JSON files with Bambu Studio's File > Import > Import Configs. Select the SHB PolyTerra process AND filament preset. Keep the H2D standard 0.4 mm nozzle and Textured PEI printer/plate selections. Your original file is unchanged.

## Review

Your source is a process preset derived from `0.08mm Extra Fine @BBL H2D`. It does not set filament temperature, fan behavior, flow ratio or volumetric limits. Its Inland name alone does not define any Inland material settings. It retains five H2D extruder-variant entries, with `nil` in the TPU variant; these are intentional inheritance values and are preserved.

The source already has useful quality settings: 18 mm/s first-layer walls and infill, 250 mm/s² first-layer acceleration, 0.8 mm top/bottom skins, three walls, 0.006 mm resolution, 0.1 mm elephant-foot compensation, precise outer walls and avoidance of unnecessary wall crossings. These remain unchanged. Wrapping detection is retained; detection by itself does not prevent lifting.

## Changes

| Setting | Original | PolyTerra copy |
|---|---:|---:|
| Outer-wall speed | 55 | 35 mm/s |
| Inner-wall speed | 90 | 60 mm/s |
| Top-surface speed | 40 | 25 mm/s |
| Internal-solid speed | 80 | 60 mm/s |
| Bridge speed | inherited 50 | 25 mm/s |
| Outer-wall acceleration | 1000 | 800 mm/s² |
| Inner-wall acceleration | 2200 | 1500 mm/s² |
| Travel speed / acceleration | 400 / 8000 | 300 mm/s / 5000 mm/s² |
| First-layer flow multiplier | 1.02 | 1.00 |
| Top surface | inherited | Monotonic line |

The bottom remains Monotonic line. The Textured PEI surface still determines the texture of a bed-facing face; monotonic extrusion will not make it smooth. Ironing is not forced globally. For the screwless holders, retain the adhesive wall plates' existing face-up orientation and per-object ironing.

The 1.02 first-layer multiplier is not necessarily wrong, but it is an uncalibrated extra 2% of extrusion. Starting at 1.00 avoids stacking it onto the filament flow ratio. If a properly cleaned plate and calibrated extrusion still show first-layer gaps, adjust from an actual first-layer test.

## Companion filament preset

Based on the installed official `PolyTerra PLA @BBL H2D` profile, preserving its material identity, compatible printers and retraction behavior:

- Nozzle: 220°C first layer, 215°C thereafter.
- Textured PEI: 55°C throughout.
- Flow ratio: official Bambu baseline 0.98; calibrate for your spool.
- Volumetric limit: conservative 8 mm³/s instead of the stock 22 mm³/s.
- Auxiliary fan off; part cooling off for the first two layers, 100% thereafter, with small-layer slowdown enabled.
- Minimum layer time target 10 s, minimum speed 15 mm/s. Geometry can prevent reaching that target.

These are quality-oriented starting values, not measured optimal settings for your spool. At 0.08 mm layers the chosen wall speeds are generally below the volumetric cap already. Its main benefit is limiting faster/wider extrusion elsewhere; it does not inherently improve a print already below the cap.

Polymaker lists 190–230°C nozzle and 25–60°C bed for the current Panchroma Matte product described as formerly PolyTerra. The selected temperatures are inside that range. Bambu may show its PLA bed-temperature/enclosure advisory at 55°C; ventilate the enclosure for PLA.

## Using with the sample holders

This preserves the source's three-wall general process. Use the existing holder project's stronger per-object settings or set six walls for structural holder parts. Preserve its per-object infill, supports, brims and adhesive-pad ironing. Selecting a new process does not replace the need for those geometry-specific settings. Re-slice after changing presets; existing G-code retains the previous settings.

The presets were accepted by the installed Bambu Studio and key effective settings were checked in its exported project. No physical print, flow calibration or comparison print was performed. The existing five-holder project was not modified.

Sources:
- Official Polymaker temperature guidance: https://shop.polymaker.com/products/matte-pla
- Official Bambu profiles: https://github.com/bambulab/BambuStudio/tree/master/resources/profiles/BBL
- Local baseline: C:/Program Files/Bambu Studio/resources/profiles/BBL/filament/PolyTerra PLA @BBL H2D.json
