// Preview only: section through the peg axis (x = -43.203) showing the pegs
// seated in the through-holes.
ramp_stl = "/home/reed/opencode-sessions/ramp-half-hex/ramp_half_hex.stl";
include <hex_ramp_clip.scad>

module half() { import(ramp_stl, convexity = 10); }
module keep() { translate([-105.6, -40, 195]) cube([105.6 - 43.203, 80, 70]); }

color([0.85, 0.72, 0.25]) intersection() { half(); keep(); }
color([0.85, 0.72, 0.25]) intersection() { translate([0, 0, 228.6]) half(); keep(); }
color([0.75, 0.12, 0.12])
    intersection() {
        translate([-43.203, 0.130691 * -43.203 + 13.8003, 228.6]) clip_use();
        keep();
    }
