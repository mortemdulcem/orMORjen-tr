# -*- coding: utf-8 -*-
"""gelen2 paketlerindeki BT NRRD'lerinden olcum — AYRINTILI KALINLIK icin.

Bu olgular kohortta ZATEN var; amac kalinligin 24 degerini doldurmaktir.
Giris bicimi NRRD (paket icindeki <denek>_CT.nrrd); olcum mantigi degismez.
`0K` §1: yeniden olcum kalinlik DISINDAKI degerleri degistirmemelidir — cagiran
betik bunu satir satir karsilastirir.
"""
import sys, os, glob, json, traceback
sys.path.insert(0, '/home/claude/orbita_hat'); sys.path.insert(0, '/home/claude/an')
import onisle
_DICOM_OKU = onisle.dicom_hacim
def _oku(k):
    return onisle.nrrd_hacim(k) if str(k).lower().endswith('.nrrd') else _DICOM_OKU(k)
onisle.dicom_hacim = _oku
import otomasyon2 as O

for n in sys.argv[1:]:
    ad = 'denek%s' % n
    bt = glob.glob('/home/claude/gelen2/d%s/%s/%s_CT.nrrd' % (n, ad, ad))
    if not bt:
        print('%s: CT NRRD yok' % ad, flush=True); continue
    try:
        print('=' * 60, flush=True); print('%s <- %s' % (ad, os.path.basename(bt[0])), flush=True)
        R = O.calistir(bt[0], ad)
        json.dump(R, open('/home/claude/an/out/%s_OLCUM.json' % ad, 'w'),
                  ensure_ascii=False, indent=1, default=str)
        print('%s BITTI' % ad, flush=True)
    except SystemExit as e:
        print('%s DURDU: %s' % (ad, e), flush=True)
    except Exception:
        print('%s HATA:' % ad, flush=True); traceback.print_exc()
