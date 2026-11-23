# Adaptive high-chair — commercial product research

Research date: 2026-11-23. Collected with Camoufox from manufacturer pages,
official spec sheets, and product manuals. All dimensions are **inches**
unless marked otherwise; convert to mm in `params.scad`.

Goal: extract real-world geometry, adjustment ranges, and feature sets to use
as design inputs. This is **not** a copy of any product and is not a safety
certification.

## Comparison

| Product | Class | Overall W × D × H | Seat W × D | Seat height | Capacity | Notable properties |
|---|---|---|---|---|---|---|
| [Rifton Activity Chair](https://www.rifton.com/products/rifton-activity-chairs) | Adaptive, paediatric→adult | frame W 21–29¾; floor seat H 9½–25 (leg/base dependent) | W 7–17 (w/ hip guides 7–14); D 7–20 | 9½–25 above floor | 75 / 150 / 250 lb by size (R820/R840/R860 and hi/lo variants) | Tool-free while seated; tilt-in-space 15° fwd–25° back; back angle 5° fwd–20° back; knee angle 45–110°; hip guides, laterals, trunk/head supports, pelvic + thigh belts, tray + handhold, hi/lo base, casters |
| [TherAdapt Feeding Chair – Height Chair](https://theradapt.com/product/feeding-chair-height-chair-by-theradapt/) (TA-FC-100) | Adaptive feeding | 31 × 30 × 19; 47 lb | W 6–11½; D 6–14 | 21–22¼ above floor; footrest 4½–15 below seat | 75 lb user | Freestanding at dining table; slotted height/depth/angle seat, angled back, adjustable footrest; 1" pelvic belt; back H 15; side H 26 (27½–30 w/ armrests); optional 24×20 tray w/ 17½×4 cutout or 26×21 tray w/ 13½×6 cutout |
| [Stokke Tripp Trapp](https://www.manua.ls/stokke/tripp-trapp/manual) | Convertible wooden | 18.1 × 19.3 × 31.1 (46 × 49 × 79 cm) | — | seat + footplate height and depth adjustable | 110 kg / 242 lb | Grows child→adult; Baby Set 6–36 mo: rail 40 cm W × 20 cm D × 20 cm H, back piece 35 × 22.5 cm, box 43 × 19 × 22 cm / 0.75 kg ([Stokke FAQ](https://www.stokke.com/USA/en-us/customer-service/faq/faq-tripp-trapp-accessories/faq-tripp-trapp-accessories-q-02.html)) |
| [IKEA ANTILOP](https://www.ikea.com/us/en/p/antilop-high-chair-with-tray-white-white-s39597517/) | Low-cost mainstream | 24 × 26 × 35⅜ | W 9⅞; D 8⅝ | 21¼ | 33 lb | PP shell + tray, powder-coated steel legs; 3-point belt; wipe-clean, light, cheap; baseline for footprint |
| [Graco Blossom 6-in-1](https://www.gracobaby.com/shop/home-and-gear/high-chairs/blossom-6-in-1-convertible-highchair/SAP_2136860.html) | Convertible, multi-child | 22.5 × 29 × 41; 32.56 lb | — | 6-position height adjust | 40 lb highchair / 60 lb toddler booster | 6 stages incl. 2 kids at once; 3-position recline; 3-position footrest; convertible 3-/5-point harness; one-hand removable tray; dishwasher-safe insert |
| [Chicco Polly](https://www.chiccousa.com/shop-our-products/high-chairs-and-boosters/standard-high-chairs/polly-high-chair/79756.html) | Folding mainstream | folds to 11" W | — | 7-position height | 40 lb / 6–36 mo | 3-position reclining seat + footrest; 5-point harness; foldaway armrests; extra-large tray w/ removable liner; tray stores on rear legs |
| [OXO Tot Sprout](https://www.oxo.com/media/wysiwyg/PDF_Files/tot_Sprout_Manual_English2.pdf) | Convertible wooden | 24 × 24 × 37; ~28 lb (retailer listing) | seat adjusts in height, width, depth | 3 seat heights + adjustable footrest | 60 lb (27 kg) | Solid birch, tool-free adjustments, depth-adjustable single-hand tray, 5-point harness, converts to youth chair at 3 yrs |

Rifton per-size details from the official
[dimensions chart PDF](https://www.rifton.com/-/media/files/rifton/product-information/rifton-activity-chair-dimensions-chart.pdf):

| Size | User height | Seat W | Seat D | Back H | Armrest above seat | Load |
|---|---|---|---|---|---|---|
| Small (R820/R830) | 32–48 (28–38 w/ mini kit) | 7–12 | 8–12 (7–11 mini) | 12½–15½ | 5–7½ | 75 lb |
| Medium (R840/R850) | 40–56 | 8½–14 | 11–16 | 15½–19 | 7–10½ | 150 lb |
| Large (R860/R870) | 50–74 | 11–17 | 15–20 | 19–24 | 7–10½ | 250 lb |

## Extracted design inputs

- **Seat width / depth:** adaptive seats span 6–17" W and 6–20" D across
  growth stages. A 6–36-month target is roughly **8–12" W × 9–12" D**;
  growth is handled by inserts rather than one oversized shell.
- **Seat height:** 21–22¼" above floor (TherAdapt, ANTILOP) suits a standard
  29–30" dining table. Adaptive frames need a wider range (9½–25") for
  wheelchair/table/floor transfer.
- **Foot support:** must be independently adjustable in height and depth;
  TherAdapt gives 4½–15" below seat, Rifton 7–21¼" depending size.
- **Posture:** tilt-in-space ±15–25°, back recline 5° forward–20° back,
  knee angle 45–110° are realistic adjustment envelopes for feeding and
  tone management.
- **Lateral support:** hip guides / trunk laterals, with spacing adjustable
  from ~5½" to 14"; backrest 12½–24" above seat.
- **Restraint:** 5-point harness plus a separate 1" pelvic positioning belt;
  thigh belt on larger adaptive chairs. Tray is never the restraint.
- **Tray:** ~24 × 20" with a body cut-out ~17½ × 4" for a full-size adaptive
  chair; child-size trays are smaller. Needs depth adjustment and one-hand
  removal.
- **Adjustment mechanism:** tool-free slotted plates, side-release levers,
  and spring detents are the common pattern. Printable parts are best used
  as brackets, sliders, and end caps around off-the-shelf tube/wood stock.

## Source notes

- Manufacturer pages were read directly in Camoufox; the IKEA measurements
  came from its "Measurements" tab, Graco/Chicco from their product pages.
- Stokke overall dimensions and OXO overall dimensions come from a manual
  mirror and a retailer listing respectively — re-verify against a current
  first-party spec sheet before treating them as exact.
- Prices were ignored; assistive seating listed at $900–$4,500 sets the
  cost context for a printed alternative.
