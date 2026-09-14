from pathlib import Path
import json,zipfile,shutil,xml.etree.ElementTree as ET,hashlib
r=Path(__file__).resolve().parent
d=json.loads((r/'sliced/result.json').read_text())
assert d['return_code']==0
assert [len(p['objects']) for p in d['sliced_plates']]==[15,10]
assert all(not p['warning_message'] for p in d['sliced_plates'])
source=r/'sliced/QuietMount_H2D_PolyTerra_sliced.3mf'
with zipfile.ZipFile(source) as z:
    assert z.testzip() is None
    cfg=json.loads(z.read('Metadata/project_settings.config'))
    assert cfg['printer_model']=='Bambu Lab H2D'
    assert cfg['curr_bed_type']=='Textured PEI Plate'
    assert float(cfg['layer_height'])==.08
    warnings=[e.attrib for e in ET.fromstring(z.read('Metadata/slice_info.config')).iter('warning')]
    assert all(w['msg']=='bed_temperature_too_high_than_filament' for w in warnings)
    for i in [1,2]:
        data=z.read(f'Metadata/plate_{i}.gcode')
        assert len(data)>100000
        assert hashlib.md5(data).hexdigest().upper()==z.read(f'Metadata/plate_{i}.gcode.md5').decode().strip().upper()
        (r/f'plate_{i}_preview.png').write_bytes(z.read(f'Metadata/plate_{i}.png'))
shutil.copyfile(source,r/'QuietMount_H2D_PolyTerra_READY.3mf')
report={'slicer':'Bambu Studio 02.08.00.50','result':'success','plates':2,'parts':25,
        'geometry_warnings':[], 'remaining_advisories':warnings,
        'estimated_seconds':sum(p['total_predication'] for p in d['sliced_plates']),
        'estimated_grams':sum(p['filaments'][0]['total_used_g'] for p in d['sliced_plates']),
        'physical_print_test':False}
(r/'verification.json').write_text(json.dumps(report,indent=2))
guide='''# QuietMount — five holders, Bambu H2D / PolyTerra PLA

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
'''
(r/'START_HERE.md').write_text(guide,encoding='utf-8')
shutil.copyfile(r.parent/'sample-holder-v2-minimal/README.md',r/'Assembly.md')
for name in ['minimal-preview.png','concealed-mechanism.png']:
    shutil.copyfile(r.parent/'sample-holder-v2-minimal'/name,r/name)
files=['QuietMount_H2D_PolyTerra_READY.3mf','START_HERE.md','Assembly.md','verification.json',
       'plate_1_preview.png','plate_2_preview.png','minimal-preview.png','concealed-mechanism.png',
       'presets/QuietMount_Process.json','presets/QuietMount_PolyTerra_PLA.json']
with zipfile.ZipFile(r/'QuietMount_H2D_Five_Holders.zip','w',zipfile.ZIP_DEFLATED) as z:
    for f in files:z.write(r/f,f)
    for p in (r/'parts').glob('*.stl'):z.write(p,'STLs/'+p.name)
with zipfile.ZipFile(r/'QuietMount_H2D_Five_Holders.zip') as z:assert z.testzip() is None
print(json.dumps(report,indent=2))
