# -*- coding: utf-8 -*-
"""LANDMARK ZINCIRI — UC KOLLU YENIDEN KURULUM SINAVI.

OLCUT (kosmadan once yazildi, sonra gevsetilmeyecek):
  Her eklenen adim ortalama sapmayi DUSURMELIDIR. Yukseltirse o adimin
  yeniden kurulumu yanlistir ve GERI ALINIR.
  Hedef: donmus hat deterministik oldugu icin dogru zincirde sapma ~0.

  A = yineleme yok (tur=1) · apeks eski yol        <- taban
  B = yineleme var (tur=3) · apeks eski yol        <- `07` §1 adim 4
  C = yineleme var (tur=3) · apeks ATLASI          <- `07` §1 adim 7
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
KOL = [('A', dict(tur=1, apeks_atlas=None)),
       ('B', dict(tur=3, apeks_atlas=None)),
       ('C', dict(tur=3, apeks_atlas=apa))]

olgular = sorted([x for x in os.listdir(PAK) if os.path.isdir(os.path.join(PAK, x))])
top = {k: [] for k, _ in KOL}
print('%-9s %-3s %8s %8s %8s  %s' % ('olgu','kol','ort','medyan','maks','en kotu'), flush=True)
for ad in olgular:
    d = os.path.join(PAK, ad)
    ct, rows, org = rayseg.load_ct(os.path.join(d, '%s_CT.nrrd' % ad))
    ref = {}
    for f in glob.glob(os.path.join(d, 'OTO_*.mrk.json')):
        b = os.path.basename(f)[4:].replace('.mrk.json','')
        if b.startswith('rim_'): continue
        P = mrk(f)
        if len(P): ref[b] = P[0]
    for kol, ayar in KOL:
        try:
            lm, bil = L.tespit(ct, rows, org, ort, ra, **ayar)
        except Exception as e:
            print('%-9s %-3s ISTISNA %s' % (ad, kol, str(e)[:50]), flush=True); continue
        if lm is None:
            print('%-9s %-3s DURDU' % (ad, kol), flush=True); continue
        dd = [(b+'-'+s, float(np.linalg.norm(np.asarray(lm[b+'-'+s],float) - ref[b+'-'+s])))
              for b in AD for s in ('r','l') if (b+'-'+s) in lm and (b+'-'+s) in ref]
        v = np.array([x[1] for x in dd]); ek = max(dd, key=lambda x: x[1])
        top[kol].extend(v.tolist())
        print('%-9s %-3s %8.3f %8.3f %8.3f  %s' % (ad, kol, v.mean(), np.median(v), v.max(), ek[0]), flush=True)

print('\n' + '='*58)
print('%-3s %6s %9s %9s %9s' % ('kol','n','ort mm','medyan','maks'))
for kol, _ in KOL:
    a = np.array(top[kol])
    if len(a): print('%-3s %6d %9.3f %9.3f %9.3f' % (kol, len(a), a.mean(), np.median(a), a.max()))
