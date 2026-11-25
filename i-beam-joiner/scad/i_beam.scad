// ============================================================================
//  I-beam joiner — 6" (152.4 mm) I-beam, split in the middle, joined with
//  printed M4 screws through the top and bottom flanges.
//
//  Cross-section: 15 mm flanges, 11 mm web, 8 mm web height, 4 mm flanges.
//  Total height 16 mm.  Two halves, 76.2 mm each, joined end-to-end.
// ============================================================================

// ------------------------------ parameters ---------------------------------
beam_len   = 152.4;     // 6 inches
half_len   = beam_len / 2;  // 76.2
flange_w   = 15.0;      // flange width
flange_t   = 4.0;       // flange thickness
web_w      = 11.0;      // web width
web_h      = 8.0;       // web height
total_h    = flange_t + web_h + flange_t;  // 16.0

// screw (M4-ish printed)
screw_d    = 4.0;       // major diameter
screw_pitch = 1.5;
screw_len  = 12.0;      // per half engagement
clearance_d = 4.4;      // clearance hole

// screw positions along the width (2 per flange)
screw_x1 = -4.0;
screw_x2 = 4.0;

$fa = 2; $fs = 0.4;

include </home/reed/opencode-sessions/3d-print-repo/3d-printing/siphon-strainer/scad/lib/threads-dk.scad>

// -------------------------------- helpers ----------------------------------
module hex2d(af) {}  // placeholder

// I-beam cross-section profile (in YZ plane, extruded along X)
module ibeam_profile() {
    // bottom flange
    translate([-flange_w/2, -total_h/2, 0])
        cube([flange_w, flange_t, 1]);  // placeholder, rebuilt below
}

// Build the I-beam as a 2D polygon in YZ, extruded along X
module ibeam_2d() {
    polygon([
        // bottom flange (left to right)
        [-flange_w/2, -total_h/2],
        [ flange_w/2, -total_h/2],
        [ flange_w/2, -total_h/2 + flange_t],
        // web (right side)
        [ web_w/2, -total_h/2 + flange_t],
        [ web_w/2,  total_h/2 - flange_t],
        // top flange (right to left)
        [ flange_w/2,  total_h/2 - flange_t],
        [ flange_w/2,  total_h/2],
        [-flange_w/2,  total_h/2],
        [-flange_w/2,  total_h/2 - flange_t],
        // web (left side)
        [-web_w/2,  total_h/2 - flange_t],
        [-web_w/2, -total_h/2 + flange_t],
        [-flange_w/2, -total_h/2 + flange_t],
    ]);
}

module ibeam_half(len, with_threads) {
    difference() {
        // solid I-beam section
        translate([0, 0, 0])
            linear_extrude(height = len)
                ibeam_2d();
        // threaded/clearance holes in top and bottom flanges at the joint end
        // (at z = len, the joining face)
        for (sx = [screw_x1, screw_x2]) {
            // top flange hole (through flange thickness, Y axis)
            translate([sx, total_h/2, len - 2])
                rotate([90, 0, 0])
                    cylinder(h = flange_t + 4, r = (with_threads ? screw_d/2 - 0.3 : clearance_d/2), $fn=24);
            // bottom flange hole
            translate([sx, -total_h/2 + flange_t, len - 2])
                rotate([-90, 0, 0])
                    cylinder(h = flange_t + 4, r = (with_threads ? screw_d/2 - 0.3 : clearance_d/2), $fn=24);
        }
    }
    // add threads on the threaded half
    if (with_threads) {
        for (sx = [screw_x1, screw_x2]) {
            // top flange thread
            translate([sx, total_h/2, len - screw_len])
                rotate([90, 0, 0])
                    metric_thread(diameter = screw_d, pitch = screw_pitch,
                                  length = screw_len, thread_size = 1.0);
            // bottom flange thread
            translate([sx, -total_h/2 + flange_t, len - screw_len])
                rotate([-90, 0, 0])
                    metric_thread(diameter = screw_d, pitch = screw_pitch,
                                  length = screw_len, thread_size = 1.0);
        }
    }
}

// print one half
mode = "half_a";
if (mode == "half_a") ibeam_half(half_len, true);
if (mode == "half_b") ibeam_half(half_len, false);
if (mode == "screw") {
    // printed screw
    metric_thread(diameter = screw_d, pitch = screw_pitch, length = screw_len, thread_size = 1.0);
    translate([0, 0, screw_len])
        cylinder(h = 3, r = screw_d/2 + 1.5, $fn=24);  // head
}