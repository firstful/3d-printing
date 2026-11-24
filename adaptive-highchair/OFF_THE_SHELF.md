# Off-the-shelf parts: Home Depot stock, no cutting, splayed legs

Research date: 2026-11-24 (Camoufox). Constraint from the operator: material
must be buyable at Home Depot, and the build should need **no cutting**.
Legs splay outward for stability.

## Stock list (Home Depot)

| Item | Product | Length / size | Price (listed) | Use |
|---|---|---|---|---|
| Legs | [Everbilt 1 in. x 3 ft. Aluminum Square Tube, model 6615](https://www.homedepot.com/p/Everbilt-1-in-x-3-ft-Aluminum-Square-Tube-6615/300918656) | 36" (914 mm), 1" square | ~$16.54 each | Four legs, used full length — **no cuts** |
| Short rails | [LUKVIZO 6063 1 in. x 1 ft. Aluminum Square Tubing](https://www.homedepot.com/p/LUKVIZO-Series-6063-1-in-x-1-ft-Aluminum-Seamless-Square-Tubing-Structural-Metal-Pipe-1-Pack/332462119) | 12" (305 mm), 1" square | ~$60/1 ft (pricey but stocked) | Cross rails and brackets, used full length |
| Optional larger stock | Everbilt 1 in. x 4 ft / 6 ft / 8 ft, or 3/4 in. x 3 ft / 4 ft | 48–96" | $22–$48 | Only if a longer uncut span is ever needed |
| Straps | [1 in. x 10 ft. 400 lb Cam Buckle Tie-Down](https://www.homedepot.com/b/Tools-Tie-Downs/Cam-Buckle-Lashing-Strap/N-5yc1vZc2b7) (Husky / Keeper / EVEREST) | 1" webbing, 10–15 ft | ~$8–$15 | Non-critical retaining straps only |
| Fasteners | 1/4"-20 or M6 bolts, Nyloc nuts, washers, set screws | Aisle stock | — | Printed hub clamps |

Home Depot's own search results confirm Everbilt 3/4 in. and 1 in. square tube
is stocked in 3 ft, 4 ft, 6 ft and 8 ft lengths; 1 ft pieces are sold by
LUKVIZO. The original 1" × 0.063" wall tube from M-D Building Products is
listed as "can be telescoped."

## No-cut frame concept

- **Legs:** four full 3 ft tubes, tilted outward ~10° from vertical. No saw
  cuts. The top of each leg sits above the tray and can carry the back panel
  or a push handle.
- **Splay geometry (current `params.scad`):** foot footprint 640 × 700 mm,
  top of legs 400 × 460 mm, horizontal run ~120 mm per axis on each leg.
  With 914.4 mm legs the vertical height is ~868 mm.
- **Hubs:** printed clamp blocks with angled sockets receive the legs at the
  splay angle. A radial set screw or through-bolt locks each tube; the printed
  angle removes any need to mitre the tube ends.
- **Rails:** 1 ft tube pieces span between legs via printed collars. Because
  the legs splay, the gap between them changes with height — adjustment is
  done by sliding the collars, not by cutting rail stock.
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

## Safety / open items

- Splayed legs increase tip resistance sideways but still need a stability
  test with a child-sized load at the tray and seat.
- Printed hubs and set-screw joints are untested; proof-load before use.
- Confirm 1 ft tube piece price/length at the local store, and whether 1"
  square tube OD actually matches the printed socket (nominal vs. measured).
- Choose the commercial harness, then cut nothing — only print slots sized
  for 25 mm webbing.
