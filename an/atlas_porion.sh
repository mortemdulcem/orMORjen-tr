#!/bin/bash
# Atlas olgularinda (hasta7-11) ALI ile RPo/LPo — `0BJ` §4.2.
# Yordam `ali_uyumluluk/porion_kosusu.sh` ile AYNI: olgu basina tek dizin, her
# adimdan sonra temp silinir, disk esigi altinda kendini durdurur (ALI skill §5).
AG=/home/claude/gelen/ali_zip/ALI_CBCT-main/src/AGENT
MOD=/home/claude/ali/models
CIK=/home/claude/porion/atlas
TMP=/home/claude/porion/atlas_temp
mkdir -p "$CIK" "$TMP"
for ct in "$@"; do
  d=$(basename "$(dirname "$ct")")                  # atlas_nii/h7/h7.nii.gz -> h7
  ad=$(echo "$d" | sed 's/^h/hasta/; s/m[0-9]*$//')  # h11 -> hasta11
  if [ -f "$CIK/${ad}_aso6.json" ]; then echo "[atla] $ad"; continue; fi
  av=$(df -BM --output=avail /home/claude | tail -1 | tr -dc '0-9')
  if [ "$av" -lt 1200 ]; then echo "DUR: disk az (${av} MB)"; break; fi
  rm -rf "$TMP"/* 2>/dev/null
  tek="$TMP/tek"; mkdir -p "$tek"
  cp "$ct" "$tek/$(basename "$ct")"
  echo "=== $ad ($(date +%H:%M), disk ${av} MB) ==="
  ( cd "$AG" && PYTHONPATH="$AG" timeout 900 python3 predict_landmarks.py \
      --dir_scans "$tek" --dir_models "$MOD" -lm RPo LPo \
      --dir_temp "$TMP/t" > "$TMP/log.txt" 2>&1 )
  out=$(find "$tek" -name "*_lm_Pred_*.mrk.json" | head -1)
  if [ -n "$out" ]; then cp "$out" "$CIK/${ad}_aso6.json"; echo "  -> BULUNDU"
  else echo "  -> CIKTI YOK"; tail -5 "$TMP/log.txt"; cp "$TMP/log.txt" "$CIK/${ad}_HATA.log" 2>/dev/null; fi
  rm -rf "$TMP"/* 2>/dev/null
done
echo "ATLAS PORION BITTI"
