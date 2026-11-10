# -*- coding: utf-8 -*-
"""FRANKFORT HORIZONTAL DUZLEMI ve 26-37 KOORDINAT CATISI.

!!! BU DOSYA BIR YENIDEN KURULUMDUR !!!
Ozgun `an/frankfort.py` ve `an/porion.py` 2026-11-10 konteyner sifirlanmasinda
kayboldu; Drive'daki `bellek yetmeyenler` klasorunde de yoklar (arandi).
Burada hicbir esik TAHMIN EDILMEMISTIR; her biri proje belgesinden alinti ve
kaynagi yanina yazilmistir. Belgede sayisi olmayan bir esik BURAYA KONMAMISTIR.

OLCUTLER (`0F` §24: "`00` §0e + 3 yeni" = alti olcut)
  1. po-r ile po-l orta sagital duzlemin KARSIT taraflarinda       [`00` §0e]
  2. iki porionun orta noktasi MSP'ye <= 3 mm                      [`00` §0e;
     esik 3,00 `0F` §24'te hasta11 "sinirda (esik 3,00)" ile teyitli]
  3. bi-porion bandi 97,3 - 114,4 mm                               [`0Z`, ON KAYIT,
     arastirmaci "ONAYLIYORUM" 2026-11-09 15:39; eski 110-150 IPTAL]
  4. her porionun altinda KEMIK olmali                             [`0F` §24 "maks HU R/L";
     yanlis porionlarda 58-75 HU, dogrularda 1298-1757 HU.
     Esik icin ayri bir sayi UYDURULMADI: `00` §0e-4'un kemik kapisi
     kullanilir (maks HU >= 220, 1,5 mm komsuluk; arastirmaci 2026-11-10)]
  5. SOL orbitale Frankfort duzlemine <= 1 mm                      [`00` §0e]
  6. KARSI (sag) orbitale duzleme <= 3 mm                          [`0F` §24;
     ayirt ediciligi olculmus: yanlista 24-30 mm, dogruda 0,55-2,83 mm]

  ⚠ OLCUT 5 UC NOKTALI KURULUMDA BOSA DUSER: duzlem po-r/po-l/o-l'den
  geciyorsa o-l'nin uzakligi yapi geregi 0'dir. `0F` §24'te olgularin yalniz
  BIRININ "alti olcutun hepsini" gecmesi bu okumayla uyusmuyor; hangi olcutun
  dustugu belgede yazili DEGIL. Bu yuzden burada IKI kurulum birden hesaplanir
  ve ALTI SAYININ HEPSI olgu basina kaydedilir:
     kurulum A = uc nokta (po-r, po-l, o-l)   -> `0Y` §6'nin kohort yontemi
     kurulum B = dort nokta en kucuk kareler  -> her iki orbitale uzakligi da
                                                 gercek sayi (teshis)
  HUKUM kurulum A ile verilir (kayitli kohort yontemi). B yalniz teshistir.

MSP TANIMI [`atlas-hasta7-8-9.md`]: "duzlem noktasi = alti apertur ciftinin orta
noktalarinin ortalamasi, normal = sag-sol vektorlerinin ortalamasi".
Apeks cifti DISLANIR (ayni belge: apeks kendi sinandigi duzlemi cekerse
asimetrisini gizler).

26-37 = ALTI rim noktasi x IKI taraf = 12 landmark (apeks HARIC),
RIM_ORDER = (d, mf, mso, fmo, ek, o)  [`rayseg.py`; `08` §C]
"""
import json
import os
import glob
import numpy as np

RAS2LPS = np.array([-1.0, -1.0, 1.0])
RIM_ORDER = ('d', 'mf', 'mso', 'fmo', 'ek', 'o')
CIFTLER = RIM_ORDER                      # MSP icin kullanilan alti cift

# --- on kayitli esikler (hicbiri tahmin degil; kaynaklar belge dizesinde) ---
ESIK_ORTA_MSP = 3.0        # mm   olcut 2  (`0F` SS24)
# `0AV` SS4: dis kaynak +3SS sinirini 3,21-3,59 mm'de veriyor ve bu aralik
# denek92 (3,320) ile denek95 (3,537) uzerine dusuyor. `00` SS0.12 geregi
# aralikten secim YAPILMADI; esik 3,00'de BIRAKILDI. Yapisal bulgu `0AV` SS4.1.
# olcut 3 bandi: `0AV` (2026-11-10) -- `0Z`'nin 97,3-114,4 bandi IPTAL.
#   merkez       105.85 mm  : `0Z` SS2 ogrenme seti n=8 + ASO altin standardi
#   yari-genislik 3 x 5.313 : Howells AUB populasyon ici havuzlanmis SS
#                             (howell.csv, n=2524, 30 populasyon, sd=2494)
#   UYARI: AUB'nin isaret noktasi ra'dir, po DEGIL. Howells'tan alinan
#   olcumun kendisi degil, DEGISKENLIGIDIR. Vekil degisken varsayimi
#   `0AV` SS3.3'te yazili ve teze sinirlilik olarak girecek.
BIPORION_MERKEZ = 105.85   # mm
BIPORION_DIS_SS = 5.313    # mm   Howells AUB, populasyon ici havuzlanmis
BIPORION_ALT = BIPORION_MERKEZ - 3.0 * BIPORION_DIS_SS   # 89.911 mm
BIPORION_UST = BIPORION_MERKEZ + 3.0 * BIPORION_DIS_SS   # 121.789 mm
ESIK_SOL_ORB = 1.0         # mm   olcut 5
ESIK_KARSI_ORB = 3.0       # mm   olcut 6


def _lps2ras(P):
    return np.asarray(P, float) * RAS2LPS


def oku_porion(yol):
    """ALI_CBCT `*_lm_Pred_*.mrk.json` -> {'RPo': RAS, 'LPo': RAS}."""
    j = json.load(open(yol, encoding='utf-8'))
    out = {}
    for m in j.get('markups', []):
        cs = str(m.get('coordinateSystem', 'LPS')).upper()
        for cp in m.get('controlPoints', []):
            p = np.asarray(cp['position'], float)
            out[cp['label']] = _lps2ras(p) if cs.startswith('LPS') else p
    return out


def oku_oto(paket):
    """Paketteki OTO_*.mrk.json dosyalari -> {'d-r': RAS, ...} (14 nokta)."""
    out = {}
    for f in sorted(glob.glob(os.path.join(paket, 'OTO_*.mrk.json'))):
        j = json.load(open(f, encoding='utf-8'))
        for m in j.get('markups', []):
            cs = str(m.get('coordinateSystem', 'LPS')).upper()
            if str(m.get('type', '')) != 'Fiducial':
                continue
            for cp in m.get('controlPoints', []):
                p = np.asarray(cp['position'], float)
                out[cp['label']] = _lps2ras(p) if cs.startswith('LPS') else p
    return out


def msp(lm):
    """Orta sagital duzlem: (nokta, normal). Alti rim cifti; apeks DISLANIR."""
    orta, vek = [], []
    for k in CIFTLER:
        a, b = lm.get(k + '-r'), lm.get(k + '-l')
        if a is None or b is None:
            continue
        orta.append((a + b) / 2.0)
        vek.append(a - b)
    if len(orta) < 3:
        raise ValueError('MSP icin yeterli cift yok: %d' % len(orta))
    c = np.mean(orta, axis=0)
    n = np.mean(vek, axis=0)
    return c, n / np.linalg.norm(n), len(orta)


def _duzlem_3n(a, b, c):
    """Uc noktadan duzlem: (nokta, birim normal)."""
    n = np.cross(b - a, c - a)
    nn = np.linalg.norm(n)
    if nn < 1e-9:
        raise ValueError('uc nokta dogrusal')
    return a.copy(), n / nn


def _duzlem_ek(P):
    """Dort+ noktadan en kucuk kareler duzlemi (SVD)."""
    P = np.atleast_2d(P)
    c = P.mean(axis=0)
    u, s, vt = np.linalg.svd(P - c)
    return c, vt[2] / np.linalg.norm(vt[2])


def _uzaklik(p, duzlem):
    c, n = duzlem
    return float(abs((p - c) @ n))


def olcutler(po, lm, kemik_maks=None):
    """Alti olcutun SAYISAL degerleri + iki kurulumun hukmu.

    po: {'RPo','LPo'} RAS · lm: OTO landmarklar RAS
    kemik_maks: {'RPo': maks_HU, 'LPo': maks_HU} ya da None (olcut 4 atlanir)
    """
    R, L = po['RPo'], po['LPo']
    o_r, o_l = lm['o-r'], lm['o-l']
    cm, nm, ncift = msp(lm)

    # olcut 1 — karsit taraflar
    sR = float((R - cm) @ nm)
    sL = float((L - cm) @ nm)
    o1 = (sR * sL) < 0

    # olcut 2 — porion orta noktasi MSP'ye uzaklik
    d_orta = float(abs(((R + L) / 2.0 - cm) @ nm))
    o2 = d_orta <= ESIK_ORTA_MSP

    # olcut 3 — bi-porion bandi
    bipo = float(np.linalg.norm(R - L))
    o3 = BIPORION_ALT <= bipo <= BIPORION_UST

    # olcut 4 — porion altinda kemik
    if kemik_maks is None:
        o4, hu = None, {}
    else:
        hu = {k: float(v) for k, v in kemik_maks.items()}
        o4 = all(v >= 220.0 for v in hu.values())

    # KURULUM A — uc nokta (po-r, po-l, o-l):  `0Y` §6 kohort yontemi
    A = _duzlem_3n(R, L, o_l)
    A_sol = _uzaklik(o_l, A)          # yapi geregi ~0
    A_karsi = _uzaklik(o_r, A)

    # KURULUM B — dort nokta en kucuk kareler (TESHIS)
    B = _duzlem_ek(np.vstack([R, L, o_r, o_l]))
    B_sol = _uzaklik(o_l, B)
    B_karsi = _uzaklik(o_r, B)

    o5_A = A_sol <= ESIK_SOL_ORB
    o6_A = A_karsi <= ESIK_KARSI_ORB

    gecer = [o1, o2, o3, o5_A, o6_A]
    if o4 is not None:
        gecer.append(o4)

    return {
        'olcut1_karsit_taraf': bool(o1),
        'olcut1_isaretli_uzaklik': {'RPo': sR, 'LPo': sL},
        'olcut2_orta_MSP_mm': d_orta,
        'olcut2_gecer': bool(o2),
        'olcut3_biporion_mm': bipo,
        'olcut3_gecer': bool(o3),
        'olcut4_maks_HU': hu,
        'olcut4_gecer': (None if o4 is None else bool(o4)),
        'olcut5_sol_orbitale_mm_A': A_sol,
        'olcut5_gecer_A': bool(o5_A),
        'olcut6_karsi_orbitale_mm_A': A_karsi,
        'olcut6_gecer_A': bool(o6_A),
        'teshis_B_sol_orbitale_mm': B_sol,
        'teshis_B_karsi_orbitale_mm': B_karsi,
        'msp_cift_sayisi': ncift,
        'hukum_A': bool(all(gecer)),
        'gecen_olcut_sayisi': int(sum(1 for g in gecer if g)),
        'olculen_olcut_sayisi': int(len(gecer)),
    }


def cerceve(po, lm):
    """Frankfort cercevesi: (R, t) oyle ki  p' = R @ (p - t).

    z = duzlem normali, SUPERIOR'a bakar (mso - o ortalamasi ile isaretlenir)
    y = (orbitale ortasi - porion ortasi)'nin z'ye dik bileseni -> ANTERIOR
    x = y x z, saga bakar (sag-sol landmark ortalamasi ile isaretlenir)
    t = iki porionun orta noktasi
    Saglik denetimi: det(R) = +1 ve butun ikili uzakliklar korunur.
    """
    R_, L_ = po['RPo'], po['LPo']
    o_r, o_l = lm['o-r'], lm['o-l']
    _, n = _duzlem_3n(R_, L_, o_l)          # KURULUM A

    yukari = np.mean([lm['mso-r'] - lm['o-r'], lm['mso-l'] - lm['o-l']], axis=0)
    z = n if (n @ yukari) > 0 else -n

    ileri = (o_r + o_l) / 2.0 - (R_ + L_) / 2.0
    y = ileri - (ileri @ z) * z
    y /= np.linalg.norm(y)

    x = np.cross(y, z)
    x /= np.linalg.norm(x)
    saga = np.mean([lm[k + '-r'] - lm[k + '-l'] for k in RIM_ORDER
                    if (k + '-r') in lm and (k + '-l') in lm], axis=0)
    if (x @ saga) < 0:
        x, y = -x, -y                        # sag el sistemini KORU (det=+1)

    Rmat = np.vstack([x, y, z])
    t = (R_ + L_) / 2.0
    return Rmat, t


def uygula(Rmat, t, lm):
    return {k: (Rmat @ (v - t)) for k, v in lm.items()}


def rijitlik(lm, lm2):
    """Donusum oncesi/sonrasi butun ikili uzakliklarin en buyuk farki (mm)."""
    ad = sorted(set(lm) & set(lm2))
    P = np.array([lm[k] for k in ad])
    Q = np.array([lm2[k] for k in ad])
    def ikili(M):
        return np.linalg.norm(M[:, None, :] - M[None, :, :], axis=2)
    return float(np.abs(ikili(P) - ikili(Q)).max())
