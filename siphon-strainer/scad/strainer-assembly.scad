// Siphon strainer -- filter sphere with the threaded collet permanently
// attached. The collar is a separate part (print from adapter-threaded.scad).
//
// Port geometry: the collet's hex straddles the sphere shell. Its outer face
// sits 11.9 mm beyond the tangent plane so there is something to put a wrench
// on; its inner face pokes 2.1 mm into the cavity.
//
// The hex hull is subtracted from the shell BEFORE the collet is unioned in.
// A plain union would leave a disc of shell material across the bore; removing
// the hull first means the bore is clear, and the collet then fills that space.
//
// Apertures are 1.5 mm -- under half the ~3.2 mm ID of 1/4" PE tubing, so
// nothing that gets through a hole can bridge the tube.

include <adapter-parts.scad>
include <generated-supports.scad>

// Sphere
sphere_d = 76.2;
sphere_w = 2;
hole_d   = 1.5;
pitch    = 3.0;               // centre-to-centre spacing, hex packing

R = sphere_d/2;
// hex packing: adjacent rings are pitch*sqrt(3)/2 apart, alternate rings
// offset by half a step, and each ring's angular step is scaled by 1/cos(lat)
// so the arc spacing is constant within the ring
d_lat    = (pitch*sqrt(3)/2)/R * 180/PI;
n_rings  = floor(168/d_lat);

// Port placement: the collet's local z=0 is the hex's outer face
port_z = 50;                  // 11.9 mm beyond the 38.1 tangent plane

module radial_hole(lat, lon) {
    x = cos(lat)*cos(lon);
    y = cos(lat)*sin(lon);
    z = sin(lat);
    translate([x*(R-sphere_w/2), y*(R-sphere_w/2), z*(R-sphere_w/2)])
        rotate([0,90-lat,lon])
            cylinder(h = sphere_w+2, d = hole_d, center = true, $fn = 16);
}

module shell() {
    difference() {
        sphere(d = sphere_d);
        sphere(d = sphere_d - 2*sphere_w);

        for (i = [0 : n_rings]) {
            lat = -84 + i*d_lat;
            lon_step = (pitch/R)*180/PI / cos(lat);
            off = (i % 2) * lon_step/2;
            for (lon = [off : lon_step : 360 + off - 0.01])
                radial_hole(lat, lon);
        }
    }
}

// Internal lattice: vertical pillars inside the cavity. Printed as part of the
// sphere so the dome has something to sit on -- internal supports could never
// be removed. Pillars rather than walls: continuous plates would partition the
// cavity, leaving only the cell around the bore able to feed the tube and the
// rest of the sphere as dead volume. Pillars support the dome without
// interrupting flow between regions.
module lattice() {
    Ri = sphere_d/2 - sphere_w + 0.4;   // bite into the wall so they weld
    for (x = [-24, -8, 8, 24], y = [-24, -8, 8, 24]) {
        r = sqrt(x*x + y*y);
        if (r < Ri - 3) {
            hz = sqrt(Ri*Ri - r*r);
            translate([x, y, -hz])
                cylinder(h = 2*hz, d = 2.5, $fn = 12);
        }
    }
}

// outer hull of the collet's hex portion
module hex_hull() {
    translate([0,0,port_z - hex_h])
        cylinder(h = hex_h, d = hex_d, $fn = 6);
}

module assembly() {
    union() {
        difference() {
            shell();
            hex_hull();
        }
        lattice();
        generated_supports();
        translate([0,0,port_z]) collet();
    }
}

// print orientation: collet down on the plate, sphere above
translate([0,0,port_z + clamp_length]) rotate([180,0,0]) assembly();
