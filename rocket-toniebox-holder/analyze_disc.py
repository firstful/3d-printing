import xml.etree.ElementTree as ET, math
from collections import Counter

path='3D/Objects/object_19.model'
tree=ET.parse(path)
root=tree.getroot()
verts=[]
for e in root.iter():
    if e.tag.endswith('vertex'):
        verts.append((float(e.get('x')),float(e.get('y')),float(e.get('z'))))
print('verts',len(verts))
# Y histogram
yc=Counter([round(v[1],4) for v in verts])
print('Y levels sorted:', sorted(yc.items(), key=lambda x:-x[1])[:30])
print('Y min/max', min(v[1] for v in verts), max(v[1] for v in verts))
# radial in XZ
rs=[math.hypot(v[0],v[2]) for v in verts]
print('r min/max', min(rs), max(rs))
rc=Counter([round(r,2) for r in rs])
print('r most common', rc.most_common(30))
# triangles
tris=[]
for e in root.iter():
    if e.tag.endswith('triangle'):
        tris.append((int(e.get('v1')),int(e.get('v2')),int(e.get('v3'))))
print('tris',len(tris))
# samples at different radii: cross-section in X-Y plane z~0
# Collect verts near z=0 (within 0.5)
near=[v for v in verts if abs(v[2])<0.6]
near_sorted=sorted(near, key=lambda v:v[0])
print('\nNear z=0, sorted by x (first 80):')
for v in near_sorted[:80]:
    print(f" x={v[0]:7.3f} y={v[1]:7.3f} z={v[2]:7.3f} r={math.hypot(v[0],v[2]):.3f}")
print('\nNear z=0 largest x:')
for v in near_sorted[-20:]:
    print(f" x={v[0]:7.3f} y={v[1]:7.3f} z={v[2]:7.3f} r={math.hypot(v[0],v[2]):.3f}")

# profile: for each r bin, y min/max
print('\nR bins -> y range:')
bins={}
for v in verts:
    r=round(math.hypot(v[0],v[2]))
    bins.setdefault(r,[]).append(v[1])
for r in sorted(bins):
    ys=bins[r]
    print(f" r~{r:2d} n={len(ys):4d} y_min={min(ys):6.3f} y_max={max(ys):6.3f} unique_y={sorted(set(round(y,2) for y in ys))[:10]}")

# ASCII cross section: X horizontal, Y vertical, using all verts projected (max density)
# grid 70 wide (x -18..18) x 12 tall (y -2.5..2.5)
print('\nASCII cross-section (X ->, Y up):')
W=73; H=13
grid=[[' ']*W for _ in range(H)]
for v in verts:
    ix=int((v[0]+18)/36*(W-1))
    iy=int((v[1]+2.5)/5*(H-1))
    grid[H-1-iy][ix]='#'
for row in grid:
    print(''.join(row))

# Also XZ top view ascii
print('\nASCII top view (X ->, Z down):')
W=73; H=37
grid=[[' ']*W for _ in range(H)]
for v in verts:
    ix=int((v[0]+18)/36*(W-1))
    iz=int((v[2]+18)/36*(H-1))
    grid[iz][ix]='#'
for row in grid:
    print(''.join(row))
