// 3D-Printed Siphon Strainer -- spherical intake strainer
// Source geometry as provided (verbatim), rendered for review.

$fn = 96;

// Dimensions
sphere_d = 76.2;
wall = 2;
hole_d = 2;
spacing = 3.5;

// Outlet
outlet_od = 9;
outlet_id = 6.6;
outlet_length = 15;

// Derived
R = sphere_d/2;
step_lat = spacing/R * 180/PI;

module radial_hole(lat, lon) {
    x = cos(lat)*cos(lon);
    y = cos(lat)*sin(lon);
    z = sin(lat);

    translate([x*(R-wall/2), y*(R-wall/2), z*(R-wall/2)])
        rotate([0,90-lat,lon])
            cylinder(h=wall+2,d=hole_d,center=true);
}

module strainer() {
    difference() {
        union() {
            sphere(d=sphere_d);

            translate([0,0,-R-outlet_length+2])
                cylinder(h=outlet_length,d=outlet_od);
        }

        // Hollow interior
        sphere(d=sphere_d-2*wall);

        // Outlet passage
        translate([0,0,-R-outlet_length-1])
            cylinder(h=outlet_length+wall+2,d=outlet_id);

        // Radial perforations
        for (lat=[-75:step_lat:75]) {
            lon_step = step_lat/max(cos(lat),0.2);

            for (lon=[0:lon_step:360]) {
                radial_hole(lat,lon);
            }
        }
    }
}

// cross-section for review: remove near half (toward viewer)
difference() {
    strainer();
    translate([-100,-100,-100]) cube([200,100,220]);
}
