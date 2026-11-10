# -*- coding: utf-8 -*-
"""RAYSEG SADAKAT SINAVI — yeniden yazilan `rayseg`, donmus hattin maskesini
yeniden uretebiliyor mu?

Paket, DONMUS HATTIN urettigi her seyi tasiyor: CT, landmarklar, rim egrisi
VE maske. Yani landmark zincirinden BAGIMSIZ olarak yalniz maske uretimi
sinanabilir -- girdiler birebir ayni, tek degisken benim kodum.

OLCUT (sinavdan ONCE yazildi):
  (1) hacim farki < %1  -> cekirdek sadik
  (2) Dice ortusmesi > 0,95
  Saglanmazsa yeniden yazim FARKLI bir hattir ve oyle bildirilir.
"""
import sys, os, json, glob
import numpy as np
sys.path.insert(0, '/home/claude/an')
import rayseg, nrrd

PAK = '/home/claude/kurtarma/paket'

def mrk(p):
    j = json.load(open(p, encoding='utf-8')); P = []
    for m in j.get('markups', []):
        lps = str(m.get('coordinateSystem', 'LPS')).upper().startswith('LPS')
        for c in m.get('controlPoints', []):
            q = np.asarray(c['position'], float)
            P.append(q * np.array([-1., -1., 1.]) if lps else q)
    return np.asarray(P, float)

print('%-9s %-4s %10s %10s %9s %8s' % ('olgu','tar','KAYITLI','YENIDEN','fark %','Dice'))
for ad in sorted(os.listdir(PAK)):
    d = os.path.join(PAK, ad)
    if not os.path.isdir(d): continue
    try:
        ct, rows, org = rayseg.load_ct(os.path.join(d, '%s_CT.nrrd' % ad))
        seg, _ = nrrd.read(os.path.join(d, '%s_Segmentation.seg.nrrd' % ad))
        lm = {}
        for f in glob.glob(os.path.join(d, 'OTO_*.mrk.json')):
            b = os.path.basename(f)[4:].replace('.mrk.json', '')
            if b.startswith('rim_'): continue
            P = mrk(f)
            if len(P): lm[b] = P[0]
        vh = rayseg.voksel_hacmi(rows)
        for deg, s, S in ((1, 'r', 'sag'), (2, 'l', 'sol')):
            E = mrk(os.path.join(d, 'OTO_rim_%s.mrk.json' % S))
            ref = (seg == deg)
            if not ref.any(): continue
            M = rayseg.kohort_maskesi(ct, rows, org, lm, s, rim_curve=E)['maske']
            vr = ref.sum() * vh / 1000.0
            vy = M.sum() * vh / 1000.0
            dice = 2.0 * (ref & M).sum() / max(1, ref.sum() + M.sum())
            print('%-9s %-4s %10.3f %10.3f %+9.2f %8.3f'
                  % (ad, S, vr, vy, 100 * (vy / vr - 1) if vr else float('nan'), dice), flush=True)
    except Exception as e:
        print('%-9s ISTISNA %s' % (ad, str(e)[:70]), flush=True)
