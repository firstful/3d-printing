// 80 mm case fan -> 72 x 28 mm right-angle duct adapter — lightweight oval outlet
//
// Derived from fixed/fan_adapter_fixed.scad (the mesh in fan_adapter_fixed.3mf).
// Critical interfaces are unchanged:
//   - fan mounting: 71.5 mm M4 hole pitch, 4.5 mm clearance holes, 76 mm throat
//   - outlet: 72 x 28 mm clear opening, now an oval (ellipse) centred on the duct
//
// Changes for the 50% mass target:
//   - duct wall 2.0 -> 1.0 mm (~2.5 perimeters at 0.4 mm)
//   - flange thickness 5 -> 3 mm, outer size 88 -> 85 mm
//   - outlet rim thickness 3 -> 1.8 mm, overhang 9 -> 8 mm
//   - rectangular duct/outlet sections morph into a true ellipse at the outlet

$fn = 64;

// ---------------- parameters ----------------
fan_hole_pitch = 71.5;   // standard 80 mm fan hole spacing (unchanged)
fan_hole_d     = 4.5;    // M4 clearance (unchanged)
fan_pad_r      = 5.5;    // reduced but still clears the M4 holes
fan_tie_w      = 6.0;
fan_tie_l      = 3.0;    // shorter so slots clear the 76 mm throat
fan_tie_pos    = 40.0;   // 1 mm web to both throat and 85 mm flange edge
fan_tie_pair   = 9.0;

inlet_clear   = 76;      // clear square throat at fan (unchanged)
wall          = 1.0;     // was 2.0 (~2.5 perimeters at 0.4 mm)

flange_t      = 3;       // was 5
flange_outer  = 85;      // was 88

fan_pilot_d       = 2.6;
fan_pilot_offset  = 4.8;

out_radial    = 72;      // outlet clear dim in bend plane (Z at outlet), unchanged
out_axis      = 28;      // outlet clear dim along bend axis (Y), unchanged
out_lip       = 10;

center_r      = 55;
lead_in       = 12;
bend_angle    = 70;

rim_t         = 1.8;     // was 3
rim_extra     = 8;       // was 9 (still 1 mm web around 6 mm tie slots)
rim_tie_pair_z = 14;
rim_tie_pair_y = 8;

n_straight    = 4;
n_bend        = 32;
n_out         = 4;
taper_exp     = 1.5;
section_points = 48;     // samples around each superellipse section
exp_in        = 32;      // near-square at the fan throat
exp_out       = 2;       // ellipse at the outlet

// ---------------- derived ----------------
in_half    = inlet_clear/2;
out_r_half = out_radial/2;
out_a_half = out_axis/2;

z_start   = flange_t - 1 + lead_in;
th_end    = bend_angle;
ce        = abs(cos(th_end)) < 1e-9 ? 0 : cos(th_end);
se        = abs(sin(th_end)) < 1e-9 ? 0 : sin(th_end);
arc_end_x = -center_r + center_r*ce;
arc_end_z = z_start + center_r*se;
outlet_x  = arc_end_x - out_lip*se;
outlet_z  = arc_end_z + out_lip*ce;
rim_rot   = 90 - bend_angle;

// ---------------- path ----------------
// Section = [cx, cz, nx, nz, half_radial, half_axis, superellipse_exponent]
function u_global(i,ns,nb,no,n) = i/n;

function path_sections(n) = [
    for (i=[0:n])
    let (
        ns=n_straight, nb=n_bend, no=n_out,
        seg = i < ns ? 0 : (i < ns+nb ? 1 : 2),
        u   = seg==0 ? i/ns : (seg==1 ? (i-ns)/nb : (i-ns-nb)/no),
        th  = seg==0 ? 0 : (seg==1 ? u*bend_angle : bend_angle),
        cx  = seg==0 ? 0
            : seg==1 ? -center_r + center_r*cos(th)
            : arc_end_x - out_lip*se*u,
        cz  = seg==0 ? z_start - lead_in*(1-u)
            : seg==1 ? z_start + center_r*sin(th)
            : arc_end_z + out_lip*ce*u,
        nx  = seg==0 ? 1 : (seg==1 ? cos(th) : ce),
        nz  = seg==0 ? 0 : (seg==1 ? sin(th) : se),
        g   = pow(u_global(i,ns,nb,no,n), taper_exp),
        hr  = in_half + (out_r_half - in_half)*g,
        ha  = in_half + (out_a_half - in_half)*g,
        ex  = exp_in + (exp_out - exp_in)*pow(u_global(i,ns,nb,no,n), 0.8)
    )
    [cx, cz, nx, nz, hr, ha, ex]
];

function spow(x,e) = sign(x) * pow(abs(x), 2/e);

function cross_point(s, ang, off) =
    let (
        u = (s[4]+off) * spow(cos(ang), s[6]),
        v = (s[5]+off) * spow(sin(ang), s[6])
    )
    [ s[0] + s[2]*u, v, s[1] + s[3]*u ];

function ring_verts(sec, off) = [
    for (s=sec) each [
        for (k=[0:section_points-1])
            cross_point(s, -135 + k*360/section_points, off)
    ]
];

function tri_quad(a,b,c,d) = [[a,c,b],[a,d,c]];
function tri_quad_rev(a,b,c,d) = [[a,b,c],[a,c,d]];

function outer_faces(nr) = [
    for (i=[0:nr-2], j=[0:section_points-1])
    let (a=i*section_points+j,
         b=i*section_points+(j+1)%section_points,
         c=(i+1)*section_points+(j+1)%section_points,
         d=(i+1)*section_points+j)
    each tri_quad(a,b,c,d)
];

function inner_faces(nr) = [
    for (i=[0:nr-2], j=[0:section_points-1])
    let (o=nr*section_points,
         a=o+i*section_points+j,
         b=o+i*section_points+(j+1)%section_points,
         c=o+(i+1)*section_points+(j+1)%section_points,
         d=o+(i+1)*section_points+j)
    each tri_quad_rev(a,b,c,d)
];

function cap_faces(nr) = [
    for (j=[0:section_points-1])
    let (j2=(j+1)%section_points,
         o=nr*section_points,
         last=(nr-1)*section_points,
         olast=o+last)
    each concat(
        tri_quad(o+j, o+j2, j2, j),
        tri_quad(last+j, last+j2, olast+j2, olast+j)
    )
];

module hollow_duct(sec) {
    nr = len(sec);
    polyhedron(
        concat(ring_verts(sec, wall), ring_verts(sec, 0)),
        concat(outer_faces(nr), inner_faces(nr), cap_faces(nr)),
        convex=false
    );
}

// ---------------- flange and rim ----------------
module fan_flange_base() {
    difference() {
        translate([0,0,flange_t/2])
            cube([flange_outer, flange_outer, flange_t], center=true);
        translate([0,0,flange_t/2])
            cube([inlet_clear, inlet_clear, flange_t+2], center=true);
    }
}

module fan_pads() {
    for (sx=[-1,1], sy=[-1,1])
        translate([sx*fan_hole_pitch/2, sy*fan_hole_pitch/2, flange_t/2])
            cylinder(r=fan_pad_r, h=flange_t, center=true);
}

module fan_tie_slots() {
    for (sy=[-1,1], dx=[-1,1])
        translate([dx*fan_tie_pair, sy*fan_tie_pos, flange_t/2])
            cube([fan_tie_w, fan_tie_l, flange_t+2], center=true);
    for (sx=[-1,1], dy=[-1,1])
        translate([sx*fan_tie_pos, dy*fan_tie_pair, flange_t/2])
            cube([fan_tie_l, fan_tie_w, flange_t+2], center=true);
}

module fan_holes() {
    p = fan_hole_pitch/2;
    for (sx=[-1,1], sy=[-1,1]) {
        translate([sx*p, sy*p, -1])
            cylinder(d=fan_hole_d, h=flange_t+2);
        if (fan_pilot_d > 0)
            translate([sx*(p + fan_pilot_offset/sqrt(2)),
                       sy*(p + fan_pilot_offset/sqrt(2)), -1])
                cylinder(d=fan_pilot_d, h=flange_t+2);
    }
}

module fan_flange() {
    difference() {
        union() {
            fan_flange_base();
            fan_pads();
        }
        fan_holes();
        fan_tie_slots();
    }
}

module rim_tie_slots_local(ow, oh) {
    // Local frame: X = upstream normal, Y = bend axis, Z = radial at outlet.
    ytab = out_axis/2 + wall + rim_extra/2;
    ztab = out_radial/2 + wall + rim_extra/2;
    xc = -rim_t + 0.5;
    xlen = rim_t + 3;
    for (sy=[-1,1], dz=[-1,1])
        translate([xc, sy*ytab, dz*rim_tie_pair_z])
            cube([xlen, fan_tie_w, fan_tie_l], center=true);
    for (sz=[-1,1], dy=[-1,1])
        translate([xc, dy*rim_tie_pair_y, sz*ztab])
            cube([xlen, fan_tie_l, fan_tie_w], center=true);
}

module oval_bore() {
    // Ellipse in the local YZ plane, semi-axes out_axis/2 (Y), out_radial/2 (Z).
    translate([-rim_t-1, 0, 0])
        scale([1, out_a_half/out_r_half, 1])
            rotate([0,90,0])
                cylinder(h=rim_t+4, r=out_r_half, center=false);
}

module rim_local() {
    ow = out_axis + 2*wall + 2*rim_extra;
    oh = out_radial + 2*wall + 2*rim_extra;
    difference() {
        translate([-rim_t, -ow/2, -oh/2])
            cube([rim_t+1, ow, oh], center=false);
        oval_bore();
        rim_tie_slots_local(ow, oh);
    }
}

module outlet_rim() {
    translate([outlet_x, 0, outlet_z])
        rotate([0, rim_rot, 0])
            rim_local();
}

module adapter() {
    union() {
        hollow_duct(path_sections(n_straight+n_bend+n_out));
        fan_flange();
        outlet_rim();
    }
}

adapter();
