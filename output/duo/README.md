# Astro Duo Pendant - visualization family

Revit 2025 face-based Lighting Fixtures family, reconstructed from the supplied product PDF, dimension drawing, and two photographs. Place on the underside of a native ceiling or other horizontal overhead face. The mounting origin is the center of the canopy at the ceiling surface; the pendant projects away from that face.

## Size and geometry

- Shade assembly: 210 mm diameter and 210 mm high, from the dimension drawing. The 8.27-inch labels are rounded conversions.
- Both rounded sections are 105 mm high, derived from the drawing's equal halves and circular side profiles. They are smooth analytic revolved shells, with a visible opening around the upper stem.
- Default overall ceiling-to-bottom drop: 1,000 mm. This is an installation assumption, not a product specification.
- Photo-estimated details: 96 mm canopy diameter, 24 mm canopy depth, 16 mm stem diameter, 65 mm stem height above the upper shade, 4 mm cord diameter, 96 mm top opening, and 3 mm shell thickness. Hidden construction is simplified.
- This version has fixed geometry. Its dimension parameters report that geometry; they are not controls for changing the suspension length.

## Materials

Three editable type material parameters: Metal Finish, Opal Glass Finish, and Cord Finish. The supplied PDF specifies matte white metal and opal glass. The lower glass has a soft warm self-illuminated appearance, as requested. The 2700 K appearance temperature and luminance are artistic settings, not manufacturer photometric data.

The appearance uses native Revit assets without external texture dependencies. The cable is a smooth white cord; its fine braid is not modeled. No IES, MEP connectors, or photometric light source is provided. The glow is a material appearance, not a verified source of room illumination.

## Review

Front, oblique, and full-pendant previews are exported from Revit. Shaded previews show geometry, not the final warm glow. The cord is hidden only in the close-up review views. Final material appearance depends on the scene, exposure, and rendering settings. The automatic Realistic viewport did not demonstrate the requested glow reliably, so that image is excluded from the package; the saved self-illumination settings were verified, but a project rendering remains to be reviewed.

The validation report checks the saved/reopened family, dimensions, placement on a native overhead face, downward orientation, editable material bindings, and warnings. A disposable project is used for testing; no existing user project is modified.

Validation passed in Revit 2025 with no family or test-project warnings. The diameter is measured by intersections through the saved analytic curved shell; Revit's display-derived bounding box slightly underestimates one radial extent, and both measurements are retained in the report.

The references govern visual reconstruction only. No manufacturer RFA was copied or used as geometry.
