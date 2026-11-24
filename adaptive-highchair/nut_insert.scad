// Captive 1/4-20 nut insert for 3/4" square aluminium tube.
// Slide into the tube end, align with a drilled hole, bolt through the tube.
// No tapping. Units mm. See BOM.md and drill_jig.scad.

include <params.scad>

/* [Insert] */
TUBE_ID       = TUBE - 2 * TUBE_WALL;   // 15.87 nominal
INSERT_CLEAR  = 0.35;                   // per side, for FDM fit
INSERT_W      = TUBE_ID - 2 * INSERT_CLEAR;  // ~15.17

/* [Fastener — all thread values come from params.scad] */
HEX_R         = (NUT_AF + NUT_POCKET_CLEAR) / 2 / cos(30);
HOLE_Z        = INSERT_L / 2;

$fn = 48;

module nut_insert() {
    difference() {
        translate([-INSERT_W / 2, -INSERT_W / 2, 0])
            cube([INSERT_W, INSERT_W, INSERT_L], center = false);

        // Bolt clearance through the insert.
        translate([0, 0, HOLE_Z])
            rotate([0, 90, 0])
                cylinder(h = INSERT_W + 2, r = BOLT_CLEAR_D / 2, center = true);

        // Hex pocket on the far wall captures the nut against rotation.
        translate([-INSERT_W / 2 - 0.01, 0, HOLE_Z])
            rotate([0, 90, 0])
                cylinder(h = NUT_H + NUT_POCKET_CLEAR, r = HEX_R, center = false, $fn = 6);
    }
}

nut_insert();
