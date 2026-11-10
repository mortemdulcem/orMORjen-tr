# -*- coding: utf-8 -*-
"""RIM EGRISI SADAKAT SINAVI — DOGRU KURGUYLA.

Onceki sinav (2026-11-10, 0/8) HATALIYDI: tek auto_rim cagrisini hattin
YINELEMELI ciktisiyla karsilastirmisti. `07` §1 adim 4 yinelemeyi tarif eder.
Bu sinav zincirin kendi urettigi egriyi (tespit, C kolu) pakettekiyle karsilastirir.

OLCUT (kosmadan once yazildi): 20 noktanin ortalama sapmasi < 0.25 mm (bir ornekleme adimi).
"""
import sys, os, glob, json
sys.path.insert(0, '/home/claude/an')
import numpy as np, rayseg, otomasyon2 as O, landmark as L

PAK = '/home/claude/kurtarma/paket'
OLCUT = 0.25

def mrk(f):
    j = json.load(open(f, encoding='utf-8')); out = []
    for m in j.get('markups', []):
        fl = np.array([-1,-1,1.0]) if (m.get('coordinateSystem') or 'LPS').upper()=='LPS' else np.ones(3)
        for cp in m.get('controlPoints', []):
            out.append(np.array(cp['position'], float) * fl)
    return np.array(out)

ort, ra, apa, kull = O.atlas_yukle()
print('%-9s %-4s %8s %8s %8s  %s' % ('olgu','tar','ort mm','medyan','maks','hukum'), flush=True)
gecti = tam = 0
hep = []
for ad in sorted(os.listdir(PAK)):
    d = os.path.join(PAK, ad)
    if not os.path.isdir(d): continue
    ct, rows, org = rayseg.load_ct(os.path.join(d, '%s_CT.nrrd' % ad))
    lm, bil = L.tespit(ct, rows, org, ort, ra, apeks_atlas=apa, tur=3)
    if lm is None:
        print('%-9s DURDU' % ad, flush=True); continue
    for s, S in (('r','sag'), ('l','sol')):
        E = bil['egri'].get(S)
        if not isinstance(E, list):
            print('%-9s %-4s EGRI YOK (%s)' % (ad, S, str(E)[:30]), flush=True); tam += 1; continue
        A = np.asarray(E, float)
        ref = mrk(os.path.join(d, 'OTO_rim_%s.mrk.json' % S))
        if len(A) != len(ref):
            print('%-9s %-4s NOKTA SAYISI %d vs %d' % (ad, S, len(A), len(ref)), flush=True); tam += 1; continue
        dd = np.linalg.norm(A - ref, axis=1)
        ok = dd.mean() < OLCUT
        gecti += ok; tam += 1; hep.extend(dd.tolist())
        print('%-9s %-4s %8.4f %8.4f %8.4f  %s'
              % (ad, S, dd.mean(), np.median(dd), dd.max(), 'GECTI' if ok else '>>> KALDI'), flush=True)
h = np.array(hep)
print('\n  %d/%d orbita gecti · tum noktalar: ort %.4f · medyan %.4f · maks %.4f'
      % (gecti, tam, h.mean(), np.median(h), h.max()) if len(h) else '  veri yok')
