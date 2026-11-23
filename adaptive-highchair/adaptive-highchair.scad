// adaptive-highchair — concept blockout
// NOT a safety-tested product. See README.md and RESEARCH.md.
// Units: mm. All inputs live in params.scad.

include <params.scad>

module upright(x, y, h) {
    translate([x, y, 0])
        cube([TUBE, TUBE, h], center = false);
}

module seat() {
    translate([-SEAT_W / 2, -SEAT_D / 2, SEAT_H])
        rotate([SEAT_TILT_DEG, 0, 0])
            cube([SEAT_W, SEAT_D, SEAT_T], center = false);
}

module back() {
    translate([-BACK_W / 2, -SEAT_D / 2 - BACK_T, SEAT_H])
        rotate([BACK_RECLINE, 0, 0])
            cube([BACK_W, BACK_T, BACK_H], center = false);
}

module footrest() {
    translate([-FOOT_W / 2, FOOT_REACH, FOOT_H])
        cube([FOOT_W, FOOT_D, FOOT_T], center = false);
}

module tray() {
    translate([-TRAY_W / 2, -TRAY_D / 2 - 40, TRAY_H])
        difference() {
            cube([TRAY_W, TRAY_D, TRAY_T], center = false);
            translate([-TRAY_NOTCH_W / 2, -1, -1])
                cube([TRAY_NOTCH_W, TRAY_NOTCH_D, TRAY_T + 2], center = false);
        }
}

module frame() {
    for (sx = [-1, 1], sy = [-1, 1]) {
        upright(sx * LEG_SPAN_X / 2 - TUBE / 2,
                sy * LEG_SPAN_Y / 2 - TUBE / 2,
                FRAME_TOP);
    }
}

frame();
seat();
back();
footrest();
tray();
