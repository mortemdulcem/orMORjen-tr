# -*- coding: utf-8 -*-
import sys, os, json, traceback
sys.path.insert(0,'/home/claude/orbita_hat'); sys.path.insert(0,'/home/claude/an')
import otomasyon2 as O
ad, kaynak = 'denek102', '/home/claude/gelen/denek102'
try:
    print('='*60, flush=True); print(ad, '<-', kaynak, flush=True)
    R = O.calistir(kaynak, ad)
    json.dump(R, open('/home/claude/an/out/%s_OLCUM.json'%ad,'w'),
              ensure_ascii=False, indent=1, default=str)
    print('%s BITTI'%ad, flush=True)
except SystemExit as e:
    print('%s DURDU: %s'%(ad,e), flush=True)
except Exception:
    print('%s HATA:'%ad, flush=True); traceback.print_exc()
