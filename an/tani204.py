# -*- coding: utf-8 -*-
"""denek204 rim tanilaması — HICBIR ESIK DEGISTIRILMEZ (§0.12).

Olculenler:
  (a) her tarafta 72 isindan kaci rim buldu (auto_rim'in `basari` degeri)
  (b) rim duzlemi normali n ile dunya +z arasindaki aci — `rimcurve.auto_rim`
      tabanini `e1 = cross(n, [0,0,1])` ile kuruyor; n +z'ye paralellesirse bu
      taban yozlasir (`0BE`'deki hatanin ayni sinifi)
Ayni olculer karsilastirma icin BASARILI iki olguda da alinir.
"""
import sys, os, json, numpy as np
sys.path.insert(0, '/home/claude/orbita_hat'); sys.path.insert(0, '/home/claude/an')
import onisle, landmark as L, rimcurve
import olcum_zinciri as oz
import otomasyon2 as O

def olc(ad, kaynak):
    print('='*60, flush=True); print(ad, flush=True)
    hacim, bilgi = onisle.dicom_hacim(kaynak)
    ct = np.transpose(hacim, (2, 1, 0))
    org = np.array(bilgi['origin'], float)
    rows = np.diag([bilgi['PixelSpacing'][0], bilgi['PixelSpacing'][1], bilgi['kesit_araligi']])
    print('  alim: %d kesit %s' % (bilgi['kesit'], ct.shape), flush=True)
    ort, ra, apa, kull = O.atlas_yukle(None)
    try:
        _msoa = json.load(open('/home/claude/an/out/mso_anatomik.json', encoding='utf-8'))
    except Exception:
        _msoa = None
    lm, bil = L.tespit(ct, rows, org, ort, ra, apeks_atlas=apa, mso_anat=_msoa)
    if lm is None:
        print('  LANDMARK BASARISIZ:', bil, flush=True); return
    cm, nv = oz._msp(lm)
    sap = [abs(float(((lm[b+'-r'] + lm[b+'-l'])/2 - cm) @ nv)) for b in ('d','mf','mso','fmo','ek','o')]
    print('  landmark: MSP ort %.2f maks %.2f mm' % (np.mean(sap), max(sap)), flush=True)
    for s, S in (('r','sag'), ('l','sol')):
        Lp = np.array([lm[b+'-'+s] for b in rimcurve.RIM_ORDER], float)
        c, n = rimcurve._plane(Lp)
        apex = np.asarray(lm['apex-'+s], float)
        if np.dot(apex - c, n) > 0: n = -n
        aci = np.degrees(np.arccos(min(1.0, abs(float(np.dot(n, [0,0,1.0]))))))
        e1 = np.cross(n, [0,0,1.0]); e1n = float(np.linalg.norm(e1))
        a, d = rimcurve.auto_rim(ct, rows, org, lm, s, win=0.75, n_out=20)
        print('  %-3s basari %s · egri %s · n-z acisi %.1f deg · |cross(n,z)| %.4f'
              % (S, ('%.3f' % d.get('basari')) if isinstance(d, dict) and 'basari' in d else '-',
                 'VAR' if a is not None else 'YOK', aci, e1n), flush=True)

if __name__ == '__main__':
    olc('denek204', '/home/claude/gelen3/d204/se')
    for n in (212, 206):
        olc('denek%d' % n, '/home/claude/gelen3/d%d/se' % n)
