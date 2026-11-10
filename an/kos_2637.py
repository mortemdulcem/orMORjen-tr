# -*- coding: utf-8 -*-
"""26-37 TAM KOSU: olcutler + uc duzlem denetimi + CSV + kapsama raporu.

Kapsama iki AYRI sebebe bolunur (karistirilmaz):
  yontem kusuru : ALI kostu ama nokta YANLIS (olcutlerden dustu)
  altyapi kusuru: ALI hic kosamadi (bellek/sure) -- bu bir yontem hukmu DEGILDIR
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dok_2637 as D
import porion_denetim as PD

PAKET = '/home/claude/kurtarma/paket'
PORION = '/home/claude/porion/cikti'
CIKTI = '/home/claude/veri_disk'
DENETIM = '/home/claude/porion/denetim'


def main():
    paketler = sorted(glob.glob(os.path.join(PAKET, 'denek*')))
    kayitlar, satirlar, yol = D.kos(paketler, PORION, CIKTI)

    # uc duzlem denetim goruntusu — porionu olan her olgu icin
    for k in kayitlar:
        d = k['denek']
        pj = os.path.join(PORION, f'{d}_porion.json')
        ct = os.path.join(PAKET, d, f'{d}_CT.nrrd')
        png = os.path.join(DENETIM, f'{d}_porion_3duzlem.png')
        if os.path.exists(pj) and os.path.exists(ct) and not os.path.exists(png):
            try:
                PD.ciz(d, ct, pj, png)
            except Exception as e:
                print('denetim goruntusu basarisiz %s: %s' % (d, e))

    altyapi = [k['denek'] for k in kayitlar
               if k.get('durum') in ('porion_kosulmadi',)]
    olculdu = [k for k in kayitlar if k.get('durum') == 'olculdu']
    gecen = [k for k in olculdu if k['hukum_A']]
    dusen = [k for k in olculdu if not k['hukum_A']]

    print('=' * 68)
    print('KAPSAMA')
    print('  paket                     : %d' % len(kayitlar))
    print('  ALI kosamadi (ALTYAPI)    : %d  %s' % (len(altyapi), altyapi))
    print('  olculdu (yontem hukmu)    : %d' % len(olculdu))
    print('    -> alti olcutu gecen    : %d' % len(gecen))
    print('    -> olcutlerden dusen    : %d' % len(dusen))
    if olculdu:
        print('  YONTEM kapsamasi          : %d/%d = %%%.0f'
              % (len(gecen), len(olculdu), 100.0 * len(gecen) / len(olculdu)))
    print('=' * 68)
    print('%-10s %9s %8s %8s %9s %7s' %
          ('denek', 'biporion', 'ortaMSP', 'karsiOrb', 'maksHU', 'hukum'))
    for k in olculdu:
        hu = k.get('olcut4_maks_HU') or {}
        hum = min(hu.values()) if hu else float('nan')
        print('%-10s %9.2f %8.3f %8.3f %9.0f %7s' %
              (k['denek'], k['olcut3_biporion_mm'], k['olcut2_orta_MSP_mm'],
               k['olcut6_karsi_orbitale_mm_A'], hum,
               'GECTI' if k['hukum_A'] else 'DUSTU'))
    print('=' * 68)
    print('CSV  :', yol, '(%d satir x %d sutun)' % (len(satirlar), 1 + len(D.SUTUNLAR)))
    print('JSON :', os.path.join(CIKTI, 'frankfort_olcutler.json'))
    return kayitlar


if __name__ == '__main__':
    main()
