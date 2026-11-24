// Shelf (bottom) - flat print, magnet pockets on underside
magnet_d = 10.4;
magnet_h = 3.2;
chamfer = 0.3;

difference() {
  import("../stl/ref_obj1.stl", convexity=10);
  for (x=[-40,40]) for (y=[-30,30]) {
    translate([x,y,-15])
      cylinder(h=magnet_h, d=magnet_d, $fn=48);
    // chamfer rim
    translate([x,y,-15+magnet_h])
      cylinder(h=chamfer, d1=magnet_d, d2=magnet_d+2*chamfer, $fn=48);
  }
}