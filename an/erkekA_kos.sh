#!/bin/bash
# Erkek olgulari BUGUNKU donmus hatla (A) yeniden olc — yalniz OLCUM json + OTO landmark klasoru.
# kohort_98.csv'ye YAZILMAZ (karar ayri). 101-102 KOR TEST: asla.
export LANG=C.UTF-8 LC_ALL=C.UTF-8
A=/mnt/user-data/attachments/9f46a888-8a38-562b-887d-ad413187b1aa
S=/tmp/claude-0/-home-claude/9f46a888-8a38-562b-887d-ad413187b1aa/scratchpad/ea
cd /home/claude/an
for n in "$@"; do
  [ "$n" -ge 101 ] && [ "$n" -le 200 ] && { echo "denek$n KOR TEST - ATLANDI"; continue; }
  [ -f out/erkekA/denek${n}_OLCUM.json ] && { echo "denek$n zaten var"; continue; }
  rm -rf $S; mkdir -p $S/r $S/x
  p1=$(ls $A/*-denek${n}d_com.part1.rar 2>/dev/null | head -1); p2=$(ls $A/*-denek${n}d_com.part2.rar 2>/dev/null | head -1); tek=$(ls $A/*-denek${n}d_com.rar 2>/dev/null | head -1)
  if [ -n "$p1" ]; then cp "$p1" $S/r/a.part1.rar; [ -n "$p2" ] && cp "$p2" $S/r/a.part2.rar; ilk=$S/r/a.part1.rar
  elif [ -n "$tek" ]; then cp "$tek" $S/r/a.rar; ilk=$S/r/a.rar
  else echo "denek$n KAYNAK YOK"; continue; fi
  unrar x -o+ -idq $ilk $S/x/ || { echo "denek$n ACILAMADI"; continue; }
  rm -rf $S/r
  se=$(find $S/x -type d -name 'se0*' -exec sh -c 'echo $(ls "$1" | wc -l) "$1"' _ {} \; | sort -n | tail -1 | cut -d' ' -f2-)
  mkdir -p /home/claude/gelen3/d$n; rm -rf /home/claude/gelen3/d$n/se; mv "$se" /home/claude/gelen3/d$n/se; rm -rf $S
  python3 -u - $n > out/erkekA/kos_$n.log 2>&1 <<'P'
import sys, json, traceback
sys.path.insert(0,'/home/claude/orbita_hat'); sys.path.insert(0,'/home/claude/an')
import otomasyon2 as O
n=int(sys.argv[1]); ad='denek%d'%n
try:
    R=O.calistir('/home/claude/gelen3/d%d/se'%n, ad)
    json.dump(R, open('/home/claude/an/out/erkekA/%s_OLCUM.json'%ad,'w'), ensure_ascii=False, indent=1, default=str); print(ad,'BITTI')
except SystemExit as e: print(ad,'DURDU',e)
except Exception: print(ad,'HATA'); traceback.print_exc()
P
  echo "$(tail -1 out/erkekA/kos_$n.log)  $(grep -o 'AYNI TARAMA[^(]*' out/erkekA/kos_$n.log | head -1)"
  rm -rf /home/claude/gelen3/d$n; echo "$(date "+%F %T") denek$n gecici acilmis DICOM (gelen3/d$n) silindi; ozgun: yukleme RARlari. Onay: \"devam et tamamla\" 2026-11-23 22:28" >> /home/claude/ormorjen-tr/kohort/silme_kaydi/erkekA_gecici_silme.log
done
echo PARTI_BITTI
