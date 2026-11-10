#!/bin/bash
# ALI_CBCT ile porion kosusu — denek basina tek tek, her adimdan sonra temp temizlenir.
# `0AD` §2: ALI altin standartta 0,39-0,61 mm nokta hatasi; determinist.
AG=/home/claude/gelen/ali_zip/ALI_CBCT-main/src/AGENT
MOD=/home/claude/ali/models
CIK=/home/claude/porion/cikti
TMP=/home/claude/porion/temp
mkdir -p "$CIK" "$TMP"
for ct in "$@"; do
  d=$(basename "$ct" | sed -E 's/_CT\.nrrd$//')
  if [ -f "$CIK/${d}_porion.json" ]; then echo "[atla] $d"; continue; fi
  rm -rf "$TMP"/* 2>/dev/null
  tek="$TMP/tek"; mkdir -p "$tek"
  cp "$ct" "$tek/${d}_CT.nrrd"
  echo "=== $d ==="
  ( cd "$AG" && PYTHONPATH="$AG" timeout 900 python3 predict_landmarks.py \
      --dir_scans "$tek" --dir_models "$MOD" -lm RPo LPo \
      --dir_temp "$TMP/t" > "$TMP/log.txt" 2>&1 )
  out=$(find "$tek" -name "*_lm_Pred_*.mrk.json" | head -1)
  if [ -n "$out" ]; then cp "$out" "$CIK/${d}_porion.json"; echo "  -> bulundu"
  else echo "  -> CIKTI YOK"; cp "$TMP/log.txt" "$CIK/${d}_HATA.log" 2>/dev/null; fi
  rm -rf "$TMP"/* 2>/dev/null
done
echo "BITTI"
