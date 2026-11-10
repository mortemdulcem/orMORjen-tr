# -*- coding: utf-8 -*-
"""MEDIAL LANDMARK KESTIRICISI — `d` ve `mf` icin sablon hizalamasi (NICP).

NEDEN: `d` ve `mf` hattin en zayif yeri. Mevcut atlas (benzerlik donusumuyle
oturtulan ortalama sekil) d/mf'de LOO ort **3,44 mm**, en kotu **6,71 mm** veriyor;
hasta13'te IOD band disina cikti (29,57/31,13 vs elle seri 18,53-22,76).

YONTEM
 1. ON HIZALAMA — Procrustes, ama YALNIZ 12 MEDIAL-OLMAYAN nokta ile
    (mso, fmo, ek, o, apex). `d` ve `mf` KASITLI OLARAK DISARIDA: hedefin d/mf'sini
    hizalamada kullanmak, cevabi cevabi bulmak icin kullanmak olur.
 2. NICP — sablon kemik yuzeyi hedef yuzeye esnek oturtulur (an/nicp.py).
 3. AKTARIM — sablonun elle isaretli d/mf'si deforme uzaya tasinir.
 4. COK SABLON — her sablondan bir kestirim; sonuc MEDYAN, yayilim ise
    BELIRSIZLIK olcusudur. Tek sablon o kisinin kendine ozguluunu tasir.

Yayilim neden onemli: hasta13'te medial noktalar BIRLIKTE dısa kaydigi icin MSP
uyumu serinin en iyisi cikti ve kapi sessiz kaldi. Sablonlar arasi yayilim,
MSP'den bagimsiz bir uyari verir.
"""
import sys
sys.path.insert(0, '/home/claude/an')
import numpy as np
import nicp as N
import alpaca as AL

HEDEF_NOKTA = ('d-r', 'd-l', 'mf-r', 'mf-l')
# hizalamada kullanilan 12 nokta — d ve mf YOK
HIZA_NOKTA = ('mso-r', 'mso-l', 'fmo-r', 'fmo-l', 'ek-r', 'ek-l',
              'o-r', 'o-l', 'apex-r', 'apex-l')
ALPHA = (200.0, 80.0, 30.0, 10.0, 3.0)


def procrustes(A, B):
    """A -> B benzerlik donusumu (olcek + donme + oteleme). Donus: (s, R, t)."""
    A = np.asarray(A, float); B = np.asarray(B, float)
    ca, cb = A.mean(0), B.mean(0)
    A0, B0 = A - ca, B - cb
    U, S, Vt = np.linalg.svd(A0.T @ B0)
    R = U @ Vt
    if np.linalg.det(R) < 0:
        Vt = Vt.copy(); Vt[-1] *= -1; R = U @ Vt
    s = S.sum() / (A0 ** 2).sum()
    return s, R, cb - s * (ca @ R)


def _uygula(P, s, R, t):
    return s * (np.asarray(P, float) @ R) + t


def kestir_tek(sablon, hedef_v, hedef_lm_hiza, alphalar=ALPHA, ic_tur=2,
               ayrinti=False):
    """Bir sablondan d/mf kestirimi.

    sablon        : sablon.yukle() cikti sozlugu (v, f, lm)
    hedef_v       : hedef kemik yuzeyi tepe noktalari (RAS)
    hedef_lm_hiza : hedefin 12 medial-olmayan noktasi {ad: (3,)} — elle ya da
                    hattin kestirimi; d/mf ICERMEZ ve kullanilmaz
    """
    ad = [k for k in HIZA_NOKTA if k in hedef_lm_hiza and k in sablon['lm']]
    if len(ad) < 6:
        return None, {'hata': 'hizalama icin yeterli nokta yok (%d)' % len(ad)}
    A = np.array([sablon['lm'][k] for k in ad])
    B = np.array([hedef_lm_hiza[k] for k in ad])
    s, R, t = procrustes(A, B)
    Vs = _uygula(sablon['v'], s, R, t)
    Ls = {k: _uygula(v, s, R, t) for k, v in sablon['lm'].items()}
    TV, X = N.nicp(Vs, sablon['f'], hedef_v, alphalar=alphalar, ic_tur=ic_tur,
                   ayrinti=ayrinti)
    out = {k: N.nokta_aktar(Ls[k], Vs, X) for k in HEDEF_NOKTA}
    bilgi = {'hizalama_noktasi': len(ad), 'olcek': round(float(s), 4),
             'yuzey_kaymasi_mm': round(float(np.linalg.norm(TV - Vs, axis=1).mean()), 3),
             'kati_oncesi_hata_mm': round(float(np.linalg.norm(
                 np.array([Ls[k] for k in ad]) - B, axis=1).mean()), 2)}
    return out, bilgi


def kestir(hedef_v, hedef_lm_hiza, kutuphane, alphalar=ALPHA, ic_tur=2,
           ayrinti=False):
    """Butun sablonlardan kestirip MEDYAN ve YAYILIM dondurur."""
    tek, bilgiler = {k: [] for k in HEDEF_NOKTA}, {}
    for s in kutuphane:
        o, b = kestir_tek(s, hedef_v, hedef_lm_hiza, alphalar, ic_tur)
        bilgiler[s['ad']] = b
        if o is None:
            continue
        for k in HEDEF_NOKTA:
            tek[k].append(o[k])
        if ayrinti:
            print('     %-8s olcek %.3f  yuzey kaymasi %.2f mm'
                  % (s['ad'], b['olcek'], b['yuzey_kaymasi_mm']))
    son, yay, koord = {}, {}, {}
    for k in HEDEF_NOKTA:
        if not tek[k]:
            son[k], yay[k], koord[k] = None, None, None; continue
        P = np.array(tek[k])
        # 2026-10-26: BIRLESTIRICI = ALPACA/MALPACA'nin GEOMETRIK MEDYANI
        # (Weiszfeld), koordinat-bazli `np.median` DEGIL. Kaynak: SlicerMorph
        # ALPACA.calculateGeometricMedian, BSD-2 (an/alpaca.py; KAYNAKCA B5/B6).
        # On-kayitli sinav n=28 d/mf degerinde GECTI (`07` §AX-2):
        #   ort 2,798 -> 2,718 mm · en kotu 5,122 -> 5,016 · iyilesen 18 / kotulesen 10.
        # Koordinat medyani yalniz KARSILASTIRMA icin hesaplanmaya devam eder.
        med = AL.geometrik_medyan(P)
        son[k] = med
        # yayilim = birlestirilmis noktaya ortalama uzaklik (belirsizlik olcusu)
        yay[k] = float(np.linalg.norm(P - med[None, :], axis=1).mean())
        koord[k] = np.median(P, axis=0)
    return son, dict(yayilim={k: (None if v is None else round(v, 2))
                              for k, v in yay.items()},
                     birlestirici='geometrik medyan (ALPACA, Weiszfeld)',
                     koord_medyan={k: ([round(float(x), 4) for x in v]
                                       if v is not None else None)
                                   for k, v in koord.items()},
                     sablon_sayisi=len(tek[HEDEF_NOKTA[0]]),
                     tek_kestirimler={k: [[round(float(x), 4) for x in p]
                                          for p in tek[k]] for k in HEDEF_NOKTA},
                     sablon_bilgi=bilgiler)
