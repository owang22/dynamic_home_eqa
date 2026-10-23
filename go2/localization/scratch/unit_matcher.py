import sys,math,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import common,matcher
def field_from(pts, res=0.05, pad=1.0):
    x0, y0 = pts[:, 0].min() - pad - res/2, pts[:, 1].min() - pad - res/2
    W = int((pts[:, 0].max() + pad - x0) / res) + 1; H = int((pts[:, 1].max() + pad - y0) / res) + 1
    occ = np.zeros((H, W), bool)
    occ[np.floor((pts[:, 1] - y0) / res).astype(int), np.floor((pts[:, 0] - x0) / res).astype(int)] = True
    return matcher.Field(occ, res, (x0, y0), sigma=0.07)
d=common.load('2026-10-20_111931');A,_=common.cloud(d,500);A=A[:,:2].astype(float);p=d['odom'][d['c_row'][500]]
F=field_from(A)
for true in [(0,0,0),(0.1,-0.07,3),(0.3,0.2,-8),(-0.25,0.0,11)]:
    T=(p[0]+true[0],p[1]+true[1],math.radians(true[2]))
    # query points: B = A expressed relative to T  (so that T*B = A)
    c,s=math.cos(T[2]),math.sin(T[2]);rel=A-np.array(T[:2]);B=np.stack([c*rel[:,0]+s*rel[:,1],-s*rel[:,0]+c*rel[:,1]],-1)
    r=matcher.match(F,B,(p[0],p[1],0.0),12,1.0,0.4,top_k=1)[0]
    print('true',true,'found',round(r[1]-p[0],3),round(r[2]-p[1],3),round(math.degrees(r[3]),2),'score',round(r[0],3),'score@true',round(F.score(B,T),3))
