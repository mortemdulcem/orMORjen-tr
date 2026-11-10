#!/bin/bash
# ASO'nun yedi landmarkini ALI ile cikarir (Ba S N RPo LPo ROr LOr).
# `0AV` §8.5: ASO'nun yayimlanmis kapisi (15 mm uzaklik + 0,4 rad yon)
# bizim alti ad hoc olcutumuzun yerine gecebilsin diye.
AG=/home/claude/gelen/ali_zip/ALI_CBCT-main/src/AGENT
MOD=/home/claude/ali/models
CIK=/home/claude/porion/cikti7
TMP=/home/claude/porion/temp7
mkdir -p "$CIK" "$TMP"
for ct in "$@"; do
  d=$(basename "$ct" | sed -E 's/_CT\.nrrd$//')
  if [ -f "$CIK/${d}_aso7.json" ]; then echo "[atla] $d"; continue; fi
  rm -rf "$TMP"/* 2>/dev/null
  tek="$TMP/tek"; mkdir -p "$tek"
  cp "$ct" "$tek/${d}_CT.nrrd"
  echo "=== $d  $(date +%H:%M:%S) ==="
  ( cd "$AG" && PYTHONPATH="$AG" timeout 2400 python3 predict_landmarks.py \
      --dir_scans "$tek" --dir_models "$MOD" -lm Ba S N RPo LPo ROr LOr \
      --dir_temp "$TMP/t" > "$TMP/log.txt" 2>&1 )
  # ALI cikitiyi GRUP BASINA ayri dosyaya yazar (CB: Ba,S,N,RPo,LPo | U: ROr,LOr).
  # Hepsi toplanip tek dosyada birlestirilir.
  mapfile -t outs < <(find "$tek" -name "*_lm_Pred_*.mrk.json")
  if [ ${#outs[@]} -gt 0 ]; then
    python3 /home/claude/an/birlestir_mrk.py "$CIK/${d}_aso7.json" "${outs[@]}" \
      && echo "  -> ${#outs[@]} dosya birlestirildi" \
      || { echo "  -> BIRLESTIRME HATASI"; cp "$TMP/log.txt" "$CIK/${d}_HATA.log" 2>/dev/null; }
  else echo "  -> CIKTI YOK"; cp "$TMP/log.txt" "$CIK/${d}_HATA.log" 2>/dev/null; tail -5 "$TMP/log.txt"; fi
  rm -rf "$TMP"/* 2>/dev/null
done
echo "YEDI LANDMARK KOSUSU BITTI"
echo "basarili: $(ls $CIK/*_aso7.json 2>/dev/null | wc -l) / 14"
