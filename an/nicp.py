# -*- coding: utf-8 -*-
"""NICP — Esnek olmayan ICP (Amberg, Romdhani & Vetter 2007, "Optimal Step
Nonrigid ICP Algorithms for Surface Registration", CVPR).

NEDEN KENDIMIZ YAZDIK: yazildigi sirada T-AbdelAlim/CraniumPy'nin LICENSE
dosyasi YOKTU (varsayilan: butun haklari sakli) — kodu kopyalanamazdi. Bu dosya
yayinlanmis formulasyondan yazilmistir ve trimesh/open3d bagimliligi yoktur;
yalniz numpy + scipy.sparse.
  ⚠ 2026-11-10 GUNCELLEME: o depo ARTIK Apache License 2.0 tasiyor (son isleme
  2026-11-09) ve citation.cff ile DOI'si var: 10.5281/zenodo.7430069,
  Abdel-Alim T., CraniumPy v0.3.0. Yani engel kalkmistir. BU DOSYA YINE DE
  DEGISTIRILMEDI: `0M` SS5'in dogrulanmis sayilari (apeks 3B hatasi 2,69 mm,
  derinlik MAE 1,65 mm) BU uygulamayla uretildi; baska bir NICP'e gecmek `0K`
  SS1 geregi ayri on kayit ve yeniden olcum ister. CraniumPy'nin uygulamasi
  BAGIMSIZ DOGRULAMA olarak kullanilir (ikisi de Amberg ve ark. 2007'den,
  ayri ayri yazilmis).

NEDEN CPD DEGIL: pycpd yogun M x M Gauss cekirdegi ve E adiminda M x N x 3 dizi
kuruyor; orbita kutusunun izo-yuzeyi 328.891 tepe veriyor -> G matrisi 806 GB.
Bellege sigdirmak icin 2.418 noktaya seyreltmek gerekti ve komsu uzakligi
0,31 -> 2,77 mm'ye cikti, yani suturler nokta bulutundan silindi (07 §7d).
NICP seyrek calisir: bellek O(tepe sayisi), on binlerce tepeyi kaldirir.

FORMULASYON
  Bilinmeyen: her tepe icin 4x3 afin donusum X_i; X = (4n x 3).
  Veri terimi    : D X ~ U      D (n x 4n) seyrek, satir i = [v_i^T, 1]
  Sertlik terimi : a (M (x) G) X ~ 0   M = kenar-dugum matrisi (m x n), G = diag(1,1,1,gamma)
  Cozum          : (A^T A) X = A^T B,  A = [a(M(x)G); W D],  B = [0; W U]
  Dis dongu      : alpha buyukten kucuge (kati -> esnek)
  Ic dongu       : en yakin komsu ile U yenilenir, kotu karsiliklar W=0 ile atilir
"""
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.spatial import cKDTree

VAR = (200.0, 120.0, 70.0, 40.0, 20.0, 10.0, 5.0, 2.0)   # varsayilan alpha dizisi


def kenarlar(yuzler):
    """Ucgen listesinden tekil kenar listesi (m x 2)."""
    f = np.asarray(yuzler, np.int64)
    e = np.vstack([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    e = np.sort(e, axis=1)
    return np.unique(e, axis=0)


def _sertlik(E, n, gamma=1.0):
    """a (M (x) G): M kenar-dugum matrisi, G = diag(1,1,1,gamma)."""
    m = len(E)
    # M (x) G -> 4m x 4n;  kenar k: +G sutun 4*i.., -G sutun 4*j..
    g = np.array([1.0, 1.0, 1.0, gamma])
    sat, sut, deg = [], [], []
    for b in range(4):
        sat.append(np.arange(m) * 4 + b); sut.append(E[:, 0] * 4 + b)
        deg.append(np.full(m, g[b]))
        sat.append(np.arange(m) * 4 + b); sut.append(E[:, 1] * 4 + b)
        deg.append(np.full(m, -g[b]))
    return sparse.csr_matrix((np.concatenate(deg),
                              (np.concatenate(sat), np.concatenate(sut))),
                             shape=(4 * m, 4 * n))


def _veri(V):
    """D: n x 4n, satir i = [v_i^T, 1] sutun 4i..4i+3'te."""
    n = len(V)
    sat = np.repeat(np.arange(n), 4)
    sut = np.arange(4 * n)
    deg = np.hstack([np.append(V[i], 1.0) for i in range(n)])
    return sparse.csr_matrix((deg, (sat, sut)), shape=(n, 4 * n))


def nicp(kaynak_v, kaynak_f, hedef_v, alphalar=VAR, gamma=1.0, ic_tur=3,
         maks_mesafe=None, hedef_normal=None, ayrinti=False):
    """Kaynak agi hedef nokta bulutuna esnek olarak oturtur.

    kaynak_v (n,3) · kaynak_f (f,3) · hedef_v (N,3)   — hepsi AYNI uzayda (RAS),
    ve ON HIZALAMA YAPILMIS olmali (bu islev yalniz esnek artigi cozer).
    maks_mesafe: bundan uzak karsiliklar atilir (W=0). None -> 5 x ortalama kenar.

    Donus: (TV, X) — TV deforme tepe konumlari (n,3), X afin katsayilar (4n,3).
    """
    V = np.asarray(kaynak_v, float)
    F = np.asarray(kaynak_f, np.int64)
    Xh = np.asarray(hedef_v, float)
    n = len(V)
    E = kenarlar(F)
    if maks_mesafe is None:
        kl = np.linalg.norm(V[E[:, 0]] - V[E[:, 1]], axis=1).mean()
        maks_mesafe = 5.0 * kl
    MG = _sertlik(E, n, gamma)
    D = _veri(V)
    agac = cKDTree(Xh)
    # X baslangici: birim afin (her tepe icin [I; 0])
    X = np.tile(np.vstack([np.eye(3), np.zeros((1, 3))]), (n, 1))
    TV = V.copy()
    for a in alphalar:
        for _ in range(ic_tur):
            d, i = agac.query(TV)
            U = Xh[i]
            w = (d <= maks_mesafe).astype(float)
            if hedef_normal is not None:
                pass                      # normal uyumu bu surumde kullanilmiyor
            if w.sum() < 10:
                w[:] = 1.0                # hic karsilik kalmadiysa hepsini kabul et
            W = sparse.diags(w)
            A = sparse.vstack([a * MG, W @ D]).tocsr()
            B = np.vstack([np.zeros((MG.shape[0], 3)), (W @ U)])
            AtA = (A.T @ A).tocsc()
            AtB = A.T @ B
            X = np.column_stack([spsolve(AtA, AtB[:, k]) for k in range(3)])
            TV = D @ X
        if ayrinti:
            d, _ = agac.query(TV)
            print('   alpha %7.1f  ort karsilik %.3f mm  atilan %d/%d'
                  % (a, d.mean(), int((d > maks_mesafe).sum()), n))
    return TV, X


def nokta_aktar(p, kaynak_v, X, k=8):
    """Sablon uzayindaki p noktasini deforme uzaya tasir.

    Her tepenin kendi afin donusumu var; p'nin en yakin k tepesinin afinleri
    ters-uzaklik agirligiyla harmanlanir. Bu, p'nin yuzey UZERINDE olmasini
    gerektirmez — bizim landmarklar kemik yuzeyine yakin ama tam tepede degil.
    """
    V = np.asarray(kaynak_v, float)
    p = np.asarray(p, float)
    d = np.linalg.norm(V - p[None, :], axis=1)
    i = np.argsort(d)[:k]
    w = 1.0 / (d[i] + 1e-6)
    w = w / w.sum()
    ph = np.append(p, 1.0)
    out = np.zeros(3)
    for wj, ij in zip(w, i):
        out += wj * (ph @ X[4 * ij:4 * ij + 4, :])
    return out
