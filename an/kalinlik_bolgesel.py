# -*- coding: utf-8 -*-
"""Orbita duvar kalinligi — parametre 11-14.

TEZ KARARI (gerec-yontem-tasarim-kararlari.md): tek-nokta HU profili DEGIL;
butun-kavite coklu-isin, bolgesel medyan (Treece 2010 / BoneJ local-thickness
mantigi). Her kavite sinir vokselinde dis normal boyunca HU profili okunur,
ilk kortikal kesit olculur, vokseller superior/inferior/medial/lateral
bolgelere ayrilir, bolge basina min / medyan / maks raporlanir.

Kabul olcutleri araştırmacının kendi betiginden korunmustur:
  HU esigi 300, adim 0.08 mm, kalinlik 0.2-4.0 mm, peak < 1600 HU,
  tarama araligi sonuna degen (kapanmayan) kesit reddedilir.
"""
import numpy as np
from scipy.ndimage import distance_transform_edt, binary_erosion, map_coordinates

HU_THR = 300.0
T_MAX = 8.0          # dis normal boyunca tarama derinligi (mm)
T_STEP = 0.08
TH_MIN, TH_MAX = 0.2, 4.0
PEAK_MAX = 1600.0
AXIS_EXCL = 0.6      # |normal . eksen| > bu ise apertur/apeks yuzeyi -> dislanir
REGIONS = ('superior', 'inferior', 'medial', 'lateral')


def _frame(side):
    """RAS'ta bolge yonleri. Sag orbita: medial = -x, sol orbita: medial = +x."""
    med = np.array([-1.0, 0, 0]) if side == 'r' else np.array([1.0, 0, 0])
    return {'superior': np.array([0, 0, 1.0]), 'inferior': np.array([0, 0, -1.0]),
            'medial': med, 'lateral': -med}


def measure_side(ct, rows, org, mask, axis_ras, side, batch=40000):
    sp = np.array([np.linalg.norm(rows[a]) for a in range(3)])
    Rt = rows.T

    def ras2ijk(P):
        lps = np.atleast_2d(P) * np.array([-1.0, -1.0, 1.0])
        return np.linalg.solve(Rt, (lps - org).T).T

    def ijk2ras(P):
        return (org + np.atleast_2d(P) @ rows) * np.array([-1.0, -1.0, 1.0])

    # --- sinir vokselleri + SDF gradyanindan dis normaller (kirpilmis kutuda) ---
    nz = np.array(np.nonzero(mask))
    lo = np.maximum(nz.min(1) - 25, 0)
    hi = np.minimum(nz.max(1) + 26, np.array(mask.shape))
    sl = tuple(slice(lo[a], hi[a]) for a in range(3))
    m = mask[sl]
    sdf = distance_transform_edt(~m, sampling=sp) - distance_transform_edt(m, sampling=sp)
    shell = m & ~binary_erosion(m, iterations=1)
    ii, jj, kk = np.where(shell)
    gi, gj, gk = np.gradient(sdf, sp[0], sp[1], sp[2])
    nor = np.stack([gi[ii, jj, kk], gj[ii, jj, kk], gk[ii, jj, kk]], 1)  # +grad = disa
    nor = nor * np.array([-1.0, -1.0, 1.0])                              # IJK -> RAS
    n = np.linalg.norm(nor, axis=1, keepdims=True)
    ok = n[:, 0] > 1e-6
    nor = nor[ok] / n[ok]
    pts = ijk2ras(np.stack([ii + lo[0], jj + lo[1], kk + lo[2]], 1).astype(float))[ok]

    # --- apertur/apeks yuzeylerini disla ---
    ax = axis_ras / np.linalg.norm(axis_ras)
    keep = np.abs(nor @ ax) <= AXIS_EXCL
    pts, nor = pts[keep], nor[keep]

    # --- bolge ataması: en buyuk normal bileseni ---
    F = _frame(side)
    proj = np.stack([nor @ F[r] for r in REGIONS], 1)
    reg = np.argmax(proj, 1)

    # --- HU profilleri ---
    ts = np.arange(0.0, T_MAX + T_STEP / 2, T_STEP)
    nt = len(ts)
    th = np.full(len(pts), np.nan)
    rej = np.zeros(len(pts), dtype=np.uint8)   # 0 kabul, 1 kemik yok, 2 kapanmayan, 3 >4mm, 4 peak
    for s in range(0, len(pts), batch):
        e = min(s + batch, len(pts))
        Q = pts[s:e, None, :] + ts[None, :, None] * nor[s:e, None, :]
        hus = map_coordinates(ct, ras2ijk(Q.reshape(-1, 3)).T,
                              order=1, mode='nearest').reshape(e - s, nt)
        above = hus >= HU_THR
        # her satirda ilk kemik kosusu
        first = np.argmax(above, 1)
        has = above.any(1)
        rej[s:e][~has] = 1
        for r in np.where(has)[0]:
            a = first[r]
            b = a
            while b < nt and above[r, b]:
                b += 1
            if b >= nt:                       # tarama sinirina degdi -> kapanmayan kesit
                rej[s + r] = 2
                continue
            t = ts[b - 1] - ts[a] + T_STEP
            pk = float(hus[r, a:b].max())
            if pk >= PEAK_MAX:
                rej[s + r] = 4
            elif t > TH_MAX:
                rej[s + r] = 3
            elif t >= TH_MIN:
                th[s + r] = t

    out = {}
    for q, rname in enumerate(REGIONS):
        v = th[(reg == q) & ~np.isnan(th)]
        tot = int((reg == q).sum())
        if len(v) < 20:
            out[rname] = dict(durum='YETERSIZ', n=int(len(v)), n_sinir=tot)
            continue
        rr = rej[reg == q]
        out[rname] = dict(durum='TAMAM', n=int(len(v)), n_sinir=tot,
                          basari=round(100.0 * len(v) / tot, 1),
                          red_kemikyok=int((rr == 1).sum()), red_kapanmayan=int((rr == 2).sum()),
                          red_kalin=int((rr == 3).sum()), red_peak=int((rr == 4).sum()),
                          medyan=round(float(np.median(v)), 2),
                          q1=round(float(np.percentile(v, 25)), 2),
                          q3=round(float(np.percentile(v, 75)), 2),
                          min=round(float(v.min()), 2), maks=round(float(v.max()), 2))
    return out
