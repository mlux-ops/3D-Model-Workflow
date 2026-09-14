# Desktop verification — September 7, 2026

Opened the saved `Gola_2025_Placement_Examples.rvt` in Autodesk Revit 2025.4 through the normal Open dialog, without an upgrade or recovery prompt.

In Structural Plan: Level 1, selected the Horizontal - C - Double Grip instance. Revit displayed native circular endpoint grips and a 1,000.0 mm temporary length dimension.

1. Dragged the start grip left. The model length and temporary dimension changed to 1,160.0 mm. The opposite endpoint stayed in place; the start cap and nearby clip followed.
2. Dragged the end grip right. The model length and temporary dimension changed to 1,560.0 mm. The start endpoint stayed in place; the end cap and nearby clip followed.
3. Undid both test edits to restore the sample.

No family edits were needed for the desktop grip test. The automated report separately measures the actual solids for all four types.
