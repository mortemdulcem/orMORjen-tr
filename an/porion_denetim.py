# -*- coding: utf-8 -*-
"""PORION UC DUZLEM DENETIMI  [`00B` §T9 · `00` §0e adim 3]

Her porion icin aksiyel, koronal ve sagittal kesit cizilir ve nokta
artı ile isaretlenir. Amac: ALI'nin buldugu noktanin GERCEKTEN dis akustik
meatusun ust kemik kenarinda olup olmadigini GOZLE denetlemek.
`00` §0e-4: "Yalniz 3B yuzey modeline guvenilmez."
`00` §0.2: ciktida hasta kimligi yok; yalniz `denek` etiketi.
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rayseg
import frankfort as F

PENCERE = (-200.0, 1800.0)      # kemik penceresi
YARIM = 30.0                    # mm, kesit yarim-kenari


def _ijk(rows, org, P):
    lps = np.atleast_2d(np.asarray(P, float)) * rayseg.RAS2LPS
    return np.linalg.solve(rows.T, (lps - org).T).T[0]


def ciz(denek, ct_yol, porion_json, cikti):
    ct, rows, org = rayseg.load_ct(ct_yol)
    po = F.oku_porion(porion_json)
    sp = np.array([np.linalg.norm(rows[a]) for a in range(3)])

    etiketler = [k for k in ('RPo', 'LPo') if k in po]
    fig, axes = plt.subplots(len(etiketler), 3, figsize=(12, 4.2 * len(etiketler)))
    axes = np.atleast_2d(axes)

    for r, lab in enumerate(etiketler):
        ijk = _ijk(rows, org, po[lab])
        i, j, k = [int(round(v)) for v in ijk]
        yarim = (YARIM / sp).astype(int)
        for c, (eksen, ad) in enumerate(((0, 'sagittal (i sabit)'),
                                         (1, 'koronal (j sabit)'),
                                         (2, 'aksiyel (k sabit)'))):
            ax = axes[r, c]
            if eksen == 0:
                dilim = ct[np.clip(i, 0, ct.shape[0] - 1), :, :]
                cx, cy = k, j
                h = (yarim[2], yarim[1])
            elif eksen == 1:
                dilim = ct[:, np.clip(j, 0, ct.shape[1] - 1), :]
                cx, cy = k, i
                h = (yarim[2], yarim[0])
            else:
                dilim = ct[:, :, np.clip(k, 0, ct.shape[2] - 1)]
                cx, cy = j, i
                h = (yarim[1], yarim[0])
            ax.imshow(dilim, cmap='gray', vmin=PENCERE[0], vmax=PENCERE[1],
                      origin='lower', aspect='equal')
            ax.plot([cx - 6, cx - 2], [cy, cy], '-', color='#ff2d55', lw=1.4)
            ax.plot([cx + 2, cx + 6], [cy, cy], '-', color='#ff2d55', lw=1.4)
            ax.plot([cx, cx], [cy - 6, cy - 2], '-', color='#ff2d55', lw=1.4)
            ax.plot([cx, cx], [cy + 2, cy + 6], '-', color='#ff2d55', lw=1.4)
            ax.set_xlim(cx - h[0], cx + h[0])
            ax.set_ylim(cy - h[1], cy + h[1])
            ax.set_title('%s  %s' % (lab, ad), fontsize=9)
            ax.set_xticks([]); ax.set_yticks([])

    fig.suptitle('%s — porion uc duzlem denetimi (kemik penceresi)' % denek,
                 fontsize=11)
    fig.tight_layout()
    os.makedirs(os.path.dirname(cikti), exist_ok=True)
    fig.savefig(cikti, dpi=110)
    plt.close(fig)
    return cikti


if __name__ == '__main__':
    denek = sys.argv[1]
    print(ciz(denek,
              '/home/claude/kurtarma/paket/%s/%s_CT.nrrd' % (denek, denek),
              '/home/claude/porion/cikti/%s_porion.json' % denek,
              '/home/claude/porion/denetim/%s_porion_3duzlem.png' % denek))
