# 43 parametre ölçüm zinciri

**Dosya:** `orbita_hat/olcum_zinciri.py` · sürücü `an/olc_paket.py`

**DOĞRULAMA:** denek98/99/100/101 yeniden ölçüldü ve `0AS`/`0AT`'nin kilitli
kayıtlarıyla **birebir** örtüştü:

| denek | hacim sağ/sol | APalan sağ/sol | RED/UYARI |
|---|---|---|---|
| denek98 | 22,246 / 22,746 | 1051,0 / 1057,0 | 0 / 2 |
| denek99 | 29,929 / 29,458 | 1161,2 / 1211,4 | 0 / 2 |
| denek100 | 24,850 / 26,094 | 1337,7 / 1426,8 | 0 / 1 |
| denek101 | 26,825 / 26,315 | 1177,5 / 1188,7 | 0 / 2 |

⚠ **TUZAK — bilinmesi şart.** `olcum_zinciri.py`'nin komut satırı arayüzü rim
eğrilerini `olc()`'ye **GEÇİRMİYOR**; kohort ise `otomasyon2.calistir()`
üzerinden ölçülmüştü. Eğri geçirilmezse APalan **altıgen yedek kolundan**
hesaplanır ve kayıttan sapar (denek98: 1051,0 yerine **1016,9**). Hata vermez,
sessizce yanlış sayı üretir. `an/olc_paket.py` eğrileri geçirir ve
`on_sinir_duzlemde=True` kullanır (`0AT` §2'nin kaydettiği kohort ayarı).
