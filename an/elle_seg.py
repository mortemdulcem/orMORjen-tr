# -*- coding: utf-8 -*-
"""Arastirmacinin Slicer segmentasyonunu (Segmentation.seg.nrrd) BT izgarasina okur.
Bos yer tutucu (sizes 1 1 1) ya da segmentsiz dosya -> None."""
import os, glob
import numpy as np, nrrd


def elle_seg(kl, shape, org, rows, ad='Segmentation.seg.nrrd'):
    """Segmentation.seg.nrrd -> {'sag','sol'} tam izgarada bool maske (kirpik kayit desteklenir)."""
    a, h = nrrd.read(kl + '/' + ad)
    so = np.array(h['space origin'], float)
    off = np.round(np.linalg.solve(rows.T, so - org)).astype(int)
    out = {}
    i = 0
    while 'Segment%d_Name' % i in h:
        ad = h['Segment%d_Name' % i].lower()
        lv = int(h.get('Segment%d_LabelValue' % i, i + 1))
        ly = int(h.get('Segment%d_Layer' % i, 0))
        A = a[ly] if a.ndim == 4 else a
        m = np.zeros(shape, bool)
        sl = tuple(slice(max(o, 0), max(o, 0) + A.shape[k] - max(-o, 0)) for k, o in enumerate(off))
        src = tuple(slice(max(-o, 0), A.shape[k]) for k, o in enumerate(off))
        m[sl] = (A[src] == lv)
        key = 'sag' if ad.startswith('sa') else ('sol' if ad.startswith('so') else None)
        if key is None:      # terminoloji karisikligi: konuma gore (LPS x>0 = sol)
            c = np.argwhere(m).mean(0) if m.any() else None
            key = 'sol' if c is not None and (org + rows @ c)[0] > 0 else 'sag'
        out[key] = out.get(key, np.zeros(shape, bool)) | m
        i += 1
    return out


def bul(kl, shape, org, rows):
    """klasordeki ELLE segmentasyon: once Segmentation*.seg.nrrd (OTOMATIK/ISIN adlilar haric)."""
    for f in sorted(glob.glob(kl + '/*.seg.nrrd')):
        b = os.path.basename(f).upper()
        if 'OTOMATIK' in b or 'ISIN' in b or '_SEGMENTATION' in b and not b.startswith('SEGMENTATION'):
            continue
        h = nrrd.read_header(f)
        if 'Segment0_Name' not in h or int(np.prod(h['sizes'][-3:])) <= 1:
            continue
        E = elle_seg(os.path.dirname(f), shape, org, rows, ad=os.path.basename(f))
        if E.get('sag') is not None and E.get('sol') is not None and E['sag'].any() and E['sol'].any():
            return E, f
    return None, None
