# -*- coding: utf-8 -*-
"""Yeni olgular (DICOM'dan olculenler) icin kohort satiri.

`kohort/tablo_kur.satir` olgunun NRRD BASLIGINI okur; DICOM'dan olculen
olgularda NRRD yoktur. Tek fark budur: `kesit` ve `voksel_mm` raporun kendi
`bt` blogundan alinir. Diger butun alanlar `satir` ile BIREBIR ayni kurala gore
doldurulur; altigen yine `tablo_kur.altigen` ile hesaplanir.
"""
import sys, csv, json
from datetime import datetime
sys.path.insert(0, '/home/claude/an'); sys.path.insert(0, '/home/claude/orbita_hat')
sys.path.insert(0, '/home/claude/ormorjen-tr/kohort')
from tablo_kur import altigen

RAP = '/home/claude/orbita_hat/raporlar/%s_OTO.json'
LM  = '/home/claude/veri_disk/otomatik_landmark/%s_TAMOTO'
CSV = '/home/claude/ormorjen-tr/kohort/kohort_98.csv'


def satir(denek, basliklar, damga):
    rapor = json.load(open(RAP % denek, encoding='utf-8'))
    R = rapor['olcum']
    den = rapor.get('denetim', {})
    red, uya = den.get('red', []), den.get('uyari', [])
    s = {k: '' for k in basliklar}
    s.update({k: R[k] for k in basliklar if k in R})
    s.update(altigen(LM % denek, denek))
    s['denek'] = denek
    s['olcum_tarihi'] = damga
    s['kesit'] = int(rapor['bt']['kesit'])
    s['voksel_mm'] = round(float(rapor['bt']['voksel_mm']), 6)
    s['cekirdek'] = rapor['bt'].get('cekirdek', '')
    s['kemik_kapisi'] = ''                      # `0AS` kilit zinciri bu olgular icin YOK
    s['RED'] = len(red)
    s['UYARI'] = len(uya)
    s['red_kapilari'] = ';'.join(sorted({g.get('kapi', '') for g in red}))
    s['uyari_kapilari'] = ';'.join(sorted({g.get('kapi', '') for g in uya}))
    s['havuz'] = str(bool(den.get('hacim_veri_setine_yazilabilir')))
    s['sure_sn'] = rapor.get('sure_sn', '')
    return s


if __name__ == '__main__':
    basliklar = next(csv.reader(open(CSV)))
    eski = list(csv.DictReader(open(CSV)))
    var = {r['denek'] for r in eski}
    damga = datetime.now().strftime('%Y-%m-%d %H:%M')
    yeni = [satir(d, basliklar, damga) for d in sys.argv[1:] if d not in var]
    with open(CSV, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=basliklar); w.writeheader()
        for r in eski + yeni:
            w.writerow({k: r.get(k, '') for k in basliklar})
    print('yazildi: %d eski + %d yeni = %d satir' % (len(eski), len(yeni), len(eski)+len(yeni)))
    for r in yeni:
        print('  %-9s OW %s/%s · OH %s/%s · hacim %s/%s · APalan6 %s/%s · RED %s UYARI %s havuz %s'
              % (r['denek'], r['OW_sag'], r['OW_sol'], r['OH_sag'], r['OH_sol'],
                 r['hacim_sag'], r['hacim_sol'], r['APalan6_sag'], r['APalan6_sol'],
                 r['RED'], r['UYARI'], r['havuz']))
    bos = [k for k in basliklar if yeni and all(r.get(k) in ('', None) for r in yeni)]
    print('yeni satirlarda bos kalan %d sutun: %s' % (len(bos), ', '.join(bos)))
