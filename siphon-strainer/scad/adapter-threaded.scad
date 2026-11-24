// Siphon strainer -- standalone adapter print (collet + collar).
// The collet geometry lives in adapter-parts.scad, which the filter assembly
// also includes, so the test print is the same part that goes into the sphere.

include <adapter-parts.scad>

// Both parts on one plate, both resting on z=0. Collar flipped so its
// threaded bore faces up. The collet is lifted by hex_h because its hex base
// extends below the thread datum.
translate([0,0,hex_h]) collet();
translate([27,0,0]) rotate([180,0,0]) translate([0,0,-(thread_len+squeeze_len)]) collar();
