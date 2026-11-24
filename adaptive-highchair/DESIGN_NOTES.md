# Design notes

## Requirements derived from RESEARCH.md

| Requirement | Target | Basis |
|---|---|---|
| Seat width | 200–300 mm, adjustable via inserts | 8–12" child range; Rifton 7–17" |
| Seat depth | 230–300 mm | TherAdapt 6–14", ANTILOP 8⅝" |
| Seat height above floor | 520–570 mm | 21–22¼" fits a 29–30" table |
| Footrest | 110–380 mm below seat, depth-adjustable | TherAdapt 4½–15" |
| Back height above seat | ≥380 mm | TherAdapt 15", Rifton 12½–24" |
| Seat tilt | −15° to +25° | Rifton tilt-in-space |
| Back recline | −5° to +20° | Rifton |
| Lateral supports | 140–355 mm spacing | Rifton trunk support / hip guides |
| Tray | ~600 × 500 mm with body cut-out | TherAdapt 24 × 20", cut-out 17½ × 4" |
| Restraint | 5-point harness + separate pelvic belt anchors | All mainstream + adaptive products |
| Adjustment | tool-free levers/detents | Rifton, OXO |

## Architecture

Revised 2026-11-24 after `OFF_THE_SHELF.md` research: the frame stock is now
**20 × 20 mm T-slot extrusion** with M5 sliding nuts, not welded square tube.
Size changes become bolt repositioning instead of drilling or tube fitting.

1. **Frame** — off-the-shelf 2020 extrusion posts and rails, joined by printed
   clamp plates. Keeps printed volume small and avoids printing long spans.
2. **Seat module** — printed pan with slots for depth and width inserts;
   pivots on the frame for tilt.
3. **Back module** — printed panel carrier with vertical slots for back
   height and lateral-support positions.
4. **Footrest** — printed clamp + plate, adjustable in height and reach.
5. **Tray** — printed clips on the frame arms; tray itself is flat stock with
   a body cut-out, not a large printed slab.
6. **Harness** — anchor geometry is reserved in the model but deliberately
   left unimplemented until load cases and hardware are specified.

## Open questions

- Confirm local supply and price of 2020 extrusion + M5 sliding-nut kits.
- Which commercial 5-point harness to design the anchors around (25 mm webbing).
- Target growth range: 6–36 months only, or extend to Rifton-style paediatric
  sizing?
- Folding/stacking needed, or static frame acceptable?
- Required proof-load factor for T-slot joints and printed clamp plates.
- Print material: PETG for brackets vs. PA/GF for load-bearing clamps.

## Next steps

- Parameterise the tube cross-section and clamp wall thickness in `params.scad`.
- Add the slotted tilt plate and validate adjustment ranges in OpenSCAD.
- Prototype one clamp and test fit before printing the full set.
