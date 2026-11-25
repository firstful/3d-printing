// ============================================================================
//  hex_ramp_insert — screw-down registration post for the hex ramp's top row
//
//  Solid hex prism: bottom follows the measured transition arc, top is a flat
//  plane coplanar with (parallel to) the driving surface, 10 mm above it.
//  One bore down the centre, vertical to that top plane, with a countersink
//  colinear with it.  One countersunk screw into the transition underneath.
//
//  Measured reference (ramp_half_hex.stl)
//    hole            15.86 mm across flats, vertical through-bore, x = +16.19
//    top surface     plane y = 0.130691*x + 13.8003   (7.446 deg)
//    underside       rolled transition: arc R = 118.82, centre (63.0, -96.64)
//    band thickness  3.42 mm at the hole centre
// ============================================================================

// ------------------------------ parameters ---------------------------------
hole_af   = 15.86;      // measured hex hole, across flats
clearance = 0.30;       // total diametral clearance (0.15 per side)
insert_af = hole_af - clearance;

slope     = 0.130691;   // ramp surface slope
theta     = atan(slope);

boss_h    = 10.0;       // how far the post stands proud of the surface

hole_x    = 16.189;     // part-local origin = this hole's centre on the surface
y_face    = slope * hole_x + 13.8003;      // surface height in ramp coords
arc_cx    = 63.00 - hole_x;                // arc centre in part-local coords
arc_cy    = -96.64 - y_face;
arc_r     = 118.82;

// screw detent (M3 countersunk), on the hole axis
screw_d   = 3.4;
cs_d      = 6.0;
cs_depth  = 1.5;

$fa = 2; $fs = 0.4;

// -------------------------------- helpers ----------------------------------
module hex2d(af) {
    R = af / sqrt(3);
    polygon([for (k = [0:5]) [R * cos(60 * k), R * sin(60 * k)]]);
}

// half-space below the rolled transition's underside (the measured arc)
module below_arc() {
    R = arc_r; CX = arc_cx; CY = arc_cy;
    pts = [for (x = [-20:0.5:40]) [x, CY + sqrt(R * R - (x - CX) * (x - CX))]];
    translate([0, 0, -40]) linear_extrude(height = 80)
        polygon(concat(pts, [[40, -40], [-20, -40]]));
}

// -------------------------------- geometry ---------------------------------
module body() {
    // top is a flat plane parallel to the driving surface, boss_h above it
    top_off = boss_h / cos(theta);
    difference() {
        intersection() {
            // vertical hex prism through the bore
            translate([0, -14, 0]) rotate([-90, 0, 0])
                linear_extrude(height = 28) hex2d(insert_af);
            // top half-space: everything below the top plane
            rotate([0, 0, theta])
                translate([-200, -200, -200]) cube([400, 200 + top_off, 400]);
        }
        // remove everything above the curved underside
        below_arc();
    }
}

module part() {
    top_off = boss_h / cos(theta);
    difference() {
        body();
        // bore: straight down the centre, along the top plane's normal
        rotate([0, 0, theta])
            translate([0, top_off, 0]) rotate([-90, 0, 0])
                cylinder(h = top_off + 16, r = screw_d / 2);
        // countersink colinear with the bore
        rotate([0, 0, theta])
            translate([0, top_off, 0]) rotate([-90, 0, 0])
                cylinder(h = cs_depth + 0.2, r1 = cs_d / 2, r2 = screw_d / 2);
    }
}

// print: hex flat on the bed, post axis horizontal
mp = [[0, 1, 0, 0], [-1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]];

module part_print() {
    translate([12, 0, insert_af / 2]) multmatrix(mp) part();
}

mode = "print";
if (mode == "print") part_print();
if (mode == "use") part();