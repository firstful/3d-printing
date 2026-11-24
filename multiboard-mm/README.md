# MultiBoard stacked multi-material print — process doc

Goal: print several 8×8 MultiBoard octagon plates **stacked in one build** —
boards directly on top of each other, with **exactly one layer of an interface
material (AMS spool M_3 = filament slot 4)** sandwiched between every pair of
boards. Boards use M_0–M_2 (slots 1–3). Everything here was verified by real
slicing with Bambu Studio CLI 2.8.2.61 and G-code auditing.
Runs on Linux without GUI tooling; works headless.

> **Repository note:** the downloaded source model (`Orig/`) and the `build/`
> output trees (sliced G-code, stacked 3MFs, the 34 MB board STL) are not
> committed. Re-download the MultiBoard plate and re-run the pipeline below to
> regenerate them. The derived geometry that is worth keeping —
> `face_polygon.json` and the two interface STLs — is committed.

## Design geometry (measured, exact)

Source STL: `Orig/8x8 MU - MultiBoard Octagon Plate.stl` — 200 × 200 × 6.2 mm.

The two surfaces that meet when boards are stacked are the flat top face
(z = 6.2) and the flat bottom face (z = 0) fills. Extracted as exact polygons
(`extract_face_polygon.py` → `face_polygon.json`):

| quantity                        | value          |
|---------------------------------|----------------|
| flat-face outline area          | 39,892.77 mm²  |
| through-holes (114 loops)       | 31,487.41 mm²  |
| **net contact patch**           | **8,405.35 mm²** |
| outer loops (top vs bottom)     | identical, single 4-connected component |

So each interface slab is the exact contact patch: material only where a
board's flat face meets the next board's flat face; the 114 through-holes stay
open (they carry no flat face, there is nothing to bond).

Layer height must divide the 6.2 mm board height exactly, so allowed lh ∈
{0.1, 0.2}; default **0.2** (31 board layers per board). Stack height for N
boards: `N × 6.2 + (N−1) × 0.2` (3 boards → 19.00 mm, 95 layers).

## Pipeline (repeatable)

Working dir: `~/opencode-sessions/multiboard-mm/`. Python 3 + numpy only; all
OpenSCAD/Bambu calls below are headless CLI.

```bash
cd ~/opencode-sessions/multiboard-mm

# 1. extract the exact contact-patch polygons (faces at z=6.2 and z=0)
python3 extract_face_polygon.py            # -> face_polygon.json

# 2. build the one-layer interface slabs from those loops (OpenSCAD)
python3 make_interface.py                  # -> build/interface_0.2.stl (+ _0.1)
#    binary-STL conversion + checks via ~/.opencode/skills/3d-printing/scripts

# 3. compose the 3mf project (board mesh stored once per part per slot)
python3 make_stack_3mf.py --out build/stack.3mf \
    --boards 3 --lh 0.2 \
    --slots 1,2,3 --interface-slot 4 \
    --board-stl build/board.stl --slab-stl build/interface_0.2.stl \
    --y 112

# 4. slice headless
~/.local/bin/BambuStudio --slice 1 \
    --outputdir build/slice build/stack.3mf

# 5. audit the gcode (layers, tools per layer, zones)
python3 audit_gcode.py build/slice/plate_1.gcode \
    --boxes '{"board":[28,10,228,214],"tower":[160,212,200,244]}' --lh 0.2

# illustration of the contact patch (no matplotlib needed)
python3 render_patch.py                    # -> build/contact_patch.png
```

Result for the 3-board default: `; model printing time: 7h 54m 12s; total
estimated time: 8h 0m 27s`, 95 layers, max z 19.00, filament usage
(length/weight): 21,732.95 mm/65.87 g, 21,360.58/64.74, 21,557.87/65.33,
**1,481.78 mm/4.49 g (interface)**.

## Audit result (the contract, verified)

`tool sequence: [0, 3, 1, 3, 2]` and per-layer data:

| layers   | z band        | tool | meaning                          |
|----------|---------------|------|----------------------------------|
| 1–31     | 0.20 → 6.20   | 0    | board_0 on M_0                   |
| 32       | 6.40          | 3    | **interface (M_3), one layer**   |
| 33–63    | 6.60 → 12.60  | 1    | board_1 on M_1                   |
| 64       | 12.80         | 3    | **interface (M_3), one layer**   |
| 65–95    | 13.00 → 19.00 | 2    | board_2 on M_2                   |

Interface layers extrude the full 200 × 200 footprint (`x 28.2–227.8,
y 10.2–209.8` from the audit) and their extrusion volume matches the net
contact patch: ≈ 20,000 mm of line at 0.42 mm width = 8,405 mm² ÷ width
(holes excluded, as the slab geometry prescribes). A first isolated test
(cube) reproduced the same per-part extruder behavior before the real stack.

## Things that made it work (Bambu CLI-verified contract)

These are the actual rules Bambu Studio 2.8.2.61 CLI honours for a
multi-material **one-object, multi-part** project — learned by experiment
(failed slices and probe builds) against a known-good 4-filament reference
(`four_mat.3mf`, dumped and diffed by @rook):

1. **model_settings.config** — ONE `<object id="1">` block; each part is its
   own `<part id="odd">` (ids 1,3,5,...); every part carries
   `<metadata key="extruder" value="slot"/>` (1-based), `name`, `matrix`
   (16 column values, tz at value index 12), `source_*`, `mesh_stat`.
   The plate needs `<model_instance>` entries. `<assemble/>` may be
   self-closing.
2. **3D/3dmodel.model** — one `<object id="1">` containing N `<component>`
   entries; each component references **its own mesh file**
   `3D/Objects/object_<pid>.model` whose `<object id>` equals the part id;
   the component transform mirrors the part matrix (z offset).
3. **project_settings.config** — filament count = `len(filament_colour)`.
   Filament-domain arrays (many `filament_*`, temps, densities, flush
   payloads...) must length n; printer-domain arrays (`extruder_type`,
   `nozzle_volume_type`, `nozzle_diameter` = one row per nozzle-volume row,
   `printer_extruder_id`...) must stay at profile size (1/2). Delete keys the
   reference doesn't carry: `extruder_max_nozzle_count`,
   `extruder_nozzle_stats(_new)`, `filament_nozzle_map`,
   `filament_volume_map`, `filament_extruder_compatibility`.
   `flush_volumes_matrix` is n×n (diag 0, off-diag 280 here).
   `default_nozzle_volume_type` × n, `filament_extruder_variant` = the two
   profile variants repeated to n, `extruder_ams_count` `['1#0|3']` at n=4.
4. **Wipe tower** — profile pins `wipe_tower_x=165, wipe_tower_y=216.972`
   (200 mm-wide boards centered at (128,128) overlap it → `-101 "gcode path
   conflicts found between WipeTower and multiboard_stack"`). Keep the stack
   at `--y 112`: board spans y 12–212, tower brim occupies y ≥ 214.
   (Observed print lands 2 mm lower in y than the item transform says — the
   tower/auto-position nudge; consistent on cube and stack tests.)
5. Two layers between stacked boards are NOT allowed: `lh` must divide 6.2,
   and the interface slab is generated with the exact `lh` as its thickness.
6. Do **not** use `--load-filament-ids` or `--load-assemble-list` (SIGSEGV).
   Slot-out-of-range parts don't abort in this version — keep slot ≤
   filament count and audit the output.

## Tuning knobs

| knob               | effect                                                    |
|--------------------|-----------------------------------------------------------|
| `--boards N`       | repeat the board/interface pattern; N boards              |
| `--lh 0.1/0.2`     | interface layer thickness; 6.2/lh must be integer          |
| `--slots`          | AMS spool per board (1-based); default 1,2,3               |
| `--interface-slot` | interface spool (default 4 = M_3)                          |
| `--x/--y`          | bed placement (keep `--y 112`, `--x` anything within bed)  |

Colors in the generated project are cosmetic (`filament_colour` preview);
the physical mapping is the AMS tray order: filament 1..4 = trays M_0..M_3.

## Files

| file                        | role                                              |
|-----------------------------|---------------------------------------------------|
| `extract_face_polygon.py`   | exact face-polygon extractor → face_polygon.json  |
| `make_interface.py`         | OpenSCAD slab generator (uses face_polygon.json)  |
| `make_stack_3mf.py`         | 3mf composer (the verified contract)              |
| `audit_gcode.py`            | gcode auditor (layers/tools/zones)                |
| `render_patch.py`           | contact-patch top view PNG (dependency-free)      |
| `build/board.stl`           | 200×200×6.2 board (from the supplied STL)         |
| `build/interface_0.1/0.2.stl` | single-layer slabs (exact contact patch)        |
| `build/stack_v2.3mf`        | verified 3-board/lh-0.2 project                   |
| `build/slice_v2/plate_1.gcode` | audited, 8h 0m print                           |
| `build/contact_patch.png`   | top view: gray = interface bond, white = holes    |
| `mm_*` / `build_mm.py`      | the probe series that derived the contract        |
| `refx-p1s-project_settings.json` | P1S baseline profile (CLI-exported)          |
| `refx/`                     | reference project skeleton (Content_Types etc.)   |
| `Orig/…stl`                 | supplied MultiBoard plate                         |

## Print instructions

1. Load AMS: M_0..M_2 = the board filaments (all PLA 1.75 g/h whatever you
   like), M_3 = the interface spool (gray in the preview).
2. Send `build/stack_v2.3mf`, or reproduce it with the pipeline above.
3. Expect the previewed stack of 3 boards with gray "web" layers between
   them; the print is 19.00 mm tall, ~8 h, 4 tool changes total (all inside
   layers 32/33 and 64/65 of 95).
4. Board-to-board bond strength comes from the 8,405 mm² contact web printed
   as one interface layer; peel the stack apart like a single-contact print
   when done (interface material is consumed only ~4.5 g per 3 boards).
