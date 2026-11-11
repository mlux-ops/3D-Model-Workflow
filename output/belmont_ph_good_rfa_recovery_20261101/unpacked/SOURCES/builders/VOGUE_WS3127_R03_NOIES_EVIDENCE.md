# Vogue WS-3127-CH R03 - Preliminary distribution, exact current type values

**Quality:** VISUALIZATION_PRELIMINARY_NON_OEM_DISTRIBUTION.
This is a source-only candidate. No Revit 2025 execution or R03 RFA exists from
this task. Do not use it for illuminance compliance, beam spread verification,
manufacturer photometry, electrical panel load, or circuit sizing.

## Verified native R02 evidence

Read-only QA source:
`E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\vogue_ws3127_r03_photometry_qa_fix01.json`.

- Light distribution: PhotometricWebLightDistribution, WS-3127.IES.
- InitialFluxIntensity = 2400 lumens; CustomInitialColor = 3000 Kelvin.
- IES tilt 1.047197551 rad = 60 degrees; photometric orientation is not reinterpreted.
- ConnectorElement count = ZERO.
- `FBX_LIGHT_PHOTOMETRIC_FILE` is a string value referencing WS-3127.IES.
- `FBX_LIGHT_LIMUNOUS_FLUX` and `FBX_LIGHT_INITIAL_COLOR_TEMPERATURE`
  are absent from FamilyManager type parameters, though LightType has the
  native intensity and temperature objects.
- `RBS_ELEC_APPARENT_LOAD` is a Double parameter with no readable value.
- Native R02 chrome material RGB 207,211,216 / transparency 0. Native R02 opal
  material's coarse material values appeared as RGB 0,0,0 / transparency 0,
  despite earlier R02 builder metadata claiming RGB 245,244,239 / transparency
  14. Actual appearance assets are preserved without attempting correction.

## Exact manufacturer authority

- Product: https://modernforms.com/product/vogue/
- Current official specification:
  https://modernforms.com/dynamic-specsheet/?download=specs5&ppid=1546
- The ONLY official IES archive directly linked from the current product
  page: https://modernforms.com/images/products/IES_FILES/WS-3120_IESF.zip
- Original RFA archive from which WS-3127.RFA was extracted:
  https://modernforms.com/images/products/REVIT/WS-3120_REVIT.zip

The manufacturer publishes **WS-3127-CH**, Chrome, mouth-blown etched opal
glass, 3000 K default (2700/3000/3500 K field adjustable), **40.6 W input**,
**2993 delivered lumens**, 3895 LED module lumens, 120 VAC / 50/60Hz and
277V special-order option. The archived `WS-3127.IES` was tested
**2017-11-09** with **38.9472 W / 2424.9 lumens**. Distributors and WAC Group
BIM searches did not yield a verified current 40.6W / 2993lm IES. The missing
source remains a manufacturer technical-support request.

## R03 design and strict status

R03 only exists after the isolated source-guarded converter saves and reopens
a new family. It retires the mismatched IES by switching the native light
distribution to Revit's **Spherical** (generic visualization) mode, in a
separate transaction from LightType/FamilyManager numeric edits. It is not
a source-backed manufacturer angular distribution.

Native initial flux changes from 2400 to **2993 lumens**. Native Kelvin remains
**3000 K**, independently verified after reopen. Three type parameters are
added with native Forge data types:
`PH GOOD OEM Input Power` (ElectricalPower/Watts = 40.6),
`PH GOOD OEM Delivered Flux` (LuminousFlux/Lumens = 2993), and
`PH GOOD OEM Default CCT` (ColorTemperature/Kelvin = 3000).
Status metadata clearly says no current IES and no electrical connector.
These are type reference values. **40.6 W is real input power, not 40.6 VA**;
no power factor is provided, and apparent circuit load cannot be derived.

The original Chrome/opal R02 physical elements and entire material inventory
are compared before/after and reopened. The script aborts if the obsolete
`WS-3127.IES` parameter or PhotometricWeb style remains, if materials change,
or if the source hash differs. Only validated staged candidates are promoted.

New builder:
`E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\scripts\build_vogue_ws3127_ch_r03_noies.py`

Independent native QA:
`E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\qa_vogue_ws3127_r03_noies.py`

Proposed R03 candidate:
`E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\candidates\ModernForms_Vogue_WS-3127_CH_R2025_R03.rfa`

### Revit 2025 API references

- https://www.revitapidocs.com/2025/54a4212a-9694-5032-bdc4-a7cc0603f0e1.htm
- https://www.revitapidocs.com/2025/c572d26c-9344-9256-64b0-88b19b6d768d.htm
- https://www.revitapidocs.com/2025/b5a83b94-c75b-f7d7-bd38-310c6e89bc3b.htm
- https://www.revitapidocs.com/2025/0efb807e-bc7f-50dc-886f-ab8e9958901a.htm
- https://www.revitapidocs.com/2025/3ac89d60-4b71-694f-002f-125d2e6565fc.htm

Autodesk's `SetLightDistribution` docs explicitly warn that family element
light distribution modifications should run in a separate transaction from
family type light intensity values. The converter implements this separation.
If Revit 2025 retains a stale filename after switching to spherical, it fails
before SaveAs; it does not blank undocumented internal IES parameters.
