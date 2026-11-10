# -*- coding: utf-8 -*-
"""D KOLU — KEMIGE CEKME.  C kolu ciktisina `kemik_kapisi.uygula` uygulanir.

OLCUT (kosmadan once yazildi): ortalama sapma DUSMELI. Yukselirse geri alinir.
`00` §0e-3 olcut (C): onarim YALNIZ kapiyi dusen noktada atesler.
"""
import sys, os, glob, json
sys.path.insert(0, '/home/claude/an')
import numpy as np, rayseg, otomasyon2 as O, landmark as L, kemik_kapisi as kk

AD = ['d','mf','fmo','ek','mso','o','apex']
PAK = '/home/claude/kurtarma/paket'

def mrk(f):
    j = json.load(open(f, encoding='utf-8')); out = []
    for m in j.get('markups', []):
        fl = np.array([-1,-1,1.0]) if (m.get('coordinateSystem') or 'LPS').upper()=='LPS' else np.ones(3)
        for cp in m.get('controlPoints', []):
            out.append(np.array(cp['position'], float) * fl)
    return np.array(out)

def sapma(lm, ref):
    return np.array([float(np.linalg.norm(np.asarray(lm[b+'-'+s],float) - ref[b+'-'+s]))
                     for b in AD for s in ('r','l')
                     if (b+'-'+s) in lm and (b+'-'+s) in ref])

ort, ra, apa, kull = O.atlas_yukle()
print('esik %.0f · yaricap %.1f mm' % (kk.ESIK, kk.YARICAP), flush=True)
print('%-9s %8s %8s %8s  %s' % ('olgu','C ort','D ort','fark','ates'), flush=True)
C=[]; D=[]; ates=0; nokta=0
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
    lm, _ = L.tespit(ct, rows, org, ort, ra, apeks_atlas=apa, tur=3)
    if lm is None:
        print('%-9s DURDU' % ad, flush=True); continue
    lm2, rapor = kk.uygula(ct, rows, org, lm)
    c = sapma(lm, ref); dd = sapma(lm2, ref)
    C.extend(c.tolist()); D.extend(dd.tolist())
    ates += len(rapor); nokta += 12
    print('%-9s %8.3f %8.3f %+8.3f  %d/12  %s'
          % (ad, c.mean(), dd.mean(), dd.mean()-c.mean(), len(rapor),
             ','.join(sorted(rapor)) if rapor else '-'), flush=True)
C=np.array(C); D=np.array(D)
print('\n' + '='*54)
print('C (yineleme+apeks atlasi) : ort %.3f · medyan %.3f · n=%d' % (C.mean(), np.median(C), len(C)))
print('D (+kemige cekme)         : ort %.3f · medyan %.3f' % (D.mean(), np.median(D)))
print('fark                      : %+.3f mm' % (D.mean()-C.mean()))
print('kapiyi dusen nokta        : %d / %d  (%%%.1f)' % (ates, nokta, 100.0*ates/max(1,nokta)))
print('\nHUKUM: %s' % ('ALINIR' if D.mean() < C.mean() else 'GERI ALINIR'))
