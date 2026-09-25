from pathlib import Path
p = Path(r"output\lightology_20260923\f10_1242580\sources_and_inferences.json")
s = p.read_text(encoding="utf-8-sig")
s = s.replace('"alabaster body with slight side taper", "thin brass ceiling canopy", "brass side retaining/prong plates"', '"alabaster body with ceiling-side edge wider than exposed underside", "thin brass ceiling canopy", "two opposite-side brass retaining elements"')
s = s.replace('"17.50 in top of stone body", "2.60 in prong width", "0.22 in prong thickness", "prong vertical extents and corner radii"', '"17.50 in exposed underside width", "retainer exact seating/edge offsets and corner radii"')
s = s.replace('"manufacturer_page_crosscheck_in": {"width": 18.25, "height": 3.0, "canopy": 17.5},', '"manufacturer_page_crosscheck_in": {"width": 18.25, "height": 3.0, "canopy": 17.5},\n  "manufacturer_rfa_reference_geometry": {"aggregate_bbox_in_approx": [18.09, 3.02, 18.09], "retainer_solids_count": 2, "retainer_bbox_in_approx": [1.60, 3.02, 11.01], "use": "reference evidence only; generated family remains independent"},')
p.write_text(s, encoding="utf-8")

p = Path(r"output\lightology_20260923\f10_1242580\README.md")
s = p.read_text(encoding="utf-8-sig")
s = s.replace("The alabaster body is a shallow square tapered solid below a thin brass canopy. Retaining/prong plates are inferred from the exact option photograph and are documented as inferred rather than manufacturing dimensions.", "The alabaster body is a shallow square tapered solid below a thin brass canopy, with the 18.25 in ceiling-side stone edge narrowing to an inferred 17.50 in exposed underside. Two opposite-side brass retainers are modeled from the exact option photograph and native manufacturer-reference bounds: the reference RFA contains two matching solids approximately 1.60 x 3.02 x 11.01 in. Their exact seating and corner treatment remain inferred.")
s += "\n\n## Native revision history\n\nThe first native run passed every technical gate but was rejected in self-review because four small retainers and an overly dark alabaster underside did not match the source. The saved builder has been corrected to two large seated retainers, reversed stone taper (wider at ceiling side, narrower underside), and stronger 2700K alabaster emission. A new native run is required; the first validation/evidence remain superseded until that rerun passes.\n"
p.write_text(s, encoding="utf-8")
