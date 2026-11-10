# -*- coding: utf-8 -*-
"""26-37 — 12 rim landmarkinin 3B koordinatlari, FRANKFORT catisinda.

`08` §C ve `0F` §25d geregi: karar A (Frankfort hizalamasi sonrasi yazilir).
Kapsama tamamlandiginda tek kosuda dokulur; bu dosya o kosudur.

`00` §0.2: hicbir ciktida hasta kimligi / TC yer almaz. Sutun anahtari
yalniz `denek` etiketidir.

CIKTI
  veri_disk/26-37_landmark_FRANKFORT.csv   36 sutun + denek  (hukum_A gecenler)
  veri_disk/frankfort_olcutler.json        olgu basina ALTI OLCUTUN SAYISI
                                            (hukum degil, sayi — `0Y` §5 usulu)
"""
import csv
import json
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frankfort as F
import kemik_kapisi as KK
import rayseg

TARAFLAR = ('r', 'l')
SUTUNLAR = [f'{k}-{s}_{eks}' for s in TARAFLAR for k in F.RIM_ORDER
            for eks in ('x', 'y', 'z')]          # 6 x 2 x 3 = 36


def bir_olgu(denek, paket, porion_json):
    """Bir denegin alti olcutu + (gecerse) Frankfort catisindaki 12 nokta."""
    po = F.oku_porion(porion_json)
    if not {'RPo', 'LPo'} <= set(po):
        return {'denek': denek, 'durum': 'porion_eksik',
                'bulunan': sorted(po)}, None
    lm = F.oku_oto(paket)
    eksik = [f'{k}-{s}' for s in TARAFLAR for k in F.RIM_ORDER
             if f'{k}-{s}' not in lm]
    if eksik:
        return {'denek': denek, 'durum': 'landmark_eksik', 'eksik': eksik}, None

    # olcut 4 — porion altinda kemik (`00` §0e-4 kapisi, esik 220)
    ct_yol = os.path.join(paket, f'{denek}_CT.nrrd')
    hu = None
    if os.path.exists(ct_yol):
        ct, rows, org = rayseg.load_ct(ct_yol)
        hu = {k: KK.maks_hu(ct, rows, org, po[k]) for k in ('RPo', 'LPo')}

    kayit = F.olcutler(po, lm, kemik_maks=hu)
    kayit['denek'] = denek
    kayit['durum'] = 'olculdu'

    if not kayit['hukum_A']:
        return kayit, None

    R, t = F.cerceve(po, lm)
    lm2 = F.uygula(R, t, lm)
    kayit['det_R'] = float(np.linalg.det(R))
    kayit['rijitlik_mm'] = F.rijitlik(lm, lm2)

    satir = {'denek': denek}
    for s in TARAFLAR:
        for k in F.RIM_ORDER:
            p = lm2[f'{k}-{s}']
            for i, eks in enumerate(('x', 'y', 'z')):
                v = round(float(p[i]), 4)
                satir[f'{k}-{s}_{eks}'] = v + 0.0 if v else 0.0   # -0,0 -> 0,0
    return kayit, satir


def kos(paketler, porion_dizin, cikti_dizin):
    os.makedirs(cikti_dizin, exist_ok=True)
    kayitlar, satirlar = [], []
    for paket in sorted(paketler):
        denek = os.path.basename(paket.rstrip('/'))
        pj = os.path.join(porion_dizin, f'{denek}_porion.json')
        if not os.path.exists(pj):
            kayitlar.append({'denek': denek, 'durum': 'porion_kosulmadi'})
            continue
        k, s = bir_olgu(denek, paket, pj)
        kayitlar.append(k)
        if s:
            satirlar.append(s)

    with open(os.path.join(cikti_dizin, 'frankfort_olcutler.json'), 'w',
              encoding='utf-8') as fh:
        json.dump(kayitlar, fh, ensure_ascii=False, indent=1)

    yol = os.path.join(cikti_dizin, '26-37_landmark_FRANKFORT.csv')
    with open(yol, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=['denek'] + SUTUNLAR)
        w.writeheader()
        for s in satirlar:
            w.writerow(s)
    return kayitlar, satirlar, yol


if __name__ == '__main__':
    import glob
    pk = sorted(glob.glob('/home/claude/kurtarma/paket/denek*'))
    kayitlar, satirlar, yol = kos(pk, '/home/claude/porion/cikti',
                                  '/home/claude/veri_disk')
    olc = [k for k in kayitlar if k.get('durum') == 'olculdu']
    print('paket %d · olculdu %d · hukum_A gecen %d'
          % (len(kayitlar), len(olc), len(satirlar)))
    print('CSV:', yol, '· sutun:', 1 + len(SUTUNLAR))
