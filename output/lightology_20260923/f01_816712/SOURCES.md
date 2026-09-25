# F01 source record - Visual Comfort Fan Maverick II

Assigned Lightology page:
https://www.lightology.com/index.php?module=prod_detail&prod_id=816712&option_id=816709

Verified selected option:
- Product: Maverick II Indoor / Outdoor Ceiling Fan with Light
- Brand: Visual Comfort Fan
- Lightology spec: MTC816709
- Manufacturer ID: 3MAVR52BKBKD
- Finish: Matte Black
- Blade span: 52 in
- Overall height: 19.8 in
- Blade count: 3
- Nominal blade pitch: 13 degrees
- Included downrod: 6 in
- Integrated LED: 18 W, 3000 K, 90 CRI, 1100 delivered lumens
- High airflow: 6928 CFM
- Damp location, DC motor, ETL, Energy Star

Preserved local image references:
- sources/816709_product.jpg - selected option product image from Lightology.
- sources/3MAVR52BKBKD_app1.png - 52 in BKBKD application image.
- sources/maverick_add1.png - Lightology application/detail image.
- sources/maverick_add2.png - Lightology close-up/detail image.

Source URLs:
- Product image: https://www.lightology.com/img/prod/650/816709.jpg
- 52 in application image: https://www.lightology.com/img/prod/650/MC_Maverick-II_BKBKD_APP1_3MAVR52BKBKD.jpg
- Additional image 1: https://www.lightology.com/img/prod/650/mtc-maverickiiled-add1.jpg
- Additional image 2: https://www.lightology.com/img/prod/650/mtc-maverickiiled-add2.jpg
- Specification sheet endpoint: https://www.lightology.com/index.php?module=pdf_specification_sheet&prod_id=816709
- Installation instructions: https://www.lightology.com/img/prod/pdf/montecarlo-maverickiiled-install.pdf

Visual observations from the preserved images:
- The three blades are sculpted wood forms, not planar paddles or triangles.
- Each blade leaves the motor through a narrow neck, widens into a broad rounded paddle in the outer third, then closes with a soft rounded tip.
- The planform sweeps backward progressively from root to tip.
- The blade face visibly twists/cambers: root pitch is stronger and relaxes toward the tip while the product's nominal pitch is 13 degrees.
- The blade thickness is visibly greatest near the root and thins toward the rounded end.
- The motor housing is compact and smoothly tapered into the blade roots; the integrated opal light sits directly below the hub.

Modeling interpretation:
Printed Lightology dimensions override image proportions. The builder uses CreateLoftGeometry through nine 3D cross-sections per blade, varying tangential width, aft sweep, thickness, center elevation and twist. Root and tip twist values are photo-derived to reproduce the visible sculptural transition; the 13 degree product pitch remains recorded as the authoritative nominal pitch parameter. Canopy, motor-shell and diffuser diameters are also photo-derived.
