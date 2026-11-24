// 3D-Printed Siphon Strainer -- split-collet tubing clamp
// Source geometry as provided (verbatim), rendered for review.

$fn = 64;

// Tubing
tube_od = 6.35;
clearance = 0.25;

// Collet
clamp_length = 18;
wall = 3;
slot_width = 1.2;
num_slots = 4;
taper = 1.5;

// Collar
collar_length = 12;
collar_clearance = 0.2;

// Derived
bore = tube_od + clearance;
clamp_od = bore + 2*wall;
collar_id = clamp_od - 0.5;

module collet() {
    difference() {
        cylinder(
            h=clamp_length,
            d1=clamp_od+taper,
            d2=clamp_od
        );

        translate([0,0,-0.1])
            cylinder(
                h=clamp_length+0.2,
                d=bore
            );

        for (a=[0:360/num_slots:359]) {
            rotate([0,0,a])
                translate([0,-slot_width/2,-0.1])
                    cube([
                        clamp_od+taper,
                        slot_width,
                        clamp_length+0.2
                    ]);
        }
    }
}

module collar() {
    difference() {
        cylinder(
            h=collar_length,
            d=collar_id+2*wall
        );

        translate([0,0,-0.1])
            cylinder(
                h=collar_length+0.2,
                d=collar_id
            );
    }
}

// Print collar (uncommented for separate render)
// collet();

// Uncomment to print collar separately
collar();
