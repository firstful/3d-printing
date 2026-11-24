// Siphon strainer -- 1/4" tubing adapter, THREADED
// Collet + collar. Screwing the collar on draws it down the finger taper and
// squeezes the fingers onto the tubing; backing it off releases them.
//
// Threads: dkprojects.net/openscad-threads (GPL-3, v3.0) -- scad/lib/threads-dk.scad
//
// Layout (radii, about the collet axis):
//
//   collet  z 0..6    solid section, external thread (major = core + 2.5 dia)
//           z 6..18   four fingers, tapering core -> core-1.0 dia
//   collar  z 0..6    internal thread; its minor dia sits 0.33 over the core,
//                     so the fingers pass through it when the collar is off
//           z 6..12   squeeze bore = core - 0.5 dia -> bites the finger base
//
// The step between those two bores is what makes it work: the internal thread
// has to clear the fingers or the collar binds on the way off, while the
// squeeze bore has to sit under the finger diameter or it never grips.

include <lib/threads-dk.scad>

$fn = 64;

// ---- grip class (edit this) ----
tube_bore = 6.50;          // nominal tubing OD is 6.35

// Collet
clamp_length = 18;
thread_len   = 6;
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

module collet() {
    difference() {
        union() {
            cylinder(h = thread_len, r = core_r);
            metric_thread(diameter = thread_od, pitch = thread_pitch,
                          length = thread_len, thread_size = thread_size);
            translate([0,0,thread_len])
                cylinder(h = clamp_length - thread_len, r1 = core_r, r2 = finger_tip_r);
        }

        translate([0,0,-0.1])
            cylinder(h = clamp_length + 0.2, r = tube_bore/2);

        for (a = [0:360/num_slots:359])
            rotate([0,0,a])
                translate([0, -slot_width/2, thread_len])
                    cube([core_r + 1, slot_width, clamp_length - thread_len + 0.1]);
    }
}

module collar() {
    difference() {
        cylinder(h = thread_len*2, r = collar_r);

        // squeeze bore, upper half
        translate([0,0,thread_len])
            cylinder(h = thread_len + 0.1, r = squeeze_r);

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

zb = 3;
difference() {
    union() {
        color("SteelBlue") collet();
        color("DarkOrange") translate([0,0,zb]) collar();
    }
    translate([-40,-40,-10]) cube([80,40,40]);
}
