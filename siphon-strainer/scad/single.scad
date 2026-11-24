// One aperture at a chosen (lat, lon index) for open/blocked testing.
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
    lon = idx * lon_step;
    echo(str("PROBE ring=", ring, " idx=", idx, " lat=", lat, " lon=", lon));
    difference() {
        sphere(d=sphere_d);
        sphere(d=sphere_d-2*wall);
        radial_hole(lat, lon);
    }
}

model();
