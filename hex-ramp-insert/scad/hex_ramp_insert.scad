// ============================================================================
//  hex_ramp_insert — screw-down anchor / registration insert for the top row
//  of the hex ramp (the row after the vertical jump, over the rolled,
//  curved transition).
//
//  How it is used
//    1. ramp in place, insert dropped into a top-row hole: the hex post goes
//       through the bore down to the floor, the plate sits flush with the
//       driving surface, slider in "rest" (screw covered).
//    2. slide the slider out (down-slope): it overlaps the ramp surface, the
//       ramp is captive, and the screw detent in the plate is exposed.
//    3. drive one countersunk screw through the plate and post into the floor.
//    4. later: slide the slider back in, lift the ramp away - the screwed
//       posts stay behind as registration pillars.
//
//  Measured reference (ramp_half_hex.stl)
//    hole                15.86 mm across flats, vertical through-bore
//    top row             x = +16.19 column, in the rolled lip; the lip
//                        underside is an arc R = 118.82 centred (63.0, -96.64)
//    top surface         plane y = 0.130691*x + 13.8003  (7.446 deg)
//    floor -> surface    15.92 mm at that column
//
//  Print: lying on its side, hex post flat on the bed, slider plane vertical.
//  Every running gap is horizontal - no supports, no bridging.
// ============================================================================

// ------------------------------ parameters ---------------------------------
hole_af   = 15.86;      // measured hex hole, across flats
clearance = 0.30;       // total diametral clearance (0.15 per side)
insert_af = hole_af - clearance;
R_hex     = insert_af / sqrt(3);

slope     = 0.130691;   // ramp surface slope
theta     = atan(slope);

post_len  = 3.42;       // driving surface -> the curved underside (band thickness)

// the rolled transition's underside, measured on the ramp
arc_cx    = 63.00;      // in ramp coordinates (hole centre at x = 16.189)
arc_cy    = -96.64;
arc_r     = 118.82;
hole_x    = 16.189;     // part local origin is this hole's centre on the surface
y_face    = 0.130691 * hole_x + 13.8003;   // surface height there (ramp coords)
arc_lx    = arc_cx - hole_x;               // arc centre in part-local coords
arc_ly    = arc_cy - y_face;

// screw detent (M3 countersunk)
screw_x   = 3.0;
screw_d   = 3.4;
cs_d      = 6.0;
cs_depth  = 1.5;

// slider
sl_len    = 12.5;
sl_w      = 7.2;
sl_t      = 1.25;
sl_gap    = 0.25;
fl_w      = 1.00;
fl_t      = 0.30;
travel    = 5.5;

// rails (T-slot)
rail_len  = 10.6;
rail_wall = 1.15;
rail_h    = 0.75;
rail_oh_t = 0.20;

// retracted stop (also supports the slider while printing)
stop_x    = 6.20;
stop_d    = 0.55;

$fa = 2; $fs = 0.4;

// -------------------------------- helpers ----------------------------------
module hex2d(af) {
    R = af / sqrt(3);
    polygon([for (k = [0:5]) [R * cos(60 * k), R * sin(60 * k)]]);
}

// profile in local (Z, Y), extruded along local X
module prism_x(pts, len) {
    translate([-len / 2, 0, 0]) rotate([0, 90, 0])
        linear_extrude(height = len) polygon(pts);
}

// half-space y < slope*x  (below the ramp's driving surface)
module below_face() {
    rotate([0, 0, theta]) translate([-200, -200, -200]) cube([400, 200, 400]);
}

// -------------------------------- body -------------------------------------
// region below the rolled transition's underside (arc, measured)
module below_arc() {
    R = arc_r; CX = arc_lx; CY = arc_ly;
    pts = [for (x = [-20:0.5:40]) [x, CY + sqrt(R * R - (x - CX) * (x - CX))]];
    translate([0, 0, -40]) linear_extrude(height = 80)
        polygon(concat(pts, [[40, -40], [-20, -40]]));
}

module post() {
    difference() {
        intersection() {
            translate([0, -12, 0]) rotate([-90, 0, 0])
                linear_extrude(height = 16) hex2d(insert_af);
            below_face();
        }
        below_arc();
    }
}

module rail_pair() {
    w2 = sl_w / 2;
    outer = w2 + fl_w + 0.15;
    for (s = [1, -1]) {
        translate([-rail_len / 2, 0, s > 0 ? outer : -(outer + rail_wall)])
            cube([rail_len, rail_h, rail_wall]);
        translate([-rail_len / 2, rail_h, s > 0 ? w2 + 0.15 : -(outer + rail_wall)])
            cube([rail_len, rail_oh_t, outer + rail_wall - (w2 + 0.15)]);
    }
}

module stop_post() {
    translate([stop_x, 0, -sl_w / 2])
        cube([stop_d, sl_gap + sl_t, sl_w]);
}

module slider() {
    x0 = stop_x - 0.05;
    xc = x0 - sl_len / 2;
    translate([xc - sl_len / 2, sl_gap, -sl_w / 2])
        cube([sl_len, sl_t, sl_w]);
    for (s = [1, -1])
        translate([xc - sl_len / 2, sl_gap, s * sl_w / 2 - (s > 0 ? 0 : fl_w)])
            cube([sl_len, fl_t, fl_w]);
    // registration boss at the hole centre, on the slider's top
    translate([0, sl_gap + sl_t, 0]) cylinder(h = 0.35, d = 3.2, $fn = 48);
}

module fixtures() {
    rotate([0, 0, theta]) {
        rail_pair();
        stop_post();
    }
}

// running clearance around the slider, so the body can never weld to it
module slider_shell() {
    minkowski() {
        rotate([0, 0, theta]) slider();
        cube([0.44, 0.44, 0.44], center = true);   // 0.22 each way
    }
}

// -------------------------------- assembly ---------------------------------
module part_open(k) {
    yf = slope * screw_x;                    // face height at the screw
    difference() {
        difference() {
            union() { post(); fixtures(); }
            slider_shell();
        }
        // screw clearance, vertical through the post
        translate([screw_x, -post_len - 1, 0]) rotate([-90, 0, 0])
            cylinder(h = yf + 12, r = screw_d / 2);
        // countersink, flush with the face
        translate([screw_x, yf - cs_depth, 0])
            cylinder(h = cs_depth + 0.2, r1 = screw_d / 2, r2 = cs_d / 2);
    }
    rotate([0, 0, theta]) translate([-travel * k, 0, 0]) slider();
}

module part() { part_open(open); }

// print: hex post flat on the bed (use-Y -> print X, use-Z -> print Z)
mp = [[0, 1, 0, 0], [-1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]];

module part_print() {
    translate([post_len / 2 + 1, 0, insert_af / 2]) multmatrix(mp) part();
}

open = 0;   // 0 = rest, 1 = fully out (only affects "use")

mode = "print";
if (mode == "print") part_print();
if (mode == "use") part();
