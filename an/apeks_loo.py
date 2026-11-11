# -*- coding: utf-8 -*-
"""APEKS NICP — OLGU-BIRAK-BIR DOGRULAMASI (`0M` SS4 olcut 4, SS5).

Her sablon YALNIZ diger 6 sablonla kestirilir. Hedefin kendi apeksi ne
hizalamaya ne kutuphaneye girer.

TUTTURULMASI GEREKEN (`0M` SS5.1, sonuc gorulmeden kilitlenmisti):
  olcut 1: apeks 3B hatasi ORTALAMA  < 5,14 mm   (kayitli olculen: 2,69)
  olcut 2: derinlik MAE kalibresiz   < 1,72 mm   (kayitli olculen: 1,65)
  olcut 3: sag/sol derinlik farkli (AI >= 0,50 mm) >= 6/7 olguda
Bu betik kayitli SAYILARI tutturmayi hedefler; tutmazsa kurulan surucu
`0M`'in yontemi DEGILDIR ve oyle bildirilir.

Derinlik tanimi (`0M` SS6, Gerec ve Yontem): apertur DUZLEMINE DIK uzaklik --
`olcum_zinciri.olc` ile ayni: |(apeks - c) . n|, (c,n) rim egrisinin duzlemi.
"""
import json
import os
import sys
import time

sys.path.insert(0, '/home/claude/an')
import numpy as np
import apeks_nicp as A
import params
import rayseg
import sablon
import yuzey as Y

OLGULAR = ('hasta5', 'hasta6', 'hasta7', 'hasta8', 'hasta9', 'hasta10', 'hasta11')
if os.environ.get('APEKS_OLGULAR'):
    OLGULAR = tuple(os.environ['APEKS_OLGULAR'].split(','))
DS = int(os.environ.get('APEKS_DS', '4'))   # `0M` ~800 sn/olgu kaydetmis; ds=4 100 sn verdi

# `0AY` on kaydi: CraniumPy'nin YAYIMLANMIS varsayilani (Apache-2.0,
# DOI 10.5281/zenodo.7430069, src/craniumpy_core/registration/nicp.py).
# Dis kaynakli sabit; bizim secimimiz degil. APEKS_CIZELGE=dis ile acilir.
CIZELGE = {}
if os.environ.get('APEKS_CIZELGE') == 'dis':
    import numpy as _np
    CIZELGE = {'alphalar': tuple(_np.linspace(200, 1, 20)), 'ic_tur': 3}


def _duzlem(lm, egriler, s):
    """Apertur duzlemi = ALTI RIM LANDMARKININ duzlemi (rim egrisi DEGIL).

    OLCULEREK belirlendi: `0M` SS5.2 hasta8 icin elle derinlik 41,32 / 41,66
    kaydetmis. Rim egrisinin duzlemi 42,85 / 43,09 veriyor; altigen duzlemi
    41,32 / 41,66 -- birebir. Yani ozgun LOO altigen duzlemini kullanmis.
    `egriler` imzada tutuluyor ama kullanilmiyor.
    """
    H = np.array([lm[b + '-' + s] for b in ('d', 'mf', 'mso', 'fmo', 'ek', 'o')])
    c, n, _, _ = params.plane(H)
    return c, n


def derinlik(lm, egriler, s, apeks):
    c, n = _duzlem(lm, egriler, s)
    return abs(float((np.asarray(apeks, float) - c) @ n))


def kos(cikti=None):
    cikti = cikti or os.environ.get('APEKS_CIKTI') or '/home/claude/an/out/apeks_loo_ds%d.json' % DS
    print('ds = %d' % DS, flush=True)
    kut = {ad: sablon.yukle(ad, ds=DS) for ad in OLGULAR}
    print('sablon tepe sayisi: %s' % {a: int(k['v'].shape[0]) for a, k in kut.items()}, flush=True)
    sonuc = []
    for hedef in OLGULAR:
        t0 = time.time()
        kayit = [k for ad, k in kut.items() if ad != hedef]      # olgu-birak-bir
        S = kut[hedef]
        lm = S['lm']
        hiza = {k: lm[k] for k in A.HIZA_NOKTA if k in lm}       # apeks YOK
        kes, bilgi = A.kestir(S['v'], hiza, kayit, **CIZELGE)
        _, egriler = params.load_scene(
            [o for o in sablon.OLGULAR if o[0] == hedef][0][1])
        r = {'olgu': hedef, 'sure_sn': round(time.time() - t0, 1)}
        for s, etiket in (('r', 'sag'), ('l', 'sol')):
            k = 'apex-' + s
            p = kes.get(k)
            if p is None:
                r[etiket] = None
                continue
            elle = np.asarray(lm[k], float)
            r[etiket] = {
                'hata_3b_mm': round(float(np.linalg.norm(np.asarray(p, float) - elle)), 3),
                'derinlik_kestirim': round(derinlik(lm, egriler, s, p), 3),
                'derinlik_elle': round(derinlik(lm, egriler, s, elle), 3),
                'yayilim_mm': (None if bilgi.get('yayilim', {}).get(k) is None
                               else round(float(bilgi['yayilim'][k]), 3)),
            }
        sonuc.append(r)
        print('%-8s %6.0f sn  sag %s  sol %s' % (
            hedef, r['sure_sn'],
            '-' if not r.get('sag') else '%.2f mm' % r['sag']['hata_3b_mm'],
            '-' if not r.get('sol') else '%.2f mm' % r['sol']['hata_3b_mm']), flush=True)
        json.dump(sonuc, open(cikti, 'w'), ensure_ascii=False, indent=1)

    h = [r[t]['hata_3b_mm'] for r in sonuc for t in ('sag', 'sol') if r.get(t)]
    d = [abs(r[t]['derinlik_kestirim'] - r[t]['derinlik_elle'])
         for r in sonuc for t in ('sag', 'sol') if r.get(t)]
    ai = sum(1 for r in sonuc if r.get('sag') and r.get('sol') and
             abs(r['sag']['derinlik_kestirim'] - r['sol']['derinlik_kestirim']) >= 0.50)
    print('=' * 60)
    print('olcut 1  apeks 3B hatasi ort : %.2f mm   (taban <5,14 · kayit 2,69)'
          % (float(np.mean(h)) if h else float('nan')))
    print('olcut 2  derinlik MAE        : %.2f mm   (taban <1,72 · kayit 1,65)'
          % (float(np.mean(d)) if d else float('nan')))
    print('olcut 3  sag/sol farkli      : %d/7      (taban >=6)' % ai)
    print('=' * 60)
    return sonuc


if __name__ == '__main__':
    kos()
