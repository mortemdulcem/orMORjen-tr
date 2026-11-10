# -*- coding: utf-8 -*-
"""ATLAS: her rim landmarkinin APERTUR EGRISI uzerindeki acisal yeri.
10 orbitada (5 olgu) olculur; tutarliysa otomatik yerlestirme buna dayanir.
"""
import sys, json
sys.path.insert(0, '/home/claude/an')
import numpy as np, params

ORD = ('d', 'mf', 'mso', 'fmo', 'ek', 'o')
OLG = [('hasta7', '/home/claude/h7/ham/ölçüm1'),
       ('hasta8', '/home/claude/h8m/ham/ölçüm2'),
       ('hasta9', '/home/claude/h9m/ham/ölçüm5'),
       ('hasta10', '/home/claude/h10m/ham/ölçüm4'),
       ('hasta11', '/home/claude/h11m3/ham/ölçüm3')]


def egri_al(egri, S):
    for k, v in egri.items():
        kl = k.lower()
        if kl == S or kl.endswith('_' + S) or kl.endswith(S) or ('_' + S + '_') in kl:
            a = np.asarray(v, float)
            if a.ndim == 2 and len(a) >= 10:
                return a
    return None


def cerceve(E, apex):
    """Apertur duzlemi + in-plane eksenler. u = YUKARI (S'ye en yakin), v = u x n."""
    c, n, _, _ = params.plane(E)
    if np.dot(apex - c, n) > 0:
        n = -n                                  # n ONE baksin
    up = np.array([0., 0., 1.0])
    u = up - np.dot(up, n) * n
    u /= np.linalg.norm(u)                      # duzlem icinde YUKARI
    v = np.cross(n, u)                          # saga/sola
    return c, n, u, v


SON = {}
print('%-9s %-4s %-5s %8s %8s   (aci: 0=YUKARI, +saat yonu)' % ('olgu', 'yan', 'nokta', 'aci_deg', 'r/r_ort'))
for ad, F in OLG:
    lm, egri = params.load_scene(F)
    for a, b in (('fso-r', 'mso-r'), ('fso-l', 'mso-l')):
        if a in lm and b not in lm:
            lm[b] = lm[a]
    for S, s in (('sag', 'r'), ('sol', 'l')):
        E = egri_al(egri, S)
        if E is None:
            print('%-9s %-4s EGRI YOK' % (ad, S)); continue
        apex = np.asarray(lm['apex-' + s], float)
        c, n, u, v = cerceve(E, apex)
        # egri yariçaplari
        E2 = np.stack([(E - c) @ u, (E - c) @ v], 1)
        r_ort = float(np.linalg.norm(E2, axis=1).mean())
        key = '%s_%s' % (ad, S)
        SON[key] = {}
        for b in ORD:
            P = np.asarray(lm[b + '-' + s], float)
            p2 = np.array([(P - c) @ u, (P - c) @ v])
            # sol tarafta v yonu ters cevrilir ki iki taraf ayni dolasima sahip olsun
            sgn = 1.0 if s == 'r' else -1.0
            aci = float(np.degrees(np.arctan2(sgn * p2[1], p2[0])))
            rr = float(np.linalg.norm(p2) / r_ort)
            SON[key][b] = (round(aci, 1), round(rr, 3))
            print('%-9s %-4s %-5s %8.1f %8.3f' % (ad, S, b, aci, rr))

# atlas ozeti
print()
print('=' * 70)
print('ATLAS — nokta basina acisal yer (10 orbita)')
print('=' * 70)
print('%-5s %10s %8s %8s | %10s %8s' % ('nokta', 'aci ort', 'aci SS', 'aci yay', 'r/r ort', 'r SS'))
ATL = {}
for b in ORD:
    a = np.array([SON[k][b][0] for k in SON if b in SON[k]])
    r = np.array([SON[k][b][1] for k in SON if b in SON[k]])
    # acilari -180..180 sarmasini duzelt
    if a.max() - a.min() > 180:
        a = np.where(a < 0, a + 360, a)
    ATL[b] = dict(aci=round(float(a.mean()), 1), aci_ss=round(float(a.std(ddof=1)), 1),
                  r=round(float(r.mean()), 3), r_ss=round(float(r.std(ddof=1)), 3), n=len(a))
    print('%-5s %10.1f %8.1f %8.1f | %10.3f %8.3f'
          % (b, a.mean(), a.std(ddof=1), a.max() - a.min(), r.mean(), r.std(ddof=1)))
json.dump(dict(olgu=SON, atlas=ATL), open('/home/claude/an/out/rimatlas.json', 'w'),
          ensure_ascii=False, indent=1)
print('\nyazildi: out/rimatlas.json')
