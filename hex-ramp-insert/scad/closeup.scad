// Preview only: two inserts in the ramp's top row, one at rest, one out.
ramp_stl = "/home/reed/opencode-sessions/ramp-half-hex/ramp_half_hex.stl";
include <hex_ramp_insert.scad>

sx = 16.189;
sy = 0.130691 * sx + 13.8003;

module scene() {
    intersection() { import(ramp_stl, convexity = 10);
                     translate([-8, -3, 168]) cube([56, 32, 80]); }
    translate([sx, sy, 182.88]) part_open(0);
    translate([sx, sy, 205.74]) part_open(1);
}
rotate([90, 0, 0]) scene();
