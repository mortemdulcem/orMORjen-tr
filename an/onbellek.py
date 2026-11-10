# -*- coding: utf-8 -*-
"""Otomatik egri + ilk kestirimi her olgu icin ONBELLEGE al (LOO). Sonraki adimlar hizli olsun."""
import sys, json, os
sys.path.insert(0, '/home/claude/an')
import numpy as np, params, rayseg, landmark as L

OLG = [('hasta7', '/home/claude/h7/ham/ölçüm1'),
       ('hasta8', '/home/claude/h8m/ham/ölçüm2'),
       ('hasta9', '/home/claude/h9m/ham/ölçüm5'),
       ('hasta10', '/home/claude/h10m/ham/ölçüm4'),
       ('hasta11', '/home/claude/h11m3/ham/ölçüm3')]
AD, ORD = L.AD, L.ORD
RA = json.load(open('/home/claude/an/out/rimatlas.json'))

X = {}
for ad, F in OLG:
    lm, _ = params.load_scene(F)
    for a, b in (('fso-r', 'mso-r'), ('fso-l', 'mso-l')):
        if a in lm and b not in lm:
            lm[b] = lm[a]
    X[ad] = np.array([np.asarray(lm[k], float) for k in AD])


def rim_atlas_loo(disla):
    out = {}
    for b in ORD:
        a, r = [], []
        for k, v in RA['olgu'].items():
            if k.startswith(disla + '_') or b not in v:
                continue
            a.append(v[b][0]); r.append(v[b][1])
        a = np.array(a, float)
        if a.max() - a.min() > 180:
            a = np.where(a < 0, a + 360, a)
        m = float(a.mean())
        out[b] = dict(aci=(m - 360 if m > 180 else m), r=float(np.mean(r)))
    return out


OB = {}
for ad, F in OLG:
    ct, rows, org = rayseg.load_ct(F + '/4 1.25MM BONE.nrrd')
    ort = L.gpa([X[b] for b, _ in OLG if b != ad])
    son, bilgi = L.tespit(ct, rows, org, ort, rim_atlas_loo(ad))
    OB[ad] = dict(
        nokta={k: [float(x) for x in son[k]] for k in AD} if son else None,
        egri={S: (bilgi['egri'][S] if isinstance(bilgi['egri'].get(S), list) else None)
              for S in ('sag', 'sol')},
        orbita=bilgi.get('orbita'))
    print('%-8s tamam  egri sag=%s sol=%s' % (
        ad, OB[ad]['egri']['sag'] is not None, OB[ad]['egri']['sol'] is not None))

json.dump(OB, open('/home/claude/an/out/onbellek.json', 'w'))
print('yazildi: out/onbellek.json')
