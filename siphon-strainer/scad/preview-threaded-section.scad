// Siphon strainer -- 1/4" tubing adapter, THREADED version
// Collet + collar. Screwing the collar on draws it down the finger taper and
// squeezes the fingers onto the tubing; backing it off releases them.
//
// Layout (radii, all relative to the collet axis):
//
//   collet  z 0..6    solid cylindrical section carrying the external thread
//           z 6..18   four fingers, tapering 12.5 -> 11.5 dia
//   collar  z 0..6    internal thread (crest 12.9) -> clears the fingers
//           z 6..12   squeeze bore (12.0) -> smaller than the finger base
//
// The step between those two bores is what makes it work: the thread has to
// clear the fingers (else the collar binds on the way off), while the squeeze
// bore has to be under the finger diameter (else it never grips).
//
// Travel: 6 mm of thread (3 turns at 2 mm pitch) takes the squeeze bore from
// zero interference at z=12 to 0.25 mm radial at the finger base.

$fn = 64;

// ---- grip class (edit this) ----
tube_bore = 6.50;          // nominal tubing OD is 6.35

// Collet
clamp_length = 18;
thread_len   = 6;
wall         = 3;
slot_width   = 1.2;
num_slots    = 4;
finger_tip_r = 5.75;       // radius at the free end (11.5 dia)

// Thread
thread_pitch = 2.0;
thread_depth = 0.55;
thread_clear = 0.25;      // deliberately loose -- compression, not friction, holds it
crest_flat   = 0.5;
flank_run    = 0.6;

// Collar
collar_wall  = 2.5;

// Derived
core_r      = tube_bore/2 + wall;          // 6.25 -> 12.5 dia
thread_maj  = core_r + thread_depth;       // 6.80 -> 13.6 dia
int_crest   = core_r + thread_clear;       // 6.45 -> 12.9 dia
int_groove  = thread_maj + thread_clear;   // 7.00 -> 14.0 dia
squeeze_r   = core_r - 0.25;               // 6.00 -> 12.0 dia
collar_od   = int_groove + collar_wall;    // 9.50 -> 19.0 dia
turns       = thread_len/thread_pitch;

echo(str("GRIP: bore=", tube_bore, " core=", 2*core_r, " squeeze_bore=", 2*squeeze_r,
         " interference_at_base=", core_r - squeeze_r,
         " | collar_id_thread=", 2*int_crest, " od=", 2*collar_od));

// ---- helical thread -------------------------------------------------------
// Sweeps a trapezoidal ridge along a helix. r0 = root (core) radius,
// r1 = crest radius. Used as a solid for the external thread and as a
// cutter for the internal one (just pass radii offset by the clearance).
module helical_thread(r0, r1, pitch, turns, steps_per_turn = 48) {
    n = ceil(turns*steps_per_turn);
    root = pitch - 2*flank_run - crest_flat;
    prof = [[0, r0], [root, r0], [root+flank_run, r1],
            [root+flank_run+crest_flat, r1], [pitch, r0]];

    pts = [ for (i = [0:n])
              let (a = 360*turns*i/n, dz = pitch*turns*i/n)
                for (k = [0:4])
                  [ prof[k][1]*cos(a), prof[k][1]*sin(a), prof[k][0] + dz ] ];

    side = [ for (i = [0:n-1]) for (k = [0:4])
               let (a = i*5 + k,
                    b = i*5 + (k+1)%5,
                    c = (i+1)*5 + (k+1)%5,
                    d = (i+1)*5 + k)
                 [a, b, c, d] ];

    faces = concat(side,
                   [[4, 3, 2, 1, 0]],
                   [[n*5, n*5+1, n*5+2, n*5+3, n*5+4]]);

    polyhedron(points = pts, faces = faces, convexity = 8);
}

module collet() {
    difference() {
        union() {
            // threaded base section
            cylinder(h = thread_len, r = core_r);
            helical_thread(core_r - 0.15, thread_maj, thread_pitch, turns);
            // finger section
            translate([0,0,thread_len])
                cylinder(h = clamp_length - thread_len, r1 = core_r, r2 = finger_tip_r);
        }

        // tubing bore
        translate([0,0,-0.1])
            cylinder(h = clamp_length + 0.2, r = tube_bore/2);

        // slots, only through the finger section
        for (a = [0:360/num_slots:359])
            rotate([0,0,a])
                translate([0, -slot_width/2, thread_len])
                    cube([core_r + 1, slot_width, clamp_length - thread_len + 0.1]);
    }
}

module collar() {
    difference() {
        cylinder(h = thread_len*2, r = collar_od);

        // squeeze bore, upper half
        translate([0,0,thread_len])
            cylinder(h = thread_len + 0.1, r = squeeze_r);

        // threaded bore, lower half
        cylinder(h = thread_len, r = int_crest);
        helical_thread(int_crest - 0.15, int_groove, thread_pitch, turns);

        // lead-in chamfer
        translate([0,0,-0.01])
            cylinder(h = 0.6, r1 = int_groove + 0.3, r2 = int_crest);
    }
}

// --- cross-section, near half removed, collar partly screwed on ---
zb = 3;

difference() {
    union() {
        color("SteelBlue") collet();
        color("DarkOrange") translate([0,0,zb]) collar();
        color("Silver") translate([0,0,-25]) cylinder(h=70, r=tube_bore/2 - 0.05);
    }
    translate([-50,-50,-70]) cube([100,50,140]);
}
