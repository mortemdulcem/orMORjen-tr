#!/bin/bash
cd /home/claude/an
for n in "$@"; do
  f=$(ls /mnt/user-data/uploads/denek${n}_slicer*d*.rar 2>/dev/null | sort | tail -1)
  [ -n "$f" ] || { echo "denek$n DOSYA YOK"; continue; }
  python3 duzeltme_isle.py denek$n "$f" 2>&1 | grep -v Warn | tail -1
done
echo PARTI_BITTI
