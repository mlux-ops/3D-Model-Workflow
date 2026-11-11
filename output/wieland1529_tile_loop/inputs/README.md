# Inputs (owner provides)

Drop or link these here before starting the loop. The loop never edits files in this folder.

- `PRICE_BAND.md` — sale price band per unit type (PH, TX), optional $/SF, and target buyer.
  Required. Without it the market critic scores against "unconfirmed band" and the loop asks.
- `plumbing/` — plumbing selections per room (export of the Smartsheet Plumbing rows, the
  fixtures deck `1529_Wieland_Fixtures_v3_2.pdf`, or both).
- `tile/HANDOFF_1529_Wieland_Tile.md` — current tile schedule v4 (seeds each room's champion).
- `revit/` — how the loop reaches Revit (plugin name in Chat On Steroids) and any exported
  room/area schedules if live access is not available.
Known source locators (usable directly if ChatGPT has the matching connector):

- Smartsheet "FINISH DATABASE - 1529 Wieland", sheet id 8569278453206916 (read only).
- Google Drive `1529_Wieland_Fixtures_v3_2.pdf`, file id 1XBZwGrspwZFDZ7jicgCe41FVjNBxPhLS.
- Google Drive `HANDOFF_1529_Wieland_Tile.md`, file id 12gJwYBe70RT8xjwjp9jpzBwvPad1iiMS.
- Prior audit with manufacturer URLs and known gaps:
  `E:\Games\Claude\1527 Wieland\worker13_plumbing_tile_hardware_appliances_audit_2026-10-01.md`.

- Anything else the owner wants considered: inspiration images, rejected options, showroom notes.
