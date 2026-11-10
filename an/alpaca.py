# -*- coding: utf-8 -*-
"""ALPACA / SlicerMorph'tan ALINAN PARCALAR — kaynak kodundan uyarlanmistir.

KAYNAK: SlicerMorph, ALPACA modulu (ALPACA/ALPACA.py), BSD 2-Clause License,
        Copyright (c) 2019 SlicerMorph Project.
        https://github.com/SlicerMorph/SlicerMorph
        Klonlandi: 2026-10-23, /home/claude/dis_kaynak/SlicerMorph

NEDEN BU IKI PARCA: ALPACA'nin tamami Slicer icinde kosar (`slicer`, MRML sahnesi,
qMRMLSegmentEditorWidget) ve bu kapta ice aktarilamaz. Fakat zincirin iki adimi
saf numpy/vtk'dir, bizim hattimizin karsilik gelen adimlariyla DOGRUDAN
karsilastirilabilir, ve ikisi de bizim halihazirda kullandigimizdan FARKLI bir
kural uyguluyor:

 1) `geometrik_medyan`  <- ALPACA.calculateGeometricMedian (ALPACA.py:1309-1342)
    MALPACA cok-sablon kipinin birlestiricisi. Bizim `medial.kestir` fonksiyonu
    `np.median(P, axis=0)` yani KOORDINAT-BAZLI medyan kullaniyor; ALPACA bunu
    yalnizca BASLANGIC NOKTASI sayip Weiszfeld yinelemesiyle GERCEK geometrik
    medyana gidiyor. Ustelik ALPACA'nin kendi belge dizesi, float32 girdiyle eski
    BFGS yaklasiminin "sessizce aritmetik medyana esitlendigini" bir HATA olarak
    kaydediyor — yani bu ayrimi onlar da onemsemis.

 2) `yuzeye_izdusur_normal` <- ALPACA.projectPointsPolydata (ALPACA.py:2934-3008)
    Landmarki hedef yuzeye, SABLON YUZEYININ NORMALI boyunca atilan isinla
    izdusurur ve kesisimlerin EN DISTAKISINI alir. Bizim `otomasyon2._yuzeye_izdusur`
    isaretli mesafe alanindan en yakin DIS vokseli buluyor — yon bilgisi yok.
    Elle isaretli 14 `mf` noktasinin kemigin tam bir voksel DISINDA oturdugu
    olculdugu icin (atlas §BL, SS 0,11 mm) "en distaki kesisim" kurali sinanmaya
    deger.

Her iki fonksiyon da ozgun algoritmaya sadik tutulmustur; degisiklikler yalnizca
(a) Slicer dugumleri yerine numpy dizileri, (b) Turkce ad ve belge dizesi.
"""
import numpy as np


def geometrik_medyan(kestirimler, en_cok_yineleme=1000, tolerans=1e-9):
    """Sablon kestirimlerinin GEOMETRIK medyani, landmark landmark.

    ALPACA.calculateGeometricMedian'in birebir karsiligi: koordinat-bazli
    medyandan baslayan Weiszfeld yinelemesi.

    kestirimler : (sablon, landmark, 3) ya da (sablon, 3)
    doner       : (landmark, 3) ya da (3,)
    """
    P = np.asarray(kestirimler, dtype=np.float64)
    tek_nokta = (P.ndim == 2)
    if tek_nokta:
        P = P[:, None, :]                      # (sablon, 1, 3)
    sonuc = np.median(P, axis=0)               # baslangic — koordinat-bazli medyan
    if P.shape[0] < 3:
        # Iki kestirim varsa aralarindaki her nokta geometrik medyandir.
        return sonuc[0] if tek_nokta else sonuc
    olcek = max(float(np.ptp(P.reshape(-1, P.shape[-1]), axis=0).max()), 1.0)
    for _ in range(int(en_cok_yineleme)):
        d = np.linalg.norm(P - sonuc[None, :, :], axis=2)        # (sablon, landmark)
        # Mevcut noktayla cakisan kestirim sifira bolerdi; kucuk bir taban konur.
        w = 1.0 / np.maximum(d, 1e-12 * olcek)
        yeni = (w[:, :, None] * P).sum(axis=0) / w.sum(axis=0)[:, None]
        kayma = float(np.linalg.norm(yeni - sonuc, axis=1).max())
        sonuc = yeni
        if kayma < tolerans * olcek:
            break
    return sonuc[0] if tek_nokta else sonuc


def yuzeye_izdusur_normal(kaynak_pd, hedef_pd, noktalar, isin_mm):
    """Noktalari kaynak yuzeyin normali boyunca hedef yuzeye izdusurur.

    ALPACA.projectPointsPolydata'nin uyarlamasi. Kural sirasi ozgun koddaki
    gibidir:
      1. Noktaya en yakin KAYNAK tepe noktasinin normali isin yonudur.
      2. Isin hedef yuzeyi kesiyorsa EN DISTAKI (son) kesisim alinir.
      3. Kesmiyorsa isin TERS cevrilir ve ILK kesisim alinir.
      4. O da yoksa hedef yuzeyin en yakin noktasina oturtulur.

    kaynak_pd, hedef_pd : vtkPolyData
    noktalar            : (n, 3) RAS
    isin_mm             : isin uzunlugu (ALPACA'da hedefin kosegeni x katsayi)
    doner               : (n, 3) izdusurulmus noktalar, (n,) hangi kural islemis
    """
    import vtk
    from vtk.util import numpy_support as ns

    # ALPACA burada vtkOBBTree kullanir (ALPACA.py:2949-2951). BU ORTAMDA
    # (VTK 9.6) vtkOBBTree AYNI yuzeyde HIC kesisim dondurmuyor: yuzeyin tam
    # capindan gecen bir isinda bile 0, oysa vtkCellLocator ve
    # vtkModifiedBSPTree ayni isinda 4 kesisim buluyor (2026-10-26'da olculdu).
    # Bu yuzden hizlandirici vtkCellLocator'a cevrildi; GEOMETRIK KURAL AYNI
    # (isin-yuzey kesisimleri, en distaki alinir). Degisiklik ALPACA'nin
    # algoritmasinda degil, VTK sinifindadir.
    # ⚠ Bu, kayitli bir sonucu GERI ALDI: 2026-10-26'da izdusum kolu once
    # vtkOBBTree ile kosuldu, 28/28 nokta "en_yakin" tabanina dustu ve iki
    # kural AYNI sayiyi verdi. O "ayrim yok" sonucu gecersizdir.
    obb = vtk.vtkCellLocator(); obb.SetDataSet(hedef_pd); obb.BuildLocator()
    kaynak_loc = vtk.vtkPointLocator(); kaynak_loc.SetDataSet(kaynak_pd); kaynak_loc.BuildLocator()
    hedef_loc = vtk.vtkPointLocator(); hedef_loc.SetDataSet(hedef_pd); hedef_loc.BuildLocator()

    nd = kaynak_pd.GetPointData().GetArray("Normals")
    if not nd:
        nf = vtk.vtkPolyDataNormals()
        nf.ComputePointNormalsOn(); nf.SetInputData(kaynak_pd); nf.Update()
        nd = nf.GetOutput().GetPointData().GetArray("Normals")
        if not nd:
            raise RuntimeError("kaynak yuzeyde normal uretilemedi")

    cikti, kural = [], []
    for p in np.asarray(noktalar, float):
        pid = kaynak_loc.FindClosestPoint(p)
        yon = np.array(nd.GetTuple(pid), float)
        kp = vtk.vtkPoints(); ki = vtk.vtkIdList()
        obb.IntersectWithLine(p.tolist(), (p + yon * isin_mm).tolist(), kp, ki)
        if kp.GetNumberOfPoints() > 0:
            cikti.append(kp.GetPoint(kp.GetNumberOfPoints() - 1)); kural.append('en_dis')
            continue
        kp2 = vtk.vtkPoints(); ki2 = vtk.vtkIdList()
        obb.IntersectWithLine(p.tolist(), (p - yon * isin_mm).tolist(), kp2, ki2)
        if kp2.GetNumberOfPoints() > 0:
            cikti.append(kp2.GetPoint(0)); kural.append('ters')
        else:
            cikti.append(hedef_pd.GetPoint(hedef_loc.FindClosestPoint(p)))
            kural.append('en_yakin')
    return np.array(cikti, float), kural
