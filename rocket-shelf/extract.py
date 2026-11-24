import xml.etree.ElementTree as ET, struct, os
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
tree=ET.parse('/home/reed/opencode-sessions/rocket-shelf/x/3D/3dmodel.model')
root=tree.getroot()
# map object id -> mesh
for obj in root.iter('{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}object'):
    oid=obj.get('id')
    mesh=obj.find('{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}mesh')
    if mesh is None: continue
    verts=mesh.find('{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}vertices')
    tris=mesh.find('{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}triangles')
    V=[(float(v.get('x')),float(v.get('y')),float(v.get('z'))) for v in verts]
    T=[(int(t.get('v1')),int(t.get('v2')),int(t.get('v3'))) for t in tris]
    # write binary stl
    out=f'/home/reed/opencode-sessions/rocket-shelf/ref_obj{oid}.stl'
    with open(out,'wb') as f:
        f.write(b'\x00'*80)
        f.write(struct.pack('<I',len(T)))
        for a,b,c in T:
            va,vb,vc=V[a],V[b],V[c]
            # normal
            import math
            e1=(vb[0]-va[0],vb[1]-va[1],vb[2]-va[2])
            e2=(vc[0]-va[0],vc[1]-va[1],vc[2]-va[2])
            n=(e1[1]*e2[2]-e1[2]*e2[1], e1[2]*e2[0]-e1[0]*e2[2], e1[0]*e2[1]-e1[1]*e2[0])
            ln=math.sqrt(sum(x*x for x in n)) or 1
            n=tuple(x/ln for x in n)
            f.write(struct.pack('<fff',*n))
            f.write(struct.pack('<fff',*va))
            f.write(struct.pack('<fff',*vb))
            f.write(struct.pack('<fff',*vc))
            f.write(struct.pack('<H',0))
    print(oid, len(V), len(T), '->', out)
