#!/usr/bin/env python3
"""Fast triangle/plane cross-section outlines -> PNG (verification aid)."""
import re, numpy as np
from pathlib import Path
from PIL import Image, ImageDraw

def load_stl(path):
    txt=Path(path).read_text()
    v=[tuple(map(float,t)) for t in re.findall(r'vertex\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)',txt)]
    return np.array(v).reshape(-1,3,3)

def section_segments(tris, axis, const):
    ai={'x':0,'y':1,'z':2}[axis]
    segs=[]
    for tri in tris:
        pts=[]
        for i in range(3):
            p,q=tri[i],tri[(i+1)%3]
            dp, dq=p[ai]-const, q[ai]-const
            if (dp<0<=dq) or (dq<0<=dp):
                t=dp/(dp-dq)
                pts.append(p+t*(q-p))
        if len(pts)==2:
            segs.append((pts[0],pts[1]))
    return segs

def draw(segs, axis, title, path, coords):
    ulo,uhi,vlo,vhi=coords
    scale=min(600/(uhi-ulo), 600/(vhi-vlo))
    ox=(640-(uhi-ulo)*scale)/2 - ulo*scale
    oy=(640-(vhi-vlo)*scale)/2 + vhi*scale
    img=Image.new('RGB',(640,640),'white')
    d=ImageDraw.Draw(img)
    for a,b in segs:
        u,v=(1,2) if axis=='x' else ((0,1) if axis=='z' else (0,2))
        p0=(int(ox+a[u]*scale), int(oy-a[v]*scale))
        p1=(int(ox+b[u]*scale), int(oy-b[v]*scale))
        d.line([p0,p1],fill='black',width=2)
    d.text((20,10),title,fill='red')
    img.save(path)

def section_plane(tris, point, normal, ubasis, vbasis):
    """Intersect triangles with an arbitrary plane; return 2D projected segments."""
    n=np.array(normal,float); p0=np.array(point,float)
    u=np.array(ubasis,float); v=np.array(vbasis,float)
    segs=[]
    for tri in tris:
        d=[float(np.dot(q-p0,n)) for q in tri]
        pts=[]
        for i in range(3):
            a,b=tri[i],tri[(i+1)%3]; da,db=d[i],d[(i+1)%3]
            if (da<0<=db) or (db<0<=da):
                tt=da/(da-db)
                q=a+tt*(b-a)
                pts.append((float(np.dot(q-p0,u)),float(np.dot(q-p0,v))))
        if len(pts)==2: segs.append((pts[0],pts[1]))
    return segs

def draw2(segs,title,path,uhi=27,ulo=-27,vlo=22,vhi=120):
    scale=min(600/(uhi-ulo),600/(vhi-vlo))
    ox=(640-(uhi-ulo)*scale)/2-ulo*scale
    oy=(640-(vhi-vlo)*scale)/2+vhi*scale
    img=Image.new('RGB',(640,640),'white'); d=ImageDraw.Draw(img)
    for a,b in segs:
        d.line([(int(ox+a[0]*scale),int(oy-a[1]*scale)),
                (int(ox+b[0]*scale),int(oy-b[1]*scale))],fill='black',width=2)
    d.text((20,10),title,fill='red'); img.save(path)

tris=load_stl('preview/fan_adapter.stl')
draw(section_segments(tris,'z',2.5),'z','fan flange z=2.5 : X-Y',Path('preview/section_fan_flange.png'),(-46,46,-46,46))
import math
rr=(90-70)*math.pi/180
normal=(math.cos(rr),0,-math.sin(rr))
ub=(0,1,0)
vb=(math.sin(rr),0,math.cos(rr))
point=(outlet_x if False else -55+55*math.cos(math.radians(70))-10*math.sin(math.radians(70)),0,
       16+55*math.sin(math.radians(70))+10*math.cos(math.radians(70)))
# shift to rim mid-plane local x=-1.5
point=(point[0]+normal[0]*-1.5,0,point[2]+normal[2]*-1.5)
draw2(section_plane(tris,point,normal,ub,vb),
      'outlet rim local section x=-1.5 : Y horizontal, Z radial',
      Path('preview/section_outlet_rim.png'))
print('wrote section PNGs')
