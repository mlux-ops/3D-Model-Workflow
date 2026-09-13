# QuietMount — five holders, Bambu H2D / PolyTerra PLA

Open **QuietMount_H2D_PolyTerra_READY.3mf** as a project in Bambu Studio. It contains the editable models, two arranged plates, embedded settings and the verified sliced toolpaths. Created with Bambu Studio 02.08.00.50; use that version or a newer compatible release. If your version requests re-slicing, keep the project presets and slice both plates.

## Included

| Set | Sample thickness | Quantity |
|---|---:|---:|
| A | 12.700 mm | 1 holder |
| B, C, D | 19.050 mm | 3 holders |
| E | 22.225 mm | 1 holder |

There are **25 printed parts**: five frames, five carriages, ten lower hooks and five upper hooks. The E filenames display 22.23 mm; their geometry uses 22.225 mm. All parts remain at 100% scale.

Plate 1 contains the 15 small hooks. Viewed from above, columns left to right are A, B, C, D, E. Each column has two lower hooks toward the front and its upper hook at the back. Plate 2 contains five identical frames and five identical carriages. Print both plates once. Supports and carriage brims are already configured; preserve the supplied orientations.

## Quality configuration

- Bambu H2D, standard-flow 0.4 mm nozzle, Textured PEI Plate; single-color PolyTerra PLA.
- 0.08 mm layers, 0.20 mm first layer; six walls.
- 25 mm/s outer walls and top surfaces; 800 mm/s² outer-wall acceleration.
- Solid hooks; 45% gyroid frame/carriage infill; 1.0 mm top and 0.8 mm bottom thickness.
- Nozzle 220°C first layer / 215°C thereafter; plate 55°C throughout.
- Bambu PolyTerra flow baseline 0.98; volumetric cap 8 mm³/s; auxiliary fan off.
- Snug supports on the concealed frames and carriages; hooks need no supports. Carriages have 3 mm outer brims.

The process and filament JSON files in `presets` are also supplied separately. The project already contains them, so a separate import is unnecessary for this print. Use Bambu Studio's Import Configs option if you want reusable user presets. The standard H2D printer configuration is embedded in the project.

## Before printing

Select the actual PolyTerra spool/AMS slot in the print dialog; its displayed green project color is only a placeholder. Confirm your installed nozzle is standard-flow 0.4 mm. If you use a high-flow nozzle, choose its actual printer variant and re-slice.

Clean the textured plate and use dry filament. For best dimensional fit, calibrate flow ratio and flow dynamics with this spool, then re-slice if the calibration changes the profile. Leave the enclosure ventilated for PLA. Bambu retains its enclosure/bed-temperature advisory (`bed_temperature_too_high_than_filament`) at the configured 55°C; this is not a geometry or slicing failure.

Estimated total: **22 h 35 min, 116 g**. Plate 1: approximately 4 h 24 min / 20 g. Plate 2: approximately 18 h 11 min / 96 g. Estimates vary with printer preparation and calibration.

Remove supports and brims carefully, especially around the carriage slide, nut pockets and keyed upper-hook socket. Test-fit one complete holder before mounting all five. The geometry and slicing are checked; physical fit, appearance and sustained load capacity in PolyTerra PLA have not been tested.

## Hardware for all five holders

- 20 M2.5 × 8 mm 90° flat-head screws (head diameter at most 5.6 mm), and 20 ordinary M2.5 nuts.
- 10 M3 × 25 mm socket-head screws, and 10 ordinary M3 nuts.
- 10 suitable wall screws/anchors; shank at most 4.5 mm.
- Optional five small M3 washers for the vertical retaining screws.

See `Assembly.md` for the assembly sequence and dimensions. This PLA project overrides the generic material and print-setting suggestions in that original design guide.

Settings use the installed official Bambu H2D and PolyTerra profiles as their base. Reference: https://github.com/bambulab/BambuStudio/tree/master/resources/profiles/BBL and https://polymaker.com/product/polyterra-pla/ . The tuning is a conservative quality starting point, not a substitute for calibration of your specific spool.
