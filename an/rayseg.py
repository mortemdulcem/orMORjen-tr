# -*- coding: utf-8 -*-
"""ISIN TABANLI KAVITE SEGMENTASYONU.

2026-11-10'da konteyner sifirlanmasindan sonra, `medial_koruma_kod.txt`
(2026-11-09 tarihli kod yigini) icindeki GERCEK imza ve govde parcalarindan
yeniden kuruldu. Tahmin degil; alinti.

IMZA (kod yiginindan, satir 47-49):
  r_pad=1.30, smooth_ang=9, t0=0.02, t1=0.985, return_mask=False,
  hu_lo=-300.0, medial_frac=0.75, mask_hu=None, acma_mm=1.5,
  alan_tek_yonlu=False, atu_bas_mm=12.0

GOVDE (kod yiginindan):
  vals  = sample(...)                       -> (n_ang, nsteps)
  solid = (vals >= bone_hu)
  solid |= (dpl < dlim)                     # MEDIAL KORUMA
  solid2 = solid[:, :-1] & solid[:, 1:]     # arka arkaya iki katı ornek
  ...
  mask = koni & (sub > hu_lo) & (sub < mh)
  mask &= (((X - cm_) @ nm_) * sgn >= dlim) # maskede ikinci uygulama
  1.5 mm ACMA -> EN BUYUK BILESEN

SABITLER `0K` §1: 160 HU kavite · 250 HU segmentasyon · adim 0,25 mm
"""
import numpy as np
import nrrd
from scipy import ndimage as ndi

RAS2LPS = np.array([-1.0, -1.0, 1.0])
HU_KAVITE = 160.0
HU_KEMIK = 250.0
RIM_ORDER = ('d', 'mf', 'mso', 'fmo', 'ek', 'o')


def load_ct(yol):
    d, h = nrrd.read(yol)
    sd = h.get('space directions')
    rows = np.array([r for r in sd if not np.any(np.isnan(np.asarray(r, float)))], float)
    org = np.asarray(h.get('space origin'), float)
    uzay = str(h.get('space', 'left-posterior-superior')).lower()
    if uzay.startswith('right-anterior') or uzay.startswith('ras'):
        rows = rows * RAS2LPS[None, :]
        org = org * RAS2LPS
    return np.asarray(d), rows, org


def _ijk(rows, org, P):
    lps = np.atleast_2d(np.asarray(P, float)) * RAS2LPS
    return np.linalg.solve(rows.T, (lps - org).T).T


def sample(ct, rows, org, P):
    """RAS noktalarinda HU (trilineer). HATTIN TEK ORNEKLEYICISI."""
    return ndi.map_coordinates(ct, _ijk(rows, org, P).T, order=1,
                               mode='constant', cval=-1024.0)


def voksel_hacmi(rows):
    return float(abs(np.linalg.det(rows)))


def hacim_cm3(M, rows):
    return float(np.asarray(M, bool).sum()) * voksel_hacmi(rows) / 1000.0


def _msp(lm, side, medial_frac):
    """MEDIAL KORUMA kurulumu — kod yigininden birebir."""
    if not medial_frac:
        return None
    try:
        pr = RIM_ORDER
        nm_ = np.mean([np.asarray(lm[b + '-r'], float) - np.asarray(lm[b + '-l'], float)
                       for b in pr], axis=0)
        nm_ = nm_ / np.linalg.norm(nm_)
        cm_ = np.mean([(np.asarray(lm[b + '-r'], float)
                        + np.asarray(lm[b + '-l'], float)) / 2 for b in pr], axis=0)
        sgn = 1.0 if side == 'r' else -1.0
        dmin = min(abs((np.asarray(lm['d-' + side], float) - cm_) @ nm_),
                   abs((np.asarray(lm['mf-' + side], float) - cm_) @ nm_))
        return (cm_, nm_, sgn, dmin * medial_frac)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# ASAGISI ARASTIRMACININ KENDI KODUDUR.
# Kaynak: proje belgesi `claude/cozumleme-betikleri-kaynak-kod.md` -> "## rayseg.py"
# (2026-10-12 arsiv duzeltmesi: plane_shift + 1.5 mm ACMA dahil).
# BIREBIR AKTARILMISTIR. Tek degisiklik: ozgun dosya load_ct/ras_to_ijk/
# fit_plane/sample'i `import rayseg` ile ceker; burada ayni modulde olduklari
# icin import satiri yoktur. Govde, imza ve sabitler DEGISTIRILMEMISTIR.
# ---------------------------------------------------------------------------
from scipy.ndimage import distance_transform_edt as edt


def ras_to_ijk(P, rows, org):
    return _ijk(rows, org, P)


def fit_plane(P):
    P = np.asarray(P, float)
    c = P.mean(axis=0)
    n = np.linalg.svd(P - c)[2][2]
    return c, n / np.linalg.norm(n)


def _open_mm(mask, sp, r_mm):
    """Oklid topu ile gercek mm olceginde morfolojik acma (anizotropik voksel icin)."""
    er = edt(mask, sampling=sp) > r_mm          # erozyon
    if not er.any():
        return np.zeros_like(mask)
    di = edt(~er, sampling=sp) <= r_mm          # dilatasyon
    return di & mask                             # acma maskeden tasmaz


def ray_volume(ct, rows, org, lm, side, rim_curve=None, plane_shift=0.0,
               bone_hu=160.0, n_ang=360, n_slice=140, step=0.25,
               r_pad=1.30, smooth_ang=9, t0=0.02, t1=0.985,
               return_mask=False, hu_lo=-300.0, medial_frac=0.75, mask_hu=None,
               acma_mm=1.5, alan_tek_yonlu=False, atu_bas_mm=12.0):
    names = ['d', 'mf', 'fmo', 'ek', 'mso', 'o']
    L = np.array([lm[n + '-' + side] for n in names], float)
    R = np.asarray(rim_curve, float) if (rim_curve is not None and len(rim_curve) >= 8) else L
    apex = np.array(lm['apex-' + side], float)
    c, n = fit_plane(R)
    if np.dot(c - apex, n) < 0:
        n = -n
    c = c + plane_shift * n            # altigen duzlemi +1.3 mm one (00 §3)
    axis_len = float(np.dot(c - apex, n))
    e1 = np.cross(n, [0, 0, 1.0]); e1 /= np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    rim_r = np.linalg.norm(np.stack([(R - c) @ e1, (R - c) @ e2], 1), axis=1)
    r_max0 = rim_r.max() * r_pad

    msp = None
    try:
        pr = names
        nm_ = np.mean([lm[b + '-r'] - lm[b + '-l'] for b in pr], axis=0); nm_ /= np.linalg.norm(nm_)
        cm_ = np.mean([(lm[b + '-r'] + lm[b + '-l']) / 2 for b in pr], axis=0)
        sgn = 1.0 if side == 'r' else -1.0
        dmin = min(abs((lm['d-' + side] - cm_) @ nm_), abs((lm['mf-' + side] - cm_) @ nm_))
        msp = (cm_, nm_, sgn, dmin * medial_frac)
    except Exception:
        msp = None

    ang = np.linspace(0, 2 * np.pi, n_ang, endpoint=False)
    dirs = np.outer(np.cos(ang), e1) + np.outer(np.sin(ang), e2)
    ts = np.linspace(t1, t0, n_slice)
    radii = np.zeros((n_slice, n_ang), np.float32)
    nsteps = int(r_max0 / step) + 1
    rr = np.arange(1, nsteps + 1) * step
    for si, t in enumerate(ts):
        ctr = apex + n * (axis_len * t)
        pts = ctr[None, None, :] + dirs[:, None, :] * rr[None, :, None]
        vals = sample(ct, rows, org, pts.reshape(-1, 3)).reshape(n_ang, nsteps)
        solid = (vals >= bone_hu)
        if msp is not None:
            cm_, nm_, sgn, dlim = msp
            dpl = ((pts.reshape(-1, 3) - cm_) @ nm_).reshape(n_ang, nsteps) * sgn
            solid |= (dpl < dlim)
        solid2 = solid[:, :-1] & solid[:, 1:]
        hit = np.argmax(solid2, axis=1); nohit = ~solid2.any(axis=1)
        r = rr[hit]; r[nohit] = np.nan
        if np.isnan(r).any():
            idx = np.arange(n_ang); good = ~np.isnan(r)
            r = np.interp(idx, idx[good], r[good], period=n_ang) if good.sum() >= 8 \
                else np.full(n_ang, np.nanmedian(rim_r) * t)
        if smooth_ang > 1:
            med = ndi.median_filter(r, size=smooth_ang, mode='wrap')
            r = np.minimum(r, med * 1.35 + 1.5)
        radii[si] = np.minimum(r, r_max0)
    radii = ndi.median_filter(radii, size=(5, 1), mode='nearest')
    # --- 0N HACIM DUZELTMESI (2026-11-07): KESIT ALANI DERINLIKLE ARTAMAZ ---
    # Belge `0N-MASKE-KACAGI-HACIM-DUZELTMESI.md` §4, birebir:
    #   "12 mm'den sonra, bir dilimin alani oncekinden buyukse o dilimin butun
    #    yaricaplari sqrt(A[i-1]/A[i]) ile olceklenir. Ilk 12 mm serbest birakilir."
    # Varsayilan KAPALI -> donmus davranis degismez; yalniz acikca istendiginde uygulanir.
    if alan_tek_yonlu:
        _dth = 2 * np.pi / n_ang
        _derinlik = axis_len * (1.0 - ts)          # apertur duzleminden iceri, mm
        _A = 0.5 * np.sin(_dth) * (radii * np.roll(radii, -1, axis=1)).sum(axis=1)
        for _i in range(1, n_slice):
            if _derinlik[_i] <= atu_bas_mm:
                continue
            if _A[_i] > _A[_i - 1] and _A[_i] > 0:
                radii[_i] *= np.sqrt(_A[_i - 1] / _A[_i])
                _A[_i] = _A[_i - 1]
    dth = 2 * np.pi / n_ang
    areas = 0.5 * np.sin(dth) * (radii * np.roll(radii, -1, axis=1)).sum(axis=1)
    dz = axis_len * abs(ts[1] - ts[0])
    out = dict(hacim_cm3=float(areas.sum() * dz) / 1000., eksen_mm=axis_len,
               alanlar=areas, ts=ts, radii=radii, merkez=c, normal=n)
    if not return_mask:
        return out

    corners = np.vstack([R + plane_shift * n, apex[None, :]])
    ij = ras_to_ijk(corners, rows, org)
    sp = np.array([np.linalg.norm(rows[a]) for a in range(3)])
    pad = np.ceil(8.0 / sp).astype(int)
    lo = np.maximum(np.floor(ij.min(0)).astype(int) - pad, 0)
    hi = np.minimum(np.ceil(ij.max(0)).astype(int) + pad + 1, np.array(ct.shape))
    gi = np.arange(lo[0], hi[0]); gj = np.arange(lo[1], hi[1]); gk = np.arange(lo[2], hi[2])
    X = (org[None, None, None, :]
         + gi[:, None, None, None] * rows[0][None, None, None, :]
         + gj[None, :, None, None] * rows[1][None, None, None, :]
         + gk[None, None, :, None] * rows[2][None, None, None, :]).astype(np.float32)
    X *= np.array([-1.0, -1.0, 1.0], np.float32)
    D = X - apex.astype(np.float32)
    tv = (D @ n.astype(np.float32)) / np.float32(axis_len)
    rel = D - tv[..., None] * (n * axis_len).astype(np.float32)
    u = rel @ e1.astype(np.float32); v = rel @ e2.astype(np.float32)
    rv = np.sqrt(u * u + v * v); av = np.mod(np.arctan2(v, u), 2 * np.pi)
    ti = np.clip(((t1 - tv) / (t1 - t0) * (n_slice - 1)), 0, n_slice - 1)
    ai = np.mod(np.round(av / dth).astype(np.int32), n_ang)
    tl = np.floor(ti).astype(np.int32); th_ = np.minimum(tl + 1, n_slice - 1)
    w = (ti - tl).astype(np.float32)
    rlim = radii[tl, ai] * (1 - w) + radii[th_, ai] * w
    koni = (tv >= t0) & (tv <= t1) & (rv <= rlim)
    sub = ct[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]
    mh = bone_hu if mask_hu is None else mask_hu
    mask = koni & (sub > hu_lo) & (sub < mh)
    if msp is not None:
        cm_, nm_, sgn, dlim = msp
        mask &= (((X - cm_) @ nm_) * sgn >= dlim)
    v0 = mask.sum()
    # --- EKSIK OLAN ADIM: 1.5 mm ACMA, SONRA EN BUYUK BILESEN ---
    if acma_mm and acma_mm > 0:
        mask = _open_mm(mask, sp, acma_mm)
    v1 = mask.sum()
    lab_, nl_ = ndi.label(mask)
    if nl_ > 1:
        sizes = ndi.sum(mask, lab_, range(1, nl_ + 1))
        mask = lab_ == (int(np.argmax(sizes)) + 1)
    v2 = mask.sum()
    mask = ndi.binary_fill_holes(mask) & koni
    vox = abs(float(np.linalg.det(rows)))
    full = np.zeros(ct.shape, bool); full[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]] = mask
    out.update(maske=full, maske_hacim_cm3=full.sum() * vox / 1000.,
               adim_cm3=(v0 * vox / 1000., v1 * vox / 1000., v2 * vox / 1000.))
    return out


# ===========================================================================
# KOL B — DAR BOYUNLU LOB TEMIZLIGI  (`0R` SINAV 4, 2026-11-08, BENIMSENDI)
# Tanim `0R` §2'den BIREBIR:
#   "Her taraf icin, her r in {1,5 . 2,0 . 2,5} mm'de: maskeye r yaricapli kure
#    ile ACMA; bilesenleri etiketle; en buyugu kavitedir. Her maske vokseli en
#    yakin bilesene atanir (oklidyen, voksel boyutuyla olcekli). Ana bilesene
#    atanmayan vokselllerin UC YARICAPTAKI BIRLESIMI maskeden cikarilir."
#   "Ayarlanmis parametre yoktur; yaricap kumesi §1'de gerekcelendirildi."
# ===========================================================================
LOB_YARICAPLAR = (1.5, 2.0, 2.5)


def lob_temizle(maske, rows, yaricaplar=LOB_YARICAPLAR):
    M = np.asarray(maske, bool)
    if not M.any():
        return M
    sp = np.array([np.linalg.norm(rows[a]) for a in range(3)])
    cikar = np.zeros_like(M)
    for r in yaricaplar:
        acik = _open_mm(M, sp, r)
        lab_, nl_ = ndi.label(acik)
        if nl_ < 1:
            continue
        sizes = ndi.sum(acik, lab_, range(1, nl_ + 1))
        ana = int(np.argmax(sizes)) + 1
        if nl_ == 1:
            continue                      # tek bilesen -> ayrilan lob yok
        # her maske vokselini EN YAKIN bilesene ata (oklidyen, mm olcekli)
        _, idx = edt(lab_ == 0, sampling=sp, return_indices=True)
        yakin = lab_[tuple(idx)]
        cikar |= M & (yakin != ana)
    return M & ~cikar

# ===========================================================================
# TEK KAYNAK AYAR  (`0P` C1 · skill `tek-kaynak-ayar` · 2026-11-07)
# Kohort maskesi DORT cagri yerinde elle yazilmaz; yalniz buradan uretilir.
# Degerlerin yetkili kaynagi: `00-BASLAMADAN-OKU-calisma-kurallari.md` §5
#   - isin durma esigi ve maskeden cikarilan kemik AYNI degiskendir: 160 HU
#   - hava: <= -300 HU (hu_lo)
#   - 140 kesit x 360 isin, adim 0,25 mm
#   - medial koruma %75 (medial_frac)
#   - 1,5 mm ACMA + en buyuk bilesen + delik doldurma
#   - on sinir: arastirmaci/otomatik EGRI varsa onun duzlemi (plane_shift=0);
#     egri yoksa altigen + 1,41 mm (n=12)
#   - `0N` (2026-11-07): alan_tek_yonlu=True, atu_bas_mm=12.0
# ===========================================================================
KOHORT_MASKE = dict(
    bone_hu=160.0,
    mask_hu=None,          # §5: maskeden cikarilan kemik = durma esigi = bone_hu
    hu_lo=-300.0,
    n_ang=360,
    n_slice=140,
    step=0.25,
    r_pad=1.30,
    smooth_ang=9,
    t0=0.02,
    t1=0.985,
    medial_frac=0.75,
    acma_mm=1.5,
    alan_tek_yonlu=True,   # 0N
    atu_bas_mm=12.0,       # 0N
)
ALTIGEN_KAYDIRMA = 1.41    # mm, n=12 (00 §5; eski +1,39 n=8, +1,3 n=6)


def kohort_maskesi(ct, rows, org, lm, side, rim_curve=None, lob=True):
    """Kohort maskesi — TEK cagri yeri. Ayar KOHORT_MASKE'den gelir.

    rim_curve verilirse on sinir o egrinin kendi duzlemidir (plane_shift=0);
    verilmezse altigen duzlemi +1,41 mm one kaydirilir.
    """
    ayar = dict(KOHORT_MASKE)
    if rim_curve is not None and len(np.asarray(rim_curve)) >= 8:
        ps = 0.0
    else:
        rim_curve = None
        ps = ALTIGEN_KAYDIRMA
    o = ray_volume(ct, rows, org, lm, side, rim_curve=rim_curve,
                   plane_shift=ps, return_mask=True, **ayar)
    if lob:
        v_once = int(o['maske'].sum())
        o['maske'] = lob_temizle(o['maske'], rows)
        o['maske_hacim_cm3'] = hacim_cm3(o['maske'], rows)
        o['lob_voksel'] = v_once - int(o['maske'].sum())
    return o
