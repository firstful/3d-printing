// 80 mm case fan -> 72 x 28 mm right-angle duct adapter
//
// Axis convention
//   Fan flange lies in the XY plane (z = 0 .. flange_t), air enters along +Z.
//   The 90 deg turn happens in the XZ plane, so the bend axis is Y.
//   The 28 mm outlet side is parallel to that bend axis (Y).
//   The 72 mm outlet side is the in-plane / radial dimension (Z at the outlet).
//   Air exits along -X.
//
// The duct is a watertight loft of matching rectangular rings along a
// vertical-lead + circular-arc + horizontal-lead path. Inner and outer lofts
// are differenced, then a fan flange and outlet rim are unioned on.
//
// Units: mm.

$fn = 64;

// ---------------- user parameters ----------------
fan_frame      = 80;     // nominal fan frame (informational)
fan_hole_pitch = 71.5;   // standard 80 mm fan mounting hole spacing
fan_hole_d     = 4.5;    // clearance for M4 screws

inlet_clear    = 75.5;   // clear square throat at the fan
wall           = 2.4;    // duct wall thickness
flange_t       = 5.0;    // fan-side flange thickness
flange_outer   = 88;     // fan-side flange outer size

out_radial     = 72;     // outlet clear dimension IN the bend plane (Z)
out_axis       = 28;     // outlet clear dimension ALONG bend axis (Y)
out_lip        = 10;     // straight horizontal run after the arc
rim_t          = 3.0;    // outlet rim axial thickness
rim_extra      = 3.0;    // outlet rim overhang per side

center_R       = 56;     // centerline radius of the 90 deg bend
lead_in        = 12;     // straight vertical lead before the arc

n_straight     = 4;
n_bend         = 32;
n_out          = 4;
taper_exp      = 1.6;    // >1 keeps the section fat deeper into the bend

// ---------------- derived ----------------
in_half  = inlet_clear/2;
out_r_half = out_radial/2;
out_a_half = out_axis/2;

z_start   = flange_t - 1 + lead_in;       // arc start height (duct overlaps flange)
outlet_x  = -center_R - out_lip;          // outlet duct plane
outlet_z  = z_start + center_R;           // outlet center height

// ---------------- helpers ----------------
function lerp(a,b,t) = a + (b-a)*t;
function smooth(t) = t*t*(3-2*t);
function taper(u) = pow(smooth(u), taper_exp);

// Section: [cx, cz, nx, nz, half_radial, half_axis]
//   (nx,nz) is the in-plane radial unit vector; tangent is perpendicular.
function path_sections(n) = [
    for (i=[0:n])
    let (
        ns = n_straight, nb = n_bend, no = n_out,
        seg = i < ns ? 0 : (i < ns+nb ? 1 : 2),
        u   = seg == 0 ? i/ns
            : seg == 1 ? (i-ns)/nb
            : (i-ns-nb)/no,
        th  = seg == 0 ? 0 : (seg == 1 ? u*90 : 90),
        cx  = seg == 0 ? 0
            : seg == 1 ? -center_R + center_R*cos(th)
            : -center_R - out_lip*u,
        cz  = seg == 0 ? z_start - lead_in*(1-u)
            : seg == 1 ? z_start + center_R*sin(th)
            : z_start + center_R,
        nx  = seg == 0 ? 1 : (seg == 1 ? cos(th) : 0),
        nz  = seg == 0 ? 0 : (seg == 1 ? sin(th) : 1),
        g   = taper(i/n),
        hr  = lerp(in_half, out_r_half, g),
        ha  = lerp(in_half, out_a_half, g)
    )
    [cx, cz, nx, nz, hr, ha]
];

function corner(s, a, b, off) =
    [ s[0] + s[2]*a*(s[4]+off),
      b*(s[5]+off),
      s[1] + s[3]*a*(s[4]+off) ];

function ring_verts(sections, off) = [
    for (s=sections) each [
        corner(s,-1,-1,off), corner(s, 1,-1,off),
        corner(s, 1, 1,off), corner(s,-1, 1,off)
    ]
];

function side_faces(nr) = [
    for (i=[0:nr-2], j=[0:3])
    let (a=4*i+j, b=4*i+(j+1)%4,
         c=4*(i+1)+(j+1)%4, d=4*(i+1)+j)
    [d,c,b,a]
];

function cap_faces(nr) = concat(
    [[0,1,2,3]],
    [[4*(nr-1)+3, 4*(nr-1)+2, 4*(nr-1)+1, 4*(nr-1)]]
);

module swept(sections, off) {
    nr = len(sections);
    polyhedron(ring_verts(sections, off),
               concat(side_faces(nr), cap_faces(nr)),
               convex=false);
}

module fan_flange() {
    difference() {
        translate([0,0,flange_t/2])
            cube([flange_outer, flange_outer, flange_t], center=true);
        translate([0,0,-1])
            cube([inlet_clear, inlet_clear, flange_t+2], center=true);
        for (sx=[-1,1], sy=[-1,1])
            translate([sx*fan_hole_pitch/2, sy*fan_hole_pitch/2, -1])
                cylinder(d=fan_hole_d, h=flange_t+2);
    }
}

module outlet_rim() {
    ow = out_axis + 2*wall + 2*rim_extra;   // Y extent
    oh = out_radial + 2*wall + 2*rim_extra; // Z extent
    difference() {
        translate([outlet_x-rim_t, -ow/2, outlet_z-oh/2])
            cube([rim_t, ow, oh], center=false);
        translate([outlet_x-rim_t-1, -out_axis/2, outlet_z-out_radial/2])
            cube([rim_t+2, out_axis, out_radial], center=false);
    }
}

module adapter() {
    n = n_straight + n_bend + n_out;
    sec = path_sections(n);
    union() {
        difference() {
            swept(sec, wall);   // outer loft
            swept(sec, 0);      // clear bore
        }
        fan_flange();
        outlet_rim();
    }
}


render() { swept(path_sections(n_straight+n_bend+n_out), wall); }
