# -*- coding: utf-8 -*-
"""Donmus hattin 43 parametresini hazir bir PAKETTEN yeniden olcer.

NICIN AYRI BETIK: `olcum_zinciri.py`'nin komut satiri arayuzu rim egrilerini
`olc()`'ye GECIRMIYOR; kohort ise `otomasyon2.calistir()` uzerinden olculmustu.
Egri gecirilmezse APalan altigen kolundan hesaplanir ve kayitli degerden sapar
(denek98'de 1016,9 yerine 1051,0 olmasi gerekiyordu). Bu betik egrileri gecirir.

`on_sinir_duzlemde=True`: `0AT` SS2'nin kaydettigi kohort ayari "egri varsa
plane_shift=0" -- `olcum_zinciri.olc` belge dizesinin tam karsiligi.
"""
import json
import os
import sys

sys.path.insert(0, '/home/claude/an')
sys.path.insert(0, '/home/claude/orbita_hat')
import numpy as np
import nrrd
import params
import rayseg
import olcum_zinciri as OZ


def olc_paket(paket, denek):
    lm, egriler = params.load_scene(paket)
    ct, rows, org = rayseg.load_ct(os.path.join(paket, '%s_CT.nrrd' % denek))
    d, _ = nrrd.read(os.path.join(paket, '%s_Segmentation.seg.nrrd' % denek))
    R = OZ.olc(ct, rows, org, lm, (d == 1), (d == 2),
               rim_r=egriler.get('oto_rim_sag'), rim_l=egriler.get('oto_rim_sol'),
               kimlik=denek, kaynak='paket', on_sinir_duzlemde=True)
    return R


if __name__ == '__main__':
    for denek in sys.argv[1:]:
        paket = '/home/claude/kurtarma/paket/%s' % denek
        R = olc_paket(paket, denek)
        yol = '/home/claude/orbita_hat/raporlar/%s_OLCUM.json' % denek
        json.dump(R, open(yol, 'w'), ensure_ascii=False, indent=1, default=float)
        den = R.get('denetim', {})
        print('%-9s RED=%d UYARI=%d havuz=%s  hacim %.3f/%.3f  APalan %.1f/%.1f'
              % (denek, len(den.get('red', [])), len(den.get('uyari', [])),
                 den.get('hacim_veri_setine_yazilabilir'),
                 R['hacim_sag'], R['hacim_sol'], R['APalan_sag'], R['APalan_sol']))
