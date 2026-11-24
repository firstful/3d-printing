// Siphon strainer -- 1/4" tubing adapter (split collet + collar)
// Printed as a standalone pair; the sphere filter is combined later.
//
// Two fixes over the original geometry:
//   1. base_ring: slot cuts stop 2.5 mm short of the base, so the collet is one
//      part instead of four loose quarter-shells.
//   2. collar_id = clamp_od + collar_gap. The original clamp_od - 0.5 was
//      smaller than the collet's small end and could not be fitted at all.
//
// GRIP is set by the two numbers below. tube_bore controls how much the
// fingers must close to reach the tubing; collar_gap controls how hard the
// collar wedges them. Printed bores come out undersize by ~0.1-0.2 mm, so
// this is guess-and-check.

$fn = 64;

// ---- grip class (these are the knobs) ----
tube_bore  = 6.50;   // nominal tubing OD is 6.35
collar_gap = 0.30;   // collar_id = clamp_od + this

// Tubing
tube_od = 6.35;

// Collet
clamp_length = 18;
wall = 3;
slot_width = 1.2;
num_slots = 4;
taper = 1.5;
base_ring = 2.5;

// Collar
collar_length = 12;

// Derived
clamp_od  = tube_bore + 2*wall;
collar_id = clamp_od + collar_gap;
collar_od = collar_id + 2*wall;

// squeeze available at the base-ring stop, and the gap the fingers must close
gap_to_tube = (tube_bore - tube_od)/2;
squeeze_max = (taper*(1-base_ring/clamp_length) - collar_gap)/2;

echo(str("GRIP: bore=", tube_bore, " gap_to_tube=", gap_to_tube,
         " | collar_id=", collar_id, " squeeze_max=", squeeze_max));

module collet() {
    difference() {
        cylinder(h=clamp_length, d1=clamp_od+taper, d2=clamp_od);

        translate([0,0,-0.1])
            cylinder(h=clamp_length+0.2, d=tube_bore);

        for (a=[0:360/num_slots:359]) {
            rotate([0,0,a])
                translate([0,-slot_width/2,base_ring])
                    cube([clamp_od+taper, slot_width, clamp_length-base_ring+0.1]);
        }
    }
}

module collar() {
    difference() {
        cylinder(h=collar_length, d=collar_od);
        translate([0,0,-0.1])
            cylinder(h=collar_length+0.2, d=collar_id);
    }
}

// Both parts on one build plate
collet();
translate([22,0,0]) collar();
