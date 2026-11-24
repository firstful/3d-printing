// 80 mm case fan -> 72 x 28 mm right-angle duct adapter
//
// Axis convention (matches request)
//   - Fan mounts to the flange in the XY plane at z = 0, air enters along +Z.
//   - The 90 degree turn is in the XZ plane, so the bend axis is Y.
//   - The 28 mm outlet side is parallel to that bend axis (Y).
//   - The 72 mm outlet side is the in-plane/radial dimension (Z at the outlet).
//   - Air exits along -X.
//
// The duct itself is one watertight polyhedron: outer skin + inner skin +
// annular caps. No boolean is needed to hollow it. The fan flange and outlet
// rim are simple CSG boxes added afterwards.

$fn = 64;

// ---------------- parameters ----------------
fan_hole_pitch = 71.5;   // standard 80 mm fan hole spacing
fan_hole_d     = 4.5;    // M4 clearance
fan_pad_r      = 6.5;    // corner pads so the M4 holes have material around them
fan_tie_w      = 6.0;    // zip-tie slot width
fan_tie_l      = 4.0;    // zip-tie slot length (1 mm web each side of flange)
fan_tie_pos    = 41.0;   // slot center distance from flange center
fan_tie_pair   = 9.0;    // ± offset of the two slots on each flange side

inlet_clear   = 76;      // clear square throat at fan
wall          = 2.0;     // duct wall thickness (5 perimeters at 0.4 mm nozzle)

flange_t      = 5;       // fan flange thickness
flange_outer  = 88;      // fan flange outer size

// M3 pilot holes for self-tapping screws in the fan corner pads (alternative
// to zip ties). Set to 0 to remove them.
fan_pilot_d       = 2.6;
fan_pilot_offset  = 4.8; // distance from M4 hole center, toward the flange edge

out_radial    = 72;      // outlet clear dim in bend plane (Z at outlet)
out_axis      = 28;      // outlet clear dim along bend axis (Y)
out_lip       = 10;      // straight run after arc

center_r      = 55;      // centerline bend radius
lead_in       = 12;      // vertical lead before arc
bend_angle    = 70;      // 90 - trim; stop 20 deg early -> min slope ~20 deg

rim_t         = 3;       // outlet rim thickness
rim_extra     = 9;       // rim overhang per side (gives 1.5 mm web around 6 mm slots)
rim_tie_pair_z = 14;     // ± Z offset of tie slots on the Y-side tabs
rim_tie_pair_y = 8;      // ± Y offset of tie slots on the Z-side tabs

n_straight    = 4;
n_bend        = 32;
n_out         = 4;
taper_exp     = 1.5;     // >1 keeps section large deeper into the bend

// ---------------- derived ----------------
in_half    = inlet_clear/2;
out_r_half = out_radial/2;
out_a_half = out_axis/2;

z_start   = flange_t - 1 + lead_in;   // arc start (duct overlaps flange)
th_end    = bend_angle * 3.14159265/180;
arc_end_x = -center_r + center_r*cos(th_end);
arc_end_z = z_start + center_r*sin(th_end);
outlet_x  = arc_end_x - out_lip*sin(th_end);
outlet_z  = arc_end_z + out_lip*cos(th_end);
rim_rot   = 90 - bend_angle;          // rim frame rotation about Y

// ---------------- path ----------------
// Section = [cx, cz, nx, nz, half_radial, half_axis]
// (nx,nz) = in-plane radial unit vector; tangent = (-nz, nx).
function path_sections(n) = [
    for (i=[0:n])
    let (
        ns=n_straight, nb=n_bend, no=n_out,
        seg = i < ns ? 0 : (i < ns+nb ? 1 : 2),
        u   = seg==0 ? i/ns : (seg==1 ? (i-ns)/nb : (i-ns-nb)/no),
        th  = seg==0 ? 0 : (seg==1 ? u*bend_angle : bend_angle),
        cx  = seg==0 ? 0
            : seg==1 ? -center_r + center_r*cos(th)
            : arc_end_x - out_lip*sin(th_end)*u,
        cz  = seg==0 ? z_start - lead_in*(1-u)
            : seg==1 ? z_start + center_r*sin(th)
            : arc_end_z + out_lip*cos(th_end)*u,
        nx  = seg==0 ? 1 : (seg==1 ? cos(th) : cos(th_end)),
        nz  = seg==0 ? 0 : (seg==1 ? sin(th) : sin(th_end)),
        g   = pow(u_global(i,ns,nb,no,n), taper_exp),
        hr  = in_half + (out_r_half - in_half)*g,
        ha  = in_half + (out_a_half - in_half)*g
    )
    [cx, cz, nx, nz, hr, ha]
];

function u_global(i,ns,nb,no,n) = i/n;

function corner(s,a,b,off) =
    [ s[0] + s[2]*a*(s[4]+off),
      b*(s[5]+off),
      s[1] + s[3]*a*(s[4]+off) ];

function ring_verts(sec,off) = [
    for (s=sec) each [
        corner(s,-1,-1,off), corner(s, 1,-1,off),
        corner(s, 1, 1,off), corner(s,-1, 1,off)
    ]
];

// Explicit triangles: non-planar quads on a curved path are triangulated here
// instead of relying on polyhedron's internal triangulation.
// Winding: these helpers emit outward-facing triangles (positive signed
// volume). The previous winding produced an inside-out duct, which made CGAL's
// union with the tilted rim fail with an assertion.
function tri_quad(a,b,c,d) = [[a,c,b],[a,d,c]];
function tri_quad_rev(a,b,c,d) = [[a,b,c],[a,c,d]];

function outer_faces(nr) = [
    for (i=[0:nr-2], j=[0:3])
    let (a=4*i+j, b=4*i+(j+1)%4,
         c=4*(i+1)+(j+1)%4, d=4*(i+1)+j)
    each tri_quad(a,b,c,d)
];

function inner_faces(nr) = [
    for (i=[0:nr-2], j=[0:3])
    let (o=4*nr, a=o+4*i+j, b=o+4*i+(j+1)%4,
         c=o+4*(i+1)+(j+1)%4, d=o+4*(i+1)+j)
    each tri_quad_rev(a,b,c,d)
];

function cap_faces(nr) = [
    for (j=[0:3])
    let (j2=(j+1)%4, o=4*nr,
         last=4*(nr-1), olast=o+last)
    each concat(
        tri_quad(o+j, o+j2, j2, j),              // inlet annulus, normal -t
        tri_quad(last+j, last+j2, olast+j2, olast+j)  // outlet annulus, +t
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
    // Flange plate with the square throat cut out. Pads are added afterwards
    // so the mounting holes at the corners have material around them.
    difference() {
        translate([0,0,flange_t/2])
            cube([flange_outer, flange_outer, flange_t], center=true);
        translate([0,0,-1])
            cube([inlet_clear, inlet_clear, flange_t+2], center=true);
    }
}

module fan_pads() {
    for (sx=[-1,1], sy=[-1,1])
        translate([sx*fan_hole_pitch/2, sy*fan_hole_pitch/2, flange_t/2])
            cylinder(r=fan_pad_r, h=flange_t, center=true);
}

module fan_tie_slots() {
    // Two slots on each edge of the flange, through its thickness.
    // Y-facing edges: slot long axis radial (Y).
    for (sy=[-1,1], dx=[-1,1])
        translate([dx*fan_tie_pair, sy*fan_tie_pos, flange_t/2])
            cube([fan_tie_w, fan_tie_l, flange_t+2], center=true);
    // X-facing edges: slot long axis radial (X).
    for (sx=[-1,1], dy=[-1,1])
        translate([sx*fan_tie_pos, dy*fan_tie_pair, flange_t/2])
            cube([fan_tie_l, fan_tie_w, flange_t+2], center=true);
}

module fan_holes() {
    p = fan_hole_pitch/2;
    for (sx=[-1,1], sy=[-1,1]) {
        // Standard M4 clearance hole.
        translate([sx*p, sy*p, -1])
            cylinder(d=fan_hole_d, h=flange_t+2);
        // Optional M3 self-tapping pilot, angled out toward the flange corner.
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
    // Y-side tabs (parallel to the bend axis): slots long in local Z.
    for (sy=[-1,1], dz=[-1,1])
        translate([xc, sy*ytab, dz*rim_tie_pair_z])
            cube([xlen, fan_tie_w, fan_tie_l], center=true);
    // Z-side tabs (bend-plane sides): slots long in local Y.
    for (sz=[-1,1], dy=[-1,1])
        translate([xc, dy*rim_tie_pair_y, sz*ztab])
            cube([xlen, fan_tie_l, fan_tie_w], center=true);
}

module rim_local() {
    ow = out_axis + 2*wall + 2*rim_extra;   // Y
    oh = out_radial + 2*wall + 2*rim_extra; // local Z
    difference() {
        // local X from -rim_t to +1 (1 mm overlap with duct)
        translate([-rim_t, -ow/2, -oh/2])
            cube([rim_t+1, ow, oh], center=false);
        translate([-rim_t-1, -out_axis/2, -out_radial/2])
            cube([rim_t+3, out_axis, out_radial], center=false);
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


hollow_duct(path_sections(n_straight+n_bend+n_out));
