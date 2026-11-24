// Siphon strainer -- PLA filter body, NO SUPPORTS version.
//
// Printed collet-down on the build plate. Every surface is 40 degrees from
// vertical (= 50 degree slope), so nothing is within 30 degrees of horizontal:
// the slicer's 30-degree threshold generates no support anywhere, inside or
// out. Practical self-support limit for PLA on this printer is ~45 deg from
// vertical, so 40 leaves margin.
//
// Body = two cones base to base (a bicone). The lower cone flares from the hex
// at 40 deg; the upper cone closes at 40 deg. A sphere fails this: both its
// inner ceiling and its outer lower surface approach horizontal near the poles.
//
// Because the interior needs no support, there is no lattice and no generated
// support tree -- the cavity is empty and the full bore is available to flow.

include <adapter-parts.scad>

// ---- print-space layout (z=0 is the build plate) --------------------------
alpha   = 40;                  // cone half-angle from vertical
cone_r  = 38.1;                // max radius at the equator
z0      = 36;                  // body bottom (hex spans 22..38, so 2mm overlap)
r0      = 11.0;                // hex INSCRIBED radius -- a wider disc would
                               // leave a horizontal ledge outside the hex flats
body_w  = 2;                   // wall

hole_d  = 1.5;
pitch   = 3.0;

tana = tan(alpha);
cosa = cos(alpha);
dz_ring = pitch*sqrt(3)/2*cosa;

h_low  = (cone_r - r0)/tana;
z_eq   = z0 + h_low;
h_up   = cone_r/tana;
z_top  = z_eq + h_up;

// inner surface is the outer offset 2mm perpendicular
off_r  = body_w/cosa;          // radial shrink at equal z
z_sh   = body_w*sin(alpha);    // axial shift

echo(str("BODY: eq z=", z_eq, " top z=", z_top));
echo(str("BODY: slope from horizontal = ", 90 - alpha, " deg (needs > 30)"));

// ---- body ----------------------------------------------------------------
module body_solid() {
    rotate_extrude($fn = 128)
        polygon([[0, z0], [r0, z0], [cone_r, z_eq], [0, z_top]]);
}

module body_cavity() {
    // true perpendicular 2mm offset of the outer profile: the lateral surfaces
    // shift radially by body_w/cos(alpha) with no z change, the horizontal
    // bottom shifts up by body_w, and the apex retreats body_w/sin(alpha)
    rotate_extrude($fn = 128)
        polygon([[0, z0 + body_w],
                 [r0 + body_w*tana - off_r, z0 + body_w],
                 [cone_r - off_r, z_eq],
                 [0, z_top - body_w/sin(alpha)]]);
}

module aperture(z, r, lon, lat) {
    translate([r*cos(lon), r*sin(lon), z])
        rotate([0, 90 - lat, lon])
            cylinder(h = body_w + 3, d = hole_d, center = true, $fn = 16);
}

module body() {
    difference() {
        body_solid();
        body_cavity();

        // port: open the bottom wall into the cavity
        translate([0,0,z0-5])
            cylinder(h = 10, r = tube_bore/2);

        // apertures on both cones, drilled normal to the surface
        for (i = [0 : 200]) {
            zl = z0 + 6 + i*dz_ring;
            if (zl < z_eq - 1) {
                rl = r0 + (zl - z0)*tana;
                n  = max(6, floor(2*PI*rl/pitch));
                st = 360/n;
                off = (i % 2)*st/2;
                for (j = [0 : n-1])
                    aperture(zl, rl, off + j*st, -alpha);
            }
            zu = z_eq + 1 + i*dz_ring;
            if (zu < z_top - 6) {
                ru = (z_top - zu)*tana;
                n  = max(6, floor(2*PI*ru/pitch));
                st = 360/n;
                off = (i % 2)*st/2;
                for (j = [0 : n-1])
                    aperture(zu, ru, off + j*st, alpha);
            }
        }
    }
}


module assembly() {
    union() {
        body();
        translate([0,0,clamp_length]) rotate([180,0,0]) collet();
    }
}

assembly();
