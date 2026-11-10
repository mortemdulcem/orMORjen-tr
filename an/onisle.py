# -*- coding: utf-8 -*-
"""DICOM ON ISLEME — konteyner sifirlanmasindan sonra yeniden yazildi (2026-11-10).

  onisle.dicom_hacim(kaynak) -> (hacim, bilgi)

`bilgi` alanlari, hayatta kalan raporlarin `bt` bolumunden cikarildi:
  kesit · boyut · voksel_mm · cekirdek (ConvolutionKernel) · kVp ·
  WindowCenter/Width · SeriesDescription · ProtocolName · StudyDescription ·
  BodyPartExamined · ImageType · SeriesUID/StudyUID ozeti

PENCERE KAPISI (T10): yumusak doku penceresi olculmez, yalniz bildirilir.
Kemik cekirdegi adi BONE/BONEPLUS/SHARP/B70/B60 gibi desenleri tasimalidir.
"""
import os, glob, hashlib
import numpy as np
import SimpleITK as sitk
import pydicom

KEMIK_DESEN = ('BONE', 'SHARP', 'B70', 'B60', 'YA', 'YB', 'YC', 'YD', 'H70', 'H60')


def _dicom_klasor_bul(kok):
    """Ic ice klasorlerde en cok .dcm barindiran dizini bulur."""
    en_iyi, en_cok = None, 0
    for d, _, f in os.walk(kok):
        n = sum(1 for x in f if x.lower().endswith('.dcm'))
        if n == 0:
            n = sum(1 for x in f if not os.path.splitext(x)[1])
        if n > en_cok:
            en_iyi, en_cok = d, n
    return en_iyi


def pencere_kapisi(bilgi):
    """Kemik penceresi mi? (T10 kurali). Doner: (kemik_mi, gerekce)."""
    ck = str(bilgi.get('cekirdek') or '').upper()
    ww = bilgi.get('WindowWidth')
    try:
        ww = float(np.ravel([ww])[0]) if ww is not None else None
    except Exception:
        ww = None
    kemik = any(p in ck for p in KEMIK_DESEN)
    if not kemik and ww is not None and ww >= 1500:
        kemik, ck = True, ck + ' (WW=%g)' % ww
    return kemik, 'cekirdek=%s WW=%s' % (ck or '?', ww)


def dicom_hacim(kaynak):
    """DICOM klasorunu okur -> (hacim ndarray [i,j,k], bilgi sozlugu)."""
    kl = kaynak if os.path.isdir(kaynak) else os.path.dirname(kaynak)
    kl = _dicom_klasor_bul(kl) or kl
    okuyucu = sitk.ImageSeriesReader()
    seri = okuyucu.GetGDCMSeriesIDs(kl)
    if not seri:
        raise RuntimeError('DICOM serisi bulunamadi: %s' % kl)
    # en cok kesitli seri
    en_iyi, dosyalar = None, []
    for sid in seri:
        f = okuyucu.GetGDCMSeriesFileNames(kl, sid)
        if len(f) > len(dosyalar):
            en_iyi, dosyalar = sid, f
    okuyucu.SetFileNames(dosyalar)
    img = okuyucu.Execute()
    a = sitk.GetArrayFromImage(img)              # (z,y,x)
    hacim = np.transpose(a, (2, 1, 0))           # -> (x,y,z) = ct[i,j,k]

    d = pydicom.dcmread(dosyalar[0], stop_before_pixels=True, force=True)
    g = lambda k, v=None: getattr(d, k, v)
    sp = img.GetSpacing()
    bilgi = dict(
        kesit=len(dosyalar),
        boyut=list(hacim.shape),
        voksel_mm=round(float(sp[0]), 6),
        kesit_kalinligi=float(g('SliceThickness', 0) or 0),
        cekirdek=str(np.ravel([g('ConvolutionKernel', '')])[0]) if g('ConvolutionKernel', '') else '',
        kVp=float(g('KVP', 0) or 0),
        WindowCenter=g('WindowCenter'), WindowWidth=g('WindowWidth'),
        SeriesDescription=str(g('SeriesDescription', '') or ''),
        ProtocolName=str(g('ProtocolName', '') or ''),
        StudyDescription=str(g('StudyDescription', '') or ''),
        BodyPartExamined=str(g('BodyPartExamined', '') or ''),
        ImageType=list(g('ImageType', []) or []),
        SeriesUID_ozet=hashlib.sha256(str(g('SeriesInstanceUID', '')).encode()).hexdigest()[:16],
        StudyUID_ozet=hashlib.sha256(str(g('StudyInstanceUID', '')).encode()).hexdigest()[:16],
        spacing=[float(x) for x in sp],
        origin=[float(x) for x in img.GetOrigin()],
        direction=[float(x) for x in img.GetDirection()],
    )
    orta = hacim[:, :, hacim.shape[2] // 2]
    bilgi['orta_kesit_ozeti'] = hashlib.sha256(np.ascontiguousarray(orta).tobytes()).hexdigest()[:16]
    bilgi['tam_ozet'] = hashlib.sha256(np.ascontiguousarray(hacim).tobytes()).hexdigest()[:24]
    return hacim, bilgi
