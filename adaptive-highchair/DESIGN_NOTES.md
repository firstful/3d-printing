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
| Adjustment | tool-free sliding collars on legs | Rifton, OXO |
| Footprint / splay | 640 × 700 mm base, 400 × 460 mm at top, legs ~10° outward | stability, no-cut stock lengths |

## Architecture

Revised 2026-11-24 after `OFF_THE_SHELF.md` research: the frame is **1" square
aluminium tube from Home Depot**, used in full stock lengths with **no cutting**.
All four legs splay outward for stability. Size changes happen by sliding
printed collars along the legs, not by drilling or mitring tube.

1. **Frame** — four full 3 ft (914 mm) Everbilt legs, splayed ~10°, plus 1 ft
   rail pieces. Printed hubs with angled sockets set the splay; set screws or
   ¼-20 through-bolts lock each joint. Footprint 640 × 700 mm, leg tops
   400 × 460 mm, frame height ~868 mm.
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

- Confirm local stock/price of Everbilt 3 ft and LUKVIZO 1 ft 1" square tube.
- Which commercial 5-point harness to design the anchors around (25 mm webbing).
- Target growth range: 6–36 months only, or extend to Rifton-style paediatric
  sizing?
- Folding/stacking needed, or static frame acceptable?
- Required proof-load factor for T-slot joints and printed clamp plates.
- Print material: PETG for brackets vs. PA/GF for load-bearing clamps.

## Next steps

- Model the printed angled hub and validate the splay angle against a real
  1" tube sample.
- Add the slotted tilt plate and validate adjustment ranges in OpenSCAD.
- Prototype one clamp and test fit before printing the full set.
