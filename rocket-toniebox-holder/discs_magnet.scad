// Rocket Toniebox Holder - Plate 7 disc replacement
// 9 discs, Ø36 x 0.8mm thick, with centered 6x2mm neodymium magnet pocket
// Pocket: Ø6.3 x 2.2mm (magnet 6x2 + 0.3mm dia / 0.2mm depth clearance)
// Top cover: 0.4mm (2 layers @ 0.2mm) over magnet

$fn = 64;

disc_d = 36;
disc_h = 2.8;         // 0.2 bottom + 2.2 cavity + 0.4 top cover
mag_d = 6.3;
mag_h = 2.2;
cover_top = 0.4;      // 2 layers @ 0.2mm (sealed top)
cover_bot = 0.2;      // 1 layer @ 0.2mm (sealed bottom)
pocket_depth = mag_h; // internal cavity

module disc_with_magnet() {
    difference() {
        cylinder(d=disc_d, h=disc_h);
        // internal cavity (sealed, no opening) - pause print to insert magnet
        translate([0,0,cover_bot])
            cylinder(d=mag_d, h=pocket_depth);
    }
    // Optional: retention lip (annular 0.2mm) - disabled; relying on glue
}

// Render one; arrange 3x3 grid for printing
for (x=[-40,0,40]) for (y=[-40,0,40])
    translate([x,y,0]) disc_with_magnet();
