Fan adapter 80 mm case fan -> 72 x 28 mm right-angle duct adapter
Recent final print files, sent by Reed via OpenCode on 2026-11-19.

Files
-----
stl/fan_adapter.stl
    Final model, 70-degree bend version (matches source/fan_adapter.scad).
stl/fan_adapter_bend70.stl
    Bend-70 workhorse variant used for the flow study.
stl/print_ready_outlet_rim_down.stl
    Print-orientation variant, outlet rim down (earlier build).

source/fan_adapter.scad
    Parametric OpenSCAD source. Air enters +Z at the fan flange, turns in the
    XZ plane (bend axis Y) and exits -X through the 72 x 28 mm outlet.

preview/
    Orthographic/isometric PNG renders for fan_adapter and bend70, plus
    section and airflow-study images.

Notes
-----
- All files dated 2026-11-19; final STLs regenerated ~13:01 local time.
- Intermediate test/iteration STLs (underscore-prefixed scratch builds under
  build/ and preview/) were intentionally excluded.
- Original session: ~/opencode-sessions/fan-adapter-80-to-72x28/
