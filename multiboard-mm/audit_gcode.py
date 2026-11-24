#!/usr/bin/env python3
"""Audit Bambu Studio gcode for stacked multi-material prints.

Single pass over the gcode. Tracks:
  * layers     : ; CHANGE_LAYER + ; Z_HEIGHT: + ; layer num/total_layer_count: i/n
  * tool state : M620 S<n>A pre-roll + T<n> select (T1000/T255 machinery skipped)
  * extrusions : G0/G1 with E>0, bucketed into declared print zones by XY
  * types      : ; TYPE: <role> lines per layer

Usage:
  audit_gcode.py <gcode> [--boxes '{"zone":[x0,y0,x1,y1], ...}']
                 [--lh 0.2] [--json out.json] [--verbose]
Prints one line per layer that extruded inside a known zone, plus global stats.
"""
import argparse
import json
import re

RE_T    = re.compile(r"^T(\d+)\b")
RE_G0G1 = re.compile(r"^(?:G0|G1)\b(.*$)")
RE_G92  = re.compile(r"^G92\b")
RE_M82  = re.compile(r"^M82\b")
RE_M83  = re.compile(r"^M83\b")
ARG     = {"X": None, "Y": None, "Z": None, "E": None}
RE_ARG  = re.compile(r"([XYZE])(-?\d*\.?\d+)")
RE_CHL  = re.compile(r"^; CHANGE_LAYER")
RE_ZH   = re.compile(r"^; Z_HEIGHT: ([\d.-]+)")
RE_LN   = re.compile(r"^; layer num/total_layer_count: (\d+)/(\d+)")
RE_OID  = re.compile(r"^; OBJECT_ID: (\S+)")
RE_TYPE = re.compile(r"^; TYPE: (\S+)")
RE_HFIL = re.compile(r"^; filament: ([\d,]+)")
RE_HLEN = re.compile(r"^; total filament length \[mm\] : ([\d.,]+)")
RE_HLAY = re.compile(r"^; total layer number: (\d+)")


def zone_name(x, y, boxes):
    for name, (x0, y0, x1, y1) in boxes.items():
        if x0 <= x <= x1 and y0 <= y <= y1:
            return name
    return ""


def audit(path, boxes):
    s = {"tool": None, "x": 0.0, "y": 0.0, "z": 0.0, "abs_e": True,
         "flushing": False, "cur": None, "total": None,
         "h_fil": None, "h_len": None, "h_layers": None,
         "layers": [], "seq": []}
    boxes = {k: tuple(v) for k, v in (boxes or {}).items()}

    def new_layer():
        cur = {"i": len(s["layers"]) + 1, "z": None, "tool": s["tool"],
               "obj": set(), "types": set(), "zones": {}, "flush_mm": 0.0}
        s["layers"].append(cur)
        s["cur"] = cur

    with open(path, "r", errors="replace") as f:
        for ln in f:
            ln = ln.rstrip("\n")
            st = ln.strip()
            if not st:
                continue
            if st.startswith(";"):
                # comments
                if st.startswith("; CHANGE_LAYER"):
                    new_layer(); continue
                if st.startswith("; FLUSH_START"):
                    s["flushing"] = True; continue
                if st.startswith("; FLUSH_END"):
                    s["flushing"] = False; continue
                cur = s["cur"]
                m = RE_ZH.match(st)
                if m and cur is not None:
                    cur["z"] = float(m.group(1)); continue
                m = RE_LN.match(st)
                if m and cur is not None:
                    cur["i"] = int(m.group(1)); s["total"] = int(m.group(2))
                    continue
                m = RE_OID.match(st)
                if m and cur is not None:
                    cur["obj"].add(m.group(1)); continue
                m = RE_TYPE.match(st)
                if m and cur is not None:
                    cur["types"].add(m.group(1)); continue
                m = RE_HFIL.match(st)
                if m:
                    s["h_fil"] = m.group(1); continue
                m = RE_HLEN.match(st)
                if m:
                    s["h_len"] = m.group(1); continue
                m = RE_HLAY.match(st)
                if m:
                    s["h_layers"] = int(m.group(1)); continue
                continue
            # machine code
            m = RE_T.match(st)
            if m:
                n = int(m.group(1))
                if n not in (1000, 255):
                    s["tool"] = n
                    if not s["seq"] or s["seq"][-1] != n:
                        s["seq"].append(n)
                continue
            if RE_M82.match(st):
                s["abs_e"] = True; continue
            if RE_M83.match(st):
                s["abs_e"] = False; continue
            if RE_G92.match(st):
                for k, g in RE_ARG.findall(st):
                    s[k.lower()] = float(g)
                continue
            m = RE_G0G1.match(st)
            if m:
                args = dict(RE_ARG.findall(m.group(1)))
                x = float(args["X"]) if "X" in args else s["x"]
                y = float(args["Y"]) if "Y" in args else s["y"]
                if "Z" in args:
                    s["z"] = float(args["Z"])
                cur = s["cur"]
                if "E" in args and cur is not None:
                    de = float(args["E"])
                    if de > 0:
                        if s["flushing"]:
                            cur["flush_mm"] += de
                        else:
                            zn = zone_name(x, y, boxes)
                            zc = cur["zones"].get(zn)
                            if zc is None:
                                zc = cur["zones"][zn] = {
                                    "tool": s["tool"], "mm": de, "moves": 0,
                                    "zmin": s["z"], "zmax": s["z"],
                                    "minx": x, "maxx": x, "miny": y, "maxy": y}
                            zc["mm"] += de
                            zc["moves"] += 1
                            zc["minx"] = min(zc["minx"], x)
                            zc["maxx"] = max(zc["maxx"], x)
                            zc["miny"] = min(zc["miny"], y)
                            zc["maxy"] = max(zc["maxy"], y)
                            zc["zmin"] = min(zc["zmin"], s["z"])
                            zc["zmax"] = max(zc["zmax"], s["z"])
                s["x"], s["y"] = x, y
    return s


def layer_tool(L):
    ts = sorted({z["tool"] for k, z in L["zones"].items() if k
                 and z["tool"] is not None})
    return ts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gcode")
    ap.add_argument("--boxes", help='JSON: {"zone":[x0,y0,x1,y1], ...}')
    ap.add_argument("--lh", type=float, default=None)
    ap.add_argument("--json")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    S = audit(args.gcode, json.loads(args.boxes) if args.boxes else None)
    print("header filament     :", S["h_fil"])
    print("header lengths      :", S["h_len"])
    print("header layers/total :", S["h_layers"], "/", S["total"],
          "| parsed CHANGE_LAYER:", len(S["layers"]))
    print("tool sequence       :", S["seq"])
    zs = sorted(L["z"] for L in S["layers"] if L["z"] is not None)
    if zs:
        diffs = sorted(set(round(zs[i + 1] - zs[i], 4)
                           for i in range(len(zs) - 1)))
        bad = ([d for d in diffs if args.lh and abs(d - args.lh) > 2e-3]
               if args.lh else [])
        print("z range             : %.2f .. %.2f over %d layers; gaps %s%s"
              % (zs[0], zs[-1], len(zs), sorted(set(diffs))[:5],
                 ("VIOLATIONS|" + str(bad)) if bad else " (lh ok: %s)" % args.lh
                 if args.lh else ""))
    n_printed = 0
    for L in S["layers"]:
        parts = []
        for k, z in L["zones"].items():
            if k:
                parts.append("%s[t%s z%.2f-%.2f x%.1f-%.1f y%.1f-%.1f mm=%d n=%d]"
                             % (k, z["tool"], z["zmin"], z["zmax"], z["minx"],
                                z["maxx"], z["miny"], z["maxy"], z["mm"],
                                z["moves"]))
        if parts:
            n_printed += 1
        if parts or args.verbose:
            print("L%-3d i=%-3d z=%-5s tool=%s obj=%-9s types=%-28s %s%s"
                  % (L["i"], L["i"], L["z"], layer_tool(L) or "-",
                     ",".join(sorted(L["obj"])) or "-",
                     ",".join(sorted(L["types"])),
                     " ".join(parts),
                     (" flush=%.0f" % L["flush_mm"]) if L["flush_mm"] else ("")))
    print("layers with print-zone extrusion:", n_printed)
    if args.json:
        with open(args.json, "w") as f:
            json.dump({k: v for k, v in S.items() if k != "cur"}, f, indent=1)


if __name__ == "__main__":
    main()
