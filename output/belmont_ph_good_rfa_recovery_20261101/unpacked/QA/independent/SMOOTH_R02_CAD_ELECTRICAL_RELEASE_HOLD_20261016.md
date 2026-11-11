# 651 Belmont PH Good | Smooth FR-W2502-52L-SB/MB | CAD finish and electrical release audit

**2026-10-16 — Read-only result: R02 geometry/material QA PASS; R03 import recolor NOT AUTHORIZED by evidence. No native Revit execution performed in this investigation.**

## Basis and final finish decision

- Saved R02: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\candidates\ModernForms_Smooth_FR-W2502-52L_SBMB_R2025_R02_PARTIAL_UNAPPROVED.rfa`, SHA-256 `f1741c711a07a26101c550b580a2db6be99bc4d3689cb75104eaafb0834379db`.
- Independent native R02 QA: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\smooth_sbmb_r02_native_qa.json`; status `NATIVE_MATERIAL_AND_SWEEP_PASS_VISUAL_HOLD`. Placed, ceiling-face hosted `WorkPlaneBased`; 27 solid elements; swept diameter **1321.692520585 mm** vs. manufacturer 52 in / 1320.8 mm, error **0.892521 mm** inside established 1 mm tolerance; zero family/project warnings. Original inputs unchanged.
- R02 visible finish: three Matte Black blades, Soft Brass outer housing/downrod/canopy. Preview `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\previews_r05\smooth_oem_oblique.png` shows gray/silver lower light ring and inner top-of-canopy hardware.
- Primary photo/finish authority: [Modern Forms Smooth](https://modernforms.com/product/smooth/), [official specification](https://modernforms.com/images/products/SPECSHEET_PDF/FR-W2502_SPSHT.pdf), [manufacturer photo gallery listing exact SBMB views](https://modernforms.com/current-images-and-documents/), and [exact SKU assembly photo](https://www.beeslighting.com/products/modern-forms-fr-w2502-52l-sb-mb-smooth-52-inch-cct-led-smart-ceiling-fan-soft-brass-with-matte-black-blades). The manufactured configuration includes a **Soft Brass body, three Matte Black blades, and an opal LED lens**; an included optional blank cover replaces the light for fan-only use. The visible external underside has a brass metal bezel and an opal-white diffuser, while exposed mounting internals are not specified as finished brass.

The remaining CAD geometry cannot safely be globally recolored. There is no part-colored OEM mesh, distinct physical layer per material, manufacturer part legend, or inspected isolated visual evidence correlating each embedded ImportInstance solid to Soft Brass / Matte Black / opal lens / concealed metal. **Do not create or run a mutating R03 family script on the current evidence.**

## Thirteen imported OEM CAD objects: actual native face/layer state

Probe: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\inspect_oem_material_parts.json` (SHA-256 `2ee88654c081a629fa324681703497a72adff29a2481a676f51b98d03b2213b3`). Exact IDs refer to the original OEM-derived RFA family, not the loaded project element IDs.

Every ID below is `Autodesk.Revit.DB.ImportInstance` with **all 21 numeric import subcategories `0`–`20` present** and each category reporting the same imported material ID `2869` (`渲染材质 255-255-255`). In the actual nested `SolidFace` geometry, `GraphicsStyleId=-1`, `MaterialElementId=-1`, and `material_source=unassigned`. Thus the nominal per-layer styles cannot be matched to individual visible surfaces; editing material `2869` would modify multiple unrelated parts. CAD imports also lack meaningful part/material names.

| ID | Local Z range (mm) | Native unassigned faces | Geometry evidence / conservative inferred role | Recolor decision |
|---|---:|---:|---|---|
| 2977 | 310.3–364.8 | 237 | ~120 mm dia. at lowest light/motor end; likely mixed diffuser, trim, LED/mechanics | HOLD mixed light components |
| 2980 | 0.0–63.5 | 568 | ~120 × 146 mm upper canopy interior assembly; white pieces visible when viewed above canopy | HOLD hidden mounting/receiver assembly |
| 2982 | 172.7–181.7 | 17 | ~36 mm dia. thin ring at downrod | HOLD joint/fastener identity |
| 2985 | 42.6–74.7 | 171 | ~57 mm dia. upper canopy/rod collar region | HOLD mixed collar hardware |
| 2986 | 321.8–358.8 | 462 | ~92 mm dia. nested lower light engine/LED structure | HOLD mixed optical/electrical parts |
| 2987 | 55.2–61.8 | 21 | 13.2 × 9.9 mm small offset part near canopy | HOLD hardware |
| 2988 | 60.7–68.1 | 21 | 8.7 mm round offset part near canopy | HOLD hardware |
| 2989 | 60.7–68.1 | 21 | matching 8.7 mm opposite offset part | HOLD hardware |
| 2990 | 214.8–226.3 | 21 | ~6.7 mm small offset part around motor/downrod | HOLD fastener |
| 2991 | 293.9–303.4 | 21 | ~10.1 mm small offset part at blade hub | HOLD fastener |
| 2992 | 309.6–313.7 | 21 | ~3.3 mm small offset part at blade hub/light connection | HOLD fastener |
| 2993 | 307.9–312.0 | 21 | matching ~3.3 mm small offset part | HOLD fastener |
| 2994 | 307.9–312.0 | 21 | matching ~3.3 mm small offset part | HOLD fastener |

Spatial classifications above are relative to the OEM Revit local coordinate system: Z=0 corresponds to the canopy end and the largest Z values approach the fan light underside. The 13 imports contain no blade sweep geometry; the three 52-inch blade surfaces were separately identified as `FreeFormElement` IDs 2997–2999 and correctly blackened in R02. Central solids IDs 3038–3042 are already Soft Brass. FreeFormElement 3000 remains physically near the opal LED lens and is deliberately unchanged. None of the remaining imported parts has authoritative manufacturer per-part finish proof sufficient for an entire-element paint action, especially 2977/2986 where brass ring, white diffuser and internal components overlap.

**Recommended next discriminating evidence:** Native Revit 2025 disposable project individual-import isolation pictures from top, below and sectional views; material/face layer re-probe using geometry references rather than identical import-wide category rosters; manufacturer's original object-grouped CAD/mesh or installation cutaway labeling exact cover, gasket, LED diffuser, screw and hub finishes. Those can justify a later isolated R03 face-level change. Do not recolor by numeric layer, material 2869, or Z-band cropping alone.

## Actual native BIM electrical, LED and hosting state

Native OEM R03 evidence: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\oem_qa_r03.json` (record `mfr1415595`).

| Property | Verified **in existing Revit family** | Manufacturer physical specification |
|---|---|---|
| Category / host | Lighting Fixtures / **WorkPlaneBased**; disposable ceiling-bottom face placement **host_verified=true**, zero project warnings | Downrod ceiling fan; included 6-in downrod; mounting slope up to 30° |
| Electrical connectors | **0 native ElectricalConnector elements detected**; no power connection usable for Revit circuit schedule validated | **120 VAC, 50/60 Hz**, wired through a canopy receiver; fan motor and light independently connect to receiver |
| Light source | One Revit light-source `Element` **ID 3044** detected | Integrated **16 W LED** with opal lens, optional fan-only cover |
| Photometric web | Type string `Photometric Web File = FR-W2502-52L.IES` exists; **no matching IES file was found** in the locally inspected Belmont family/photometry package. A filename string is insufficient evidence of a bound light-source distribution | 1497–1606 LED source lumens depending on CCT, **707 delivered lumens**, **CRI 90**, LED rated 50,000 h |
| Intensity / lamp loss | `Initial Intensity` and `Light Loss Factor` type values show **StorageType=None** in audit; no calibrated Revit light output verified | 2700, 3000, 4000 or 5000 K selectable, integrated dimming |
| Total fan power | Family parameter **`Apparent Power` exists**, but its value was not captured in the saved probe; no trustworthy assigned MEP load can be asserted | **48 W total**, 16 W LED + motor load governed by speed (manufacturer weighted-average/high fan energy 19/27 W) |
| OEM family type metadata | One family type named a single blank space (`" "`), no material type parameters; Model, Manufacturer, Wattage Comments and Description were null in native inspection | Exact published product code **FR-W2502-52L-SB/MB** |

Revit light source detection alone does **not** establish emitted light intensity, CCT switching, IES binding, or electrical load/circuit connectivity. The manufacturer's 48 W total power and 16 W light should not be blindly written into Revit's *Apparent Power* as though they were equivalent VA, without a source-backed electrical power factor / modeling decision. A manufacturer supplied receiver and LED module does not mean the BIM family contains a Revit electrical connector. Wiring authority: [official FR-W2502 installation manual](https://modernforms.com/images/products/INST_SHEET/FR-W2502_INSSHT.pdf), which identifies canopy receiver supply hot/neutral/ground, red/grey/yellow to motor, and blue/white to the light.

## Release disposition

The R02 family is **valid for geometry, face-hosted placement and source-backed three-blade vs main-housing finishes**. It remains **partial for import color fidelity and MEP/light semantics**. R03 is blocked by missing per-part finish identity and should not be created from guesses. Existing R02 and original source family files remain untouched by this review.
