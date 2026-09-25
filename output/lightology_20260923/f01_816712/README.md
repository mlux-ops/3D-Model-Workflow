# F01 - Maverick II 52 in Matte Black

This folder owns the Revit 2025 face-based Lighting Fixtures reconstruction for Visual Comfort Fan Maverick II 3MAVR52BKBKD / Lightology MTC816709.

The builder is build_f01_816712.py. It creates a 52 inch, 19.8 inch high family with three sculpted lofted wood blades, Matte Black body/blade materials, integrated 3000 K diffuser, editable material parameters, and native validation/reporting.

Blade construction is a nine-section 3D loft rather than a flat extrusion. The sections vary width, backward sweep, thickness, center height and twist from root to tip to match the preserved Lightology product/application images.

Native acceptance requires:
- Revit 2025 save and reopen.
- Lighting Fixtures category and face-based placement.
- Actual hosting to a native overhead floor face in a disposable project.
- Downward orientation from the host.
- Measured 52 in sweep and 19.8 in overall height.
- Material substitution reaching blade geometry.
- Zero Revit warnings.
- Front, side, oblique, material-QA and hosted image exports.
- Visual comparison against sources in sources/.
