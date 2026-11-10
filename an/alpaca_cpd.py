# -*- coding: utf-8 -*-
"""ALPACA'NIN DEFORMABLE ADIMI (CPD) — bizim NICP adimimizin yerine konan kol.

KAYNAK: SlicerMorph, ALPACA modulu (ALPACA/ALPACA.py), BSD 2-Clause License,
        Copyright (c) 2019 SlicerMorph Project.
        https://github.com/SlicerMorph/SlicerMorph  (klon: 2026-10-26)
Uyarlanan islevler ve satirlari:
  ALPACA.runCPDRegistration   (ALPACA.py:1627-1668)
  ALPACA.cpd_registration     (ALPACA.py:2881-2903)
  ALPACA.runSubsample         (ALPACA.py:2744-2834) — yalniz voksel-izgara
                               seyreltme ve voxel_size tanimi
Yayin: Porto A, Rolfe SM, Maga AM. ALPACA. Methods Ecol Evol. 2021;12:2129-2144.
       (KAYNAKCA B5)

ALPACA'NIN KENDI VARSAYILANLARI — Resources/UI/ALPACA.ui'den okundu:
  pointDensity 1,0  ->  voxel_size = hedef kutu kosegeni / (55 * 1,0)
  alpha (rijitlik) 2,0 · beta (hareket uyumu) 2,0
  CPDIterations 100 · CPDTolerance 0,001 · low_rank True
  projectionFactor 0,02  (kod bunu 100'e boluyor: ALPACA.py:714, 975)

NE AYNI, NE FARKLI — bizim hatta gore:
  AYNI TUTULAN : on hizalama (Procrustes, yalniz 12 medial-olmayan nokta),
                 sablon kutuphanesi (7 olgu), cok-sablon birlestirme.
  DEGISEN      : deformable model. Bizde NICP (an/nicp.py, alpha 200->3);
                 bu kolda ALPACA'nin CPD'si (cpdalp, low_rank).
  BILEREK ALINMAYAN : ALPACA'nin FPFH + RANSAC + ICP kuresel baslatmasi.
                 O adim HEDEFTE LANDMARK GEREKTIRMEZ; bizim hattimizda hedefin
                 12 noktasi zaten var ve Procrustes onu kullaniyor. Iki farki
                 ayni kosuda degistirmek, hangisinin etki ettigini olcemez
                 kilardi (`00` §0.12). Kuresel baslatma AYRI bir kol olarak
                 sinanmalidir.

ALPACA'nin olcekleme adiminda bir ayrinti var ve BIREBIR korundu: normalleme
EKSEN BASINA yapiliyor (`cloudSize` bir 3-vektor, ALPACA.py:1631-1634), yani
donusum anizotropiktir. Bu bizim tercihimiz degil, ALPACA'nin kodudur; kolun
"ALPACA" olmasi icin degistirilmedi.
"""
import sys
sys.path.insert(0, '/home/claude/an')
import numpy as np
import medial as M

ALPHA_CPD = 2.0        # ALPACA varsayilani: rijitlik
BETA_CPD = 2.0         # ALPACA varsayilani: hareket uyumu (Gauss genisligi)
ITER = 100
TOL = 1e-3
BOLEN = 55.0           # voxel_size = kosegen / (55 * pointDensity)
OLCEK_HEDEF = 25.0     # ALPACA hedef bulutu 25 birime normalliyor


def kosegen(V):
    V = np.asarray(V, float)
    return float(np.linalg.norm(V.max(axis=0) - V.min(axis=0)))


def voksel_seyrelt(V, leaf):
    """vtkVoxelGrid'in SetConfigurationStyleToLeafSize esdegeri (saf numpy).

    vtkVoxelGrid her dolu kutuda TEK temsilci nokta birakir; varsayilan
    cikti kipi kutudaki noktalarin ORTALAMASIDIR. Burada da ortalama alinir.
    """
    V = np.asarray(V, float)
    if leaf <= 0:
        return V
    ix = np.floor((V - V.min(axis=0)) / leaf).astype(np.int64)
    _, ilk, ters = np.unique(ix, axis=0, return_index=True, return_inverse=True)
    n = ilk.size
    top = np.zeros((n, 3)); say = np.zeros(n)
    np.add.at(top, ters, V)
    np.add.at(say, ters, 1.0)
    return top / say[:, None]


def cpd_aktar(kaynak_v, kaynak_lm, hedef_v, alpha=ALPHA_CPD, beta=BETA_CPD,
              yineleme=ITER, tolerans=TOL, leaf=None, ayrinti=False):
    """ALPACA.runCPDRegistration'in birebir karsiligi.

    kaynak_v : (on hizalamadan GECMIS) sablon yuzeyi tepe noktalari
    kaynak_lm: (n,3) tasinacak landmarklar — ayni uzayda
    hedef_v  : hedef yuzeyi tepe noktalari
    Donus    : (n,3) kestirilen landmarklar, bilgi sozlugu
    """
    from cpdalp import DeformableRegistration

    hedef_v = np.asarray(hedef_v, float)
    kaynak_v = np.asarray(kaynak_v, float)
    kaynak_lm = np.asarray(kaynak_lm, float).reshape(-1, 3)

    if leaf is None:
        leaf = kosegen(hedef_v) / BOLEN            # ALPACA: pointDensity = 1,0
    hd = voksel_seyrelt(hedef_v, leaf)
    kd = voksel_seyrelt(kaynak_v, leaf)

    # ALPACA.py:1628 — landmarklar kaynak bulutun SONUNA eklenir
    Y = np.append(kd, kaynak_lm, axis=0)
    X = hd

    # ALPACA.py:1631-1634 — EKSEN BASINA normalleme (anizotropik; ALPACA'nin kodu)
    bulut = X.max(axis=0) - X.min(axis=0)
    Xn = X * OLCEK_HEDEF / bulut
    Yn = Y * OLCEK_HEDEF / bulut

    reg = DeformableRegistration(**{'X': Xn, 'Y': Yn,
                                    'max_iterations': int(yineleme),
                                    'tolerance': float(tolerans),
                                    'low_rank': True},
                                 alpha=float(alpha), beta=float(beta))
    TY, _ = reg.register()
    cik = np.asarray(TY)[-len(kaynak_lm):] * bulut / OLCEK_HEDEF
    bilgi = {'leaf_mm': round(float(leaf), 3),
             'hedef_nokta': int(len(hd)), 'kaynak_nokta': int(len(kd)),
             'yuzey_kaymasi_mm': round(float(np.linalg.norm(
                 (np.asarray(TY)[:len(kd)] * bulut / OLCEK_HEDEF) - kd,
                 axis=1).mean()), 3)}
    if ayrinti:
        print('       CPD: hedef %d / kaynak %d nokta, leaf %.2f mm, kayma %.2f mm'
              % (bilgi['hedef_nokta'], bilgi['kaynak_nokta'],
                 bilgi['leaf_mm'], bilgi['yuzey_kaymasi_mm']))
    return cik, bilgi


def kestir_tek(sablon, hedef_v, hedef_lm_hiza, alpha=ALPHA_CPD, beta=BETA_CPD,
               yineleme=ITER, tolerans=TOL, ayrinti=False):
    """medial.kestir_tek ile AYNI arayuz; NICP yerine ALPACA'nin CPD'si."""
    ad = [k for k in M.HIZA_NOKTA if k in hedef_lm_hiza and k in sablon['lm']]
    if len(ad) < 6:
        return None, {'hata': 'hizalama icin yeterli nokta yok (%d)' % len(ad)}
    A = np.array([sablon['lm'][k] for k in ad])
    B = np.array([hedef_lm_hiza[k] for k in ad])
    s, R, t = M.procrustes(A, B)
    Vs = M._uygula(sablon['v'], s, R, t)
    Ls = {k: M._uygula(sablon['lm'][k], s, R, t) for k in M.HEDEF_NOKTA
          if k in sablon['lm']}
    anahtar = [k for k in M.HEDEF_NOKTA if k in Ls]
    P = np.array([Ls[k] for k in anahtar])
    Q, bilgi = cpd_aktar(Vs, P, hedef_v, alpha, beta, yineleme, tolerans,
                         ayrinti=ayrinti)
    bilgi.update({'hizalama_noktasi': len(ad), 'olcek': round(float(s), 4),
                  'kati_oncesi_hata_mm': round(float(np.linalg.norm(
                      np.array([M._uygula(sablon['lm'][k], s, R, t) for k in ad])
                      - B, axis=1).mean()), 2)})
    return {k: Q[i] for i, k in enumerate(anahtar)}, bilgi


def kestir(hedef_v, hedef_lm_hiza, kutuphane, alpha=ALPHA_CPD, beta=BETA_CPD,
           yineleme=ITER, tolerans=TOL, ayrinti=False):
    """medial.kestir ile AYNI arayuz ve AYNI birlestirici (koordinat medyani)."""
    tek, bilgiler = {k: [] for k in M.HEDEF_NOKTA}, {}
    for sb in kutuphane:
        o, b = kestir_tek(sb, hedef_v, hedef_lm_hiza, alpha, beta,
                          yineleme, tolerans, ayrinti=ayrinti)
        bilgiler[sb['ad']] = b
        if o is None:
            continue
        for k in o:
            tek[k].append(o[k])
    son, yay = {}, {}
    for k in M.HEDEF_NOKTA:
        if not tek[k]:
            son[k], yay[k] = None, None; continue
        Pk = np.array(tek[k])
        med = np.median(Pk, axis=0)
        son[k] = med
        yay[k] = float(np.linalg.norm(Pk - med[None, :], axis=1).mean())
    return son, dict(yayilim={k: (None if v is None else round(v, 2))
                              for k, v in yay.items()},
                     sablon_sayisi=len(tek[M.HEDEF_NOKTA[0]]),
                     tek_kestirimler={k: [[round(float(x), 4) for x in p]
                                          for p in tek[k]] for k in M.HEDEF_NOKTA},
                     sablon_bilgi=bilgiler)
