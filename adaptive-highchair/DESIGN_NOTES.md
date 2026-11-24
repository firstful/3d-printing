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
| Footprint / splay | 640 × 700 mm base, 400 × 460 mm at top, legs ~10° outward | stability, cut-to-length stock |

## Architecture

Revised 2026-11-24: the frame is **3/4" square aluminium tube from Home Depot**,
cut to length (straight cuts only) with a printed miter jig. All four legs
splay outward ~10° for stability. Joints use 1/4-20 through-bolts with Nyloc
nuts captured by printed inserts (`nut_insert.scad`) — no tapping, no drilling
beyond clearance holes. All thread sizes are centralised in `params.scad`.

1. **Frame** — four 760 mm legs, splayed ~10°, plus 450 mm rail pieces.
   Printed hubs with angled sockets set the splay; 1/4-20 through-bolts lock each
   joint. Footprint 640 × 700 mm, leg tops 400 × 460 mm, frame height ~740 mm.
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

- Confirm local stock/price of Everbilt 3/4" 3 ft and 6 ft 1/16" wall tube.
- Which commercial 5-point harness to design the anchors around (25 mm webbing).
- Target growth range: 6–36 months only, or extend to Rifton-style paediatric
  sizing?
- Folding/stacking needed, or static frame acceptable?
- Required proof-load factor for 1/4-20 joints and printed clamp plates.
- Print material: PETG for brackets vs. PA/GF for load-bearing clamps.

## Next steps

- Model the printed angled hub and validate the splay angle against a real
  3/4" tube sample.
- Add the slotted tilt plate and validate adjustment ranges in OpenSCAD.
- Prototype one nut insert + drill jig and test fit before printing the full set.
