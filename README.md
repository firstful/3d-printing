# 3D Printing

OpenSCAD-first repository for 3D-printable designs. Source of truth is `.scad`;
STL/3MF files are build artifacts.

## Layout

```
templates/            starter .scad files for new parts
adaptive-highchair/   parametric adaptive high-chair project
```

## Conventions

- All geometry is defined in **millimetres** in `.scad` source.
- One top-level `.scad` per part or assembly; shared dimensions live in a
  `params.scad` alongside it.
- Parameters use `snake_case`; named constants use `UPPER_SNAKE_CASE`.
- Export STLs only after the design renders cleanly (`F6`). Do not hand-edit
  STLs.
- Safety-critical projects carry a prominent scope/disclaimer note in their
  README. A rendered model is not a tested product.

## Tooling

- [OpenSCAD](https://openscad.org/) (stable or snapshot)
- Optional: `openscad -o part.stl part.scad` for headless export
