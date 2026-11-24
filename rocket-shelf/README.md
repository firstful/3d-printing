# rocket-shelf

Two-part magnetic shelf derived from the downloaded
`Rocket_Shelf_System_AssembleableForBiggerSize.3mf`. The shelf (bottom) is
printed flat with magnet pockets in its underside; the body (top) is the same
shell stretched 50 % deeper and printed on its side for layer strength.

## Files

| File | Purpose |
|---|---|
| `stl/ref_obj1.stl` | Shelf (bottom), extracted from the source 3MF |
| `stl/ref_obj7.stl` | Body (top), extracted from the source 3MF |
| `stl/ref_obj3.stl`, `stl/ref_obj5.stl` | Other source objects, kept for reference |
| `scad/body.scad` | Body with `scale([1,1,1.5])` — **print this** |
| `scad/shelf.scad` | Shelf with 4 magnet pockets — **print this** |
| `scad/*_profile.scad` | Section/projection helpers used for the previews |
| `preview/*.svg` | Body, shelf and combined cross-sections |
| `extract.py` | Re-extracts the reference STLs from the source 3MF |

`ref_obj*.stl` are the untouched source meshes (and the `import()` inputs for the
`.scad` files), not final print files. Export the two finished parts yourself:

```sh
openscad -o body.stl  scad/body.scad
openscad -o shelf.stl scad/shelf.scad
```

## Magnet pockets

Four pockets in the shelf underside, 10.4 mm diameter × 3.2 mm deep with a 0.3 mm
chamfer, at (±40, ±30) mm. Sized for 10 × 3 mm disc magnets with glue clearance.
Check your magnets with a caliper before printing; adjust `magnet_d`/`magnet_h`
at the top of `scad/shelf.scad`.

## Printing

- **Body:** on its side, as oriented in `scad/body.scad` — vertical walls land
  in-plane, so layer lines do not cross the load path.
- **Shelf:** flat on the bed, magnet pockets opening downward (they are cut from
  z = −15, i.e. the underside in the model frame). Add a pause before the top of
  the pocket if you want to glue magnets in during the print instead of after.
- No supports required for either part in the tested orientation.

## Provenance

Source model: `Rocket_Shelf_System_AssembleableForBiggerSize.3mf` (downloaded,
author/licence not recorded). The source 3MF itself is not committed; only the
extracted reference meshes and Reed's modified `.scad` are. If this leaves the
house, check the original model's licence first.
