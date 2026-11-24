// Preview only: section through the top-row hole, insert seated.
ramp_stl = "/home/reed/opencode-sessions/ramp-half-hex/ramp_half_hex.stl";
include <hex_ramp_insert.scad>

sx = 16.189;
sy = 0.130691 * sx + 13.8003;
module keep() { translate([-105.6, -20, 195]) cube([105.6 + sx, 40, 40]); }

color([0.82, 0.68, 0.20]) intersection() { import(ramp_stl, convexity=10); keep(); }
color([0.72, 0.10, 0.10]) intersection() { translate([sx, sy, 205.74]) part_open(0); keep(); }
