# 3D Printing

OpenSCAD-first repository for 3D-printable designs. Source of truth is `.scad`
(or a parametric Python builder where the geometry is procedural); STL/3MF files
are build artifacts kept alongside the source so parts can be printed without a
rebuild.

## Projects

| Project | What it is | Print files |
|---|---|---|
| [`adaptive-highchair/`](adaptive-highchair/) | Parametric adaptive high-chair concept (research/blockout) | — (render only) |
| [`hex-ramp/`](hex-ramp/) | 18 in half-ramp lightened with a tileable hex through-hole lattice | `ramp_half_hex.stl`, `ramp_half_hex.3mf` |
| [`fishtank-gantry/`](fishtank-gantry/) | Rim-mounted gantry that carries a float valve and siphon hose over a fish tank | `fishtank-gantry.3mf`, `stl/*.stl` |
| [`rocket-shelf/`](rocket-shelf/) | Two-part magnetic shelf (body + magnet-pocket shelf) derived from the Rocket Shelf System | `stl/ref_obj*.stl` (reference meshes) |
| [`rocket-toniebox-holder/`](rocket-toniebox-holder/) | Replacement magnet discs (Ø36 × 2.8 mm) for the Rocket Toniebox holder | `discs_magnet.stl`, `rocket-toniebox-holder.3mf` |
| [`multiboard-mm/`](multiboard-mm/) | Stacked multi-material MultiBoard print process + interface geometry | `interface_0p2.stl` |
| [`fan-adapter-80-to-72x28/`](fan-adapter-80-to-72x28/) | 80 mm case fan → 72 × 28 mm right-angle duct adapter | `fixed/fan_adapter_fixed.stl`, `handoff/fan_adapter_light.stl` |
| [`fan-adapter-to-rook/`](fan-adapter-to-rook/) | Self-contained handoff bundle of the final fan-adapter files | `stl/fan_adapter.stl` |
| [`siphon-strainer/`](siphon-strainer/) | Threaded siphon strainer and tube adapters | `stl/strainer-nosupport.stl`, `stl/adapter-threaded-*.stl` |

## Layout

```
templates/            starter .scad files for new parts
scripts/              repository tooling (project import)
<project-name>/       one directory per project, lowercase-hyphenated
  README.md           what it is, how it prints, how to rebuild
  *.scad              parametric source
  *.py                procedural build / analysis scripts
  stl/, preview/      exported meshes and renders
```

## Conventions

- All geometry is defined in **millimetres** in `.scad` source.
- One top-level `.scad` per part or assembly; shared dimensions live in a
  `params.scad` alongside it.
- Parameters use `snake_case`; named constants use `UPPER_SNAKE_CASE`.
- Export STLs only after the design renders cleanly (`F6`). Do not hand-edit
  STLs.
- Commit source **and** the final print-ready `.stl`/`.3mf`. Do not commit
  Bambu Studio build output (`build/`, `*.gcode`, `*.gcode.3mf`), slicing
  intermediates, or extracted 3MF trees — see `.gitignore`.
- If a design is derived from a downloaded model, say so in the project README
  and record the original file name; do not commit third-party source meshes
  unless the licence allows it.
- Safety-critical projects carry a prominent scope/disclaimer note in their
  README. A rendered model is not a tested product.

## Tooling

- [OpenSCAD](https://openscad.org/) (stable or snapshot)
- Optional: `openscad -o part.stl part.scad` for headless export
- Bambu Studio for slicing; the CLI (`--slice 1 --outputdir …`) is enough for
  headless verification

## Adding a project

See [`AGENTS.md`](AGENTS.md) for the checklist, or run:

```sh
scripts/import-project.sh ~/opencode-sessions/my-new-part
```
