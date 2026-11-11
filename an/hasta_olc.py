# -*- coding: utf-8 -*-
"""Hasta olgularini (hasta5-11) tam hatla olcer — AYRINTILI KALINLIK icin.

Giris NRRD'dir; `onisle.nrrd_hacim` kullanilir (olcum mantigi degismez).
Atlas uyesi olgular (hasta7-11) OLGU-BIRAK-BIR ile kosar: kendi sekil modeliyle
olculmezler (`disla=<olgu>`), yoksa sonuc dairesel olur.
Cikti: raporlar/<olgu>_OTO.json  — 24 kalinlik degeri dahil.
"""
import sys, os, glob, json, traceback
sys.path.insert(0, '/home/claude/orbita_hat'); sys.path.insert(0, '/home/claude/an')
import onisle
_DICOM_OKU = onisle.dicom_hacim                 # ozgun DICOM okuyucu saklanir


def _oku(kaynak):
    """Girisi bicimine gore yonlendirir: .nrrd -> nrrd_hacim, klasor -> DICOM."""
    if str(kaynak).lower().endswith('.nrrd'):
        return onisle.nrrd_hacim(kaynak)
    return _DICOM_OKU(kaynak)


onisle.dicom_hacim = _oku
import otomasyon2 as O

ATLAS = {'hasta7', 'hasta8', 'hasta9', 'hasta10', 'hasta11'}
KOK = '/home/claude/atlas_bt'

def bt_bul(d):
    """Once NRRD arar; yoksa en cok kesitli DICOM KLASORUNU dondurur."""
    n = [f for f in glob.glob(os.path.join(d, '**', '*.nrrd'), recursive=True)
         if 'seg' not in os.path.basename(f).lower()]
    if n:
        return max(n, key=os.path.getsize)
    en_iyi, en_cok = None, 0
    for kok, _, dosya in os.walk(d):
        dcm = [f for f in dosya if f.lower().endswith('.dcm')]
        if len(dcm) < 50:
            dcm = [f for f in dosya
                   if os.path.getsize(os.path.join(kok, f)) > 50000
                   and open(os.path.join(kok, f), 'rb').read(132)[128:132] == b'DICM']
        if len(dcm) > en_cok:
            en_iyi, en_cok = kok, len(dcm)
    return en_iyi

for h in sys.argv[1:]:
    ad = h.replace('h', 'hasta') if h.startswith('h') else h
    kis = 'h' + ad.replace('hasta', '')
    bt = bt_bul(os.path.join(KOK, kis))
    if not bt:
        print('%s: NRRD bulunamadi' % ad, flush=True); continue
    disla = ad if ad in ATLAS else None
    try:
        print('=' * 60, flush=True)
        print('%s <- %s%s' % (ad, os.path.basename(bt),
                              '  (OLGU-BIRAK-BIR: %s atlastan cikarildi)' % disla if disla else ''), flush=True)
        R = O.calistir(bt, ad, disla=disla)
        json.dump(R, open('/home/claude/an/out/%s_OLCUM.json' % ad, 'w'),
                  ensure_ascii=False, indent=1, default=str)
        print('%s BITTI' % ad, flush=True)
    except SystemExit as e:
        print('%s DURDU: %s' % (ad, e), flush=True)
    except Exception:
        print('%s HATA:' % ad, flush=True); traceback.print_exc()
