# -*- coding: utf-8 -*-
"""CRANIUMPY NICP MOTORU — bizim arayuzumuze uyarlanmis tureve.

KAYNAK: T-AbdelAlim/CraniumPy, src/craniumpy_core/registration/nicp.py
LISANS: Apache License 2.0 (depo 2026-11-09'da aldi) · DOI 10.5281/zenodo.7430069
Arastirmaci izni kayitli (`YONTEM-KATALOGU.md` A5).

DEGISIKLIK: ozgun `nicp()` yalnizca deforme tepe noktalarini dondurur.
Bizim `nicp.nokta_aktar()` tepe-basi afin dizisi X'i ister, bu yuzden dongu
buraya aynen alinip donus `(TV, X)` yapildi. Sayisal adimlarin HICBIRI
degistirilmedi. Yardimci islevler CraniumPy'den dogrudan ithal edilir,
kopyalanmaz.

BIZIM `an/nicp.py`'DEN FARKI (yani bu deneyin konusu):
  1. dist_threshold = 10 mm — uzak eslesmeler atilir (bizde yok)
  2. SINIR-SINIRA eslesme — kaynagin acik kenar tepeleri YALNIZ hedefin acik
     kenar tepeleriyle eslesir (bizde yok; orbita meshleri kirpik, yani
     acik kenarli)
  3. carpanlastirma onbellegi ve `workers=-1` — yalnizca hiz
"""
import sys
import numpy as np
from scipy import sparse
from scipy.spatial import cKDTree

sys.path.insert(0, '/home/claude/t-abdelalim/craniumpy/src')
from craniumpy_core.registration.nicp import (        # noqa: E402
    DEFAULT_ALPHAS, _boundary_vertex_indices, _build_stiffness,
    _build_data_term, _factorize_spd)


def nicp(kaynak_v, kaynak_f, hedef_v, hedef_f=None, alphalar=None,
         gamma=1.0, dist_threshold=10.0, ic_tur=3, ayrinti=False):
    """CraniumPy'nin NICP'i. Donus bizim `nicp.nicp` ile ayni: (TV, X)."""
    alphas = np.asarray(DEFAULT_ALPHAS if alphalar is None else alphalar, float)
    src_v = np.asarray(kaynak_v, dtype=np.float64)
    src_f = np.asarray(kaynak_f)
    n = len(src_v)

    kron_MG, m = _build_stiffness(src_f, n, gamma)
    D = _build_data_term(src_v)
    X = np.tile(np.vstack([np.eye(3), [0, 0, 0]]), (n, 1)).astype(np.float64)

    target_v = np.asarray(hedef_v, dtype=np.float64)
    tree = cKDTree(target_v)

    is_src_b = np.zeros(n, dtype=bool)
    tree_b, tgt_b_idx = None, None
    if hedef_f is not None:
        tgt_b_idx = _boundary_vertex_indices(np.asarray(hedef_f))
        src_b_idx = _boundary_vertex_indices(src_f)
        is_src_b[src_b_idx] = True
        if len(tgt_b_idx):
            tree_b = cKDTree(target_v[tgt_b_idx])
    if tree_b is None:
        is_src_b[:] = False
    if ayrinti:
        print('  sinir tepesi: kaynak %d / hedef %d'
              % (int(is_src_b.sum()), 0 if tgt_b_idx is None else len(tgt_b_idx)),
              flush=True)

    stiffness_gram = (kron_MG.T @ kron_MG).tocsc()
    data_gram_cache = None
    factor, factor_key = None, None

    for step, alpha in enumerate(alphas):
        for _ in range(ic_tur):
            transformed = D @ X
            dist = np.empty(n)
            idx = np.empty(n, dtype=np.int64)
            if is_src_b.any():
                d_b, i_b = tree_b.query(transformed[is_src_b], workers=-1)
                dist[is_src_b] = d_b
                idx[is_src_b] = tgt_b_idx[i_b]
            if (~is_src_b).any():
                d_i, i_i = tree.query(transformed[~is_src_b], workers=-1)
                dist[~is_src_b] = d_i
                idx[~is_src_b] = i_i
            matches = target_v[idx]

            w = (dist <= dist_threshold).astype(np.float64)
            WD = sparse.diags(w) @ D
            AtB = WD.T @ (w[:, None] * matches)

            key = (float(alpha), np.packbits(w.astype(bool)).tobytes())
            if factor is None or key != factor_key:
                if data_gram_cache is None or not np.array_equal(data_gram_cache[0], w):
                    data_gram_cache = (w, (WD.T @ WD).tocsc())
                AtA = (alpha * alpha * stiffness_gram + data_gram_cache[1]).tocsc()
                factor = _factorize_spd(AtA)
                factor_key = key
            X = factor(AtB)
            if X.ndim == 1:
                X = X.reshape(-1, 3)
        if ayrinti:
            print('  katilik %d/%d (alpha=%.1f) esik disi %d tepe'
                  % (step + 1, len(alphas), alpha, int((w == 0).sum())), flush=True)
    return D @ X, X
