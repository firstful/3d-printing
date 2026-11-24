# Off-the-shelf parts: adjustment hardware and strap material

Research date: 2026-11-24 (Camoufox). Goal: avoid printing structural spans and
bespoke hardware. Printed parts should be **brackets, collars, sliders and end
caps** around stock that can be bought at a hardware store or Amazon.

## Frame options

| Option | Stock / hardware | Where to buy | Adjustment | Notes |
|---|---|---|---|---|
| **2020 T-slot extrusion (recommended)** | 20 × 20 mm aluminium extrusion, M5 sliding nuts + bolts, corner brackets | Amazon, Grainger, McMaster ("80/20-compatible"), local metal suppliers | Unlimited bolt positioning along slots — seat height/depth, footrest reach, back and tray height | No tube-fit tolerances; cheap generic extrusion and hardware kits. Printed plates bolt into the slots. Downside: many small fasteners, slot nuts can spin, extrusion is heavier than tube. |
| 80/20 10-Series | 1" × 1" (25 × 25 mm) T-slot profile, matching nuts/brackets | [Grainger](https://www.grainger.com/product/80-20-T-Slot-Framing-Extrusion-10-2RCP9), [McMaster](https://www.mcmaster.com/80/20-compatible-t-slotted-framing), Amazon | Same as above, more rigid | Better brand support, higher cost. Use if generic 2020 slots prove sloppy. |
| Telescoping square tube | Outer: [1" SQ × 7/8" ID × 0.063" wall 6063-T52 aluminium](https://www.speedymetals.com/pc-4680-8379-1-sq-wall-sq-tube-6063-t52-aluminum.aspx); inner: 7/8" OD tube; [push-button tube locks](https://www.mcmaster.com/products/push-button-telescoping-tube-locks) or [quick-release pins](https://www.mcmaster.com/products/pins/pin-type~quick-release/) | Metal suppliers, McMaster, Amazon | Discrete steps at drilled hole spacing (25–50 mm) | Fewer parts and lighter, but fit is **not guaranteed**: [Speedy Metals](https://www.speedymetals.com/Information/Telescoping.html) warns OD/ID tolerances and internal weld seams can block telescoping; allow ≥0.010" clearance and expect to sand/finish the inner tube. Printed shims/collars absorb the remaining slop. |
| Slip-on pipe fittings | [Kee Klamp](https://www.keesafety.com/safety-railings/kee-klamp/fittings) (galvanised cast iron) / [Kee Lite](https://www.keesafety.com/safety-railings/kee-lite/fittings) (aluminium) + hardware-store pipe | Kee Safety distributors, industrial suppliers | Set at assembly; not meant for frequent resizing | Fast, rigid, no welding. Good for the static lower frame; use slotted printed plates where adjustment is needed. |

**Recommendation:** 2020 extrusion for the vertical posts and cross rails, with
printed clamp plates and M5 hardware. It turns "size adjustment" into loosening
a bolt and sliding a bracket — no drilling, no tolerance-fitting, no custom
parts beyond the printed interface. Keep the telescoping-tube option as a
fallback if weight or cost dominates.

## Size-adjustment features to build

- **Seat height:** post-mounted seat bracket slides on the vertical extrusion;
  target 520–570 mm above floor (from `RESEARCH.md`).
- **Seat depth / width:** printed insert pans or sliding side plates; 8–12"
  usable width, 9–12" depth.
- **Footrest:** separate slider on the front posts, adjustable in height
  (110–380 mm below seat) and reach.
- **Back:** vertical slot carrier, 380 mm minimum height above seat, with
  lateral supports repositionable 140–355 mm apart.
- **Tray:** boom or arm brackets with height adjustment; tray is flat stock,
  not a large print.
- **Tilt / recline:** printed slotted arc plate + M5 bolt, 15° forward to
  25° back as the target envelope.
- **Reusable hardware:** M5 T-nuts/bolts, 1/4" quick-release pins with lanyards,
  Nyloc nuts on pivot points.

## Strap material

| Material | Properties | Availability | Use here |
|---|---|---|---|
| **1" nylon webbing** | Highest strength of the common webbings (~3× polypropylene), excellent abrasion resistance and shock absorption; absorbs water and stretches slightly when wet; UV degrades over time | [Walmart kit: 6 yd × 1" webbing, 6 side-release buckles, 12 tri-glides, 6 D-rings, ~$15](https://www.walmart.com/ip/Buckles-Strap-1-Inch-Nylon-Webbing-Straps-6-Yards-Quick-Side-Release-Plastic-Buckles-Dual-Adjustable-6-Pack-Tri-Glide-Slide-Clip-12-PCS-Metal-D-Rings/13076257682), Amazon equivalents ([6K+/month sold](https://www.amazon.com/side-release-buckle-1-inch/s?k=side+release+buckle+1+inch)) | Restraint webbing and high-wear straps. 25 mm width matches the 1" buckle ecosystem. |
| Polypropylene webbing | Lighter, water-resistant/buoyant, UV-stable, low stretch; lower strength and poorer abrasion resistance | Same kits and fabric stores | Non-critical straps: tray retention, footrest, storage. |
| Polyester seatbelt webbing | Low stretch, good UV resistance, wide (2") and common | Auto parts / Amazon | Pelvic or lap belt if a wider, lower-stretch strap is wanted. |
| **Universal 5-point high-chair harness** | Complete, adjustable, washable replacement belt; widely compatible with Graco and most 5-point chairs | [Amazon search](https://www.amazon.com/s?k=5+point+harness+straps), baby-gear retailers | **Preferred for the actual restraint.** Buying a finished harness avoids relying on DIY stitching and untested buckles. |

Material comparison source: [National Webbing](https://www.nationalwebbing.com/nylon-webbing-articles/nylon-webbing/choosing-between-polypropylene-and-nylon-webbing-96.html)
(nylon ~3× stronger, better abrasion/shock; polypropylene better in water/UV,
lighter, lower stretch).

## Safety / verification still required

- A webbing kit or buckle is **not** a certified child restraint. Use a
  commercial replacement harness for anything beyond a fit prototype.
- Printed clamp plates and slot nuts need proof-load testing; T-slot joint
  strength depends on profile, nut and bolt torque.
- Check strap width against printed slot geometry (25 mm nominal, with
  clearance) before cutting.
- Keep all harness/pivot hardware captured (Nyloc, washers, lanyards).

## Next actions

1. Price 2020 extrusion + M5 kit locally; confirm 25 mm webbing fits the printed slots.
2. Choose the commercial harness to design anchor geometry around.
3. Add `FRAME_PROFILE = 20` and slot/pitch parameters to `params.scad`.
4. Prototype one printed T-slot clamp plate and one tilt plate before the full set.
