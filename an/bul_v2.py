# -*- coding: utf-8 -*-
"""ORBITA BULUCU v2 — landmarksiz. Glob tepesi + APERTUR ACIKLIGI testi.
Fikir: orbita, onunde genis bir kemik acikligi olan tek yumusak doku bosluğudur.
Kafa tabani/temporal bosluklar bu testi geçmez.
Donus: her taraf icin (merkez_RAS, apertur_normali, aciklik_orani)
"""
import numpy as np
from scipy import ndimage as ndi
from scipy.ndimage import distance_transform_edt as edt

KEMIK = 200.0


def _yonler(n=252):
    """Kurede yaklasik duzgun dagilmis yonler (Fibonacci)."""
    i = np.arange(n) + 0.5
    phi = np.arccos(1 - 2 * i / n)
    tht = np.pi * (1 + 5 ** 0.5) * i
    return np.stack([np.cos(tht) * np.sin(phi), np.sin(tht) * np.sin(phi), np.cos(phi)], 1)


YON = _yonler(252)


def _ornek(ct, rows, org, P):
    lps = np.atleast_2d(P) * np.array([-1., -1., 1.])
    ijk = np.linalg.solve(rows.T, (lps - org).T).T
    return ndi.map_coordinates(ct, ijk.T, order=1, mode='constant', cval=-1024.)


def aciklik(ct, rows, org, merkez, r_maks=45.0, adim=0.5):
    """Merkezden her yonde kemige kadar uzaklik. Kemik gormeyen yonler = aciklik."""
    rr = np.arange(adim, r_maks + adim / 2, adim)
    P = merkez[None, None, :] + YON[:, None, :] * rr[None, :, None]
    V = _ornek(ct, rows, org, P.reshape(-1, 3)).reshape(len(YON), len(rr))
    kat = V >= KEMIK
    kat2 = kat[:, :-1] & kat[:, 1:]
    vur = kat2.any(axis=1)
    d = np.where(vur, rr[np.argmax(kat2, axis=1)], np.nan)
    acik = ~vur
    oran = float(acik.mean())
    if acik.sum() < 3:
        return oran, None, d
    nrm = YON[acik].mean(0)
    nn = np.linalg.norm(nrm)
    return oran, (nrm / nn if nn > 1e-6 else None), d


_KAFA_MERKEZI = None


def orbita_bul(ct, rows, org, ayrinti=False):
    sp = np.array([abs(rows[0, 0]), abs(rows[1, 1]), abs(rows[2, 2])], float)

    def ijk2ras(P):
        return ((rows.T @ np.atleast_2d(P).T).T + org) * np.array([-1., -1., 1.])

    bone = ct >= KEMIK
    kafa = ct > -500
    lab, n = ndi.label(ndi.binary_closing(kafa, ndi.generate_binary_structure(3, 1), iterations=2))
    if n > 1:
        boy = ndi.sum(np.ones_like(lab), lab, range(1, n + 1))
        kafa = (lab == (1 + int(np.argmax(boy))))
    kafa = ndi.binary_fill_holes(kafa)
    global _KAFA_MERKEZI
    _ix = np.array(ndi.center_of_mass(kafa), float)
    _KAFA_MERKEZI = ((rows.T @ _ix.reshape(3, 1)).T[0] + org) * np.array([-1., -1., 1.])
    yum = kafa & (~bone) & (ct > -200)
    D = edt(yum, sampling=sp)
    aday = (D > 9.0) & (D < 20.0)
    mx = ndi.maximum_filter(D, size=(9, 9, 5))
    tepe = aday & (D >= mx - 1e-6)
    idx = np.argwhere(tepe); dv = D[tepe]
    srt = np.argsort(dv)[::-1][:600]
    idx, dv = idx[srt], dv[srt]
    ras = ijk2ras(idx.astype(float))
    tut = []
    for p, d in zip(ras, dv):
        if all(np.linalg.norm(p - q[0]) > 14.0 for q in tut):
            tut.append((p, float(d)))
        if len(tut) >= 60:
            break

    # --- APERTUR ACIKLIGI TESTI
    gecen = []
    for p, d in tut:
        oran, nrm, _ = aciklik(ct, rows, org, p)
        if nrm is None:
            continue
        # aciklik makul buyuklukte ve ONE bakiyor olmali (A bileseni baskin)
        if not (0.02 <= oran <= 0.45):
            continue
        _d = np.asarray(p, float) - _KAFA_MERKEZI
        _nd = np.linalg.norm(_d)
        if _nd < 1e-9 or float(np.dot(nrm, _d / _nd)) < 0.45:   # DISA bakiyor mu
            continue
        gecen.append(dict(p=p, D=d, oran=oran, n=nrm))
    if ayrinti:
        print('   aday tepe %d -> aciklik testini gecen %d' % (len(tut), len(gecen)))
        for g in sorted(gecen, key=lambda g: -g['D'])[:12]:
            print('     RAS %-24s D=%5.2f  aciklik %%%4.1f  normal %s'
                  % (np.round(g['p'], 1).tolist(), g['D'], 100 * g['oran'],
                     np.round(g['n'], 2).tolist()))

    # --- orta hat: kemik profili simetrisi
    prof = bone.sum(axis=(1, 2)).astype(float)
    nx = ct.shape[0]; en = None
    for c in range(nx // 4, 3 * nx // 4):
        w = min(c, nx - 1 - c)
        if w < 40:
            continue
        a_ = prof[c - w:c][::-1]; b_ = prof[c + 1:c + 1 + w]
        m = min(len(a_), len(b_))
        if m < 40:
            continue
        sk = -np.abs(a_[:m] - b_[:m]).sum() / m
        if en is None or sk > en[0]:
            en = (sk, c)
    x_msp = float(ijk2ras([en[1], 0, 0])[0][0])

    # --- simetrik ikili
    en_iyi = None
    for i in range(len(gecen)):
        for j in range(i + 1, len(gecen)):
            a, b = gecen[i], gecen[j]
            p, q = a['p'], b['p']
            if (p[0] - x_msp) * (q[0] - x_msp) > 0:
                continue
            sg, sl = (a, b) if p[0] > q[0] else (b, a)
            ayr = abs(sg['p'][0] - sl['p'][0])
            if not (38.0 < ayr < 82.0):
                continue
            sim = abs((sg['p'][0] + sl['p'][0]) / 2 - x_msp)
            da = abs(sg['p'][1] - sl['p'][1]); ds = abs(sg['p'][2] - sl['p'][2])
            # normaller de simetrik olmali (A ve S bilesenleri benzer)
            dn = abs(sg['n'][1] - sl['n'][1]) + abs(sg['n'][2] - sl['n'][2])
            ceza = 2.0 * sim + da + ds + 20.0 * dn
            skor = (sg['p'][1] + sl['p'][1]) - 3.0 * ceza + 30.0 * (sg['oran'] + sl['oran'])
            if en_iyi is None or skor > en_iyi[0]:
                en_iyi = (skor, sg, sl, sim, da, ds, ayr, dn)
    if en_iyi is None:
        return None
    _, sg, sl, sim, da, ds, ayr, dn = en_iyi
    return dict(x_msp=x_msp,
                sag=dict(merkez=sg['p'], normal=sg['n'], oran=sg['oran'], D=sg['D']),
                sol=dict(merkez=sl['p'], normal=sl['n'], oran=sl['oran'], D=sl['D']),
                ikili=dict(ayna=sim, dA=da, dS=ds, ayrilik=ayr, dnormal=dn))
