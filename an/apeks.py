# -*- coding: utf-8 -*-
"""APEKS — kemik koninin daralma profilinden. Kural olcumle konur, tahminle degil.
Profil: apertur merkezinden eksen boyunca geriye; her derinlikte eksen noktasinin
kemige en kisa in-plane uzakligi (ic yaricap).
"""
import sys, json
sys.path.insert(0, '/home/claude/an')
import numpy as np, params, rayseg
from scipy import ndimage as ndi

KEMIK = 200.0
AC = np.linspace(0, 2 * np.pi, 72, endpoint=False)


def _ornek(ct, rows, org, P):
    lps = np.atleast_2d(P) * np.array([-1., -1., 1.])
    ijk = np.linalg.solve(rows.T, (lps - org).T).T
    return ndi.map_coordinates(ct, ijk.T, order=1, mode='constant', cval=-1024.)


def ic_yaricap(ct, rows, org, P, e1, e2, r_maks=28.0, adim=0.4):
    """P'den e1-e2 duzleminde her yonde kemige uzaklik; en kucugu = ic yaricap."""
    rr = np.arange(adim, r_maks + adim / 2, adim)
    D = np.outer(np.cos(AC), e1) + np.outer(np.sin(AC), e2)
    Q = P[None, None, :] + D[:, None, :] * rr[None, :, None]
    V = _ornek(ct, rows, org, Q.reshape(-1, 3)).reshape(len(AC), len(rr))
    kat = V >= KEMIK
    kat2 = kat[:, :-1] & kat[:, 1:]
    vur = kat2.any(axis=1)
    d = np.where(vur, rr[np.argmax(kat2, axis=1)], r_maks)
    return float(np.median(d)), float(d.min()), float(np.percentile(d, 25))


def profil(ct, rows, org, c, n, t_maks=60.0, adim=1.0):
    """c = apertur merkezi, n = ONE bakan normal. Geriye dogru profil."""
    e1 = np.cross(n, [0, 0, 1.0]); e1 /= np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    ts = np.arange(0.0, t_maks + adim / 2, adim)
    med, mn, q25 = [], [], []
    for t in ts:
        P = c - n * t
        a, b, q = ic_yaricap(ct, rows, org, P, e1, e2)
        med.append(a); mn.append(b); q25.append(q)
    return ts, np.array(med), np.array(mn), np.array(q25)


if __name__ == '__main__':
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

    SON = {}
    for ad, F in OLG:
        ct, rows, org = rayseg.load_ct(F + '/4 1.25MM BONE.nrrd')
        lm, egri = params.load_scene(F)
        for a, b in (('fso-r', 'mso-r'), ('fso-l', 'mso-l')):
            if a in lm and b not in lm:
                lm[b] = lm[a]
        for S, s in (('sag', 'r'), ('sol', 'l')):
            E = egri_al(egri, S)
            apex = np.asarray(lm['apex-' + s], float)
            c, n, _, _ = params.plane(E)
            if np.dot(apex - c, n) > 0:
                n = -n                      # n ONE baksin
            t_apex = float(np.dot(c - apex, n))   # apeksin eksendeki derinligi
            ts, med, mn, q25 = profil(ct, rows, org, c, n)
            SON['%s_%s' % (ad, S)] = dict(t_apex=round(t_apex, 2),
                                          ts=ts.tolist(), med=[round(x, 2) for x in med],
                                          q25=[round(x, 2) for x in q25])
            # apeks derinliginde ic yaricap ne?
            j = int(np.argmin(np.abs(ts - t_apex)))
            print('%-8s %-4s apeks derinligi %5.1f mm | o derinlikte ic yaricap medyan %5.2f  q25 %5.2f'
                  % (ad, S, t_apex, med[j], q25[j]))
            # profilin belirli esiklere dustugu derinlikler
            for esik in (6.0, 5.0, 4.0, 3.0, 2.5):
                k = np.where(med <= esik)[0]
                t_e = ts[k[0]] if len(k) else np.nan
                print('        medyan ic yaricap <= %.1f mm -> derinlik %5.1f  (apeks hatasi %+6.1f mm)'
                      % (esik, t_e, t_e - t_apex))
    json.dump(SON, open('/home/claude/an/out/apeks_profil.json', 'w'))
    print('\nyazildi: out/apeks_profil.json')
