# adaptive-highchair

Parametric, printable adaptive high-chair concept. The design target is a
low-cost seating aid built from printed brackets and connectors around
off-the-shelf tube/wood stock, rather than a fully printed chair.

> **Scope / safety:** This is a research and prototyping project. It is not a
> medical device and has not been tested to any furniture or child-safety
> standard. Do not use it with a child without qualified engineering review,
> materials selection, and physical testing.

## Files

- `RESEARCH.md` — commercial product specs and extracted design inputs
- `OFF_THE_SHELF.md` — frame hardware, size-adjustment parts, strap materials
- `DESIGN_NOTES.md` — requirements and planned architecture
- `BOM.md` — non-printed parts (3/4" tube, 1" webbing, 1/4-20 bolts) and tools
- `params.scad` — all design dimensions (mm), edit this first
- `adaptive-highchair.scad` — concept geometry; `include`s `params.scad`
- `nut_insert.scad` — captive 1/4-20 nut insert for 3/4" tube (no tapping)
- `drill_jig.scad` — printed drill guide for the insert
- `render.sh` — regenerates `preview.png` from the `.scad`

![Concept blockout](preview.png)

## Status

Research complete. Concept geometry is a dimensioned blockout only — no
harness anchors, no structural analysis, no print profiles yet.

## Quick start

```sh
openscad -o adaptive-highchair.stl adaptive-highchair.scad
```
