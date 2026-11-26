// ============================================================================
//  I-beam joiner — 6" (152.4 mm) I-beam, split through the web, joined with
//  printed M4 screws through the top and bottom flanges.
//
//  Cross-section: 15 mm flanges, 11 mm web, 8 mm web height, 4 mm flanges.
//  Total height 16 mm.  Split horizontally through the web centre:
//  top half = top flange + upper web, bottom half = lower web + bottom flange.
//  Screws at 2 positions, 5" (127 mm) apart, 0.5" from each end.
// ============================================================================

// ------------------------------ parameters ---------------------------------
beam_len   = 152.4;     // 6 inches
flange_w   = 15.0;      // flange width
flange_t   = 4.0;       // flange thickness
web_w      = 11.0;      // web width
web_h      = 6.0;       // web height
half_web   = web_h / 2; // 4.0
total_h    = flange_t + web_h + flange_t;  // 16.0
top_half_h = flange_t + half_web;           // 8.0
bot_half_h = half_web + flange_t;           // 8.0

// screw positions along length (5" apart, 0.5" from each end)
screw_z1   = 12.7;      // 0.5"
screw_z2   = 12.7 + 127.0;  // 5.5"
screw_xs   = [0.0];           // 1 screw per position

// screw (M4-ish printed)
screw_d    = 4.0;
screw_pitch = 1.5;
screw_len  = 16.0;      // total screw length (thread + shaft)
hole_depth = flange_t + web_h/2;  // threaded hole depth (top half thickness)
clearance_d = 4.4;

$fa = 2; $fs = 0.4;

include </home/reed/opencode-sessions/3d-print-repo/3d-printing/siphon-strainer/scad/lib/threads-dk.scad>

// -------------------------------- profiles ---------------------------------
// top half: top flange + upper half of web
module top_half_profile() {
    polygon([
        [-flange_w/2, 0],
        [ flange_w/2, 0],
        [ flange_w/2, flange_t],
        [ web_w/2,    flange_t],
        [ web_w/2,    flange_t + half_web],
        [-web_w/2,    flange_t + half_web],
        [-web_w/2,    flange_t],
        [-flange_w/2, flange_t],
    ]);
}

// bottom half: lower half of web + bottom flange
module bottom_half_profile() {
    polygon([
        [-web_w/2,    0],
        [ web_w/2,    0],
        [ web_w/2,    half_web],
        [ flange_w/2, half_web],
        [ flange_w/2, half_web + flange_t],
        [-flange_w/2, half_web + flange_t],
        [-flange_w/2, half_web],
        [-web_w/2,    half_web],
    ]);
}

// -------------------------------- modules ----------------------------------
module top_half() {
    difference() {
        translate([0, 0, 0])
            linear_extrude(height = beam_len)
                top_half_profile();
        // threaded holes (top access): M4 threads, 8mm deep
        for (sz = [screw_z1, screw_z2])
            for (sx = screw_xs)
                translate([sx, top_half_h, sz])
                    rotate([90, 0, 0])
                        metric_thread(diameter = 4.6, pitch = screw_pitch,
                                      length = hole_depth, thread_size = 1.0);
    }
}

module bottom_half() {
    difference() {
        translate([0, 0, 0])
            linear_extrude(height = beam_len)
                bottom_half_profile();
        // clearance holes (top access): through the bottom half
        for (sz = [screw_z1, screw_z2])
            for (sx = screw_xs)
                translate([sx, 0, sz])
                    rotate([-90, 0, 0])
                        cylinder(h = total_h/2 + 2, r = clearance_d/2, $fn=24);
    }
}

module screw() {
    metric_thread(diameter = screw_d, pitch = screw_pitch,
                  length = hole_depth, thread_size = 1.0);
    // unthreaded shaft
    translate([0, 0, hole_depth])
        cylinder(h = screw_len - hole_depth, r = screw_d/2, $fn=24);
    // flathead slot head
    translate([0, 0, screw_len])
        difference() {
            cylinder(h = 2.5, r = screw_d/2 + 2.0, $fn=32);
            translate([0, 0, 1.25])
                cube([screw_d + 4.0, 0.8, 2.6], center = true);
        }
}

// -------------------------------- modes ------------------------------------
mode = "top";
if (mode == "top") top_half();
if (mode == "bottom") bottom_half();
if (mode == "screw") screw();
if (mode == "assembly") {
    top_half();
    translate([0, 0, 0]) bottom_half();
}