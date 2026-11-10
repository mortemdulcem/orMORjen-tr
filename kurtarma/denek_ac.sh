#!/bin/bash
# Kullanim: denek_ac.sh denek97   -> /home/claude/gelen/<ad>/ icine DICOM cikarir
A=/mnt/user-data/attachments/9f46a888-8a38-562b-887d-ad413187b1aa
ad="$1"; [ -z "$ad" ] && { echo "kullanim: denek_ac.sh denekNN"; exit 1; }
hedef=/home/claude/gelen/$ad
[ -d "$hedef" ] && [ "$(ls -A "$hedef" 2>/dev/null | wc -l)" -gt 10 ] && { echo "$ad zaten acik ($(ls "$hedef"|wc -l) dosya)"; exit 0; }
tmp=/home/claude/gelen/_rar_$ad
mkdir -p "$tmp" "$hedef"
n=0
for f in "$A"/*${ad}d_com*.rar "$A"/*${ad}_*.rar; do
  [ -e "$f" ] || continue
  cp --update=none "$f" "$tmp/$(basename "$f" | sed 's/^[0-9a-f]*-//')" 2>/dev/null
  n=$((n+1))
done
[ "$n" -eq 0 ] && { echo "$ad: arsiv bulunamadi"; exit 1; }
p1=$(ls "$tmp"/*part1.rar 2>/dev/null | head -1)
[ -z "$p1" ] && p1=$(ls "$tmp"/*.rar 2>/dev/null | head -1)
LANG=C.UTF-8 unrar e -y "$p1" "$hedef/" >/dev/null 2>&1
echo "$ad: $(ls "$hedef" | wc -l) dosya"
