// Siphon strainer -- 1/4" tubing adapter, THREADED
// Collet + collar. Screwing the collar on draws it down the finger taper and
// squeezes the fingers onto the tubing; backing it off releases them.
//
// Threads: dkprojects.net/openscad-threads (GPL-3, v3.0) -- scad/lib/threads-dk.scad
//
// Layout (radii, about the collet axis):
//
//   collet  z 0..10   solid section, external thread (major 15.0)
//           z 10..22  four fingers, tapering 12.5 -> 11.5 dia
//   collar  z 0..10   internal thread (crest 13.58) -> clears the fingers
//           z 10..16  squeeze bore 12.0 -> smaller than the finger base
//
// The step between those two bores is what makes it work: the internal thread
// has to clear the fingers or the collar binds on the way off, while the
// squeeze bore has to sit under the finger diameter or it never grips.

include <lib/threads-dk.scad>

$fn = 64;

// ---- grip class (edit this) ----
tube_bore = 6.70;          // nominal tubing OD is 6.35

// Collet
clamp_length = 22;
thread_len   = 10;
squeeze_len  = 6;
wall         = 3;
slot_width   = 1.2;
num_slots    = 4;
finger_tip_r = 5.75;

// Thread
thread_pitch     = 2.0;
thread_size      = 1.4;    // V height (shallower than the 2.0 pitch -> wide lands)
thread_clear_dia = 1.0;    // collar cut with a thread this much oversize

// Collar
collar_wall = 2.4;
knurl_n     = 24;
knurl_depth = 0.7;

// Collet base
hex_af = 22;               // across flats
hex_h  = 16;              // long enough to straddle the sphere shell + 1 cm of wrench access
hex_d  = hex_af*2/sqrt(3); // circumscribed dia for $fn=6

// Derived
core_r     = tube_bore/2 + wall;          // 6.25 -> 12.5 dia
thread_od  = 2*core_r + 2.5;              // 15.0 major
thread_h   = thread_size/(2*tan(30));     // 1.21 radial thread depth
cutter_od  = thread_od + thread_clear_dia;// 16.0 -> collar cut oversized
fem_minor  = cutter_od - 2*thread_h;      // 13.58 -> clears the fingers by 0.54
squeeze_r  = core_r - 0.25;               // 12.0 dia
collar_r   = cutter_od/2 + collar_wall;

echo(str("GRIP: bore=", tube_bore, " core=", 2*core_r, " thread=", thread_od,
         " collar_minor=", fem_minor, " finger_clearance=", (fem_minor-2*core_r)/2,
         " squeeze_bore=", 2*squeeze_r, " collar_od=", 2*collar_r));

// Barbed grip grooves inside the finger bore. Asymmetric: a long ramp on the
// low-z side (so the tubing slides in), a square shoulder on the high-z side
// (so pulling it back out has to shear the PE). Tube enters from the finger
// tips at high z, so pull-out is the +z direction.
module grip_grooves() {
    rb = tube_bore/2;
    d  = 0.40;   // groove depth
    L  = 0.80;   // ramp length
    w  = 0.30;   // flat bottom
    lip = 0.12;  // ramp starts this far inside the bore -- keeps the entry clean
                 // and lets the ramp run out gradually instead of ending on the wall
    for (z = [thread_len + 1.5 : 2.0 : thread_len + 6])
        rotate_extrude($fn = 64)
            polygon([[rb - lip,  z],
                     [rb + d,    z + L],
                     [rb + d,    z + L + w],
                     [rb - 0.05, z + L + w]]);
}

module collet() {
    difference() {
        union() {
            // hex base -- grip for fingers/wrench, and the collar's seating stop
            translate([0,0,-hex_h])
                cylinder(h = hex_h, d = hex_d, $fn = 6);
            cylinder(h = thread_len, r = core_r);
            metric_thread(diameter = thread_od, pitch = thread_pitch,
                          length = thread_len, thread_size = thread_size);
            translate([0,0,thread_len])
                cylinder(h = clamp_length - thread_len, r1 = core_r, r2 = finger_tip_r);
            // fill the gap the library's thread chamfer leaves under the hex,
            // so the hex underside is a cone rather than a flat annulus
            translate([0,0,-0.01])
                cylinder(h = 1.51, r1 = thread_od/2 + 0.1, r2 = core_r + 0.05);
        }

        translate([0,0,-hex_h-0.1])
            cylinder(h = clamp_length + hex_h + 0.2, r = tube_bore/2);

        grip_grooves();

        // chamfer the hex's inner face: the step from the hex down to the
        // thread is otherwise a horizontal annular ledge (the worst possible
        // overhang). Turning it into a ~45 deg cone makes it printable with no
        // support; the collar now stops against this cone instead of a flat.
        // Subtract only the corner WEDGE (hex minus cone), not the whole cone,
        // or the hex gets severed from the thread.
        translate([0,0,-5])
            difference() {
                cylinder(h = 5.01, d = hex_d, $fn = 6);
                // hexagonal, same facet count AND orientation as the outer
                // prism: a circular cone grazes the hex corners and leaves
                // zero-thickness fins that flicker in the viewer
                cylinder(h = 5.02, d1 = hex_d, d2 = thread_od, $fn = 6);
            }

        // lead-in at the thread's far end. The library chamfers only the
        // low-z end, and the part is printed flipped, so this end would
        // otherwise present a flat annular face. Subtract only the outer
        // wedge -- a full-radius cone here severs the fingers from the thread.
        translate([0,0,thread_len-1.2])
            difference() {
                cylinder(h = 1.21, r = thread_od/2 + 0.2);
                cylinder(h = 1.22, r1 = thread_od/2 + 0.2, r2 = core_r);
            }

        for (a = [0:360/num_slots:359])
            rotate([0,0,a])
                translate([0, -slot_width/2, thread_len + 0.6])
                    cube([core_r + 1, slot_width, clamp_length - thread_len - 0.6 + 0.1]);
    }
}

// axial knurl: V-grooves cut into a cylindrical OD
module knurl(r, h, n = 24, depth = 0.7, w = 1.2) {
    for (a = [0:360/n:359])
        rotate([0,0,a])
            translate([r - depth + w*0.7071, 0, h/2])
                rotate([0,0,45])
                    cube([w, w, h], center = true);
}

module collar() {
    difference() {
        cylinder(h = thread_len + squeeze_len, r = collar_r);

        // axial knurl on the grip surface
        knurl(collar_r, thread_len + squeeze_len, knurl_n, knurl_depth);

        // squeeze bore, upper part
        translate([0,0,thread_len])
            cylinder(h = squeeze_len + 0.1, r = squeeze_r);

        // internal thread, lower half: cut with an oversized copy of the
        // external thread rather than internal=true (which silently produced
        // no bore here). Leaves thread_clear_dia of diametral clearance.
        metric_thread(diameter = cutter_od, pitch = thread_pitch,
                      length = thread_len, thread_size = thread_size);

        // lead-in funnel at the entry face -- without this the flat thread
        // start has to be aligned by eye and will not catch
        translate([0,0,-0.01])
            cylinder(h = 1.2, r1 = cutter_od/2 + 0.2, r2 = fem_minor/2);
    }
}

