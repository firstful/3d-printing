# Fish tank filling gantry — concept v0.2

A gantry-style platform that sits on the rim of a fish tank and holds a float
valve plus a 1/4" OD siphon hose. The platform moves +2" to −4" relative to the
rim plane so the float valve's activation level can be set.

## Assembly views

- **Bambu Studio:** `fishtank-gantry.3mf` — 12 separate, named objects already
  in their assembled positions. Select objects in the list to inspect them.
- **Browser:** `http://localhost:8799/fishtank-gantry/assembly.html` — colour
  coded, orbit/zoom, and a checkbox per part. Needs the server running from
  `~/opencode-sessions` (`python3 -m http.server 8799 --directory ~/opencode-sessions`).
- **Single mesh:** `stl/assembly.stl` — convenient for a quick look, but it is
  one multi-body mesh and parts are not selectable.

## Renders

- `preview/gantry_iso_clean.png` — assembled, platform at +2"
- `preview/gantry_iso_low.png` — assembled, platform at −4"
- `preview/gantry_fit_11.png` — front view on a nominal 11" tank
- `preview/gantry_fit_14.png` — front view on a nominal 14" tank
- `preview/gantry_iso.png` / `_xz` / `_yz` / `_xy` — context and orthographic views

Source: `scad/gantry.scad`. The main modules can be exported individually with
`-D part="rail"`, `"leg_plate"`, `"bridge"`, `"platform"`, `"rails"`, or
`"span_screw"`.

## STL files (`stl/`)

| File | Notes |
|---|---|
| `assembly.stl` | All parts together, for viewing only. Multi-body. |
| `rail.stl` | Full 15" rail. **Exceeds a 256 mm bed** — split at centre before printing. |
| `leg_plate.stl` | Full leg + foot/finger, ~277 mm tall. **Exceeds a 256 mm bed** — split at rim line. |
| `bridge.stl` | Open ring/spoke bridge frame. Printable as-is. |
| `platform.stl` | 5 × 5" platform with 3/8" and 3/4" holes. Printable as-is. |
| `crossbar.stl` | One crossbar (needs 2). Printable as-is. |
| `slider.stl` | One rail sleeve (needs 4). Printable as-is. |
| `crank.stl` | One crank (needs 2). Printable as-is. |
| `lock_collar.stl` | One split lock collar (needs 2). Printable as-is. |
| `platform_nut.stl` | Lead-screw nut block. Printable as-is. |
| `platform_bushings.stl` | Three guide-rod bushings in place. |
| `span_screw.stl` | Turnbuckle/rod reference assembly, not a single print. |
| `leg_pair.stl` | One complete U-frame reference, not a single print. |

Viewer: `http://localhost:8799/stl-markup/viewer.html?stl=/fishtank-gantry/stl/assembly.stl`

The joints/dowel holes for the split rail and leg are not modeled yet; the
current STLs are full-length concept parts.

## Concept

```
            height crank
                 │
      ┌──────────┴──────────┐   two fixed, trussed top rails
      │  span turnbuckle    │   (split at the centre for printing)
  ┌───┴───┐           ┌───┴───┐
  │ leg   │  platform │  leg  │   leg pairs slide in/out for 11–14" tanks
  │ pair  │  (o) (O)  │ pair  │
  └───┬───┘           └───┬───┘
  ════╪═══════════════════╪══════  tank rim
      │                   │
```

- Two parallel trussed rails, 6" apart (the build width along the tank's long
  axis). Each rail is a fixed 15" beam.
- Two leg pairs slide along the rails. Each leg pair is a U-frame with a C-foot
  that sits on the rim: an inner leg drops inside the tank and an outer finger
  hooks down the outside.
- A central bridge between the rails carries the hoist and both adjustment
  mechanisms. It is an open ring-and-spoke frame, not a solid box, so the
  turnbuckle and lead screw are visible and the print is much lighter.
- The platform hangs from three 1/4" guide rods and a central 3/8" lead screw.
  The lead screw is turned by the top crank; a split lock collar under the
  platform holds the height.
- Span adjustment is a central turnbuckle (left/right threaded rods) with a
  crank on the side of the bridge and a sliding lock collar. Turning it moves
  both leg pairs in or out symmetrically.

## Key dimensions (current defaults)

| Item | Value |
|---|---|
| Tank short dimension | 11–14" outside |
| Build width (Y) | 6" |
| Rail length | 15" fixed; ~1.25–2.75" overhang per side |
| Rail section | 2" tall × 0.4" thick trussed plate |
| Leg spacing | 11–14" (sliding pairs) |
| Rim assumption | 1" flat rim; outer finger intended to be adjustable |
| Platform | 5" × 5" × 0.4" |
| Platform travel | +2" to −4" from rim plane |
| Holes | 3/8" float valve, 3/4" siphon/access |
| Guide rods | 3 × 1/4" |
| Lead screw | 3/8", top crank + lock collar |
| Material | PLA, low load |

## Current mass estimate (PLA, 1.24 g/cm³)

| Part | Qty | Unit volume | Total |
|---|---|---|---|
| Rail half (7.5") | 4 | ~64 cm³ | ~318 g |
| Full leg (split for print) | 4 | ~35 cm³ | ~173 g |
| Bridge frame | 1 | ~164 cm³ | ~203 g |
| Platform | 1 | ~98 cm³ | ~121 g |
| Crossbar | 2 | ~55 cm³ | ~137 g |
| Slider sleeve | 4 | ~24 cm³ | ~121 g |
| Cranks / collars / nut / bushings / dowels | — | — | ~110 g |
| **Total** | | | **~1.2 kg** |

The assembly volume is only a rough guide because overlapping bodies are counted
twice. Individual part STLs are watertight and are the number to trust.

## Print split plan

The model is designed around a 256 mm bed and PLA dowels + superglue.

1. **Rails** — split at X=0 into two 7.5" halves per rail (4 pieces). Join with a
   lap/tongue joint and two 6 mm PLA dowels; the bridge covers the joint.
   Print flat on the bed so the layer lines run along the rail.
2. **Legs** — split at the rim line into an upper leg (~5.4") and a lower
   foot/inner-leg/outer-finger piece (~5"). Join with a socket and two 6 mm
   dowels at Z=0; the foot hides the joint. Print both flat.
3. **Crossbars** — one per leg pair, ~7" long. Print on the flat side; sockets
   for the leg tops and sliders.
4. **Sliders** — four C-blocks that wrap the rails. Print with the sliding bore
   vertical (or split into two halves and bolt/glue) so the bearing surface is
   smooth.
5. **Bridge** — 6" × 6" × 2.5" housing. Print upright or split into top/bottom
   shells; it carries the turnbuckle, lead screw, and guide rods.
6. **Platform** — 5" × 5" plate, print flat. Add the bushings and nut as
   separate glued/heat-set parts.
7. **Cranks, lock collars, bushings, dowels** — small printed parts. Print
   dowels horizontally for strength, or use 1.75 mm filament offcuts.

## Open questions / assumptions to confirm

1. **Fixed rails vs telescoping arches.** The rails are fixed at 15" and the
   leg pairs slide inboard. This is much stiffer and simpler than a telescoping
   arch, but at 11" the rails overhang ~2.5" per side. Is that acceptable?
2. **Rim profile.** I assumed a flat 1" rim. What is the actual rim width and
   thickness range across your tanks? The outer finger should become a sliding
   clamp for 0.5–1.5" rims.
3. **Float valve.** What model is it, and how far does it hang below the
   platform? At −4" the valve body may approach the tank bottom.
4. **Larger hole.** Is 3/4" right, or should it be sized for a specific hose or
   bulkhead fitting? The 3/4" hole can take a reducing bushing for 3/8".
5. **Span mechanism.** Central turnbuckle needs left/right threads. Is that
   acceptable, or would you rather have a printed double-rack + pinion? A
   ratchet on the crank is the alternative to the sliding lock collar.
6. **Height mechanism.** Is a top-mounted 3/8" lead screw with a split lock
   collar enough, or do you want a ratchet/brake at the crank?
7. **Print split.** Confirm the leg split at the rim and the rail split at the
   centre; those are the two joints that need the most care.
