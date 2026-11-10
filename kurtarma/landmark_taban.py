# -*- coding: utf-8 -*-
"""LANDMARK ZINCIRI — TABAN OLCUMU.
Elimdeki (eski) zinciri paketin KENDI CT'sinde kosar ve paketteki
OTO landmarklarla karsilastirir. Donmus hat ile aradaki farki olcer.
Olcut: donmus hat deterministik oldugu icin, dogru zincirde sapma ~0 olmalidir.
"""
import sys, os, glob, json
sys.path.insert(0, '/home/claude/an')
import numpy as np, rayseg, otomasyon2 as O, landmark as L

AD = ['d','mf','fmo','ek','mso','o','apex']
PAK = '/home/claude/kurtarma/paket'

def mrk(f):
    j = json.load(open(f, encoding='utf-8')); out = []
    for m in j.get('markups', []):
        fl = np.array([-1,-1,1.0]) if (m.get('coordinateSystem') or 'LPS').upper()=='LPS' else np.ones(3)
        for cp in m.get('controlPoints', []):
            out.append(np.array(cp['position'], float) * fl)
    return np.array(out)

ort, ra, apa, kull = O.atlas_yukle()
print('atlas: sekil %d olgu · rim %d nokta · apeks %d giris' % (len(kull), len(ra), len(apa)), flush=True)

for ad in sorted(os.listdir(PAK)):
    d = os.path.join(PAK, ad)
    if not os.path.isdir(d): continue
    ct, rows, org = rayseg.load_ct(os.path.join(d, '%s_CT.nrrd' % ad))
    ref = {}
    for f in glob.glob(os.path.join(d, 'OTO_*.mrk.json')):
        b = os.path.basename(f)[4:].replace('.mrk.json','')
        if b.startswith('rim_'): continue
        P = mrk(f)
        if len(P): ref[b] = P[0]
    try:
        lm, bil = L.tespit(ct, rows, org, ort, ra)
    except Exception as e:
        print('%-9s ISTISNA %s' % (ad, str(e)[:60]), flush=True); continue
    if lm is None:
        print('%-9s DURDU %s' % (ad, bil), flush=True); continue
    dd = []
    for b in AD:
        for s in ('r','l'):
            k = b + '-' + s
            if k in lm and k in ref:
                dd.append((k, float(np.linalg.norm(np.asarray(lm[k],float) - ref[k]))))
    v = np.array([x[1] for x in dd])
    enkotu = max(dd, key=lambda x: x[1])
    print('%-9s n=%2d  ort %6.3f mm · medyan %6.3f · maks %6.3f (%s)'
          % (ad, len(dd), v.mean(), np.median(v), v.max(), enkotu[0]), flush=True)
