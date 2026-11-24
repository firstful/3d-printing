# adaptive-highchair — non-printed bill of materials

All dimensions in mm unless noted. Tolerances are nominal; measure the actual
stock before cutting.

| # | Item | Spec | Qty | Notes |
|---|---|---|---|---|
| 1 | Aluminium square tube | 3/4" (19.05) square, 1/16" (1.59) wall, 6063 | 4 legs @ 760; 4 rail pieces @ ~450 | Straight cuts only; hacksaw + printed miter jig. Deburr cut ends. Lengths in `params.scad` |
| 2 | Nylon webbing | 1" (25 mm) wide | ~6 yd (5.5 m), or one finished 5-point harness | Cut to length, heat-seal ends with a lighter/hot knife. Use a commercial harness for the actual restraint |
| 3 | Screws | **M5 × 0.8**, socket-head cap, 16 mm and 20 mm | ~20 with Nyloc nuts + washers | M5 clearance holes (5.2 mm) through both tube walls; a printed captive-nut insert (`nut_insert.scad`) holds the nut inside the tube. No tapping |

## Why M5

- 1/16" wall gives only ~1.6 mm of thread engagement per wall, so tapping
  directly into the tube is not reliable.
- Structural joints use **M5 clearance holes (5.2 mm) through both walls
  with a Nyloc nut**. The drill position is set with `drill_jig.scad`.
- The nut is held captive inside the tube by `nut_insert.scad`, which slides
  into the tube end and aligns with the drilled hole; the hex pocket stops
  the nut rotating.
- M5 is widely stocked, and 5 mm holes leave enough material in a printed
  bracket around 3/4" tube.

## Printed parts that are part of the BOM

- `nut_insert.scad` — captive M5 nut insert for 3/4" tube.
- `drill_jig.scad` — drill guide that aligns the hole with the insert.

## Tools allowed by the current plan

- Hacksaw / miter saw for straight tube cuts
- File or sandpaper to deburr
- Drill + printed drill jig
- Scissors/knife + heat source for webbing ends
