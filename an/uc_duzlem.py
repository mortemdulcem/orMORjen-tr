# -*- coding: utf-8 -*-
"""UC DUZLEM DENETIMI — aksiyel + koronal + sagital, landmarklar ustte.
Karar tablosu A1: 3B veride hukum uc duzlem BIRLIKTE gorulerek verilir.
Orbita kutusuna kirpilir -- yuz gorunmez (SS0.2)."""
import sys, os, json, glob
sys.path.insert(0, '/home/claude/an'); sys.path.insert(0, '/home/claude/orbita_hat')
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import onisle

AD = ['d','mf','mso','fmo','ek','o','apex']
W, L = 1000.0, 400.0          # OKU.txt'teki pencere: W1000/L400


def yukle_lm(klasor):
    lm = {}
    for f in glob.glob(os.path.join(klasor, 'OTO_*-?.mrk.json')):
        d = json.load(open(f))
        for m in d['markups']:
            for cp in m['controlPoints']:
                lm[cp['label']] = np.array(cp['position'], float)
    return lm


def ciz(denek, dicom_dir, mrk_dir, cikti):
    hacim, bilgi = onisle.dicom_hacim(dicom_dir)
    ct = np.transpose(hacim, (2, 1, 0))                  # x,y,z
    org = np.array(bilgi['origin'], float)
    sp = np.array([bilgi['PixelSpacing'][0], bilgi['PixelSpacing'][1], bilgi['kesit_araligi']])
    lm = yukle_lm(mrk_dir)
    P = np.array([lm[k] for k in lm])                     # LPS mm
    def ijk(p):
        return (np.asarray(p, float) - org) / sp      # mrk.json LPS, origin LPS
    I = np.array([ijk(p) for p in P])
    c = I.mean(0)
    pad = np.array([55., 55., 28.]) / sp                  # orbita kutusu
    lo = np.maximum((c - pad).astype(int), 0)
    hi = np.minimum((c + pad).astype(int) + 1, ct.shape)
    vmin, vmax = L - W / 2, L + W / 2
    sagI = np.array([ijk(lm[k]) for k in lm if k.endswith('-r')])
    cs = sagI.mean(0)
    fig, ax = plt.subplots(1, 3, figsize=(15, 5.2))
    kesit = [('aksiyel', 2), ('koronal', 1), ('sagital (sag orbita)', 0)]
    for a, (adx, eks) in zip(ax, kesit):
        k = int(round((cs if eks == 0 else c)[eks]))
        if eks == 2:
            im = ct[lo[0]:hi[0], lo[1]:hi[1], k].T
            e = (lo[0], hi[0], hi[1], lo[1]); xi, yi = 0, 1; ori = 'upper'
        elif eks == 1:
            im = ct[lo[0]:hi[0], k, lo[2]:hi[2]].T
            e = (lo[0], hi[0], lo[2], hi[2]); xi, yi = 0, 2; ori = 'lower'
        else:
            im = ct[k, lo[1]:hi[1], lo[2]:hi[2]].T
            e = (lo[1], hi[1], lo[2], hi[2]); xi, yi = 1, 2; ori = 'lower'
        a.imshow(im, cmap='gray', vmin=vmin, vmax=vmax, extent=e,
                 aspect='auto', origin=ori)
        for nm, p in lm.items():
            q = ijk(p)
            if abs(q[eks] - k) <= (10 if eks == 0 else 6):
                a.plot(q[xi], q[yi], 'o', ms=5, mfc='none',
                       mec=('#ff3b30' if nm.startswith('apex') else '#00e5ff'), mew=1.6)
                a.text(q[xi] + 1.5, q[yi], nm, color='#ffd400', fontsize=6.5)
        a.set_title('%s  (kesit %d)' % (adx, k), fontsize=10)
        a.set_xticks([]); a.set_yticks([])
    fig.suptitle('%s — uc duzlem denetimi · W%d/L%d' % (denek, W, L), fontsize=12)
    fig.tight_layout(); fig.savefig(cikti, dpi=110); plt.close(fig)
    return cikti


if __name__ == '__main__':
    for n in sys.argv[1:]:
        d = 'denek%s' % n
        try:
            p = ciz(d, '/home/claude/gelen3/d%s/se' % n,
                    '/home/claude/veri_disk/otomatik_landmark/%s_TAMOTO' % d,
                    '/home/claude/an/out/%s_ucduzlem.png' % d)
            print('OK', p, flush=True)
        except Exception as e:
            print('HATA', d, type(e).__name__, e, flush=True)
