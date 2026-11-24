// adaptive-highchair — concept blockout
// NOT a safety-tested product. See README.md, RESEARCH.md, OFF_THE_SHELF.md.
// Units: mm. All inputs live in params.scad.
// Frame uses full-length Home Depot tube stock: no cuts, splayed legs.

include <params.scad>

module upright(sx, sy) {
    // Each leg tilts inward toward the top so the feet splay outward.
    translate([sx * BASE_SPAN_X / 2 - TUBE / 2,
               sy * BASE_SPAN_Y / 2 - TUBE / 2, 0])
        rotate([sy * SPLAY_X, -sx * SPLAY_Y, 0])
            cube([TUBE, TUBE, LEG_STOCK], center = false);
}

module rails() {
    // Two 1 ft stock pieces per side, joined by a printed sleeve at centre.
    rail_y = BASE_SPAN_Y / 2 -
             (BASE_SPAN_Y - TOP_SPAN_Y) / 2 * SEAT_H / FRAME_TOP;
    for (sy = [-1, 1]) {
        translate([-RAIL_STOCK, sy * rail_y - TUBE / 2, SEAT_H])
            cube([RAIL_STOCK, TUBE, TUBE], center = false);
        translate([0, sy * rail_y - TUBE / 2, SEAT_H])
            cube([RAIL_STOCK, TUBE, TUBE], center = false);
    }
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

// Colours are for preview renders only; they do not affect geometry.
color("Silver") {
    for (sx = [-1, 1], sy = [-1, 1]) upright(sx, sy);
    rails();
}
color("SteelBlue") seat();
color("DarkSlateBlue") back();
color("SaddleBrown") footrest();
color("BurlyWood") tray();
