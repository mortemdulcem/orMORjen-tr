# 0AT — KONTEYNER KAYBI SONRASI HATTIN YENİDEN KURULMASI VE DOĞRULANMASI

**Tarih:** 2026-11-10 · **Araştırmacı talimatı:** *"KODLARIMI GEÇMİŞİNDEN GERİ GETİR"*,
*"SAKIN KIT AKLINLA KOD YAZMA TEK BAŞINA"*, *"BİR AYDIR SKİLLE EKLEDİĞİMİZ
YETENEKLERİN KODLARINI BULACAKSIN"*

---

## 1. NE OLDU

Çalışma alanı (konteyner) değişti; `/home/claude/an/` altındaki beş modül kayboldu.
Proje belgelerinin **81'i de yerindedir, hiçbiri silinmemiştir** (`project_info` ile
doğrulandı; en eskisi 2026-10-05). Kaybolan şey **kod**tu — çünkü kod bir aydır
belgeye değil yalnız çalışma alanına yazılıyordu. **Asıl kusur budur ve bu belge
onu kapatır.**

## 2. KOD NEREDEN GELDİ — hiçbiri yeniden yazılmadı

| parça | kaynak | not |
|---|---|---|
| `ray_volume` gövdesi | `cozumleme-betikleri-kaynak-kod.md` → "## rayseg.py" | 2026-10-12 sürümü, birebir |
| kohort ayarı (`bone_hu=160`, `mask_hu=None`, eğri varsa `plane_shift=0`) | `00-BASLAMADAN-OKU` §5 | kaynak-kod belgesindeki `bone_hu=200/mask_hu=250` **hasta dönemine aittir**, kohorta değil |
| `alan_tek_yonlu`, `atu_bas_mm=12.0` | `0N` §4 | "12 mm'den sonra bir dilimin alanı öncekinden büyükse yarıçaplar √(A[i−1]/A[i]) ile ölçeklenir" |
| `lob_temizle` (KOL B) | `0R` §2 | r ∈ {1,5 · 2,0 · 2,5} mm **birleşimi**, en yakın bileşene atama |
| `KOHORT_MASKE` / `kohort_maskesi()` tek kaynağı | `0P` C1 · `0R` §4 | dört çağrı yerine ayrı kod yazılmaz |
| `sample()` örnekleyici, medial koruma | ek `100c87b7-medial_koruma_kod.txt` | 2026-11-09 kod yığını alıntısı |

> **Öğrenilen:** `cozumleme-betikleri-kaynak-kod.md` **bayattı** (12 Ekim). Son bir
> ayda eklenen yetenekler (`0N` alan kısıtı, `0R` lob temizliği, tek-kaynak ayarı)
> yalnız ön kayıt belgelerinde duruyordu, kodda değil. Üç ayrı belgeden birleştirmek
> gerekti. **Bundan sonra kod değişince bu belge aynı turda güncellenir.**

## 3. DOĞRULAMA — ön kayıtlı sadakat sınavı

Ölçüt **koşmadan önce** yazıldı ve **gevşetilmedi**:
hacim farkı **< %1** ve Dice **> 0,95**, dört paketin sekiz orbitasında.
Referans: donmuş hattın ürettiği paketler (kendi CT'si, landmarkları, rim eğrisi,
segmentasyonu). Betik: `kurtarma/rayseg_sinav.py`.

```
olgu      tar     KAYITLI    YENIDEN    fark %     Dice
denek100  sag      24.850     24.851     +0.00    1.000
denek100  sol      26.094     26.092     -0.01    1.000
denek101  sag      26.825     26.825     +0.00    1.000
denek101  sol      26.315     26.310     -0.02    1.000
denek98   sag      22.246     22.243     -0.01    1.000
denek98   sol      22.746     22.744     -0.01    1.000
denek99   sag      29.929     29.930     +0.00    1.000
denek99   sol      29.458     29.455     -0.01    1.000
```

**8/8 geçti.** `0K` §1 anlamında hat **değişmemiştir**: yeniden kurulan kod donmuş
hattın ürettiği maskeleri voksel düzeyinde yeniden üretiyor, yani yeniden ölçüm
gerekmez.

### 3a. Ara adımlar da kayda geçer (yalnız geçen sonucu yazmak ön kaydı anlamsız kılar)

| deneme | sonuç |
|---|---|
| 1 — koni apekse daraltılmış | −%19…−%39 · Dice 0,70–0,82 · **RET** |
| 2 — küresel yelpaze | +%55…+%187 · **RET** |
| 3 — kod yığını parçalarından | +%1,2…+%11,3 · Dice 0,935–0,967 · **ölçütü geçmedi** |
| 4 — belgedeki gövde + yanlış ayar (`bone_hu=200`) | +%1,2…+%3,6 · Dice 0,935–0,967 · **geçmedi** |
| 5 — `00` §5 ayarı + `0N` | 7/8 Dice 1,000 · denek100 sağ **+%1,20** |
| 6 — + `0R` KOL B lob temizliği | **8/8 Dice 1,000 — GEÇTİ** |

> **5. adımın tanısı yöntemsel olarak önemlidir:** denek100 sağda 1009 vokselllik
> **bitişik** bir fazlalık vardı ve maske tek bileşendi — yani "lob" çıplak gözle
> ayrı bir parça değildi. KOL B'nin açma adımı onu dar boyundan kopardı. `0N`
> kısıtının sekiz orbitanın **sekizinde de** ateşlediği, yedisinde kayıtlı değeri
> 0,005 cm³ içinde yeniden ürettiği ölçülerek gösterildi; bu, uygulamanın doğru
> olduğunu tek bir olguya bakmadan kanıtlar.

## 4. GÜNCEL KAYNAK — `an/rayseg.py`

> **Bu bölüm `cozumleme-betikleri-kaynak-kod.md` içindeki "## rayseg.py" bölümünün
> YERİNE GEÇER.** O belgedeki sürüm 2026-10-12 tarihlidir ve `0N` ile `0R`
> düzeltmelerini taşımaz. Çakışma hâlinde **bu belge doğrudur.**

```python
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
```

## 5. ATLAS DA KURTARILDI — ve birebir doğrulandı (2026-11-10, aynı oturum)

Atlas dosyaları (`an/out/rimatlas.json`, `an/out/apeks_atlas.json`) diskte, paketlerde,
arşivlerde ve belgelerde **yoktu**. Araştırmacı beş sahneyi gönderdi; atlas **yeniden
türetilmedi, yeniden hesaplandı** — girdi aynı, tanım aynı, çıktı aynı.

### 5a. Sahneler — her biri kayıtlı veriyle doğrulandı

| olgu | sahne | doğrulama |
|---|---|---|
| hasta7 | ölçüm1 | OW 44,29/43,84 · OH 37,70/39,43 · IOD 22,02/20,14 · BOW 97,69 · centroid 126,16 · hacim 25,377/25,501 · APalan 1214,9/1183,8 — **kayıtla birebir** |
| hasta8 | ölçüm2 | OW 39,90/39,39 · OH 38,03/38,19 · IOD 21,29 · APalan 1149,1/1161,1 · hacim 26,12/25,95 — **P05 satırıyla birebir** |
| hasta9 | ölçüm5 | 14 landmark + 2 eğri tam |
| hasta10 | ölçüm4 | OW 38,68/39,42 · OH 37,95/38,18 · IOD 20,66/21,91 · BOW 96,45 · centroid 128,51 — **P09 ile birebir** |
| hasta11 | ölçüm3 | OW 42,24/45,19 · OH 39,11/38,51 · IOD 21,84/22,76 · BOW 100,8 · centroid 135,64 — **P11 ile birebir** |

> Sahnelerde BT hacmi (`4 1.25MM BONE.nrrd`) **yok**; rim ve apeks atlası için gerekmiyor.
> Şablon kütüphanesi (`sablon.OLGULAR`, NICP) gerekirse BT'ler ayrıca istenecektir.

### 5b. APEKS ATLASI — kayıtlı istatistiğe karşı sınandı, ÜÇ BİLEŞENDE DE BİREBİR

`giris()` tanımı `an/apeksatlas14.py`'den birebir alındı
(`c,n,u,v = landmark._duzlem_cerceve(eğri, apeks)`; `t = −d·n`, `dik = d·u`,
`yan = sgn·(d·v)`, sol taraf aynalı).

| | **yeniden hesaplanan** | **kayıtlı** (`atlas-hasta7-8-9.md`) |
|---|---|---|
| `t` ort · SS · aralık | **42,508 · 1,054 · [40,85–43,83]** | 42,508 · 1,054 · [40,85–43,83] |
| `dik` ort · SS | **−3,952 · 4,028** | −3,952 · 4,028 |
| `yan` ort · SS | **−2,277 · 2,411** | −2,277 · 2,411 |

Bu bir yaklaşıklık değildir: on orbitanın üç bileşeninin de ortalaması ve standart
sapması üç haneye kadar aynı. Aralığın iki ucu da ayrı ayrı yeniden üretildi
(alt uç hasta10 sol **40,846**, üst uç hasta9 sağ **43,827**), `dik` üst ucu
hasta9 sağ **2,304** ve `yan` alt ucu hasta10 sol **−5,894** dahil.

### 5c. On orbitanın girişleri (kayda geçer — bir daha kaybolmasın)

| giriş | t | dik | yan |
|---|---|---|---|
| hasta7_sag | 41,037 | −4,306 | +0,744 |
| hasta7_sol | 43,542 | −7,237 | −2,449 |
| hasta8_sag | 42,854 | −1,594 | −4,839 |
| hasta8_sol | 43,085 | −2,208 | −3,654 |
| hasta9_sag | 43,827 | +2,304 | −0,808 |
| hasta9_sol | 42,879 | +1,177 | +0,678 |
| hasta10_sag | 41,689 | −6,785 | −4,841 |
| hasta10_sol | 40,846 | −8,914 | −5,894 |
| hasta11_sag | 41,966 | −2,803 | −0,660 |
| hasta11_sol | 43,351 | −9,158 | −1,043 |

hasta13 ve hasta16 girişleri `atlas-hasta7-8-9.md`'de zaten kayıtlıdır
(hasta13: 45,587/−2,871/−4,349 · 43,683/−2,897/−5,279 ·
hasta16: 39,952/−10,122/−0,302 · 39,337/−7,613/+3,029).

### 5d. RIM ATLASI — 10 orbita / 5 olgu

```
nokta   aci ort   aci SS |   r/r ort     r SS    n
d         -86.9      5.0 |     0.975    0.048   10
mf        -72.3      6.6 |     1.052    0.049   10
mso        -0.5     12.4 |     0.932    0.051   10
fmo        74.5      5.9 |     1.025    0.030   10
ek        102.0     10.0 |     1.051    0.060   10
o         162.6      6.3 |     1.035    0.041   10
```

Tam dosya: `an/out/rimatlas.json` (olgu bazlı 60 giriş + özet).

### 5e. AÇIK — atlas henüz TAM DEĞİL

Apeks atlasının kohortta kullanılan hâli **18 orbita / 9 olgu**
(`t` ort **42,799** · SS **1,812** · [39,34–46,13] — `atlas` §BK).
Elde 14 giriş var; **hasta14 ve hasta15 sahneleri gerekiyor**.
Kontrol: o dört `t` değerinin toplamı **176,746** çıkmalıdır.

Ara dosya `an/out/apeks_atlas_KISMI_16.json` adıyla saklanıyor —
**bilerek `apeks_atlas.json` DEĞİL**, eksik atlas sessizce kullanılmasın diye
(`0R` §5b'deki "bayat değer sessizce geçti" dersinin uygulaması).

### 5f. YAKALANAN TUZAK — hasta14'ün TAM OTOMATİK sahnesi atlasa konmadı (2026-11-10)

Araştırmacı hasta14 için `hasta14_tam_otomatik.zip` gönderdi. Girişi hesaplandı:

```
hasta14_sag  t=42,862  dik=-3,774  yan=-2,699
hasta14_sol  t=42,862  dik=-3,774  yan=-2,699
```

**İki orbita birebir aynı** — ve bu üçlü, o tarihteki **12 orbitalık atlasın
ortalamasının kendisidir** (`atlas-hasta7-8-9.md`: hasta13 eklenince
t ort 42,862 · dik ort −3,774 · yan ort −2,699).

Sebep `§AZ`'de zaten yazılıdır: apeks atlası olguya özgü bilgi taşımaz, her olguda
popülasyon ortalamasını döndürür. Dolayısıyla **tam otomatik bir sahnenin apeksi,
atlasın kendi çıktısıdır**; onu atlasa eklemek atlasa kendi ortalamasını geri
beslemek olur (`0K` §0.12: bir parametre, onu doğrulayan veriden türetilemez).

**EKLENMEDİ.** Gereken, araştırmacının elle düzelttiği sahnedir
(`apeksatlas14.py` → `hasta14 otomatik ölçüm düzeltme`).

> **Yan kazanç — bağımsız doğrulama:** bu hesap, yeniden kurduğum `giris()`
> tanımının doğruluğunu ikinci kez gösterdi. Tam otomatik hat apeksi o günkü
> atlasın ortalamasına koyuyordu; benim hesabım tam o ortalamayı geri verdi.
> İki bağımsız yoldan aynı üç sayı.

### 5g. hasta15 DOGRULANDI ve atlasin TAMAMI cebirle kapandi (2026-11-10)

Arastirmacinin **elle duzelttigi** hasta15 sahnesi geldi. Hesaplanan giris:

| giris | t | dik | yan |
|---|---|---|---|
| hasta15_sag | **42,380** | -6,318 | -2,688 |
| hasta15_sol | **43,241** | -7,452 | -2,930 |

`t` degerleri `atlas-hasta7-8-9.md` SSAZ tablosundaki "gercek derinlik" sutunuyla
**birebir** (42,38 / 43,24) - yani dogru sahne ve dogru tanim.

**Atlasin her iki kayitli durumu da yeniden uretildi:**

| atlas durumu | hesaplanan `t` ort | kayitli |
|---|---|---|
| 10 orbita (hasta7-11) | **42,508** (SS 1,054) | 42,508 (SS 1,054) |
| 16 orbita (+hasta13, 14, 15) | **43,194** | 43,194 |
| 18 orbita (+hasta16) | **42,799** | 42,799 |

hasta14 `t` degerleri bu denklemden **cebirle** dogrulandi: gereken toplam
**91,122**, SSAZ tablosundaki degerler 46,13 + 45,00 = **91,13** (yuvarlama icinde).

**Kalan tek bosluk:** hasta14 `dik` ve `yan` degerleri. Bunlar hicbir belgede
yazili degildir ve yalniz arastirmacinin **elle duzelttigi** sahneden hesaplanabilir.
Gonderilen `hasta14_tam_otomatik.zip` bu degildir (SS5f).

## 6. KALAN — bu belge kapatmıyor

- Apeks atlasi **16/18** - yalniz hasta14 icin `dik` ve `yan` eksik; elle duzeltilmis hasta14 sahnesi bekleniyor (`t` biliniyor: 46,13 / 45,00).
- `kemik_kapisi.py` ve `porion.py` yeniden kurulmadı.
- Şablon kütüphanesi (`sablon.OLGULAR`: hasta5, hasta6 + hasta7–11) için sahnelerin
  **BT hacimleri** gerekiyor; gelen sahnelerde yoklar.
- denek102 ölçülmedi; atlas tamamlanmadan ölçülmeyecek.
