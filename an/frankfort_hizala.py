# -*- coding: utf-8 -*-
"""0BP — Frankfort hizalama adimi (on kayitli tanim, birebir).

z = Frankfort duzleminin normali (yukari): duzlem Po-R, Po-L ve orta(Or-R, Or-L)'den gecer
x = (Po-L - Po-R) vektorunun duzleme izdusumu (hastanin soluna)
y = z x x (one)          -- orta sagital duzlem biporion eksenine diktir; N/S KULLANILMAZ
Kapi (0Z/0AV/0BJ esikleri, degistirilmez): biporion 97,3-114,4 mm ve
porion orta noktasinin MSP'ye uzakligi <= 3 mm.  MSP burada iki orbitalenin orta noktasindan
gecen, x'e dik duzlemdir (porion orta noktasi ile orbitale orta noktasinin yanal farki).
Yeniden ornekleme: kati donusum, izotropik (ozgun en kucuk aralik), dogrusal, dolgu -1024.

Koordinatlar LPS (DICOM/ITK dunyasi). Cikti goruntu LPS cercevesinde: yeni eksenler
L=+x, P=-y, S=+z olacak sekilde yonlendirilir -> hizali hacim standart LPS gibi okunur.
"""
import numpy as np, SimpleITK as sitk

BIPORION = (97.3, 114.4)
MSP_MAKS = 3.0


def cerceve(P):
    poR, poL = np.asarray(P['Po-R'], float), np.asarray(P['Po-L'], float)
    orm = 0.5 * (np.asarray(P['Or-R'], float) + np.asarray(P['Or-L'], float))
    # LPS: +x = sol, +y = arka, +z = ust
    n = np.cross(poL - poR, orm - poR)
    n /= np.linalg.norm(n)
    if n[2] < 0:
        n = -n                                    # yukari
    x = poL - poR
    x = x - (x @ n) * n
    x /= np.linalg.norm(x)                        # sola
    y_on = np.cross(n, x)                         # z x x
    if (orm - 0.5 * (poR + poL)) @ y_on < 0:      # orbita onde olmali
        y_on = -y_on
    return x, y_on, n


def kapi(P, x):
    poR, poL = np.asarray(P['Po-R'], float), np.asarray(P['Po-L'], float)
    orm = 0.5 * (np.asarray(P['Or-R'], float) + np.asarray(P['Or-L'], float))
    bip = float(np.linalg.norm(poL - poR))
    msp = float(abs((0.5 * (poR + poL) - orm) @ x))
    gec = BIPORION[0] <= bip <= BIPORION[1] and msp <= MSP_MAKS
    return dict(biporion=round(bip, 2), msp_mm=round(msp, 2), gecti=bool(gec))


def hizala(img, P):
    """img: SimpleITK goruntu (LPS). Donus: (hizali_img, R, merkez, kapi_sonucu)."""
    x, y_on, z = cerceve(P)
    k = kapi(P, x)
    # yeni dunya eksenleri: L=x, P=-y_on, S=z  -> R satirlari yeni eksenler (eski->yeni)
    R = np.vstack([x, -y_on, z])
    merkez = 0.5 * (np.asarray(P['Po-R'], float) + np.asarray(P['Po-L'], float))
    sp = min(img.GetSpacing())
    # cikti izgarasi: ozgun hacmin 8 kosesini yeni cerceveye tasi, kapsayan kutu
    sz = np.array(img.GetSize())
    kos = [img.TransformIndexToPhysicalPoint([int(a), int(b), int(c)])
           for a in (0, sz[0] - 1) for b in (0, sz[1] - 1) for c in (0, sz[2] - 1)]
    yk = (np.asarray(kos) - merkez) @ R.T
    lo, hi = yk.min(0), yk.max(0)
    yeni_sz = [int(np.ceil((h - l) / sp)) + 1 for l, h in zip(lo, hi)]
    # yeni -> eski nokta donusumu: p_eski = R^T p_yeni + merkez
    T = sitk.AffineTransform(3)
    T.SetMatrix(R.T.ravel().tolist())
    T.SetTranslation(merkez.tolist())
    out = sitk.Resample(img, yeni_sz, T, sitk.sitkLinear, lo.tolist(), [sp] * 3,
                        np.eye(3).ravel().tolist(), -1024, img.GetPixelID())
    return out, R, merkez, k


def eski_to_yeni(p, R, merkez):
    return (np.asarray(p, float) - merkez) @ R.T


def yeni_to_eski(q, R, merkez):
    return np.asarray(q, float) @ R + merkez
