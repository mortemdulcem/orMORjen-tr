# -*- coding: utf-8 -*-
"""denek204 sag: 72 isindan hangileri rim bulamiyor? Sektor dagilimi.
Esik DEGISTIRILMEZ; auto_rim'in ic durumu disardan yeniden kurulur (ayni kodla).
"""
import sys, json, numpy as np
sys.path.insert(0, '/home/claude/orbita_hat'); sys.path.insert(0, '/home/claude/an')
import onisle, landmark as L, rimcurve
import olcum_zinciri as oz
import otomasyon2 as O
from scipy import ndimage as ndi

hacim, bilgi = onisle.dicom_hacim('/home/claude/gelen3/d204/se')
ct = np.transpose(hacim, (2, 1, 0))
org = np.array(bilgi['origin'], float)
rows = np.diag([bilgi['PixelSpacing'][0], bilgi['PixelSpacing'][1], bilgi['kesit_araligi']])
print('hacim %s · org %s' % (ct.shape, np.round(org,1)), flush=True)
ort, ra, apa, kull = O.atlas_yukle(None)
try: _msoa = json.load(open('/home/claude/an/out/mso_anatomik.json', encoding='utf-8'))
except Exception: _msoa = None
lm, bil = L.tespit(ct, rows, org, ort, ra, apeks_atlas=apa, mso_anat=_msoa)

for s, S in (('r','sag'), ('l','sol')):
    Lp = np.array([lm[b+'-'+s] for b in rimcurve.RIM_ORDER], float)
    c, n = rimcurve._plane(Lp)
    apex = np.asarray(lm['apex-'+s], float)
    if np.dot(apex - c, n) > 0: n = -n
    e1 = np.cross(n, [0,0,1.0]); e1 /= np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    # auto_rim'i cagirip hangi acilarin NaN kaldigini ogrenmek icin kodu tekrar etmek
    # yerine, isin boyunca ornekleyip hacmin DISINA tasan acilari sayiyorum.
    rl = np.linalg.norm(np.stack([(Lp-c)@e1, (Lp-c)@e2],1), axis=1)
    r_lo, r_hi = 0.45*rl.mean(), 1.75*rl.mean()
    ang = np.linspace(0, 2*np.pi, 72, endpoint=False)
    Rt = rows.T
    disari = np.zeros(72, int); toplam = 0
    for a in range(72):
        d = np.cos(ang[a])*e1 + np.sin(ang[a])*e2
        P = c[None,:] + np.arange(r_lo, r_hi, 0.25)[:,None]*d[None,:]
        for sh in (-30.0, -15.0, 0.0, 15.0):
            Q = P + sh*n
            lps = Q*np.array([-1.0,-1.0,1.0])
            ijk = np.linalg.solve(Rt, (lps-org).T).T
            dis = ((ijk < 0) | (ijk >= np.array(ct.shape)-1)).any(1)
            disari[a] += int(dis.sum()); toplam += len(dis)
    # aci etiketi: e2 yukari mi? n-z 79 deg oldugundan e2 kabaca +z
    print('== %s · hacim disina tasan ornek orani %.3f' % (S, disari.sum()/toplam), flush=True)
    kotu = [int(np.degrees(ang[a])) for a in range(72) if disari[a] > 0]
    print('   tasma olan acilar (deg):', kotu, flush=True)
