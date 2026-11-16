#!/bin/bash
# Pilot duzeltme paketlerini sirayla ac -> elle_olc -> acilan kopyayi sil (kaynak RAR ekte duruyor)
export LANG=C.UTF-8 LC_ALL=C.UTF-8
A=/mnt/user-data/attachments/9f46a888-8a38-562b-887d-ad413187b1aa
T=/tmp/claude-0/-home-claude/9f46a888-8a38-562b-887d-ad413187b1aa/scratchpad/pilot
isle(){ ad=$1; shift; rm -rf $T; mkdir -p $T/r $T/x; i=1
  for p in "$@"; do cp "$A/$p" $T/r/p.part$i.rar; i=$((i+1)); done
  unrar x -idq $T/r/p.part1.rar $T/x/ || { echo "$ad ACILAMADI"; return; }
  kl=$(dirname "$(find $T/x -name '*.mrml' | head -1)")
  ct=$(ls -S "$kl"/*.nrrd | grep -v seg.nrrd | head -1)
  cd /home/claude/an && python3 elle_olc.py $ad "$ct" "$kl" 2>&1 | tail -1
  mkdir -p /home/claude/gelen_elle/$ad && cp "$kl"/*.mrk.json "$kl"/*.mrml /home/claude/gelen_elle/$ad/ 2>/dev/null
  rm -rf $T; }
isle hasta12 0d66f611-hasta12_part1.rar d21c369b-hasta12_part2.rar
isle hasta13 e5df41fb-hasta13_otomatik_d_zeltme__l__m_.part1.rar 6e30d995-hasta13_otomatik_d_zeltme__l__m_.part2.rar
isle hasta14 593c90d4-hasta14_otomatik__l__m_d_zeltme.part1.rar bac136c2-hasta14_otomatik__l__m_d_zeltme.part2.rar 82249b14-hasta14_otomatik__l__m_d_zeltme.part3.rar
isle hasta15 5aadc0cc-hasta15_d_zeltme.part1.rar 1362e8b9-hasta15_d_zeltme.part2.rar 104837e3-hasta15_d_zeltme.part3.rar
isle hasta16 10a43f36-hasta16_2._d_zeltme.part1.rar 00ff4bfe-hasta16_2._d_zeltme.part2.rar
isle hasta17 b8ae6097-hasta17otomatikd_zeltmesi.part1.rar c0f47669-hasta17otomatikd_zeltmesi.part2.rar
isle hasta18 50532559-hasta18otomatikd_zeltme.part1.rar 488f2c1b-hasta18otomatikd_zeltme.part2.rar f38d4e6e-hasta18otomatikd_zeltme.part3.rar
echo HEPSI_BITTI
