#!/usr/bin/env python3
"""Ray-cast cross-sections of the STL to verify holes/slots actually exist."""
import re, numpy as np, sys
from pathlib import Path

def load_stl(path):
    txt=Path(path).read_text()
    v=[tuple(map(float,t)) for t in re.findall(r'vertex\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)',txt)]
    return np.array(v).reshape(-1,3,3)

def inside(tris, pts):
    """pts: (n,3). Ray along +X. Returns boolean array."""
    out=np.zeros(len(pts),dtype=bool)
    d=np.array([1.,0,0])
    for a,b,c in tris:
        e1=b-a; e2=c-a
        h=np.cross(d,e2)
        det=e1@h
        if abs(det)<1e-12:
            continue
        s=pts-a
        u=(s@h)/det
        q=np.cross(s,e1)
        v=q[:,0]/det
        t=q@e2/det
        hit=(t>0)&(u>=0)&(v>=0)&((u+v)<=1)
        out^=hit
    return out

def section(tris, axis, const, r1, r2, step=1.0, title=''):
    vals=np.arange(r1,r2+step/2,step)
    grid=np.zeros((len(vals),len(vals)),dtype=bool)
    for i,a in enumerate(vals):
        for j,b in enumerate(vals):
            p=np.zeros((1,3))
            if axis=='z': p[0]=[a,b,const]
            elif axis=='x': p[0]=[const,a,b]
            grid[i,j]=inside(tris,p)[0]
    print(f'=== {title} === (axis {axis}={const})')
    # downsample for display
    stride=max(1,len(vals)//70)
    for i in range(0,len(vals),stride):
        print(''.join('#' if grid[i,j] else '.' for j in range(0,len(vals),stride)))

if __name__=='__main__':
    tris=load_stl('preview/fan_adapter.stl')
    section(tris,'z',2.5,-44,44,1.0,'FAN FLANGE mid-plane z=2.5 (X horizontal, Y vertical)')
    section(tris,'x',-69.0,-23,23,1.0,'OUTLET RIM mid-plane x=-69 (Y horizontal, Z relative to outlet center)')
