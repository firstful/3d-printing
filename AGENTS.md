# AGENTS.md — 3D printing repository

Instructions for agents working in this repository.

## Rule: every 3D print project lives here

This repo is the canonical home for Reed's 3D-printing work. When a new design
is created anywhere else (usually `~/opencode-sessions/<name>/`), it must be
imported here before the task is considered finished.

```sh
scripts/import-project.sh ~/opencode-sessions/<name> [dest-name]
```

The script rsyncs the project with the repository's exclude rules, then prints
the remaining checklist. Default destination name is the source directory name
(lowercase, hyphens).

## When adding or updating a project

1. **Layout.** One directory per project at the repo root, `lowercase-hyphenated`.
   Do not nest projects inside each other.
2. **Source first.** Commit the parametric source (`.scad`, or `.py` builder +
   inputs). STLs are exports, not the source of truth.
3. **Print files.** Commit the final print-ready `.stl`/`.3mf` only. Drop
   iteration builds, `build/` trees, `*.gcode`, `*.gcode.3mf`, `*.bak`, extracted
   3MF folders (`3D/`, `Metadata/`, `_rels/`, `Auxiliaries/`), and Python
   intermediates (`*.npy`, `*.npz`).
4. **README.** Every project needs one, covering:
   - what the part is and what it mounts/fits
   - print orientation, material, supports (or why none)
   - key dimensions and tolerances
   - how to rebuild/export (`openscad -o …`, `python build.py …`)
   - provenance if derived from a downloaded model
   - a safety note for anything load-bearing, child-related, plumbing, or
     electrical
5. **Previews.** Keep a small set of PNG/SVG renders under `preview/`. Delete
   superseded iteration renders rather than accumulating them.
6. **Index.** Add or update the project row in the top-level `README.md`.
7. **Commit.** One commit per project change is fine:
   `hex-ramp: add 57-hole revision and rebuilt 3MF`.
   Push to `ssh://gitea@gitea.ffilt.us:2222/reeds/3d-printing.git` (or HTTPS with
   a Gitea token).
8. **Working copy.** Keep the live working directory under
   `~/opencode-sessions/`; this repo is a committed mirror. Do not move or delete
   the working copy when publishing.

## Large files

- Keep the repo comfortably under ~100 MB. Anything above roughly 50 MB of new
  binaries in one project needs a reason recorded in its README.
- Exclude third-party source models (`Orig/`, vendor 3MF reference meshes) and
  note where they came from instead. Commit only meshes Reed generated.
- Do not use Git LFS; this Gitea instance has no LFS storage configured.

## Style

- Units are millimetres. State them once, use them everywhere.
- `snake_case` parameters, `UPPER_SNAKE_CASE` constants, `//` comments.
- Keep design inputs at the top of a `.scad` file and include a `params.scad`
  when a project has more than one part.
