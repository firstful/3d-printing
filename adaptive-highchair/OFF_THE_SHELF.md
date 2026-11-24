# Off-the-shelf parts: Home Depot stock, splayed legs, cut to length

Research date: 2026-11-24 (Camoufox). Constraint from the operator: material
must be buyable at Home Depot. Cutting is allowed: straight tube cuts,
webbing cut to length with heat-sealed ends, and M5 through-bolts with
captive inserts (no tapping). Legs splay outward for stability.

## Stock list (Home Depot)

| Item | Product | Length / size | Price (listed) | Use |
|---|---|---|---|---|
| Legs | [Everbilt 3/4 in. x 3 ft. Aluminum Square Tube, model 6605](https://www.homedepot.com/p/Everbilt-3-4-in-x-3-ft-Aluminum-Square-Tube-6605/300918653) | 36" (914 mm), 3/4" square, 1/16" wall | ~$14.85 each | 4 legs cut to 760 mm — see `params.scad` |
| Longer stock | [Everbilt 3/4 in. x 6 ft. Aluminum Square Tube, model 6607](https://www.homedepot.com/p/Everbilt-3-4-in-x-6-ft-Aluminum-Square-Tube-Metal-Stock-6607/340451342) | 72" (1829 mm) | ~$27.58 | Source for the 450 mm rails (one 6 ft tube yields 4 rails) |
| Straps | [1 in. x 10 ft. 400 lb Cam Buckle Tie-Down](https://www.homedepot.com/b/Tools-Tie-Downs/Cam-Buckle-Lashing-Strap/N-5yc1vZc2b7) (Husky / Keeper / EVEREST) | 1" webbing, 10–15 ft | ~$8–$15 | Non-critical retaining straps only |
| Fasteners | M5 × 0.8 socket-head cap screws, 16 mm and 20 mm, Nyloc nuts, washers | Aisle stock | — | Through both tube walls; captive nut via `nut_insert.scad` |
| Webbing (yardage) | [1 in. nylon webbing kit](https://www.walmart.com/search?q=1+inch+nylon+webbing+by+the+yard) or similar | 1" (25 mm) | ~$15 for 6 yd | For printed strap anchors; heat-seal cut ends |

Home Depot stocks 3/4" and 1" square tube in 3 ft, 4 ft, 6 ft and 8 ft lengths;
1 ft pieces are also sold (LUKVIZO). M-D Building Products 1" × 0.063" wall tube
is listed as "can be telescoped."

## Frame concept

- **Legs:** four 760 mm pieces of 3/4" tube, tilted outward ~10° from
  vertical. The top of each leg sits above the tray and can carry the back
  panel or a push handle.
- **Splay geometry (current `params.scad`):** foot footprint 640 × 700 mm,
  top of legs 400 × 460 mm, horizontal run ~120 mm per axis on each leg.
  With 760 mm legs the vertical height is ~740 mm.
- **Hubs:** printed clamp blocks with angled sockets receive the legs at the
  splay angle. M5 through-bolts lock each joint; a printed captive-nut
  insert (`nut_insert.scad`) holds the Nyloc nut inside the tube. The printed
  angle removes any need to mitre the tube ends.
- **Rails:** 450 mm pieces of 3/4" tube span between legs. Because the legs
  splay, the gap between them changes with height — adjustment is done by
  sliding the collars, not by cutting rail stock.
- **Size adjustment:** seat, footrest, back and tray brackets all slide along
  the legs and lock with a bolt. Growth changes are collar moves.
- **Avoid:** T-slot extrusion and specialist fittings are out — they are not
  Home Depot aisle stock.

## Strap material

- Home Depot does **not** stock 1" nylon webbing by the yard in the general
  aisles; its webbing products are finished tie-downs, tool belts and tree
  straps. A 1" cam-buckle tie-down strap is the closest easily found source of
  25 mm webbing, but the cam buckle is not a child-restraint buckle.
- For the actual restraint, use a **commercial universal 5-point high-chair
  harness** (widely sold online). Design printed anchors around 25 mm
  webbing and the harness hardware; do not rely on DIY stitching.
- Nylon webbing is ~3× stronger than polypropylene with better abrasion and
  shock absorption; polypropylene is lighter, UV/water resistant and low
  stretch ([National Webbing](https://www.nationalwebbing.com/nylon-webbing-articles/nylon-webbing/choosing-between-polypropylene-and-nylon-webbing-96.html)).
- Cut webbing to length and heat-seal the ends with a lighter/hot knife.

## Safety / open items

- Splayed legs increase tip resistance sideways but still need a stability
  test with a child-sized load at the tray and seat.
- Printed hubs, inserts and joints are untested; proof-load before use.
- Confirm the 3/4" tube OD actually matches the printed socket (nominal vs.
  measured) and that the captive-nut insert fits the ID.
- Choose the commercial harness, then size print slots for 25 mm webbing.