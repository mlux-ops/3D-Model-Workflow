# Malibu II RF visualization review

Reference: official Icera C-6360 two-page specification, preserved in this package. Geometry is an independent reconstruction.

Reviewed the native Revit front, side, top and oblique exports against the manufacturer photo and dimension drawing. The model retains the compact round-front silhouette, taller integrated tank, narrower floor skirt, closed seat/lid, and observer-left tank lever. The initial bowl underside extended too far rearward; the revised lower contours shorten that underside and provide a rounded rise toward the tank. Lid and tank interpolation were revised after native surface checks detected overshoot.

The model is suitable for architectural visualization. Small ceramic blend radii, lid crown, lever size, bolt covers, and material response remain estimates. Bowl interior, trapway, hinges hidden by the closed lid, and ceramic wall thickness are omitted. This is not manufacturer-authored BIM or fabrication geometry. The fixed dimension parameters describe nominal product dimensions, not adjustable geometry controls.

Technical verification: saved and reopened in Revit 2025; Plumbing Fixtures category; placed on a disposable project's native floor face; family mounting axis aligned with the host normal; Ceramic Finish, Seat Finish and Lever Finish each changed and restored successfully. Family and disposable-project warnings are recorded in validation.json. The temporary project was closed without saving.

Both Revit display bounds and triangulated surface bounds are recorded. Display bounds may conservatively enclose curved surfaces; triangulation is sampled and is not an exact extrema proof. The lever projects outside the specified tank width. Use the manufacturer's specification for installation layout and clearances.

Preview images use Revit's default lighting; white upper surfaces have low contrast against the white background. The material review is a viewport appearance check, not a calibrated production render.
