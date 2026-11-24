// Preview only: close-up of the seam, one clip seated, one exploded.
// Scene is rotated so the ramp's +Y is screen up before rendering.
ramp_stl = "/home/reed/opencode-sessions/ramp-half-hex/ramp_half_hex.stl";
include <hex_ramp_clip.scad>

module scene() {
    module half() { import(ramp_stl, convexity = 10); }
    module region() { translate([-70, -3, 228.6 - 50]) cube([90, 32, 100]); }

    color([0.82, 0.68, 0.20]) intersection() { half(); region(); }
    color([0.82, 0.68, 0.20])
        intersection() { translate([0, 0, 228.6]) half(); region(); }

    // seated clip at the mid-ramp column
    color([0.72, 0.10, 0.10])
        translate([-43.203, 0.130691 * -43.203 + 13.8003, 228.6]) clip_use();

    // exploded clip at the near-lip column
    color([0.10, 0.28, 0.75])
        translate([-3.609, 0.130691 * -3.609 + 13.8003 + 14, 228.6]) clip_use();
}

rotate([90, 0, 0]) scene();
