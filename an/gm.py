# -*- coding: utf-8 -*-
"""GEOMETRIK MORFOMETRI — 43 parametrenin 38-42'si.

KAYNAK: SlicerMorph, GPA modulu (GPA/Support/gpa_lib.py), BSD 2-Clause,
        Copyright (c) 2019 SlicerMorph Project.
        https://github.com/SlicerMorph/SlicerMorph
        Klonlandi: 2026-11-11, /home/claude/dis_kaynak/SlicerMorph

gpa_lib.py yalniz numpy + scipy.linalg kullanir; Slicer GEREKMEZ. Kod
KOPYALANMADI, dogrudan ithal edilir. Burada yapilan tek sey: paketlerden
landmark okumak, gpa_lib'in zincirini kosmak, ciktiyi tabloya yazilabilir
bicime getirmek.

PARAMETRE KARSILIKLARI
  38  centroid size        — zaten olculuyordu (olcum_zinciri)
  39  Procrustes           — gpa_lib.runGPA + procDist
  40-42 sekil PCA          — gpa_lib.calcCov + ozdeger ayristirma
  43  TPS                  — HENUZ YOK (vtk_lib.createTPS vtk ister)

DIKKAT — `0K` SS1: bu, olcum hattina EK bir analiz katmanidir, hattin kendisini
DEGISTIRMEZ. Kohorta sutun olarak yazilmasi ayri bir on kayit gerektirir.
"""
import os
import sys
import glob
import numpy as np

sys.path.insert(0, '/home/claude/an')
sys.path.insert(0, '/home/claude/orbita_hat')
sys.path.insert(0, '/home/claude/dis_kaynak/SlicerMorph/GPA/Support')
import params                                            # noqa: E402
import gpa_lib as G                                      # noqa: E402

# 12 nokta: apeks YOK (olculemiyor, `0AZ`), fma/fso YOK (her olguda yok)
AD = [b + '-' + s for b in ('d', 'mf', 'mso', 'fmo', 'ek', 'o')
      for s in ('r', 'l')]


def oku(kok):
    """kok altindaki her paketten 12 landmark okur."""
    olgu, M = [], []
    for p in sorted(glob.glob(os.path.join(kok, 'd*', 'denek*'))):
        ad = os.path.basename(p)
        try:
            lm, _ = params.load_scene(p)
            X = np.array([lm[k] for k in AD], float)
        except Exception:
            continue
        if X.shape == (len(AD), 3):
            olgu.append(ad); M.append(X)
    return olgu, np.dstack(M).astype(float)


def kos(A, n_pc=4):
    """GPA + sekil PCA. A = (landmark, boyut, olgu)."""
    N = A.shape[2]
    csize = np.array([np.linalg.norm(A[:, :, i] - A[:, :, i].mean(0))
                      for i in range(N)])
    hiz, ort = G.runGPA(A.copy())
    pd = G.procDist(hiz, ort)
    V = G.makeTwoDim(hiz)
    C = G.calcCov(V)
    ev, evec = np.linalg.eigh(C)
    o = np.argsort(ev)[::-1]
    ev, evec = ev[o], evec[:, o]
    ev = ev[ev > 1e-12]
    pay = 100 * ev / ev.sum()
    skor = (V - V.mean(axis=1, keepdims=True)).T @ evec[:, :n_pc]
    return {'centroid': csize, 'proc_uzaklik': pd, 'varyans_yuzde': pay,
            'pc_skor': skor, 'ortalama_sekil': ort, 'hizalanmis': hiz}


if __name__ == '__main__':
    kok = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/gelen2'
    olgu, A = oku(kok)
    R = kos(A)
    print('GPA — %d olgu x %d landmark' % (len(olgu), len(AD)))
    print('centroid  ort %.2f ss %.2f mm' % (R['centroid'].mean(),
                                             R['centroid'].std(ddof=1)))
    print('Procrustes uzakligi  ort %.4f ss %.4f' % (R['proc_uzaklik'].mean(),
                                                     R['proc_uzaklik'].std(ddof=1)))
    for i, v in enumerate(R['varyans_yuzde'][:6]):
        print('  PC%-2d %%%5.1f  kumulatif %%%5.1f'
              % (i + 1, v, R['varyans_yuzde'][:i + 1].sum()))
