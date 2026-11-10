# -*- coding: utf-8 -*-
"""BT hacminden KEMIK IZO-YUZEYI (RAS, orbita bolgesine kirpik).

Seyreltme nasil yapiliyor: marching_cubes'u TAM cozunurlukte kosup sonra agi
seyreltmek bir seyreltici kutuphane ister (open3d/trimesh/vtk — kurulu degil).
Onun yerine HACIM once kucultuluyor, sonra marching_cubes kosuyor: ag topolojisi
gecerli kalir, tepe sayisi ~ (1/ds)^2 olcusunde duser, ek bagimlilik gerekmez.

ds = 1 -> tam cozunurluk (orbita kutusu ~330k tepe, NICP icin fazla)
ds = 3 -> ~37k · ds = 4 -> ~21k · ds = 5 -> ~13k

UYARI: hacmi kuculttukce medial duvar (lamina papyracea, 0,24-1,36 mm; kesit
yonunde bir vokselden ince) daha da bulaniklasir. Tam da `d`/`mf`'nin oturdugu
yer burasi, yani ds secimi bir odunlesmedir ve LOO ile secilmelidir (§0.12).
"""
import numpy as np
from scipy import ndimage as ndi
from skimage import measure

KEMIK_HU = 200.0


def orbita_kutusu(ct, rows, org, lm, ad14, pay_mm=15.0):
    """14 landmarkin voksel kutusu + pay. Donus: (lo, hi) voksel indisleri."""
    P = np.array([np.asarray(lm[k], float) for k in ad14])
    inv = np.linalg.inv(rows)
    ix = np.rint((P * np.array([-1., -1., 1.]) - org) @ inv).astype(int)
    sp = np.abs(np.diag(rows))
    pay = np.rint(pay_mm / sp).astype(int)
    lo = np.maximum(ix.min(0) - pay, 0)
    hi = np.minimum(ix.max(0) + pay + 1, np.array(ct.shape))
    return lo, hi


def yuzey(ct, rows, org, lo, hi, ds=4, esik=KEMIK_HU):
    """Kirpik bolgeden kemik izo-yuzeyi. Donus: (tepe_RAS (n,3), yuzler (f,3))."""
    sp = np.abs(np.diag(rows))
    alt = ct[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]].astype(np.float32)
    if ds and ds != 1:
        alt = ndi.zoom(alt, 1.0 / ds, order=1)
        sp_e = sp * ds                      # kuculen hacmin etkin voksel boyu
    else:
        sp_e = sp
    v, f, _, _ = measure.marching_cubes(alt, level=esik, spacing=tuple(sp_e))
    # v: kirpik+kucultulmus hacmin yerel mm'si -> LPS -> RAS
    v_lps = org + lo * sp + v
    v_ras = v_lps * np.array([-1., -1., 1.])
    return v_ras, f.astype(np.int64)


def en_buyuk_parca(v, f):
    """Baglantili en buyuk bileseni tut (kucuk ada ucgenleri NICP'yi bozar)."""
    n = len(v)
    E = np.vstack([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    A = coo_matrix((np.ones(len(E)), (E[:, 0], E[:, 1])), shape=(n, n))
    k, et = connected_components(A, directed=False)
    if k == 1:
        return v, f
    buyuk = np.argmax(np.bincount(et))
    tut = et == buyuk
    yeni = -np.ones(n, np.int64)
    yeni[tut] = np.arange(tut.sum())
    fm = tut[f].all(axis=1)
    return v[tut], yeni[f[fm]]


def hazirla(ct, rows, org, lm, ad14, ds=4, pay_mm=15.0, esik=KEMIK_HU):
    lo, hi = orbita_kutusu(ct, rows, org, lm, ad14, pay_mm)
    v, f = yuzey(ct, rows, org, lo, hi, ds=ds, esik=esik)
    return en_buyuk_parca(v, f)
