// Template for a new parametric part.
// Units: mm. Keep all design inputs at the top.

/* [Dimensions] */
part_width  = 40;
part_depth  = 40;
part_height = 10;

/* [Print] */
layer_height = 0.20;
wall_count   = 3;

$fn = 64;

module part() {
    cube([part_width, part_depth, part_height], center = true);
}

part();
