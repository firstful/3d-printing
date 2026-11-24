// Fish tank filling gantry — concept v0.2
// Units: mm. X = across the tank's short dimension, Y = along the tank length,
// Z = vertical with Z=0 at the rim plane.

$fn = 32;
IN = 25.4;

// ---------------- tank / fit ----------------
tank_w       = 12.5 * IN;   // outside short dimension, 11..14 in
rim_w        = 1.0  * IN;   // rim top width
finger_t     = 0.35 * IN;   // outer finger thickness
leg_t        = 0.50 * IN;   // vertical leg thickness (X)
leg_below    = 5.0  * IN;   // inner leg below the rim
finger_below = 2.0  * IN;   // outer finger below the rim
foot_t       = 0.40 * IN;   // foot plate thickness

// ---------------- frame ----------------
build_w      = 6.0  * IN;   // spacing between the two rails (Y)
rail_len     = 15.0 * IN;   // fixed rail length; legs slide inboard
rail_h       = 2.0  * IN;
rail_t       = 0.35 * IN;
rail_z       = 7.0  * IN;   // rail centreline above the rim
chord        = 0.40 * IN;   // top/bottom chord thickness

bridge_x     = 6.0  * IN;
bridge_y     = 6.0  * IN;
bridge_z     = 2.5  * IN;

// ---------------- platform ----------------
plat_x       = 5.0  * IN;
plat_y       = 5.0  * IN;
plat_t       = 0.25 * IN;
plat_z       = 2.0  * IN;   // +2 .. -4
h1           = 0.375 * IN;
h2           = 0.750 * IN;

// ---------------- hoist ----------------
rod_d        = 0.25 * IN;
screw_d      = 0.375 * IN;

show_tank    = true;

// ---------------- derived ----------------
foot_inner_x = tank_w/2 - rim_w;
foot_outer_x = tank_w/2 + finger_t;
leg_x        = foot_inner_x + leg_t/2;
slider_h     = rail_h + 0.6 * IN;
leg_top      = rail_z - slider_h/2 + 0.2*IN;  // top of the flat leg plate

// =====================================================================
module rail_profile() {
    n  = 10;
    end_margin = 0.5*IN;
    dx = (rail_len - 2*end_margin) / n;
    h  = rail_h/2 - chord - 0.06*IN;   // keep the cutouts clear of the chords
    difference() {
        square([rail_len, rail_h], center=true);
        for (i = [0 : n-1]) {
            x0 = -rail_len/2 + end_margin + i*dx;
            // alternating triangular openings leave diagonal web members
            if (i % 2 == 0)
                polygon([[x0, h], [x0+dx, h], [x0+dx/2, -h]]);
            else
                polygon([[x0, -h], [x0+dx, -h], [x0+dx/2, h]]);
        }
    }
}

module rail() {
    color([0.22, 0.42, 0.82])
        translate([0, 0, rail_z])
            rotate([90, 0, 0])
                linear_extrude(height=rail_t, center=true)
                    rail_profile();
}

module leg_profile() {
    foot_len = rim_w + finger_t;
    foot_inner_rel = -leg_t/2;
    foot_outer_rel = foot_inner_rel + foot_len;
    difference() {
        union() {
            // vertical leg
            translate([0, (leg_top - leg_below)/2, 0])
                square([leg_t, leg_top + leg_below], center=true);
            // foot across the rim
            translate([(foot_inner_rel + foot_outer_rel)/2, foot_t/2, 0])
                square([foot_len, foot_t], center=true);
            // outer finger
            translate([foot_outer_rel - finger_t/2, -finger_below/2, 0])
                square([finger_t, finger_below], center=true);
        }
        // lightening slots in the vertical leg
        for (z = [0.8*IN : 0.9*IN : leg_top - 0.6*IN])
            translate([0, z, 0])
                circle(d=0.26*IN);
    }
}

module leg_plate() {
    color([0.22, 0.68, 0.38])
        rotate([90, 0, 0])
            linear_extrude(height=rail_t, center=true)
                leg_profile();
}

module slider() {
    // thin-walled sleeve wrapping the rail, sliding along X
    color([0.95, 0.55, 0.15])
    difference() {
        translate([0, 0, rail_z])
            cube([0.9*IN, 1.0*IN, slider_h], center=true);
        translate([0, 0, rail_z])
            cube([1.0*IN, rail_t + 0.08*IN, rail_h + 0.08*IN], center=true);
        // lightening pockets on both sides
        for (sx = [-1, 1])
            translate([sx*0.43*IN, 0, rail_z])
                cube([0.18*IN, 0.55*IN, 1.7*IN], center=true);
    }
}

module crossbar() {
    color([0.22, 0.68, 0.38])
        translate([0, 0, rail_z - slider_h/2 - 0.4*IN])
            cube([0.6*IN, build_w + 1.0*IN, 0.8*IN], center=true);
}

module leg_pair(x, side) {
    translate([x, 0, 0]) {
        // crossbar under the rails
        crossbar();
        for (sy = [-1, 1]) {
            translate([0, sy*build_w/2, 0]) {
                slider();
                if (side < 0) mirror([1, 0, 0]) leg_plate();
                else leg_plate();
            }
        }
    }
}

module bridge_plate(z) {
    translate([0, 0, z])
    difference() {
        union() {
            // square ring
            difference() {
                cube([bridge_x, bridge_y, 0.25*IN], center=true);
                cube([bridge_x - 0.8*IN, bridge_y - 0.8*IN, 0.4*IN], center=true);
            }
            // X spoke to the central hub
            cube([bridge_x, 0.4*IN, 0.25*IN], center=true);
            // hub
            cylinder(h=0.25*IN, d=1.4*IN, center=true);
        }
        // lead-screw clearance
        cylinder(h=0.5*IN, d=screw_d + 0.15*IN, center=true);
    }
}

module bridge() {
    color([0.95, 0.58, 0.12]) render() union() {
        bridge_plate(rail_z + bridge_z/2 - 0.125*IN);
        bridge_plate(rail_z - bridge_z/2 + 0.125*IN);
        // four corner posts
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx*(bridge_x/2 - 0.30*IN),
                       sy*(bridge_y/2 - 0.30*IN),
                       rail_z])
                cube([0.6*IN, 0.6*IN, bridge_z + 0.3*IN], center=true);
        // guide-rod bosses under the bottom plate
        for (p = [[-2.2*IN, 0], [2.2*IN, 0], [0, 2.2*IN]])
            translate([p[0], p[1], rail_z - bridge_z/2 + 0.05*IN])
                difference() {
                    cylinder(h=0.5*IN, d=0.9*IN, center=true);
                    translate([0, 0, 0.1*IN])
                        cylinder(h=0.7*IN, d=rod_d + 0.08*IN, center=true);
                }
    }
}

module span_screw() {
    sy = 2.0*IN;
    sz = rail_z - 0.2*IN;
    // two threaded rods from the central turnbuckle to the leg-pair nuts
    color([0.82, 0.82, 0.84])
        translate([0, sy, sz])
            rotate([0, 90, 0])
                cylinder(h=2*leg_x, d=screw_d, center=true);
    // central hex turnbuckle body
    color([0.90, 0.30, 0.18])
        translate([0, sy, sz])
            rotate([0, 90, 0])
                cylinder(h=2.0*IN, d=1.15*IN, $fn=6, center=true);
    // crank shaft out past the +X side of the bridge
    color([0.90, 0.30, 0.18])
        translate([3.5*IN, sy, sz])
            rotate([0, 90, 0])
                cylinder(h=2.2*IN, d=0.30*IN, center=true);
    // crank arm and handle at the end of the shaft
    color([0.90, 0.30, 0.18])
        translate([4.5*IN, sy + 0.65*IN, sz])
            rotate([90, 0, 0])
                cylinder(h=1.3*IN, d=0.30*IN, center=true);
    color([0.90, 0.30, 0.18])
        translate([4.5*IN, sy + 1.25*IN, sz + 0.45*IN])
            cylinder(h=0.9*IN, d=0.34*IN, center=true);
    // sliding lock collar on the span screw, just outside the bridge
    color([0.90, 0.25, 0.18])
        translate([3.15*IN, sy, sz])
            rotate([0, 90, 0])
                difference() {
                    cylinder(h=0.55*IN, d=screw_d + 0.8*IN, center=true);
                    cylinder(h=0.7*IN, d=screw_d + 0.05*IN, center=true);
                }
    // nut posts rising from each crossbar to the screw
    color([0.22, 0.68, 0.38])
        for (sx = [-1, 1])
            translate([sx*leg_x, sy, (sz + rail_z - slider_h/2 - 0.55*IN)/2])
                cube([0.9*IN, 0.9*IN, sz - (rail_z - slider_h/2 - 0.55*IN)], center=true);
}

module tank_context() {
    tank_len = 24.0 * IN;
    tank_h   = 16.0 * IN;
    glass_t  = 0.25 * IN;
    %color([0.35, 0.70, 0.90, 0.22])
    difference() {
        translate([0, 0, -tank_h/2])
            cube([tank_w, tank_len, tank_h], center=true);
        translate([0, 0, -tank_h/2 + glass_t])
            cube([tank_w - 2*glass_t, tank_len - 2*glass_t, tank_h + 1], center=true);
    }
    %color([0.20, 0.45, 0.60, 0.35])
    translate([0, 0, 0.15*IN])
        difference() {
            cube([tank_w + 2*0.15*IN, tank_len + 2*0.15*IN, 0.3*IN], center=true);
            cube([tank_w - 2*rim_w, tank_len - 2*rim_w, 0.4*IN], center=true);
        }
}

module platform() {
    color([0.95, 0.86, 0.22])
    difference() {
        translate([0, 0, plat_z])
            cube([plat_x, plat_y, plat_t], center=true);
        // float valve hole
        translate([-1.2*IN, -1.2*IN, plat_z])
            cylinder(h=plat_t + 2, d=h1, center=true);
        // larger accessory hole
        translate([ 1.2*IN, -1.2*IN, plat_z])
            cylinder(h=plat_t + 2, d=h2, center=true);
        // guide rod holes
        for (p = [[-2.2*IN, 0], [2.2*IN, 0], [0, 2.2*IN]])
            translate([p[0], p[1], plat_z])
                cylinder(h=plat_t + 2, d=rod_d + 0.15*IN, center=true);
        // lead screw
        translate([0, 0, plat_z])
            cylinder(h=plat_t + 2, d=screw_d + 0.15*IN, center=true);
    }
}

module platform_bushings() {
    color([0.75, 0.75, 0.78])
        for (p = [[-2.2*IN, 0], [2.2*IN, 0], [0, 2.2*IN]])
            translate([p[0], p[1], plat_z])
                difference() {
                    cylinder(h=plat_t + 0.5*IN, d=rod_d + 0.5*IN, center=true);
                    cylinder(h=plat_t + 1*IN, d=rod_d + 0.06*IN, center=true);
                }
}

module rods() {
    color([0.72, 0.72, 0.75])
        for (p = [[-2.2*IN, 0], [2.2*IN, 0], [0, 2.2*IN]])
            translate([p[0], p[1], (rail_z - 5.5*IN)/2])
                cylinder(h=rail_z + 5.5*IN, d=rod_d, center=true);
    color([0.82, 0.82, 0.84])
        translate([0, 0, (rail_z + 1.0*IN - 5.5*IN)/2])
            cylinder(h=rail_z + 1.0*IN + 5.5*IN, d=screw_d, center=true);
}

module platform_nut() {
    color([0.72, 0.72, 0.75])
        translate([0, 0, plat_z - plat_t/2 - 0.45*IN])
            difference() {
                cube([1.2*IN, 1.2*IN, 0.9*IN], center=true);
                cylinder(h=1.2*IN, d=screw_d + 0.05*IN, center=true);
            }
}

module lock_collar() {
    color([0.9, 0.25, 0.18])
        translate([0, 0, plat_z - plat_t/2 - 1.1*IN])
            difference() {
                cylinder(h=0.55*IN, d=screw_d + 0.8*IN, center=true);
                cylinder(h=0.7*IN, d=screw_d + 0.05*IN, center=true);
            }
}

module crank(z, rot=0) {
    color([0.9, 0.25, 0.18])
        translate([0, 0, z])
            rotate([0, 0, rot])
                union() {
                    cylinder(h=0.45*IN, d=1.3*IN, center=true);
                    translate([0.55*IN, 0, 0])
                        cylinder(h=0.55*IN, d=0.35*IN, center=true);
                    translate([0.55*IN, 0, 0.35*IN])
                        rotate([0, 90, 0])
                            cylinder(h=1.8*IN, d=0.35*IN, center=true);
                }
}

module assembly() {
    if (show_tank) tank_context();
    // fixed rails
    for (sy = [-1, 1])
        translate([0, sy*build_w/2, 0]) rail();
    // sliding leg pairs
    leg_pair(-leg_x, -1);
    leg_pair( leg_x,  1);
    // central bridge / hoist housing
    bridge();
    // span adjustment
    span_screw();
    // hoist
    rods();
    platform();
    platform_bushings();
    platform_nut();
    lock_collar();
    // height crank on the lead screw
    crank(rail_z - 0.2*IN + bridge_z/2 + 0.6*IN);
}

part = "assembly";
if (part == "assembly") assembly();
else if (part == "rail") rail();
else if (part == "rails") for (sy = [-1, 1]) translate([0, sy*build_w/2, 0]) rail();
else if (part == "leg_plate") leg_plate();
else if (part == "bridge") bridge();
else if (part == "platform") platform();
else if (part == "span_screw") span_screw();
else if (part == "leg_pair") leg_pair(0, 1);
else if (part == "crossbar") crossbar();
else if (part == "slider") slider();
else if (part == "crank") crank(0);
else if (part == "lock_collar") lock_collar();
else if (part == "platform_nut") platform_nut();
else if (part == "platform_bushings") platform_bushings();
// assembled-position exports used to build the multi-object 3MF
else if (part == "asm_rail_left") translate([0, -build_w/2, 0]) rail();
else if (part == "asm_rail_right") translate([0, build_w/2, 0]) rail();
else if (part == "asm_leg_left") leg_pair(-leg_x, -1);
else if (part == "asm_leg_right") leg_pair(leg_x, 1);
else if (part == "asm_bridge") bridge();
else if (part == "asm_platform") platform();
else if (part == "asm_rods") rods();
else if (part == "asm_span_screw") span_screw();
else if (part == "asm_crank") crank(rail_z - 0.2*IN + bridge_z/2 + 0.6*IN);
else if (part == "asm_platform_nut") platform_nut();
else if (part == "asm_lock_collar") lock_collar();
else if (part == "asm_bushings") platform_bushings();
else echo(str("unknown part: ", part));
