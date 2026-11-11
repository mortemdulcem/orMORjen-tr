# -*- coding: utf-8 -*-
"""kohort.csv'ye kilit sonrasi olgulari ekler. `tablo_uret.py` kayboldu (konteyner).

HER SUTUNUN KAYNAGI ACIKCA BELLI:
  29 olcum sutunu  -> orbita_hat/raporlar/<denek>_OLCUM.json  (0AS/0AT ile dogrulandi)
   6 altigen sutun -> `0T` tanimi, uc olguda dogrulandi (0AV SS10)
  kesit/voksel_mm  -> paketin CT nrrd basligi
  RED/UYARI/havuz  -> raporun denetim bolumu
  cekirdek/kemik_kapisi -> `0AS` kilit zinciri (yalniz denek98/99/100)
  BOS BIRAKILANLAR -> apeks (10 sutun, sablon eksik) · lob (2 sutun, kod inert)
                      mukerrer_uyari (parmak izi veritabani kayip) · sure_sn
"""
import csv
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, '/home/claude/an')
import numpy as np
import nrrd
import params

ORD = ('d', 'mf', 'mso', 'fmo', 'ek', 'o')
CSV = '/home/claude/kohort/kohort.csv'
RAP = '/home/claude/orbita_hat/raporlar/%s_OLCUM.json'
PAKET = '/home/claude/kurtarma/paket/%s'
# `0AS` kilit zincirinden; denek101 o zincirde YOK -> bos birakilir
AS_KAYIT = {'denek98': ('BONEPLUS 120 kVp', 'GECTI'),
            'denek99': ('BONEPLUS 120 kVp', 'GECTI'),
            'denek100': ('BONEPLUS 120 kVp', 'GECTI')}


def altigen(paket, denek):
    lm, _ = params.load_scene(paket)
    cik = {}
    for s, S in (('r', 'sag'), ('l', 'sol')):
        H = np.array([lm[b + '-' + s] for b in ORD])
        c, n, _, _ = params.plane(H)
        u, sv, vt = np.linalg.svd(H - c)
        x = (H - c) @ vt[0]
        y = (H - c) @ vt[1]
        cik['APalan6_' + S] = round(float(abs(np.dot(x, np.roll(y, -1)) -
                                             np.dot(y, np.roll(x, -1))) / 2), 2)
        cik['APcevre6_' + S] = round(params.perim(H), 2)
        cik['APduzlemsizlik6_' + S] = round(float(np.abs((H - c) @ n).mean()), 4)
    return cik


def satir(denek, basliklar, damga):
    R = json.load(open(RAP % denek))
    paket = PAKET % denek
    h = nrrd.read_header(os.path.join(paket, '%s_CT.nrrd' % denek))
    sd = np.array(h['space directions'], float)
    sp = float(np.linalg.norm([r for r in sd if not np.isnan(r).any()][0]))
    den = R.get('denetim', {})
    red, uya = den.get('red', []), den.get('uyari', [])
    cek, kemik = AS_KAYIT.get(denek, ('', ''))

    s = {k: '' for k in basliklar}
    s.update({k: R[k] for k in basliklar if k in R})
    s.update(altigen(paket, denek))
    s['denek'] = denek
    s['olcum_tarihi'] = damga
    s['kesit'] = int(h['sizes'][2])
    s['voksel_mm'] = round(sp, 6)
    s['cekirdek'] = cek
    s['kemik_kapisi'] = kemik
    s['RED'] = len(red)
    s['UYARI'] = len(uya)
    s['red_kapilari'] = ';'.join(sorted({g.get('kapi', '') for g in red}))
    s['uyari_kapilari'] = ';'.join(sorted({g.get('kapi', '') for g in uya}))
    # mevcut 94 satirin yazimi 'True'/'False' -- ayni bicim korunur
    s['havuz'] = str(bool(den.get('hacim_veri_setine_yazilabilir')))
    return s


def main(yeniler):
    basliklar = next(csv.reader(open(CSV)))
    eski = list(csv.DictReader(open(CSV)))
    var = {r['denek'] for r in eski}
    damga = datetime.now().strftime('%Y-%m-%d %H:%M')
    yeni = [satir(d, basliklar, damga) for d in yeniler if d not in var]
    cikti = '/home/claude/kohort/kohort_%d.csv' % (len(eski) + len(yeni))
    with open(cikti, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=basliklar)
        w.writeheader()
        for r in eski + yeni:
            w.writerow({k: r.get(k, '') for k in basliklar})
    bos = [k for k in basliklar if yeni and all((r.get(k) in ('', None)) for r in yeni)]
    print('yazildi: %s  (%d eski + %d yeni)' % (cikti, len(eski), len(yeni)))
    print('yeni satirlarda BOS kalan %d sutun:' % len(bos))
    print(' ', ', '.join(bos))
    return cikti


if __name__ == '__main__':
    main(sys.argv[1:] or ['denek98', 'denek99', 'denek100', 'denek101'])
