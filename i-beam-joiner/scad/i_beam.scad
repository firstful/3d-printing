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
web_h      = 8.0;       // web height
half_web   = web_h / 2; // 4.0
total_h    = flange_t + web_h + flange_t;  // 16.0
top_half_h = flange_t + half_web;           // 8.0
bot_half_h = half_web + flange_t;           // 8.0

// screw positions along length (5" apart, 0.5" from each end)
screw_z1   = 12.7;      // 0.5"
screw_z2   = 12.7 + 127.0;  // 5.5"
screw_xs   = [-4.0, 4.0];   // 2 screws across the width

// screw (M4-ish printed)
screw_d    = 4.0;
screw_pitch = 1.5;
screw_len  = 8.0;       // engagement per half
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
                translate([sx, flange_t/2, sz])
                    rotate([90, 0, 0])
                        metric_thread(diameter = screw_d, pitch = screw_pitch,
                                      length = screw_len, thread_size = 1.0, internal = true);
        // clearance holes (bottom access): through the web into top half
        for (sz = [screw_z1, screw_z2])
            for (sx = screw_xs)
                translate([sx, flange_t + half_web/2, sz])
                    rotate([90, 0, 0])
                        cylinder(h = half_web + 2, r = clearance_d/2, $fn=24);
    }
}

module bottom_half() {
    difference() {
        translate([0, 0, 0])
            linear_extrude(height = beam_len)
                bottom_half_profile();
        // threaded holes (bottom access)
        for (sz = [screw_z1, screw_z2])
            for (sx = screw_xs)
                translate([sx, half_web + flange_t/2, sz])
                    rotate([-90, 0, 0])
                        metric_thread(diameter = screw_d, pitch = screw_pitch,
                                      length = screw_len, thread_size = 1.0, internal = true);
        // clearance holes (top access): through the web into bottom half
        for (sz = [screw_z1, screw_z2])
            for (sx = screw_xs)
                translate([sx, half_web/2, sz])
                    rotate([-90, 0, 0])
                        cylinder(h = half_web + 2, r = clearance_d/2, $fn=24);
    }
}

module screw() {
    metric_thread(diameter = screw_d, pitch = screw_pitch,
                  length = screw_len, thread_size = 1.0);
    translate([0, 0, screw_len])
        cylinder(h = 3, r = screw_d/2 + 1.5, $fn=24);  // head
    // hex socket
    translate([0, 0, screw_len + 1.5])
        cylinder(h = 1.6, r = 2.0, $fn=6);
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