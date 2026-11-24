// Single latitude ring of apertures, for per-ring genus verification.
$fn = 96;

sphere_d = 76.2;
wall = 2;
hole_d = 2;
spacing = 3.5;

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

module model() {
    lat = -75 + ring * step_lat;
    lon_step = step_lat/max(cos(lat),0.2);
    n = len([for (lon=[0:lon_step:360]) lon]);
    echo(str("RING ", ring, " lat=", lat, " lon_step=", lon_step,
             " holes=", n, " expect_genus=", n-1));
    difference() {
        sphere(d=sphere_d);
        sphere(d=sphere_d-2*wall);
        for (lon=[0:lon_step:360]) radial_hole(lat, lon);
    }
}

model();
