# -*- coding: utf-8 -*-
"""SABLON KUTUPHANESI — elle etiketlenmis olgulari OTOMATIK bulup okur.

Kaynak: `01` veri setindeki elle olculmus olgular. Her sablon = kemik izo-yuzeyi
(RAS) + 14 elle isaretlenmis landmark (RAS). Bilinen tuzaklar burada ele alinir:
  · landmark takma adlari: fso->mso, mfo->fmo (§0.4)
  · landmark dosya adlari genel olabilir (F_2..F_15) — etiket JSON'un ICINDEN okunur
  · egri/segment adlari olgudan olguya degisir; BU MODUL EGRI/MASKE KULLANMIYOR,
    yalniz BT + 14 nokta, yani o tuzaklar burada etkisiz
Onbellek: /home/claude/an/out/sablonlar/<olgu>_ds<N>.npz
"""
import os, sys, json
sys.path.insert(0, '/home/claude/an'); sys.path.insert(0, '/home/claude/orbita_hat')
import numpy as np
import params, rayseg, yuzey as Y

AD14 = ['d-r', 'd-l', 'mf-r', 'mf-l', 'mso-r', 'mso-l', 'fmo-r', 'fmo-l',
        'ek-r', 'ek-l', 'o-r', 'o-l', 'apex-r', 'apex-l']
# ELLE OLCULMUS olgular (veri setindeki P04-P09, P11 + hasta8).
# P10 (hasta12) ve P12 (hasta13) BILEREK YOK: landmarklari otomatik, sablon olamaz.
OLGULAR = [
    ('hasta5', '/home/claude/h5m/ham/ölçüm denemesi 2', '4 1.25MM BONE.nrrd', 'P04'),
    # hasta6 ölçüm3'te `o-r` EKSIK (atlas §AM) -> veri setinin yaptigi gibi
    # olcum2'den tamamlaniyor; `o-r` hedef nokta degil, yalniz baglamdir.
    ('hasta6', '/home/claude/h6m3/ham/hasta6 ölçüm 3', None, 'P06',
     '/home/claude/h6m/ham/hasta6 ölçüm 2'),
    ('hasta7', '/home/claude/h7/ham/ölçüm1', '4 1.25MM BONE.nrrd', 'P07'),
    ('hasta8', '/home/claude/h8m/ham/ölçüm2', '4 1.25MM BONE.nrrd', 'P05'),
    ('hasta9', '/home/claude/h9m/ham/ölçüm5', '4 1.25MM BONE.nrrd', 'P08'),
    ('hasta10', '/home/claude/h10m/ham/ölçüm4', '4 1.25MM BONE.nrrd', 'P09'),
    ('hasta11', '/home/claude/h11m3/ham/ölçüm3', None, 'P11'),
]
ONBELLEK = '/home/claude/an/out/sablonlar'


def _bt_bul(klasor, tercih=None):
    import glob
    if tercih and os.path.exists(os.path.join(klasor, tercih)):
        return os.path.join(klasor, tercih)
    aday = [f for f in glob.glob(os.path.join(klasor, '*.nrrd'))
            if 'segmentation' not in os.path.basename(f).lower()
            and 'seg' not in os.path.basename(f).lower()]
    if not aday:
        raise FileNotFoundError('BT bulunamadi: %s' % klasor)
    aday.sort(key=lambda f: -os.path.getsize(f))         # en buyuk = ham BT
    return aday[0]


def landmarklar(klasor, yedek=None):
    """yedek: `OLGULAR` kaydinin 5. ogesi. Yalniz EKSIK landmarklar oradan
    tamamlanir; klasorde bulunan hicbir nokta degistirilmez (hasta6 olcum3'te
    `o-r` yok, veri setinin yaptigi gibi olcum2'den gelir -- OLGULAR notu)."""
    lm, _ = params.load_scene(klasor)
    for a, b in (('fso-r', 'mso-r'), ('fso-l', 'mso-l'),
                 ('mfo-r', 'fmo-r'), ('mfo-l', 'fmo-l')):
        if a in lm and b not in lm:
            lm[b] = lm[a]
    eksik = [k for k in AD14 if k not in lm]
    if eksik and yedek and os.path.isdir(yedek):
        ylm, _ = params.load_scene(yedek)
        for a, b in (('fso-r', 'mso-r'), ('fso-l', 'mso-l'),
                     ('mfo-r', 'fmo-r'), ('mfo-l', 'fmo-l')):
            if a in ylm and b not in ylm:
                ylm[b] = ylm[a]
        for k in list(eksik):
            if k in ylm:
                lm[k] = ylm[k]
        eksik = [k for k in AD14 if k not in lm]
    if eksik:
        raise KeyError('%s: eksik landmark %s' % (klasor, eksik))
    return {k: np.asarray(lm[k], float) for k in AD14}


def yukle(ad, ds=4, yeniden=False):
    """Bir sablonu (yuzey + landmark) dondur; onbellege alir."""
    kayit = [o for o in OLGULAR if o[0] == ad]
    if not kayit:
        raise KeyError('bilinmeyen olgu: %s' % ad)
    k0 = kayit[0]
    _, klasor, tercih, kod = k0[:4]
    yedek = k0[4] if len(k0) > 4 else None       # `OLGULAR` 5. oge (hasta6)
    os.makedirs(ONBELLEK, exist_ok=True)
    yol = os.path.join(ONBELLEK, '%s_ds%d.npz' % (ad, ds))
    L = landmarklar(klasor, yedek)
    if os.path.exists(yol) and not yeniden:
        z = np.load(yol)
        return dict(ad=ad, kod=kod, v=z['v'], f=z['f'],
                    lm={k: L[k] for k in AD14})
    ct, rows, org = rayseg.load_ct(_bt_bul(klasor, tercih))
    v, f = Y.hazirla(ct, rows, org, L, AD14, ds=ds)
    np.savez_compressed(yol, v=v, f=f)
    return dict(ad=ad, kod=kod, v=v, f=f, lm=L)


def kutuphane(ds=4, disla=None, yeniden=False, ayrinti=True):
    """Butun sablonlari (istege gore birini dislayarak) dondur."""
    out = []
    for k0 in OLGULAR:
        ad, _, _, kod = k0[:4]
        if disla and ad == disla:
            continue
        s = yukle(ad, ds=ds, yeniden=yeniden)
        if ayrinti:
            print('  sablon %-8s (%s) tepe %6d  ucgen %6d' % (ad, kod, len(s['v']),
                                                              len(s['f'])))
        out.append(s)
    return out


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--ds', type=int, default=4)
    ap.add_argument('--yeniden', action='store_true')
    a = ap.parse_args()
    print('SABLON KUTUPHANESI (ds=%d)' % a.ds)
    K = kutuphane(ds=a.ds, yeniden=a.yeniden)
    print('\n%d sablon hazir. Onbellek: %s' % (len(K), ONBELLEK))
    json.dump({s['ad']: dict(kod=s['kod'], tepe=int(len(s['v'])),
                             ucgen=int(len(s['f']))) for s in K},
              open('/home/claude/an/out/sablon_ozet.json', 'w'),
              ensure_ascii=False, indent=1)
