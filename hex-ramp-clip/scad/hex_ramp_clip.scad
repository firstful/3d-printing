// ============================================================================
//  Hex-ramp join clip  —  joins two 228.6 mm hex ramp halves side by side
//
//  The ramp halves ("ramp_half_hex", 57-hole pattern) butt along their
//  228.6 mm edges.  The lattice row nearest that seam is 11.43 mm in on each
//  half and both end rows share the same X columns, so hole centres are
//  22.86 mm apart across the joint.
//
//  Seam-row hole columns are x = -82.80, -43.20 and -3.61.  The plate is only
//  ~3.0 mm thick at x = -82.80, so use the -43.20 or -3.61 column (8.1 /
//  13.4 mm of material).  Two clips per seam.
//
//  The clip drops two hex pegs into the hole pair either side of the seam and
//  bridges the joint with a low, chamfered bar on top.  Peg is a friction/glue
//  fit: `clearance` is the total diametral play.
//
//  Measured reference geometry (ramp_half_hex.stl):
//    hole across flats    15.86 mm  (hexagon vertices point along ramp X)
//    hole depth           through-hole; 8.1 or 13.4 mm at the two usable columns
//    top surface          plane y = 0.130691*x + 13.8003   (7.446 deg)
//    peg span             22.86 mm across the seam
//
//  Print (mode="print"): Z is up, bar top face on the bed, pegs pointing up.
// ============================================================================

// ------------------------------ parameters ---------------------------------
hole_af   = 15.86;      // measured hex hole, across flats
clearance = 0.30;       // total diametral clearance (0.15 per side)
peg_af    = hole_af - clearance;

peg_len   = 6.0;        // peg depth into the hole (plate is 8.2 deep here)
tip_ch    = 0.60;       // lead-in inset per side at the peg tip
tip_h     = 1.20;       // lead-in height

span      = 22.86;      // peg centres either side of the seam
plate_len = 40.0;       // bar length along Z (seam direction)
plate_w   = 24.0;       // bar width along X (slope direction)
plate_t   = 2.2;        // bar thickness above the ramp surface
edge_ch   = 2.0;        // chamfer on the two X edges

slope     = 0.130691;   // ramp top surface slope (7.446 deg)

$fa = 2; $fs = 0.4;

// -------------------------------- modules ----------------------------------
module hex_2d(af) {
    R = af / sqrt(3);
    polygon([for (k = [0:5]) [R * cos(60 * k), R * sin(60 * k)]]);
}

// thin hexagon lying in XZ at height y, extruded +Y
module hex_disc(af, y) {
    translate([0, y, 0]) rotate([-90, 0, 0])
        linear_extrude(height = 0.02) hex_2d(af);
}

// peg: lead-in tip at y = -len, axis +Y.  Runs 2.5 mm up into the bar so the
// union is flush with the bar's sloped underside (no wedge gap at the base).
module hex_peg(af, len, ch, chh) {
    merge = 2.5;
    hull() {
        hex_disc(af - 2 * ch, -len);
        hex_disc(af, -len + chh);
    }
    translate([0, -len + chh, 0]) rotate([-90, 0, 0])
        linear_extrude(height = len - chh + merge) hex_2d(af);
}

module bar() {
    w2 = plate_w / 2;
    c  = min(edge_ch, plate_t - 0.05);
    yb = slope * -w2;
    pts = [
        [-w2,     yb],
        [ w2,     slope * w2],
        [ w2,     slope * w2 + plate_t - c],
        [ w2 - c, slope * (w2 - c) + plate_t],
        [-w2 + c, slope * (-w2 + c) + plate_t],
        [-w2,     yb + plate_t - c],
    ];
    translate([0, 0, -plate_len / 2]) linear_extrude(height = plate_len) polygon(pts);
}

// everything above the plane y = slope*x + off (used to bury the peg tops
// inside the bar, so the union has no exposed peg/base wedge)
module above_surface(off) {
    th = atan(slope);
    rotate([0, 0, th])
        translate([0, off * cos(th), 0])
            translate([-120, 0, -120]) cube([240, 120, 240]);
}

// in-use orientation: bar underside on the ramp surface y = slope*x
module clip_use() {
    bar();
    for (z = [-span / 2, span / 2])
        translate([0, 0, z]) difference() {
            hex_peg(peg_af, peg_len, tip_ch, tip_h);
            above_surface(0.45);
        }
}

// print orientation: Z up, bar top face on the bed, pegs up
module clip_print() {
    th = atan(slope);
    rotate([90, 0, 0])
        translate([0, plate_t * cos(th), 0])
            rotate([0, 0, th]) rotate([180, 0, 0]) clip_use();
}

mode = "print";
if (mode == "print") clip_print();
if (mode == "use") clip_use();
