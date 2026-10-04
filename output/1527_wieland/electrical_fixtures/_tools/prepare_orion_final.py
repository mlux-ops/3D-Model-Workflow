"""Stage only the remaining Orion family using the reviewed US specification."""
from pathlib import Path
from PIL import Image
import json

ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'Best_option_-_Orion_Tube_Pendant__1967952628416388'
source=folder/'source'
materials=[
    dict(label='Metal Finish',rgb=[193,152,80],gloss=.90,reflectivity=.65),
    dict(label='Opal Tube Finish',rgb=[244,244,238],gloss=.20,transparency=.06,reflectivity=.03,material_class='Plastic'),
    dict(label='Clear Cord Finish',rgb=[219,224,225],gloss=.35,transparency=.55,reflectivity=.04,material_class='Plastic'),
    dict(label='Tensile Wire Finish',rgb=[176,182,185],gloss=.65,reflectivity=.45)]
job=dict(key='ORION_TUBE_UNSPECIFIED',manufacturer='Lee Broom',model='ORI0120 - ASSUMED FINISH / HORIZONTAL',
    name='Lee_Broom_Orion_Tube_ORI0120_Horizontal_Assumed_R2025',host='ceiling',
    dimensions=[36.125,5.125,48.0],body_dimensions=[34.5,5.125,5.125],
    source_url='https://leebroom.com/wp-content/uploads/2026/06/Orion-Tube-Light_0626REV21.pdf',
    source_page=2,materials=materials,out=str(folder),
    notes='Current manufacturer US specification EN 0626rev21 page 2: body 34.5 inches long and 5.125-inch globe; two 1.625-inch diameter by 0.625-inch high mini canopies. US printed inches control; corresponding metric labels are rounded and differ by up to 1.3 mm. These current dimensions supersede legacy 88.5-cm web and 2019 CAD length. Overall mounting envelope is 36.125 inches including mini canopies centered over the body ends; body is checked independently. ASSUMPTION: polished gold ORI0120, single horizontal module, 48-inch installed drop, globe center at one-quarter body length, 30-mm opal tube diameter from manufacturer EU product text, and small end-cap/cable sizes. Inventory names Orion Tube but specifies no finish, code or configuration. This is a reviewable representative family; exact finish, orientation, array and installed drop remain NEEDS_USER_ORION_CONFIGURATION. Remote driver and optional covers are not included. No engineering connectors or photometric source. Editable materials; fixed dimensional geometry.')
textures=source/'textures';textures.mkdir(exist_ok=True)
for m in materials:
    Image.new('RGB',(32,32),tuple(m['rgb'])).save(textures/(m['label'].replace(' ','_')+'.png'))
(source/'orion_definition.json').write_text(json.dumps(job,indent=2),encoding='utf-8')
(source/'SOURCE_REVIEW.md').write_text('''# Orion source review - 2026-10-02

Inventory rows 1967952628416388 and 7223540899774340 name Orion Tube only. The exact finish, orientation, quantity of connected modules and installation drop are unspecified.

The anonymous manufacturer Orion-1.zip passed CRC. Its 2019 Orion Tube RFA opens in Revit 2025 and an upgraded source copy is preserved. It contains one imported solid as Generic Models, has no product identity or editable material assignment, and measures approximately 34.7835 x 5.1153 x 5.1181 inches. It is source evidence, not the final face-based family.

The current manufacturer PDF is EN 0626rev21. Page 2 is the 110-130 V US sheet. Its actual image was reviewed: a long opal tube with an off-center polished metal globe, two suspension points, and two mini canopies. The globe is near one quarter of the tube length, not central. The Tube product has a metal globe and luminous tube; the alternate Globe product reverses those materials.

Use printed US dimensions 34-1/2 inch body and 5-1/8 inch globe. Mini canopies are 1-5/8 inch diameter by 5/8 inch high. Metric labels 875/130/40/15.5 mm are rounded differently. The older public product-page 885 mm length and the source RFA do not override this dated sheet. The overall ceiling-attachment width includes the two end canopies and is therefore 36.125 inches. Separate component checks measure the actual 34.5-inch body.

ASSUMPTION: gold ORI0120, horizontal single module, 48-inch drop. This creates a concrete visualization candidate without treating an unspecified procurement choice as approved. NEEDS_USER_ORION_CONFIGURATION remains for final finish, orientation, array and drop. Diameter of the acrylic tube is 30 mm from the manufacturer EU listing; globe location, cable diameters and small ferrules are drawing-derived/inferred.

Sources:
- https://leebroom.com/wp-content/uploads/2026/06/Orion-Tube-Light_0626REV21.pdf
- https://leebroom.com/wp-content/uploads/2025/07/Orion-1.zip
- https://www.leebroomeu.com/products/orion-light-gold
- https://leebroom.com/lighting/orion-tube-light-polished-gold/

The current public gold URL has an inconsistent Gunmetal page heading; the PDF product-code table is used for ORI0120 polished gold. No login, account creation or license acceptance was used. Manufacturer copyright remains with Lee Broom. Original downloads are retained unchanged.
''',encoding='utf-8')
print('Orion definition and four companion bitmaps staged.')
