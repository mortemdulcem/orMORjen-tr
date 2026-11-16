#!/bin/bash
# Yeni olgu: ac -> olc (donmus hat) -> satir -> Slicer paketi -> acilan DICOM'u sil (kaynak RAR yerinde)
export LANG=C.UTF-8 LC_ALL=C.UTF-8
A=/mnt/user-data/attachments/9f46a888-8a38-562b-887d-ad413187b1aa; U=/mnt/user-data/uploads
S=/tmp/claude-0/-home-claude/9f46a888-8a38-562b-887d-ad413187b1aa/scratchpad/yeni
cd /home/claude/an
for n in "$@"; do
  f=$(ls $U/denek${n}dıcom.rar $A/*-denek${n}d_com.rar 2>/dev/null | head -1)
  [ -n "$f" ] || { echo "denek$n KAYNAK YOK"; continue; }
  rm -rf $S; mkdir -p $S; unrar x -idq "$f" $S/ || { echo "denek$n ACILAMADI"; continue; }
  ns=$(find $S -type d -name 'se0*' | wc -l); se=$(find $S -type d -name 'se0*' | head -1)
  mkdir -p /home/claude/gelen3/d$n; rm -rf /home/claude/gelen3/d$n/se; mv "$se" /home/claude/gelen3/d$n/se; rm -rf $S
  echo "denek$n seri=$ns kesit=$(ls /home/claude/gelen3/d$n/se | wc -l)"
  python3 -u kos10.py $n > out/kos_$n.log 2>&1
  grep -E "BITTI|DURDU|HATA|AYNI" out/kos_$n.log | head -3
  if [ -f out/denek${n}_OLCUM.json ] && grep -q "BITTI" out/kos_$n.log; then
    python3 satir_yeni.py denek$n 2>&1 | tail -1
    python3 -I teslim.py denek$n /home/claude/gelen3/d$n/se > out/teslim_$n.log 2>&1 && \
      (cd /home/claude && rm -f teslim/tam/denek${n}_slicer.zip && zip -qr teslim/tam/denek${n}_slicer.zip denek${n}_teslim && rm -rf denek${n}_teslim && echo "  paket TAMAM") || { echo "  paket HATA"; tail -2 out/teslim_$n.log; }
  fi
  rm -rf /home/claude/gelen3/d$n
  df -h / | tail -1 | awk '{print "  disk bos " $4}'
done
echo YENI_BITTI
