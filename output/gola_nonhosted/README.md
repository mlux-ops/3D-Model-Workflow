# Richelieu Gola profiles — non-hosted Generic Model versions (Revit 2025)

Converted 2026-09-25 from the line-based families in `F:\My Drive\3D Model Workflow\`:

| Source (line based) | Converted (non-hosted) |
|---|---|
| `Richelieu_Gola_L_Channel_Horizontal_2025.rfa` | `Richelieu_Gola_L_Channel_Horizontal_NonHosted_2025.rfa` |
| `Richelieu_Gola_Vertical_Double_Grip_2025.rfa` | `Richelieu_Gola_Vertical_Double_Grip_NonHosted_2025.rfa` |

`Richelieu_Gola_L_Channel_Horizontal_2025.0001.rfa` is an older Revit backup of the horizontal file. It was not converted.

## What changed

- **Template:** built from `Generic Model.rft`. The result is one-level based and not work-plane based, so it places with a single click on a level, with no line and no host.
- **Length:** the line length is now an ordinary instance parameter named **Length** (default 1000 mm). A labelled **Channel End** reference plane gives a drag arrow on placed instances. Every solid, end cap, clip, bracket and corner-joint position still follows it through your original formulas.
- **Orientation:**
  - Horizontal: runs along X, with the profile height upright.
  - Vertical: runs up (Z).
  - In both, the mounting plane is the family's front/back centre plane, and the profile's depth sits behind it (+Y). Rotate in plan to face a cabinet front.
- **Placement Plane (horizontal only):** your "Placement Plane" (48.05 mm from the channel back, set to Defines Origin) is honoured. The channel sits 21.05–48.05 mm behind the mounting plane, exactly as the line-based original did.
- **Kept:** all 77 parameters with their formulas and type values, both types' materials, subcategories, and "Cut with Voids When Loaded". The recess void's end is now tied to Length, so it keeps the full run instead of stopping at 1000 mm.

## Limitations

- **Recess dimension labels:** "Recess lower edge" and "Recess upper edge" are recreated at their exact positions, but their two labelled dimensions are not.
  - *Effective Recess Clearance* is 0.5 mm, below Revit's 0.8 mm short-curve limit, so the API cannot draw it.
  - Labelling *Recess Opening Width* against its formula makes Revit roll back the transaction.
  - Both parameters and formulas are kept, and no geometry depends on those planes. Re-add the labels by hand if you want them to move with the parameters.
- **Sketch constraints:** the ~190 sketch constraints inside each solid (for example, the void outline locked to the channel edges) do not carry across a copy. The shapes are identical, but editing a sketch won't re-snap to those references.
- **Horizontal channel volume:** 2.795 mm³ larger per 1000 mm (0.0023 %). Face topology (32 faces) and extents are identical to 0.01 mm, and the source has no void cut or geometry combination. The cause is unconfirmed, probably a sub-micron sketch re-solve. The vertical family matches exactly.

## Verification (Revit 2025.4, headless, `validation.json`, re-checked by `verify_nonhosted.py`: all gates pass)

Each family was:

- saved and reopened, and confirmed OneLevelBased and not work-plane based;
- checked for form count and solid volume against the source, and for every parameter link restored (horizontal 52, vertical 35);
- placed in a disposable project with no host;
- flexed to Length 600 / 1000 / 2400 mm, with the run following exactly;
- compared with the original line-based family placed on a 1000 mm line in the same project. Volume and extents match (horizontal within the tolerance above).

Close-up previews are in `preview/`.

## Re-running

```
pyrevit run "<repo>/output/gola_nonhosted/convert_gola_nonhosted.py" --revit=2025
python "<repo>/output/gola_nonhosted/verify_nonhosted.py"
```

The converter reads copies of the sources in `source/` and writes only inside this folder. Attempt RFAs and diagnostic probes are kept in `logs/`.
