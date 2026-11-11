#!/bin/bash
# Kuyruk kostukca biten olgularin satirlarini tabloya yazar.
# Capraz denetim satir_yeni.py icinde (0BF §4): kutukle celisen satir YAZILMAZ.
cd /home/claude/an
CSV=/home/claude/ormorjen-tr/kohort/kohort_98.csv
while true; do
  for d in $(grep -o 'denek[0-9]\+ BITTI' out/kos_kuyruk.log 2>/dev/null | awk '{print $1}' | sort -u); do
    if ! cut -d, -f1 "$CSV" | grep -qx "$d"; then
      echo "[isci] $d yaziliyor $(date +%H:%M)"
      python3 -u satir_yeni.py "$d" 2>&1 | sed -n '2p'
    fi
  done
  pgrep -f "kuyruk.sh" > /dev/null || { echo "[isci] kuyruk bitti, son tarama $(date +%H:%M)"; break; }
  sleep 20
done
for d in $(grep -o 'denek[0-9]\+ BITTI' out/kos_kuyruk.log 2>/dev/null | awk '{print $1}' | sort -u); do
  cut -d, -f1 "$CSV" | grep -qx "$d" || python3 -u satir_yeni.py "$d" 2>&1 | sed -n '2p'
done
echo "[isci] TAMAM · tablo satir sayisi: $(( $(wc -l < $CSV) - 1 ))"
