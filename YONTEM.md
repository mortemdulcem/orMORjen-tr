# Maske — ışın tabanlı kavite

**Dosya:** `an/rayseg.py` · tek çağrı yeri `kohort_maskesi()`

**AYAR (tek kaynak, `0P` C1):** ışın durma eşiği ve maskeden çıkarılan kemik
**aynı değişken** (160 HU) · hava ≤ −300 HU · 140 kesit × 360 ışın, adım
0,25 mm · medial koruma %75 · 1,5 mm açma + en büyük bileşen + delik doldurma ·
ön sınır: eğri varsa onun düzlemi (`plane_shift=0`), yoksa altıgen + 1,41 mm ·
`0N`: `alan_tek_yonlu=True`, `atu_bas_mm=12.0`.

**DOĞRULAMA (`0AT` §3):** ön kayıtlı sadakat sınavı — ölçüt koşmadan önce
yazıldı: hacim farkı <%1 **ve** Dice >0,95. Dört paketin sekiz orbitasında
**8/8 geçti**, Dice **1,000**, fark ≤%0,02.

⚠ **SINAVIN KAPSAMADIĞI:** lob temizliği kolu (bkz. `yontem/lob-temizligi`).
O dört olguda lob olmadığı için sınav o kolu **hiç çalıştırmadı**.
