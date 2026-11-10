# -*- coding: utf-8 -*-
"""OTOMATIK 14 LANDMARK — landmark girdisi olmadan, ham BT'den.
Zincir:
 1. bul.orbita_bul      : iki orbita merkezi + apertur normali (goruntuden)
 2. atlas sekli         : 14 noktanin ilk kestirimi (benzerlik hizalamasi)
 3. rimcurve.auto_rim   : apertur kenar egrisi (ilk kestirimle baslatilir)
 4. atlas acisi         : 6 rim noktasi egri uzerine oturtulur
 5. ek                  : alan-ikiye-bolme tanimi (atlas acisina gore ustun)
 6. apex                : isin maskesinin en arka noktasi
"""
import sys, json
sys.path.insert(0, '/home/claude/an')
import numpy as np, params, rayseg, rimcurve, bul

ORD = ('d', 'mf', 'mso', 'fmo', 'ek', 'o')
AD = ['d-r', 'd-l', 'mf-r', 'mf-l', 'mso-r', 'mso-l', 'fmo-r', 'fmo-l',
      'ek-r', 'ek-l', 'o-r', 'o-l', 'apex-r', 'apex-l']


def benzerlik(A, B):
    ca, cb = A.mean(0), B.mean(0)
    A0, B0 = A - ca, B - cb
    U, S, Vt = np.linalg.svd(A0.T @ B0)
    R = U @ Vt
    if np.linalg.det(R) < 0:
        Vt = Vt.copy(); Vt[-1] *= -1; R = U @ Vt
    return (A0 @ R) * (S.sum() / (A0 ** 2).sum()) + cb


def gpa(ss, tur=30):
    ort = ss[0].copy()
    for _ in range(tur):
        y = np.mean([benzerlik(S, ort) for S in ss], axis=0)
        if np.abs(y - ort).max() < 1e-10:
            return y
        ort = y
    return ort


def _cerceve_capa(ms, ml, ns, nl):
    o = (ms + ml) / 2.0
    ex = ms - ml; L = float(np.linalg.norm(ex)); ex = ex / L
    ny = ns + nl; ny /= np.linalg.norm(ny)
    ey = ny - np.dot(ny, ex) * ex
    nn = np.linalg.norm(ey)
    ey = ey / nn if nn > 1e-6 else np.array([0., 1., 0.])
    return o, np.stack([ex, ey, np.cross(ex, ey)]), L


def _atlas_capa(S):
    out = []
    for s in ('r', 'l'):
        rim = np.array([S[AD.index(b + '-' + s)] for b in ORD])
        c = rim.mean(0); ap = S[AD.index('apex-' + s)]
        u = ap - c; u /= np.linalg.norm(u)
        cc, nn, _, _ = params.plane(rim)
        if np.dot(nn, -u) < 0:
            nn = -nn
        out.append((c + u * 9.0, nn))
    return out[0][0], out[1][0], out[0][1], out[1][1]


def _duzlem_cerceve(E, ic_nokta):
    """Apertur duzlemi; n ONE bakar (ic_nokta = kavitenin icinde bir nokta)."""
    c, n, _, _ = params.plane(E)
    if np.dot(ic_nokta - c, n) > 0:
        n = -n
    up = np.array([0., 0., 1.0])
    u = up - np.dot(up, n) * n; u /= np.linalg.norm(u)
    return c, n, u, np.cross(n, u)


def _duzlem_cerceve_anatomik(E, ic_nokta, lm):
    """Apertur duzlemi, in-plane YUKARI ekseni ANATOMIK.

    `0F` §20: "B = anatomik (MSP normali, YALNIZ `d` ve `mf` ciftlerinden —
    ikisi de sutur noktasidir)". Dunya +z yerine bu kullanilir.
    `0F` §21 hukmu: GENEL kapsamda BENIMSENMEZ; `0F2` §36: `mso` icin kabul
    (4,755 -> 3,444 mm, her uc olcutte iyi). Bu yuzden YALNIZ `mso` icin cagrilir.
    """
    c, n, _, _ = params.plane(E)
    if np.dot(ic_nokta - c, n) > 0:
        n = -n
    nm = np.mean([np.asarray(lm[b + '-r'], float) - np.asarray(lm[b + '-l'], float)
                  for b in ('d', 'mf')], axis=0)
    nm = nm / np.linalg.norm(nm)
    u = np.cross(n, nm)
    u = u - np.dot(u, n) * n
    u = u / np.linalg.norm(u)
    if u[2] < 0:
        u = -u                      # dunya +z surumuyle ayni yonde (YUKARI) olsun
    return c, n, u, np.cross(n, u)


def _aci_yerlestir(E, c, u, v, s, aci_deg, r_oran):
    """Egri uzerinde verilen acida nokta. r_oran yalniz dogrulama icin dondurulur."""
    E2 = np.stack([(E - c) @ u, (E - c) @ v], 1)
    sgn = 1.0 if s == 'r' else -1.0
    aci = np.degrees(np.arctan2(sgn * E2[:, 1], E2[:, 0]))
    # egriyi yogunlastir
    t = np.arange(len(E))
    tt = np.linspace(0, len(E), 1440, endpoint=False)
    Ed = np.stack([np.interp(tt, np.r_[t, len(E)], np.r_[E[:, k], E[0, k]]) for k in range(3)], 1)
    E2d = np.stack([(Ed - c) @ u, (Ed - c) @ v], 1)
    acid = np.degrees(np.arctan2(sgn * E2d[:, 1], E2d[:, 0]))
    d = np.abs(((acid - aci_deg + 180) % 360) - 180)
    j = int(np.argmin(d))
    return Ed[j], float(np.linalg.norm(E2d[j]) / np.linalg.norm(E2d, axis=1).mean())


def _ek_alan(E, c, u, v, mf_noktasi):
    """`ek`: mf'den cikan kirisin apertur alanini ikiye boldugu nokta (Tip II tanimi)."""
    t = np.arange(len(E)); tt = np.linspace(0, len(E), 720, endpoint=False)
    Ed = np.stack([np.interp(tt, np.r_[t, len(E)], np.r_[E[:, k], E[0, k]]) for k in range(3)], 1)
    P2 = np.stack([(Ed - c) @ u, (Ed - c) @ v], 1)

    def pa(Q):
        x, y = Q[:, 0], Q[:, 1]
        return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
    tot = pa(P2); N = len(P2)
    mf2 = np.array([(mf_noktasi - c) @ u, (mf_noktasi - c) @ v])
    i0 = int(np.argmin(np.linalg.norm(P2 - mf2, axis=1)))
    en = None
    for j in range(N):
        if j == i0:
            continue
        yay = P2[i0:j + 1] if j > i0 else np.vstack([P2[i0:], P2[:j + 1]])
        if len(yay) < 3:
            continue
        f = abs(pa(yay) - tot / 2)
        if en is None or f < en[0]:
            en = (f, j)
    return Ed[en[1]]


def tespit(ct, rows, org, atlas_sekil, rim_atlas, ayrinti=False,
           apeks_atlas=None, tur=3, mso_anat=None):
    """14 landmarki dondur. atlas_sekil: (14,3) ortalama sekil; rim_atlas: nokta->(aci, r).

    YENIDEN KURULAN ADIMLAR (2026-11-10, `0AT`):
      - YINELEME (`07` §1 adim 4): egri -> duzlem/merkez -> egri, en cok `tur` tur.
        Gerekce `07` §4: "Egriden kurulan duzlem, kestirimden kurulandan iyidir."
      - APEKS ATLASI (`07` §1 adim 7, `atlas` §: c - n*t + u*dik + v*(sgn*yan)).
        apeks_atlas=None ise eski yol (isin maskesinin en arka noktasi) korunur.
    """
    r = bul.orbita_bul(ct, rows, org)
    if r is None:
        return None, {'hata': 'orbita bulunamadi'}
    ms = np.array(r['sag']['merkez'], float); ml = np.array(r['sol']['merkez'], float)
    ns = np.array(r['sag']['normal'], float); nl = np.array(r['sol']['normal'], float)
    oB, FB, LB = _cerceve_capa(ms, ml, ns, nl)
    aS, aL, anS, anL = _atlas_capa(atlas_sekil)
    oA, FA, LA = _cerceve_capa(aS, aL, anS, anL)
    T = ((atlas_sekil - oA) @ FA.T * (LB / LA)) @ FB + oB
    ilk = {k: T[i] for i, k in enumerate(AD)}
    if ayrinti:
        print('   ilk kestirim hazir (atlas sekli + 2 capa)')

    son = dict(ilk)
    bilgi = {'orbita': {'sag': {k: (v.tolist() if hasattr(v, 'tolist') else v)
                                for k, v in r['sag'].items()},
                        'sol': {k: (v.tolist() if hasattr(v, 'tolist') else v)
                                for k, v in r['sol'].items()}}, 'egri': {}, 'tur': {}}
    for s, S, mrk in (('r', 'sag', ms), ('l', 'sol', ml)):
        lmo = {b + '-' + s: ilk[b + '-' + s] for b in ORD}
        lmo['apex-' + s] = ilk['apex-' + s]
        E = None; cnuv = None; kosulan = 0
        for _t in range(max(1, int(tur))):
            try:
                E2, _ = rimcurve.auto_rim(ct, rows, org, lmo, s, win=0.75, n_out=20)
            except Exception as e:
                bilgi['egri'][S] = 'HATA: %s' % e
                E2 = None
            if E2 is None:
                break
            E = np.asarray(E2, float)
            c, n, u, v = _duzlem_cerceve(E, mrk)
            cnuv = (c, n, u, v)
            kosulan += 1
            for b in ORD:
                P, rr = _aci_yerlestir(E, c, u, v, s, rim_atlas[b]['aci'], rim_atlas[b]['r'])
                son[b + '-' + s] = P
            try:
                son['ek-' + s] = _ek_alan(E, c, u, v, son['mf-' + s])
            except Exception:
                pass
            # `mso` ANATOMIK cercevede (`0F2` §36; `0F` §21 genel kapsamda RET).
            # Atlas acisi ayni cercevede turetilir: `an/out/mso_anatomik.json`.
            if mso_anat:
                try:
                    ca, na, ua, va = _duzlem_cerceve_anatomik(E, mrk, son)
                    son['mso-' + s], _ = _aci_yerlestir(E, ca, ua, va, s,
                                                        mso_anat['aci'], mso_anat['r'])
                except Exception:
                    pass
            if apeks_atlas:
                sgn = 1.0 if s == 'r' else -1.0
                son['apex-' + s] = (c - n * float(apeks_atlas['t'])
                                    + u * float(apeks_atlas['dik'])
                                    + v * (sgn * float(apeks_atlas['yan'])))
            # --- YINELEME: yeni noktalardan cerceveyi yeniden kur ---
            kom = {b + '-' + s: son[b + '-' + s] for b in ORD}
            kom['apex-' + s] = son.get('apex-' + s, lmo['apex-' + s])
            if all(np.allclose(kom[k], lmo[k], atol=1e-9) for k in kom):
                break
            lmo = kom
        bilgi['tur'][S] = kosulan
        if E is None:
            bilgi['egri'].setdefault(S, 'uretilemedi')
            continue
        bilgi['egri'][S] = E.tolist()
        if not apeks_atlas:
            c, n, u, v = cnuv
            try:
                o = rayseg.ray_volume(ct, rows, org, lmo, s, rim_curve=E, plane_shift=0.0,
                                      return_mask=True, acma_mm=1.5)
                M = o['maske']
                ii = np.argwhere(M)
                lps = (rows.T @ ii.astype(float).T).T + org
                P = lps * np.array([-1., -1., 1.])
                t2 = (P - c) @ n
                son['apex-' + s] = P[int(np.argmin(t2))]
            except Exception as e:
                bilgi.setdefault('apeks_hata', {})[S] = str(e)
    return son, bilgi
