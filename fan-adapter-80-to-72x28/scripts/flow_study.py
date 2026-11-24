#!/usr/bin/env python3
"""Flow study for the 80 mm fan -> 72x28 right-angle adapter.

Two parts:
  1. 1-D area/velocity/bend-loss model + generative parameter sweep.
  2. Qualitative D2Q9 lattice-Boltzmann visualization of the elbow in the
     bend plane (XZ). This is NOT quantitative CFD: air viscosity at this
     resolution gives Re far beyond what LBM can stably represent, so an
     artificial viscosity is used and only the flow pattern is meaningful.

Dependencies: numpy, Pillow. No scipy/matplotlib required.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "preview"
OUT.mkdir(exist_ok=True)

# ---------------- shared geometry ----------------
@dataclass(frozen=True)
class Params:
    inlet_clear: float = 76.0
    wall: float = 2.4
    flange_t: float = 5.0
    out_radial: float = 72.0   # bend-plane dimension (Z at outlet)
    out_axis: float = 28.0     # bend-axis dimension (Y)
    out_lip: float = 10.0
    center_r: float = 55.0
    lead_in: float = 12.0
    taper_exp: float = 1.5
    bend_angle: float = 70.0   # OpenSCAD model stops 20 deg early
    n_straight: int = 4
    n_bend: int = 32
    n_out: int = 4


def smooth(t: float) -> float:
    return t * t * (3 - 2 * t)


def sections(p: Params) -> list[tuple]:
    """Return (cx, cz, nx, nz, hr, ha, global_u) for each loft ring."""
    ns, nb, no = p.n_straight, p.n_bend, p.n_out
    n = ns + nb + no
    z_start = p.flange_t - 1 + p.lead_in
    out = []
    for i in range(n + 1):
        seg = 0 if i < ns else (1 if i < ns + nb else 2)
        if seg == 0:
            u = i / ns
        elif seg == 1:
            u = (i - ns) / nb
        else:
            u = (i - ns - nb) / no
        th = 0.0 if seg == 0 else (u * p.bend_angle if seg == 1 else p.bend_angle)
        a = math.radians(th)
        if seg == 0:
            cx, cz = 0.0, z_start - p.lead_in * (1 - u)
        elif seg == 1:
            cx, cz = -p.center_r + p.center_r * math.cos(a), z_start + p.center_r * math.sin(a)
        else:
            cx, cz = -p.center_r - p.out_lip * u, z_start + p.center_r
        nx, nz = ((1.0, 0.0) if seg == 0 else (math.cos(a), math.sin(a)))
        g = smooth(i / n) ** p.taper_exp
        hr = p.inlet_clear / 2 + (p.out_radial / 2 - p.inlet_clear / 2) * g
        ha = p.inlet_clear / 2 + (p.out_axis / 2 - p.inlet_clear / 2) * g
        out.append((cx, cz, nx, nz, hr, ha, i / n))
    return out


# ---------------- 1-D flow model ----------------
CFM_TO_M3S = 0.00047194745


def flow_1d(p: Params, cfm: float = 20.0, rho: float = 1.2) -> dict:
    sec = sections(p)
    q = cfm * CFM_TO_M3S
    areas = np.array([4 * s[4] * s[5] * 1e-6 for s in sec])  # mm^2 -> m^2
    vel = q / areas

    a_in = (p.inlet_clear ** 2) * 1e-6
    a_out = (p.out_radial * p.out_axis) * 1e-6
    v_in, v_out = q / a_in, q / a_out

    # Crane-style bend loss: K depends on R/D and whether the duct is square.
    d_h_in = (4 * a_in / (4 * p.inlet_clear * 1e-3))  # = inlet_clear in m
    d_h_out = 2 * (p.out_radial * p.out_axis) * 1e-3 / (p.out_radial + p.out_axis) * 1e-3
    d_ref = 0.5 * (d_h_in + d_h_out)
    r_d = p.center_r * 1e-3 / d_ref
    # Long-radius 90 deg bend K ~ 0.2 at R/D=1, falling toward 0.1 at R/D=3.
    k_bend = (0.12 + 0.16 / max(0.35, r_d)) * (p.bend_angle / 90.0)
    # Abrupt-ish contraction from fan throat to outlet area.
    beta = a_out / a_in
    k_contract = 0.42 * (1 - beta) ** 2
    k_total = k_bend + k_contract

    dp_bend = 0.5 * rho * v_out ** 2 * k_bend
    dp_contract = 0.5 * rho * v_out ** 2 * k_contract
    dp_total = dp_bend + dp_contract

    # Straight-wall friction (Darcy), rough PLA f~0.03
    length = (p.lead_in + math.pi / 2 * p.center_r + p.out_lip) * 1e-3
    f = 0.03
    dp_fric = f * length / d_ref * 0.5 * rho * ((v_in + v_out) / 2) ** 2

    return dict(
        q=q, areas=areas, vel=vel, v_in=v_in, v_out=v_out,
        a_in=a_in, a_out=a_out, r_d=r_d, k_bend=k_bend,
        k_contract=k_contract, k_total=k_total,
        dp_bend=dp_bend, dp_contract=dp_contract,
        dp_fric=dp_fric, dp_total=dp_total + dp_fric,
        dp_pa=dp_total + dp_fric,
        dp_inh2o=(dp_total + dp_fric) / 9.80665,
    )


def sweep() -> tuple[list[dict], dict]:
    rows = []
    for cr in (40, 46, 55, 65, 78):
        for te in (1.0, 1.3, 1.6, 2.0):
            for w in (2.0, 2.4, 3.0):
                p = Params(center_r=cr, taper_exp=te, wall=w)
                f = flow_1d(p)
                # compactness proxy: part envelope volume (arbitrary units)
                env = (cr + p.out_lip + 44) * 88 * (p.flange_t + p.lead_in + cr)
                # wall cost proxy: material volume rough estimate
                mass = w * (
                    sum(4 * s[4] * s[5] for s in sections(p)) * 2.0 / len(sections(p))
                ) * (p.lead_in + math.pi / 2 * cr + p.out_lip) / 1000
                score = 1.0 * f["dp_total"] + 0.0000012 * env + 0.02 * mass
                rows.append(dict(cr=cr, te=te, wall=w, dp=f["dp_total"],
                                 dp_inh2o=f["dp_inh2o"], env=env, mass=mass,
                                 score=score, rd=f["r_d"]))
    rows.sort(key=lambda r: r["score"])
    return rows, dict(center_r=rows[0]["cr"], taper_exp=rows[0]["te"], wall=rows[0]["wall"])


def plot_profile(p: Params, f: dict, path: Path) -> None:
    w, h = 900, 360
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    d.text((16, 12), "Cross-section area and air velocity along duct (20 CFM)", fill="black")

    def axes(x0, y0, x1, y1, label, vals, color, fmt):
        d.rectangle([x0, y0, x1, y1], outline="gray")
        d.text((x0, y0 - 14), label, fill=color)
        vmin, vmax = float(min(vals)), float(max(vals))
        rng = max(vmax - vmin, 1e-9)
        pts = []
        for i, v in enumerate(vals):
            x = x0 + (x1 - x0) * i / (len(vals) - 1)
            y = y1 - (y1 - y0) * (v - vmin) / rng
            pts.append((x, y))
        d.line(pts, fill=color, width=2)
        d.text((x1 - 120, y0 + 4), fmt.format(vmin), fill=color)
        d.text((x1 - 120, y1 - 12), fmt.format(vmax), fill=color)

    axes(60, 60, 850, 170, "Area (mm^2)", f["areas"] * 1e6, "blue", "{:.0f}")
    axes(60, 220, 850, 330, "Velocity (m/s)", f["vel"], "red", "{:.2f}")
    img.save(path)


# ---------------- qualitative potential-flow visualization ----------------
def build_mask(p: Params, nx: int, nz: int, dx: float,
               x0: float, z0: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Fluid mask in XZ plane. Returns (fluid, inlet_cells, outlet_cells)."""
    xs = x0 + (np.arange(nx) + 0.5) * dx
    zs = z0 + (np.arange(nz) + 0.5) * dx
    X, Z = np.meshgrid(xs, zs, indexing="ij")
    fluid = np.zeros((nx, nz), dtype=bool)
    for cx, cz, nvx, nvz, hr, ha, _ in sections(p):
        a = (X - cx) * nvx + (Z - cz) * nvz       # radial coordinate
        fluid |= (np.abs(a) <= hr)
    inlet = fluid & (Z <= z0 + dx * 2.0) & (np.abs(X) <= p.inlet_clear / 2)
    outlet_x = -(p.center_r + p.out_lip)
    outlet = fluid & (X <= outlet_x + dx * 2.0) & (
        np.abs(Z - (p.flange_t - 1 + p.lead_in + p.center_r)) <= p.out_radial / 2)
    return fluid, inlet, outlet


def potential_flow(p: Params, iters: int = 4000) -> dict:
    """Solve Laplace(phi)=0 in the duct with fixed inlet/outlet potentials and
    zero normal flux at walls. Velocity = -grad(phi). Qualitative only."""
    dx = 1.5
    x0 = -(p.center_r + p.out_lip) - 15.0
    z0 = -4.0
    nx = int((44.0 - x0) / dx)
    nz = int((p.flange_t + p.lead_in + p.center_r + p.out_radial / 2 + 12 - z0) / dx)
    fluid, inlet, outlet = build_mask(p, nx, nz, dx, x0, z0)

    phi = np.zeros((nx, nz))
    phi[inlet] = 1.0
    phi[outlet] = 0.0
    for _ in range(iters):
        nb = np.zeros_like(phi)
        for sh in ((1,0), (-1,0), (0,1), (0,-1)):
            shifted = np.roll(np.roll(phi, sh[0], axis=0), sh[1], axis=1)
            fshift = np.roll(np.roll(fluid, sh[0], axis=0), sh[1], axis=1)
            nb += np.where(fshift, shifted, phi)
        new = nb / 4.0
        new[~fluid] = 0.0
        new[inlet] = 1.0
        new[outlet] = 0.0
        phi = new

    gy, gx = np.gradient(phi)
    ux, uy = -gx, -gy
    speed = np.hypot(ux, uy)
    return dict(speed=speed, ux=ux, uy=uy, fluid=fluid, inlet=inlet,
                outlet=outlet, x0=x0, z0=z0, dx=dx)


def _colormap(t: np.ndarray) -> np.ndarray:
    stops = np.array([[10, 20, 80], [0, 150, 200], [40, 220, 60],
                      [250, 210, 0], [230, 40, 20]], dtype=float)
    idx = np.clip(t, 0, 1) * (len(stops) - 1)
    lo = np.floor(idx).astype(int).clip(0, len(stops) - 2)
    f = (idx - lo)[..., None]
    return (stops[lo] * (1 - f) + stops[lo + 1] * f).astype(np.uint8)


def _streamlines(res: dict, n_lines: int = 13) -> list[list[tuple[int, int]]]:
    """Integrate seed points from the inlet along the potential-flow velocity."""
    fluid, inlet, ux, uy = res["fluid"], res["inlet"], res["ux"], res["uy"]
    h, w = fluid.shape
    col = np.where(inlet[:, 0])[0]
    if len(col) == 0:
        return []
    lines = []
    for frac in np.linspace(0.06, 0.94, n_lines):
        row = int(col[0] + frac * (col[-1] - col[0]))
        xi, yi = float(row), 0.0
        pts = []
        for _ in range(900):
            i, j = int(round(xi)), int(round(yi))
            if not (0 <= i < h and 0 <= j < w) or not fluid[i, j]:
                break
            mag = math.hypot(ux[i, j], uy[i, j])
            if mag < 1e-9:
                break
            pts.append((j, i))
            xi += ux[i, j] / mag * 0.7
            yi += uy[i, j] / mag * 0.7
        if len(pts) > 2:
            lines.append(pts)
    return lines


def save_flow_png(res: dict, path: Path) -> None:
    fluid, sp = res["fluid"], res["speed"]
    h, w = fluid.shape
    t = np.clip(sp / (np.percentile(sp[fluid], 98) + 1e-12), 0, 1)
    rgb = _colormap(t)
    rgb[~fluid] = (240, 240, 240)
    img = Image.fromarray(rgb.transpose(1, 0, 2)[::-1], "RGB")
    img = img.resize((w * 4, h * 4), Image.Resampling.NEAREST)
    d = ImageDraw.Draw(img)
    for line in _streamlines(res):
        for (j1, i1), (j2, i2) in zip(line[:-1], line[1:]):
            d.line([(j1*4, (h-1-i1)*4), (j2*4, (h-1-i2)*4)],
                   fill=(255, 255, 255), width=2)
    d.text((12, 8), "Qualitative potential-flow speed + streamlines (bend plane XZ)",
           fill=(0, 0, 0))
    img.save(path)


# ---------------- main ----------------
def main() -> None:
    p = Params()
    f = flow_1d(p)
    print("BASELINE 80mm fan -> 72x28, 90 deg bend about the 28mm axis")
    print(f"  inlet area   {f['a_in']*1e6:8.1f} mm^2   v = {f['v_in']:.2f} m/s")
    print(f"  outlet area  {f['a_out']*1e6:8.1f} mm^2   v = {f['v_out']:.2f} m/s")
    print(f"  R/Dh = {f['r_d']:.2f}   Kbend = {f['k_bend']:.3f}   Kcontract = {f['k_contract']:.3f}")
    print(f"  dP bend {f['dp_bend']:.1f} Pa, contraction {f['dp_contract']:.1f} Pa, "
          f"friction {f['dp_fric']:.1f} Pa")
    print(f"  dP total = {f['dp_total']:.1f} Pa = {f['dp_inh2o']:.3f} in H2O")

    plot_profile(p, f, OUT / "flow_profile.png")

    rows, best = sweep()
    print("\nGENERATIVE SWEEP (ranked by mass+size+loss proxy)")
    print(f"{'R':>4} {'taper':>6} {'wall':>5} {'R/D':>5} {'dP Pa':>8} {'score':>10}")
    for r in rows[:8]:
        print(f"{r['cr']:4d} {r['te']:6.2f} {r['wall']:5.1f} {r['rd']:5.2f} "
              f"{r['dp']:8.1f} {r['score']:10.2f}")
    print(f"best: {best}")

    print("\nRunning qualitative potential-flow solve ...")
    res = potential_flow(p)
    save_flow_png(res, OUT / "flow_lbm.png")
    print(f"wrote {OUT/'flow_profile.png'} and {OUT/'flow_lbm.png'}")


if __name__ == "__main__":
    main()
