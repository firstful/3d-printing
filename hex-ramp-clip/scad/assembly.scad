// Preview only: two ramp halves butted along their 228.6 mm edges with the
// join clip seated in the lattice holes either side of the seam.
//   openscad -D mode='"none"' -D ramp_stl='"<path>/ramp_half_hex.stl"' assembly.scad
ramp_stl = "/home/reed/opencode-sessions/ramp-half-hex/ramp_half_hex.stl";

include <hex_ramp_clip.scad>

module half() { import(ramp_stl, convexity = 10); }

color([0.85, 0.72, 0.25]) half();
color([0.85, 0.72, 0.25]) translate([0, 0, 228.6]) half();

// two clips per seam, one per usable hole column
for (x0 = [-43.203, -3.609])
    color([0.75, 0.15, 0.15])
        translate([x0, 0.130691 * x0 + 13.8003, 228.6]) clip_use();

// mark the seam
color([0.2, 0.4, 0.9])
    translate([-105.6, 0, 228.55]) cube([137.1, 0.1, 0.1]);
