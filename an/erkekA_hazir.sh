#!/bin/bash
# denek10/78: dogru yukleme secilerek (arastirmaci BT'si ile kesit+voksel eslesen) hazirlanmis seriler
export LANG=C.UTF-8 LC_ALL=C.UTF-8; cd /home/claude/an
for n in "$@"; do
  [ -f out/erkekA/denek${n}_OLCUM.json ] && { echo "denek$n zaten var"; continue; }
  python3 -u - $n > out/erkekA/kos_$n.log 2>&1 <<'P'
import sys, json, traceback
sys.path.insert(0,'/home/claude/orbita_hat'); sys.path.insert(0,'/home/claude/an')
import otomasyon2 as O
n=int(sys.argv[1]); ad='denek%d'%n
try:
    R=O.calistir('/home/claude/gelen3/hazir%d/se'%n, ad)
    json.dump(R, open('/home/claude/an/out/erkekA/%s_OLCUM.json'%ad,'w'), ensure_ascii=False, indent=1, default=str); print(ad,'BITTI')
except SystemExit as e: print(ad,'DURDU',e)
except Exception: print(ad,'HATA'); traceback.print_exc()
P
  echo "$(tail -1 out/erkekA/kos_$n.log)"
  rm -rf /home/claude/gelen3/hazir$n; echo "$(date "+%F %T") denek$n gecici acilmis DICOM (gelen3/hazir$n) silindi; ozgun: yukleme RARlari. Onay: \"devam et tamamla\"" >> /home/claude/ormorjen-tr/kohort/silme_kaydi/erkekA_gecici_silme.log
done
