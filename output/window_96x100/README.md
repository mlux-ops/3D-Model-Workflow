# Fixed over paired awnings — Revit 2025

Load `Window_Fixed_Over_Two_Awnings_96x100_R2025.rfa` into a Revit 2025 or newer project and place with the Window tool on a native wall.

- Rough opening: 96 inches wide × 100 inches high.
- Horizontal transom center: 36 inches above rough-opening bottom.
- Center mullion divides only the lower section into two equal modules.
- Upper section: one uninterrupted fixed pane, nominal module 96 × 64 inches.
- Lower section: two top-hinged awning sashes, nominal modules 48 × 36 inches, modeled closed. Opening angle is not adjustable.
- Generic stepped profiles: 2-inch frame/transom/mullion face, 4.5-inch frame depth, 1.75-inch sash face, glazing beads, seals, top hinges and interior latches. These are assumed generic dimensions, not a manufacturer-specific system.
- Assumed installation clearance: 0.25 inch each side. Actual frame outside dimensions are 95.5 × 99.5 inches. Module dimensions are not clear glass dimensions.
- Fixed size family: width, height and division dimensions are locked to this requested configuration. Frame Finish, Glass and Gasket materials are editable type parameters. Use the project Sill Height instance parameter for placement elevation.

Validation: reopened in Revit 2025; Windows category; native wall hosting; exact wall-cut volume corresponding to 96 × 100 inches; all three material substitutions passed; no family or test-project warnings. Front and oblique exported views reviewed. Detailed manufacturer profiles, thermal ratings and engineering performance are not specified.
