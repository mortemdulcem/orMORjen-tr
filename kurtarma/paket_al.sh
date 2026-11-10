#!/bin/bash
# Yeni gelen denek*_slicer*.zip paketlerini kurtarma/paket altina alir. Idempotent.
cd /home/claude/kurtarma/paket || exit 1
yeni=0
for z in /mnt/user-data/uploads/denek*_slicer*.zip; do
  [ -e "$z" ] || continue
  ad=$(basename "$z" | sed 's/_slicer.*\.zip$//')
  [ -d "$ad" ] && continue
  mkdir -p "$ad" "_t_$ad"
  unzip -o -q "$z" -d "_t_$ad" 2>/dev/null
  find "_t_$ad" -type f -exec mv -n {} "$ad"/ \; 2>/dev/null
  rm -rf "_t_$ad"
  n=$(ls "$ad" 2>/dev/null | wc -l)
  if [ "$n" -lt 18 ]; then echo "$ad: EKSIK ($n dosya)"; else echo "$ad: alindi ($n dosya)"; yeni=$((yeni+1)); fi
done
echo "--- toplam paket: $(ls -d */ 2>/dev/null | wc -l) | bu turda yeni: $yeni"
