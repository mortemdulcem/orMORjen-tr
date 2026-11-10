# -*- coding: utf-8 -*-
"""KEMIK KAPISI ve KEMIGE CEKME.

Kaynak: proje belgesi `00-BASLAMADAN-OKU-calisma-kurallari.md` §0e-3 ve §0e-4.
2026-11-10 (`0AT`) konteyner kaybindan sonra o tariflerden yeniden kuruldu;
ozgun dosya kayiptir, bu yuzden SADAKAT SINAVINDAN gecmeden kullanilmaz.

TARIF (§0e-3, birebir):
  "her landmarkin ve her rim noktasinin 1,5 mm komsulugundaki maks HU >= 250"
  -> esik §0e-4 karariyla 250 -> 226; arastirmaci 2026-11-10'da 220 oldugunu bildirdi.
  "Apeks dislanir (kavitenin arka ucudur)."
  Yaricap gerekcesi: nokta kemik YUZEYINDE isaretlenir ve kismi hacim etkisiyle
  tam voksel esigin altinda kalabilir; 1,5 mm en buyuk piksel araliginin (0,625)
  ~2,4 kati.

ONARIM (§0e-3, birebir):
  "kapiyi dusen nokta, en yakin KEMIK YUZEYI vokseline (kemigin bir voksel disi
   — `_yuzeye_izdusur`'un ve arastirmacinin elle `mf` bandinin ayni sozlesmesi)
   cekilir."
  Onarim arastirmacinin duzeltmesinin YERINE GECMEZ; kapi yerinde kalir ve
  onarilan nokta pakette isaretlenir.
"""
import numpy as np
from scipy import ndimage as ndi

ESIK = 220.0        # ARASTIRMACI, 2026-11-10: "maks 226'yi maks 220 olarak degistirmistik".
                    # NOT: `00` §0e-4 hala 226 yaziyor (Slicer Threshold ayari); belge
                    # ile kod arasindaki bu fark KAYDA GECTI ve uzlastirilmalidir.
YARICAP = 1.5       # mm, §0e-3
ARAMA = 12.0        # mm, onarim icin yerel kutu yari-kenari
ATLA = ('apex',)    # §0e-3: apeks dislanir

RAS2LPS = np.array([-1.0, -1.0, 1.0])


def _ijk(rows, org, P):
    lps = np.atleast_2d(np.asarray(P, float)) * RAS2LPS
    return np.linalg.solve(rows.T, (lps - org).T).T


def _ornekle(ct, rows, org, P):
    return ndi.map_coordinates(ct, _ijk(rows, org, P).T, order=1,
                               mode='constant', cval=-1024.0)


def maks_hu(ct, rows, org, nokta, yaricap=YARICAP, n=5):
    """Noktanin `yaricap` mm komsulugundaki en buyuk HU."""
    P = np.asarray(nokta, float)
    g = np.linspace(-yaricap, yaricap, n)
    X, Y, Z = np.meshgrid(g, g, g, indexing='ij')
    ofs = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
    ofs = ofs[np.linalg.norm(ofs, axis=1) <= yaricap + 1e-9]
    return float(_ornekle(ct, rows, org, P[None, :] + ofs).max())


def gecer(ct, rows, org, nokta, esik=ESIK, yaricap=YARICAP):
    return maks_hu(ct, rows, org, nokta, yaricap) >= esik


def kemige_cek(ct, rows, org, nokta, esik=ESIK, arama=ARAMA):
    """Noktayi en yakin KEMIK YUZEYI vokseline ceker (kemigin bir voksel disi).

    Bulunamazsa noktayi DEGISTIRMEDEN dondurur.
    """
    P = np.asarray(nokta, float)
    sp = np.array([np.linalg.norm(rows[a]) for a in range(3)])
    ij = _ijk(rows, org, P)[0]
    pad = np.ceil(arama / sp).astype(int)
    lo = np.maximum(np.floor(ij).astype(int) - pad, 0)
    hi = np.minimum(np.ceil(ij).astype(int) + pad + 1, np.array(ct.shape))
    if np.any(hi <= lo):
        return P, None
    sub = ct[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]
    kemik = sub >= esik
    if not kemik.any() or kemik.all():
        return P, None
    # "kemigin bir voksel disi" = genisletilmis kemik eksi kemik
    dis = ndi.binary_dilation(kemik) & ~kemik
    if not dis.any():
        return P, None
    gi, gj, gk = np.nonzero(dis)
    IJ = np.stack([gi + lo[0], gj + lo[1], gk + lo[2]], 1).astype(float)
    lps = (rows.T @ IJ.T).T + org
    Q = lps * RAS2LPS
    d = np.linalg.norm(Q - P, axis=1)
    j = int(np.argmin(d))
    return Q[j], float(d[j])


def uygula(ct, rows, org, lm, esik=ESIK, yaricap=YARICAP, atla=ATLA):
    """Kapiyi DUSEN noktalari kemige ceker. Gecenlere DOKUNMAZ (§0e-3 olcut C).

    Dondurur: (yeni_lm, rapor) — rapor nokta basina (eski_maks_hu, cekme_mm).
    """
    yeni = dict(lm); rapor = {}
    for k, P in lm.items():
        if k.split('-')[0] in atla:
            continue
        mh = maks_hu(ct, rows, org, P, yaricap)
        if mh >= esik:
            continue
        Q, d = kemige_cek(ct, rows, org, P, esik)
        if d is None:
            rapor[k] = (round(mh, 1), None)
            continue
        yeni[k] = Q
        rapor[k] = (round(mh, 1), round(d, 3))
    return yeni, rapor
