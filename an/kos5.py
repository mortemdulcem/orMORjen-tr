# -*- coding: utf-8 -*-
"""denek201-205 — dondurulmus hat, tam otomatik."""
import sys, os, json, glob, traceback
sys.path.insert(0, '/home/claude/orbita_hat'); sys.path.insert(0, '/home/claude/an')
import otomasyon2 as O

for n in (205,):
    ad = 'denek%d' % n
    try:
        se = ['/home/claude/gelen3/d%d/se' % n]
        if not se:
            print('%s: DICOM serisi bulunamadi' % ad, flush=True); continue
        print('=' * 60, flush=True); print(ad, '<-', se[0], flush=True)
        R = O.calistir(se[0], ad)
        json.dump(R, open('/home/claude/an/out/%s_OLCUM.json' % ad, 'w'),
                  ensure_ascii=False, indent=1, default=str)
        print('%s BITTI' % ad, flush=True)
    except Exception:
        print('%s HATA:' % ad, flush=True); traceback.print_exc()
