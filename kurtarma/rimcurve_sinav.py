# -*- coding: utf-8 -*-
"""RIMCURVE SADAKAT SINAVI — olcut KOSMADAN once yazildi:
   8 orbitanin tamaminda nokta sapmasi < 0.25 mm (bir ornekleme adimi)."""
import sys, os, glob, json
sys.path.insert(0, '/home/claude/an')
import numpy as np, rayseg, rimcurve

PAK = '/home/claude/kurtarma/paket'
OLCUT = 0.25

def mrk(f):
    j = json.load(open(f, encoding='utf-8')); out = []
    for m in j.get('markups', []):
        fl = np.array([-1, -1, 1.0]) if (m.get('coordinateSystem') or 'LPS').upper() == 'LPS' else np.ones(3)
        for cp in m.get('controlPoints', []):
            out.append(np.array(cp['position'], float) * fl)
    return np.array(out)

print('%-9s %-4s %8s %8s %8s  %s' % ('olgu','tar','ort mm','maks mm','basari','hukum'))
gecti = tamam = 0
for ad in sorted(os.listdir(PAK)):
    d = os.path.join(PAK, ad)
    if not os.path.isdir(d): continue
    ct, rows, org = rayseg.load_ct(os.path.join(d, '%s_CT.nrrd' % ad))
    lm = {}
    for f in glob.glob(os.path.join(d, 'OTO_*.mrk.json')):
        b = os.path.basename(f)[4:].replace('.mrk.json', '')
        if b.startswith('rim_'): continue
        P = mrk(f)
        if len(P): lm[b] = P[0]
    for s, S in (('r','sag'), ('l','sol')):
        ref = mrk(os.path.join(d, 'OTO_rim_%s.mrk.json' % S))
        A, bilgi = rimcurve.auto_rim(ct, rows, org, lm, s)
        if A is None:
            print('%-9s %-4s  EGRI URETILEMEDI' % (ad, S)); tamam += 1; continue
        dd = np.linalg.norm(A - ref, axis=1)
        ok = dd.max() < OLCUT
        gecti += ok; tamam += 1
        print('%-9s %-4s %8.4f %8.4f %8.3f  %s'
              % (ad, S, dd.mean(), dd.max(), bilgi['basari'], 'GECTI' if ok else '>>> KALDI'),
              flush=True)
print('\n  %d/%d orbita olcutu gecti (olcut: maks < %.2f mm)' % (gecti, tamam, OLCUT))
