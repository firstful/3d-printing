Fan adapter lightweight oval — handoff to Rook
================================================

Source/reference:
- Original Bambu Studio project: fan_adapter_fixed.3mf (reference only; not modified)
- Original workdir: ~/opencode-sessions/fan-adapter-80-to-72x28/

New design:
- fan_adapter_light.scad  — source, derived from fixed/fan_adapter_fixed.scad
- fan_adapter_light.stl   — binary STL, 11818 facets
- fan_adapter_light_*.png — XY/XZ/YZ/ISO renders

Changes:
- Outlet is a true 72 x 28 mm oval (major axis in bend plane); fan end keeps
  71.5 mm M4 pitch, 4.5 mm holes, 76 mm throat.
- Duct wall 2.0 -> 1.0 mm; flange 5 -> 3 mm thick and 88 -> 85 mm outer;
  outlet rim 3 -> 1.8 mm thick, overhang 9 -> 8 mm.
- Duct cross-section morphs from near-square at fan to ellipse at outlet.

Measured:
- Volume 33.951 cm^3, PLA mass 42.10 g (original 67.223 cm^3 / 83.36 g).
- 49.5% lighter.
- Bbox 105.168 x 85.000 x 112.005 mm.
- Watertight, 1 body, 0 degenerate triangles.
- Downward-facing area below 30 deg slope: 1.85% (original 2.89%).

Caveat: 1.0 mm wall is ~2.5 perimeters at 0.4 mm; a 3-perimeter slice will
print slightly heavier/stronger than the 42 g estimate.
