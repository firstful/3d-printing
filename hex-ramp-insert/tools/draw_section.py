"""Draw an annotated cross-section through the top-row hole (x = 16.189)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, FancyArrowPatch

M = 0.130691
C = 13.8003
CX, CY, R = 63.00, -96.64, 118.82
def top(x): return M * x + C
def arc(x): return CY + np.sqrt(R**2 - (x - CX)**2)

x_hole = 16.189
R_hole = 15.86 / 3**0.5 / 2 * 2      # across corners / 2 = 9.157
R_ins = 15.56 / 3**0.5 / 2 * 2       # 8.983
y_face = top(x_hole)

# lip's outer edge = where the top plane meets the arc
xs = np.linspace(25, 31.4, 2000)
x_end = xs[np.argmin(abs(top(xs) - arc(xs)))]
y_end = top(x_end)

# ramp solid
xs_arc = np.linspace(0.0, x_end, 400)
ramp = np.column_stack([xs_arc, arc(xs_arc)]).tolist()
ramp += [[x_end, top(x_end)], [-105.6, top(-105.6)], [-105.6, 0], [0, 0], [0, arc(0.0)]]

fig, ax = plt.subplots(figsize=(13, 6.2), dpi=150)
ax.add_patch(Polygon(ramp, closed=True, facecolor="#d8c37a", edgecolor="#7a6a2a", lw=1.2))
# lip band, cut away where the hole passes
band = np.column_stack([xs_arc, arc(xs_arc)]).tolist()
band += [[x_end, top(x_end)], [-0.2, top(-0.2)]]
ax.add_patch(Polygon(band, closed=True, facecolor="#cbb56a", edgecolor="#7a6a2a", lw=1.2, alpha=.0))

# hole: remove the band between x_hole +/- R_hole
hole = [[x_hole - R_hole, arc(x_hole - R_hole)], [x_hole + R_hole, arc(x_hole + R_hole)],
        [x_hole + R_hole, top(x_hole + R_hole)], [x_hole - R_hole, top(x_hole - R_hole)]]
ax.add_patch(Polygon(hole, closed=True, facecolor="white", edgecolor="none", zorder=3))
for xx in (x_hole - R_hole, x_hole + R_hole):
    ax.plot([xx, xx], [arc(xx), top(xx)], color="#b06a00", lw=1.0, ls=(0, (3, 2)), zorder=4)

# insert: fills the hole, plus the post down to the floor
ins = [[x_hole - R_ins, arc(x_hole - R_ins)], [x_hole + R_ins, arc(x_hole + R_ins)],
       [x_hole + R_ins, 0], [x_hole - R_ins, 0]]
ax.add_patch(Polygon(ins, closed=True, facecolor="#c04040", edgecolor="#7a1010", lw=1.0, zorder=5))
# plate on the face
plate = [[x_hole - R_ins, top(x_hole - R_ins) + 0.25], [x_hole + R_ins, top(x_hole + R_ins) + 0.25],
         [x_hole + R_ins, top(x_hole + R_ins) + 1.5], [x_hole - R_ins, top(x_hole - R_ins) + 1.5]]
ax.add_patch(Polygon(plate, closed=True, facecolor="#a02020", edgecolor="#7a1010", lw=1.0, zorder=6))
# slider, extended down-slope over the ramp
sl = [[x_hole - R_ins - 5.5, top(x_hole - R_ins - 5.5) + 0.25],
      [x_hole + R_ins, top(x_hole + R_ins) + 0.25],
      [x_hole + R_ins, top(x_hole + R_ins) + 1.5],
      [x_hole - R_ins - 5.5, top(x_hole - R_ins - 5.5) + 1.5]]
ax.add_patch(Polygon(sl, closed=True, facecolor="#e08080", edgecolor="#7a1010", lw=1.0, alpha=.9, zorder=7))

# screw
sx = x_hole + 3.0
ax.add_patch(Rectangle((sx - 1.7, 0), 3.4, y_face, facecolor="#404040", edgecolor="none", zorder=8))
ax.add_patch(Polygon([[sx - 3.0, y_face], [sx + 3.0, y_face], [sx + 1.7, y_face - 1.5],
                      [sx - 1.7, y_face - 1.5]], closed=True, facecolor="#202020", zorder=9))

# floor
ax.axhline(0, color="#666", lw=1.0, ls=":")
ax.text(-104, -0.9, "floor / transition you screw into", fontsize=9, color="#444")

def note(xy, xytext, txt, color="#222"):
    ax.annotate(txt, xy=xy, xytext=xytext, fontsize=9, color=color,
                arrowprops=dict(arrowstyle="->", lw=1.0, color=color),
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=color, lw=.8))

note((6, 17.5), (-52, 21.5), "driving surface (7.45°)")
note((24, 13.5), (30, 8.0), "rolled transition\nunderside = R118.8 arc")
note((x_hole, 6.0), (-30, 5.5), "hex hole 15.86 AF, through the\nband (only ~3.4 mm of material here)")
note((x_hole + 2, 1.0), (26, 2.0), "post 15.56 AF -> floor\n(15.92 mm)")
note((x_hole - 6, y_face + 1.2), (-40, 12.0), "plate, flush with the surface", "#7a1010")
note((x_hole - 11, y_face - 1.0), (-46, 8.2), "slider out over the ramp\n(ramp is now captive)", "#7a1010")
note((sx, 12.0), (14, 20.5), "M3 countersunk screw\n(revealed only when the\nslider is out)", "#202020")

ax.set_xlim(-105.6, 40)
ax.set_ylim(-2, 24)
ax.set_aspect("equal")
ax.set_xlabel("x along the ramp (mm)")
ax.set_ylabel("y (mm)")
ax.set_title("Section through the top-row hole (x = 16.19) — insert seated, slider out", fontsize=11)
ax.grid(alpha=.15)
fig.tight_layout()
fig.savefig("/home/reed/opencode-sessions/hex-ramp-insert/preview/section_explained.png")
print("wrote", x_end, y_end)
