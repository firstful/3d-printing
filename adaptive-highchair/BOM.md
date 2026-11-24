# adaptive-highchair — non-printed bill of materials

All dimensions in mm unless noted. Tolerances are nominal; measure the actual
stock before cutting. All thread dimensions live in `params.scad` — edit the
`Thread / fastener` block to swap hardware.

| # | Item | Spec | Qty | Notes |
|---|---|---|---|---|
| 1 | Aluminium square tube | 3/4" (19.05) square, 1/16" (1.59) wall, 6063 | 4 legs @ 760; 4 rail pieces @ ~450 | Straight cuts only; hacksaw + printed miter jig. Deburr cut ends. Lengths in `params.scad` |
| 2 | Nylon webbing | 1" (25 mm) wide | ~6 yd (5.5 m), or one finished 5-point harness | Cut to length, heat-seal ends with a lighter/hot knife. Use a commercial harness for the actual restraint |
| 3 | Hex bolts | **1/4-20 × 1" zinc-plated** ([Everbilt 800596](https://www.homedepot.com/p/Everbilt-1-4-in-20-x-1-in-Zinc-Plated-Hex-Bolt-800596/204633241)) | ~20 | Long enough to reach the nut captured inside the tube; short M5 × 10 mm bolts do not reach |
| 4 | Nyloc nuts | **1/4-20** ([Everbilt 800174](https://www.homedepot.com/p/Everbilt-1-4-in-20-Chrome-Nylon-Lock-Nut-4-Pack-800174/204604732)) | ~20 | Held captive inside the tube by `nut_insert.scad` |
| 5 | Washers | 1/4" flat washer | ~20 | Under the bolt head |
| 6 | Drill bit | 17/64" (6.75 mm) | 1 | M5 × 0.8 would use 5.2 mm — see `params.scad` |

## Thread details (all in `params.scad`)

| Parameter | Value | Meaning |
|---|---|---|
| `THREAD_NAME` | `1/4-20 UNC` | Label only |
| `THREAD_MAJOR` | 6.35 mm | Nominal bolt diameter (0.25") |
| `THREAD_PITCH` | 1.27 mm | mm per thread (1/4-20) |
| `THREAD_TPI` | 20 | Derived: 25.4 / pitch |
| `NUT_AF` | 11.11 mm | 7/16" across flats |
| `NUT_H` | 8.0 mm | Nyloc height (pocket adds `NUT_POCKET_CLEAR`) |
| `BOLT_CLEAR_D` | 6.75 mm | 17/64" drill, through one tube wall |
| `BOLT_LEN` | 25.4 mm | 1" bolt |

To switch back to M5 × 0.8, change only that block in `params.scad`:
`THREAD_MAJOR=5`, `THREAD_PITCH=0.8`, `NUT_AF=8.0`, `NUT_H=5.0`,
`BOLT_CLEAR_D=5.2`, `BOLT_LEN=20`; `THREAD_TPI` is derived automatically.
Both `nut_insert.scad` and `drill_jig.scad` read these values.

## Why 1/4-20 instead of M5

- 1/16" tube wall gives only ~1.6 mm of thread engagement per wall, so tapping
  directly into the tube is not reliable.
- The joint uses a **clearance hole through one wall** and a Nyloc nut captured
  inside the tube by `nut_insert.scad`; the hex pocket stops the nut rotating.
- Home Depot stocks 1/4-20 bolts, nuts, washers and drill bits in quantity.
  The M5 × 10 mm bolt from [product 801328](https://www.homedepot.com/p/Everbilt-M5-0-8-x-10-mm-Class-8-8-Zinc-Plated-Hex-Bolt-4-Pack-801328/204273656)
  is the right thread but far too short.

## Printed parts that are part of the BOM

- `nut_insert.scad` — captive 1/4-20 nut insert for 3/4" tube.
- `drill_jig.scad` — drill guide that aligns the hole with the insert.

## Tools allowed by the current plan

- Hacksaw / miter saw for straight tube cuts
- File or sandpaper to deburr
- Drill + 17/64" bit + printed drill jig
- Scissors/knife + heat source for webbing ends
