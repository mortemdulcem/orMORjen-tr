# -*- coding: utf-8 -*-
"""Apertur kenar (rim) egrisini landmarklardan ve BT'den otomatik bulur.

KAYNAK (2026-11-10 konteyner kurtarmasi, `0AT`):
  - govde: proje belgesi `cozumleme-betikleri-kaynak-kod.md` -> "## rimcurve.py"
  - medial koruma imzasi ve kurulumu: ek `100c87b7-medial_koruma_kod.txt` (2026-11-09)
  - korumanin isin uzerinde uygulanmasi: ayni ekin OKUMA NOTU -> "bone |= (dpl < dlim)"
Bu dosya SAYISAL OLARAK dogrulanmistir: donmus hattin urettigi OTO rim egrilerini
yeniden uretir (bkz. `0AT` sinavi).
"""
import numpy as np
from scipy import ndimage as ndi

BONE_HU = 200.0
RIM_ORDER = ('d', 'mf', 'mso', 'fmo', 'ek', 'o')   # cevresel sira


def _plane(P):
    c = P.mean(0)
    _, _, vt = np.linalg.svd(P - c)
    return c, vt[2]


def auto_rim(ct, rows, org, lm, side, n_ang=72, n_out=20,
             s_range=(-30.0, 15.0), s_step=0.25, r_step=0.25,
             s_min_front=-4.0, smooth=7, mode='pencere', win=0.75,
             medial_frac=0.75):
    """medial_frac: isin orta sagittal duzleme bu kadar yaklasirsa DUVAR sayilir
    (rayseg.ray_volume ile ayni mantik; 2026-10-14'te eklendi — otomatik egri medialde
    ince kenari gecip etmoid/burun tarafina kaciyordu, hasta10'da +5,7 mm). medial_frac=None
    korumayi kapatir."""
    L = np.array([lm[b + '-' + side] for b in RIM_ORDER], float)
    apex = np.asarray(lm['apex-' + side], float)
    c, n = _plane(L)
    if np.dot(apex - c, n) > 0:
        n = -n                                     # n one baksin
    e1 = np.cross(n, [0, 0, 1.0]); e1 /= np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    rl = np.linalg.norm(np.stack([(L - c) @ e1, (L - c) @ e2], 1), axis=1)
    r_lo, r_hi = 0.45 * rl.mean(), 1.75 * rl.mean()

    msp = None
    if medial_frac:
        try:
            pr = RIM_ORDER
            nm = np.mean([np.asarray(lm[b + '-r'], float) - np.asarray(lm[b + '-l'], float)
                          for b in pr], axis=0)
            nm = nm / np.linalg.norm(nm)
            cm = np.mean([(np.asarray(lm[b + '-r'], float)
                           + np.asarray(lm[b + '-l'], float)) / 2 for b in pr], axis=0)
            sgn = 1.0 if side == 'r' else -1.0
            dmin = min(abs((np.asarray(lm['d-' + side], float) - cm) @ nm),
                       abs((np.asarray(lm['mf-' + side], float) - cm) @ nm))
            msp = (cm, nm, sgn, dmin * medial_frac)
        except Exception:
            msp = None

    Rt = rows.T

    def hu(P):
        lps = np.atleast_2d(P) * np.array([-1.0, -1.0, 1.0])
        ijk = np.linalg.solve(Rt, (lps - org).T).T
        return ndi.map_coordinates(ct, ijk.T, order=1, mode='constant', cval=-1024.0)

    ang = np.linspace(0, 2 * np.pi, n_ang, endpoint=False)
    rs = np.arange(r_lo, r_hi + r_step / 2, r_step)
    ss = np.arange(s_range[0], s_range[1] + s_step / 2, s_step)
    rim_r = np.full(n_ang, np.nan)
    rim_s = np.full(n_ang, np.nan)

    for a in range(n_ang):
        e = np.cos(ang[a]) * e1 + np.sin(ang[a]) * e2
        Q = c[None, None, :] + rs[:, None, None] * e[None, None, :] \
            + ss[None, :, None] * n[None, None, :]
        V = hu(Q.reshape(-1, 3)).reshape(len(rs), len(ss))
        bone = V >= BONE_HU
        if msp is not None:
            cm_, nm_, sgn_, dlim = msp
            dpl = ((Q.reshape(-1, 3) - cm_) @ nm_).reshape(len(rs), len(ss)) * sgn_
            bone |= (dpl < dlim)
        run = bone[:, :-1] & bone[:, 1:]           # iki ardisik voksel
        sa = np.full(len(rs), np.nan)
        for i in range(len(rs)):
            idx = np.where(run[i])[0]
            if idx.size:
                sa[i] = ss[idx.max() + 1]
        valid = ~np.isnan(sa) & (sa >= s_min_front)
        if not valid.any():
            continue
        i0 = int(np.argmax(valid))                 # kemigin ilk gorundugu yaricap
        if mode == 'kenar':
            rim_r[a], rim_s[a] = rs[i0], sa[i0]
        else:
            lim = i0 + int(round(win / r_step))
            i = imax = i0
            while i + 1 < len(rs) and i + 1 <= lim and valid[i + 1] \
                    and sa[i + 1] >= sa[imax] - 1e-9:
                i += 1; imax = i
            rim_r[a], rim_s[a] = rs[imax], sa[imax]

    ok = ~np.isnan(rim_r)
    if ok.sum() < n_ang * 0.5:
        return None, dict(basari=float(ok.mean()))
    ia = np.arange(n_ang)
    rim_r = np.interp(ia, ia[ok], rim_r[ok], period=n_ang)
    rim_s = np.interp(ia, ia[ok], rim_s[ok], period=n_ang)
    if smooth > 1:
        rim_r = ndi.median_filter(rim_r, size=smooth, mode='wrap')
        rim_s = ndi.median_filter(rim_s, size=smooth, mode='wrap')

    pts = (c[None, :] + rim_r[:, None] * (np.cos(ang)[:, None] * e1[None, :]
                                          + np.sin(ang)[:, None] * e2[None, :])
           + rim_s[:, None] * n[None, :])
    sel = np.round(np.linspace(0, n_ang, n_out, endpoint=False)).astype(int) % n_ang
    return pts[sel], dict(basari=float(ok.mean()), tum=pts,
                          r=rim_r, s=rim_s, c=c, n=n)
