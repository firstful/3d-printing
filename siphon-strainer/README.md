# Siphon strainer — threaded tubing adapter (draft)

> **Repository note:** `build/`, the 15 MB sliced `*.gcode.3mf`, the original
> third-party meshes in `stl/original/`, and the bundled `OpenSCAD.AppImage` are
> not committed. All source `.scad` and the exported print STLs/3MFs are.

**Print the adapters first.** `stl/strainer.stl` is parked; the filter is 32 g and a
multi-hour print, and the adapter fit is still being dialled in.

## Draft parts

Three grip classes. Each STL contains **both parts** (collet + collar, side by side
on the plate), ~5.1 g per pair.

| STL | tube bore | gap to 6.35 mm tube | thread | squeeze |
|---|---|---|---|---|
| `stl/adapter-threaded-tight.stl` | 6.30 mm | −0.025 (interference) | 14.8 × 2.0 | 0.25 mm |
| `stl/adapter-threaded-medium.stl` | 6.50 mm | +0.075 | 15.0 × 2.0 | 0.25 mm |
| `stl/adapter-threaded-loose.stl` | 6.70 mm | +0.175 | 15.2 × 2.0 | 0.25 mm |

Only `tube_bore` changes between them; the thread and squeeze geometry follow
from it.

## No-support body (current)

`stl/strainer-nosupport.stl` — prints with supports **completely off**.

| | |
|---|---|
| size | 76.2 × 76.2 × 113.7 mm |
| volume | 27.2 cm³ → 27.05 g sliced |
| surface | **0.152 cm² (0.039 %)** below 30° slope, all in the thread/slot junction |
| mesh | watertight, 1 body, 144,604 tris, 0 degenerate |
| slicing | BambuStudio CLI, P1S 0.4, `enable_support=0` → **0 support features** |

**Slicer evidence** (BambuStudio 02.08.02.61 CLI, P1S 0.4 nozzle profile,
supports disabled, 0.20 mm layers):

```
status:           Success.
filament:         27.06 g
FEATURE: Support  0          <- zero support, internal or external
feature mix:      Inner/Outer wall, Internal solid infill, Gap infill,
                  Sparse infill, 52 Floating vertical shell
```

Reproduce with `scad/make_slice_project.py` (wraps the STL in a 3MF, welding the
STL's duplicated vertices — without welding the slicer sees every triangle as a
separate floating shell and refuses) then:

```
BambuStudio.AppImage --slice 1 --outputdir out \
  --load-settings "machine.json;process_nosupport.json" \
  --load-filaments "filament.json" out/nosupport.3mf
```

**The shape had to change.** A sphere cannot pass a no-support rule: near its
poles both the inner ceiling and the outer lower surface approach horizontal.
The body is now two cones base-to-base (a bicone), every surface at **40° from
vertical = 50° slope**.

Per Rook, Bambu/Orca measure the support threshold **from horizontal**: a 30°
setting means "support anything with slope < 30°". A 50° slope is comfortably
clear of that, and 40° from vertical is also inside the practical ~45°
self-support limit for PLA on a P1S.

Verified by measuring every triangle in the exported mesh:

```
BODY  (z>=36):  violating 0.00 of 353.6 cm2 (0.000%)
collet(z<36 ):  violating 0.18 of  35.4 cm2 (0.50%)
whole part   :  violating 0.152 of 387 cm2 (0.039%)
```

The residual is the thread's helical starts and the slot ends at the finger
junction — sub-millimetre features inherent to a thread, and the slicer produces
no support for them.

**Consequences of the redesign**

- No internal lattice, no generated support tree — the cavity is empty, so the
  earlier "supports block the flow" problem disappears entirely.
- Two chamfers were added to the collet: the hex-to-thread step was a horizontal
  5 mm annular ledge (worst-case overhang) and the thread's far end presented a
  flat face once the part is flipped. Both are now ~45° cones. Subtracting a
  full cone instead of the outer wedge severs the hex / the four fingers —
  that caught me twice, hence the `difference()` wedges in `adapter-parts.scad`.
- Body bottom radius is 11 mm (hex *inscribed* radius); at the circumscribed
  12.7 it left a horizontal ledge hanging outside the hex flats.

**Slicer**: turn supports off entirely. The support-blocker sphere in
`strainer-assembly.3mf` is moot now and that project still references the old
sphere mesh — re-import `strainer-nosupport.stl` rather than reusing it.

## Filter assembly

`stl/strainer-assembly.stl` — the sphere with the collet permanently fused in,
one piece. The collar stays separate.

| | |
|---|---|
| size | 76.1 × 76.1 × 110.1 mm |
| mass | 57.1 cm³ → 70.8 g PLA |
| apertures | 1.5 mm, 3.0 mm hex pitch, ~2,344 holes, 22.7 % open |
| mesh | watertight, 1 body |

**Aperture pattern** is latitude rings with the angular step scaled by 1/cos(lat)
so the arc spacing is constant within each ring, and alternate rings offset by
half a step — that half-step is what stops the holes lining up in columns, which
is what looked wrong before. Rings are `pitch*sqrt(3)/2` apart, so the packing is
hexagonal and the spacing is even everywhere.

**Aperture size** is 1.5 mm, under half the ~3.2 mm ID of 1/4" PE tubing, so
nothing that passes a hole can bridge the tube bore.

**Internal lattice.** Eight vertical plates (0.9 mm thick, at x/y = ±7 and ±21)
fill the cavity so the dome has something to print onto — internal supports could
never be removed afterwards. Plates are offset from the axis so the tubing bore
stays clear, and they are clipped against a sphere 0.4 mm larger than the cavity
so they bite into the wall; meeting it tangentially left them as loose bodies.
This is the bulk of the mass: the lattice alone is ~24 cm³. Drop the ±21 pair to
halve it if you'd rather have a lighter part with a coarser support grid.

**Port geometry.** The collet's hex straddles the shell: its outer face sits
11.9 mm beyond the sphere's tangent plane (wrench access), its inner face pokes
2.1 mm into the cavity. Hex is 16 mm long, 22 mm across flats.

**Why the hull is subtracted first.** The order matters:

```
union() {
    difference() { shell(); hex_hull(); }   // clears the bore
    translate([0,0,port_z]) collet();       // fills the space, bore intact
}
```

A plain `union()` of shell and collet would leave a disc of shell material across
the bore where the hex passes through. Subtracting the hex hull first removes all
of it, and the collet then occupies that space with its own 6.7 mm bore. Verified
by intersecting the finished part with a 6.3 mm rod through the port — empty.

**Use:** push the PE tube through the collet into the sphere, then screw the
collar down to clamp it.

**Printing:** this is the awkward one. The sphere's lower hemisphere is a large
unsupported dome — support the lower ~30 mm, or split the sphere at the equator.
Everything above the port is fine as-is.

## How it works

Screwing the collar on draws it down the finger taper and squeezes the fingers
onto the tubing. Three turns of 2 mm thread gives 6 mm of travel.

```
collet  z 0..10   solid section, external thread (major 15.0)
        z 10..22  four fingers, tapering 12.5 -> 11.5 dia
collar  z 0..10   internal thread (crest 13.58) -> clears the fingers by 0.54
        z 10..16  squeeze bore 12.0 -> smaller than the finger base
```

The step between those two bores is the crux: the internal thread has to clear
the fingers, or the collar binds on the way off, while the squeeze bore has to
sit under the finger diameter, or it never grips.

**Revision 3** — rev 2 still would not start. The problem was axial, not radial:
with a 6 mm thread the collar's squeeze bore reached the fingers at the *same*
moment the thread first engaged, so it bottomed out with zero thread contact.
The thread section is now 10 mm, which buys **two full turns of free engagement**
before the squeeze bore touches the fingers:

| collar bottom | state |
|---|---|
| 10 mm | thread just engaging, no contact anywhere |
| 6 mm | still free — 2 turns in |
| < 6 mm | squeeze begins, interference rises to 0.25 mm radial at seat |

Rev 2's radial fix is retained: collar crest 13.58 vs fingers 12.5 (0.54 mm
radial clearance, so printed sag cannot close it), shallow thread V with wide
lands, and a 1.2 mm lead-in funnel at the entry.

**Grip features:** the collar has 24 axial knurl flutes (0.7 mm deep) and the
collet has a 22 mm across-flats hex base, 6 mm thick. The hex doubles as the
collar's seating stop — full seat is the collar meeting the hex face.

The finger bore also carries **three barbed grip grooves** (0.40 mm deep, 1.1 mm
long, at z = 11.5 / 13.5 / 15.5). They are recesses rather than raised ridges, so
the tubing still slides in with no extra force. Each groove is asymmetric — a
0.8 mm ramp on the low-z side and a square shoulder on the high-z side — so
pulling the tubing back out (+z) has to shear the PE over the shoulder rather
than riding it up a ramp. The ramp runs out slightly inside the bore (0.12 mm)
so the entry edge is clean instead of terminating on the wall. They sit in the
zone the collar actually squeezes (z 10..16).

Verified by CSG: with the thread engaged but the collar high (`zb=10`) the collar
and collet have **zero** interference, so it screws on freely; interference then
rises to the designed 0.25 mm radial squeeze at full seat.

## Printing

- Collet: base down, thread at the bottom. No supports (outer taper is 2.4°).
- Collar: shipped **flipped**, threaded bore facing up — better overhangs on the
  internal thread.
- Fingers must flex: 6 perimeters or 100 % infill.
- 0.16 mm layers keep the thread flanks and the 1.2 mm slots clean.
- Threads are deliberately loose — the collar is cut with a thread **1.0 mm
  oversize** in diameter, and the entry has a funnel. Compression holds the
  joint, not friction.

## Notes / caveats

- Threads come from **dkprojects.net/openscad-threads** (GPL-3, v3.0), vendored at
  `scad/lib/threads-dk.scad`. That library's `internal=true` path produced no bore
  in this model, so the collar is cut with an oversized external thread instead.
- `include <lib/threads-dk.scad>` resolves relative to the **file's** directory,
  so compile from `scad/` — copies of the model dropped elsewhere silently lose
  their threads.
- Earlier friction-collar versions are still in `stl/adapter-{tight,medium,loose}.stl`
  if you want to compare.
- The collars are chunky (21 mm OD) because a 60° metric thread at 15 mm nominal
  needs the wall. Shrinking it means a shallower/custom thread profile.

## Filter (parked)

`stl/strainer.stl` — 76.16 × 76.16 × 89.18 mm, watertight, single body, 1,461
through-holes, 25.2 % open area, 25.7 cm³ (31.9 g PLA). Volume cross-check
(25.73 measured vs 25.8 analytic) confirms every aperture is cut clean through.

- The aperture pattern is **not hexagonal** — each latitude restarts at `lon = 0`,
  so holes line up in meridional columns (square grid, 25.2 % open rather than
  ~29.6 %). Cosmetic.
- Outlet-down leaves the lower hemisphere as an unsupported dome over a 9 mm
  stalk. Support the lower ~30 mm, or print outlet-up with a pad.

## Files

```
stl/adapter-threaded-{tight,medium,loose}.stl   print these
stl/strainer.stl                                parked filter
stl/adapter-{tight,medium,loose}.stl            earlier friction-collar version
scad/adapter-threaded.scad                      template (medium)
scad/adapter-threaded-{tight,loose}.scad        generated from it
scad/lib/threads-dk.scad                        thread library
scad/pv-assy.scad, pv-sec.scad                  preview renders
preview/draft_assembly.png, draft_section.png
tools/                                          ASCII→binary STL converter, mesh inspector
```

Re-render:

```
cd scad && ../OpenSCAD.AppImage --backend manifold -o ../stl/adapter-threaded-medium.stl adapter-threaded-medium.scad
```

The distro's OpenSCAD 2021.01 needs CGAL here and does not finish the filter; the
bundled Manifold-backend nightly renders it in ~16 s.
