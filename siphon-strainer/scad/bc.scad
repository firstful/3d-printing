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

// Sphere
sphere_d = 76.2;
sphere_w = 2;
hole_d   = 1.5;
spacing  = 3.5;

R = sphere_d/2;
step_lat = spacing/R * 180/PI;

// Port placement: the collet's local z=0 is the hex's outer face
port_z = 50;                  // 11.9 mm beyond the 38.1 tangent plane

module radial_hole(lat, lon) {
    x = cos(lat)*cos(lon);
    y = cos(lat)*sin(lon);
    z = sin(lat);
    translate([x*(R-sphere_w/2), y*(R-sphere_w/2), z*(R-sphere_w/2)])
        rotate([0,90-lat,lon])
            cylinder(h = sphere_w+2, d = hole_d, center = true);
}

module shell() {
    difference() {
        sphere(d = sphere_d);
        sphere(d = sphere_d - 2*sphere_w);

        for (lat = [-75 : step_lat : 75]) {
            lon_step = step_lat/max(cos(lat), 0.2);
            for (lon = [0 : lon_step : 360])
                radial_hole(lat, lon);
        }
    }
}

// outer hull of the collet's hex portion
module hex_hull() {
    translate([0,0,port_z - hex_h])
        cylinder(h = hex_h, d = hex_d, $fn = 6);
}

module asm() { union() {
    difference() {
        shell();
        hex_hull();
    }
    translate([0,0,port_z]) collet();
}

}
intersection() { asm(); translate([0,0,30]) cylinder(h=45, d=6.3); }
