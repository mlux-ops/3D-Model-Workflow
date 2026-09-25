# Lightology: 12 fixtures / 14 face-based RFAs

Release: Revit 2025, revision 1, 2026-09-23 task.

## Load and place

Extract the ZIP before use. Load the 14 files in `RFAs` with Revit's Load Family command. Place a component using **Place on Face**, selecting the wall face for sconces or the underside of a native ceiling/floor face for overhead fixtures. These are genuine face-based Lighting Fixtures families; they report WorkPlaneBased in the API and have face-hosting behavior 5. Rotate the placed instance as needed. Materials are editable through the named family type parameters.

For Covet, add the extracted `Textures` folder under **File > Options > Rendering > Additional render appearance paths**. Its alabaster image is used by both diffuse and luminous color. Revit first checks the original bound path, then its additional render-appearance search folders. Keep the companion image with the family package. The final native review verified the bound image, its hash and material persistence in a fresh project on this workstation. Autodesk instructions: https://help.autodesk.com/cloudhelp/2022/ENU/Revit-Customize/files/GUID-232814AE-2B53-4452-B6ED-379A5C721706.htm

## What is included

Fourteen final RFAs, the required alabaster texture, a visual catalog, individual preview images, a fixture/variant catalog and independent native/prime review records. The separate Source and Review archive preserves source references, native views, readable build scripts, mesh-based render evidence and historical working records. Only the RFAs in this main package are the approved release.

## Accuracy and use

All 14 current files passed native reopening, Lighting Fixtures category, face-template behavior, actual face hosting and orientation, measured geometry, every associated material parameter affecting all its assigned faces, family-to-project appearance persistence, required CCT/texture checks and zero family/project warnings. The review records identify the exact SHA-256 of each RFA. Nominal dimensions and source/inference decisions are in `FIXTURE_CATALOG.md`.

These are fixed-geometry visualization families. Suspension lengths and fan blade placement are not user-flexible dimensions; editable numeric labels do not imply a geometry flex feature. The delivered installation choices are stated in the catalog. There are no MEP connectors, electrical circuits or IES photometric sources. Material glow/CCT provides appearance, not a lighting calculation.

Product photographs, drawings and available manufacturer models guided silhouettes, proportions, openings and finish selection. Undimensioned contours, hidden details, glass thickness and exact optical response are documented reconstructions. Stone veining and handcrafted crystal forms naturally vary. Studio proofs were rendered from the actual saved RFA meshes and saved appearance inputs using Cycles; shader translation is approximate and is not a native Revit photometric-render claim. Revit Realistic viewport lighting may differ from these studio images. Covet's catalog view isolates its saved luminous-color bitmap under normalized emission to show the natural pattern; this is an appearance review, not a calibrated luminance claim.

## Important selection decisions

The exact Maverick manufacturer specification gives a 52 in sweep and 13.8 in height with the included 6 in downrod; it overrides the retailer's conflicting 19.8 in listing. Madame's listed 2.36 in width refers to the shade; the modeled larger wall canopy is 4 in by drawing proportion, explicitly inferred. Mizu uses the requested 3000 K LED option rather than the linked Xenon default. Vantage uses the 11 in Coal option; Orbel uses Natural Brass rather than the linked Aged Brass default.

The Forked default visible cord is 18 in (37.82 in total drop); Cassia uses 12 in rods (15.875 in total drop); Mizu uses its 19.7 in minimum overall installation.

## Production record

One worker was assigned to each fixture. The connector exposed model `5.6` with `xhigh`; an exact `Sol` suffix was not verifiable. Stalled-worker and review corrections were completed by the prime. No commits, merges or pushes were performed.
