// Drill guide for 3/4" square tube — aligns a hole with the nut insert.
// Slide the tube in until it seats against the end stop, then drill.
// Units mm. See BOM.md and nut_insert.scad.

include <params.scad>

/* [Jig] */
JIG_W      = 30;                    // outer width
JIG_H      = 30;                    // outer height
JIG_L      = 30;                    // outer length
TUBE_OD    = TUBE + 0.2;            // 19.25, clearance on 3/4" tube
STOP_T     = 2;                     // end-stop plate thickness
HOLE_Z     = STOP_T + INSERT_L / 2; // 14.5, matches nut_insert.scad

$fn = 48;

module drill_jig() {
    difference() {
        cube([JIG_W, JIG_H, JIG_L], center = false);

        // Tube passage, from stop plate to open end.
        translate([JIG_W / 2 - TUBE_OD / 2, JIG_H / 2 - TUBE_OD / 2, STOP_T - 0.01])
            cube([TUBE_OD, TUBE_OD, JIG_L - STOP_T + 0.02], center = false);

        // Drill guide hole, perpendicular to the tube.
        translate([0, JIG_H / 2, HOLE_Z])
            rotate([0, 90, 0])
                cylinder(h = JIG_W + 2, r = BOLT_CLEAR_D / 2, center = true);
    }
}

drill_jig();
