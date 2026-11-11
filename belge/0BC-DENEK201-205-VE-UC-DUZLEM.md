# 0BC — DENEK201–205 ÖLÇÜMÜ VE ÜÇ DÜZLEM DENETİMİ

**Tarih:** 2026-11-11 · **Girdi:** ham DICOM, elle hiçbir şey verilmedi
**Hat:** `orbita_hat/otomasyon2.py`, dondurulmuş yapılandırma

---

## 1. Önce yakalanan hata — ölçüm DURDURULDU ve düzeltildi

İlk koşuda hat şunu bastı ve **çökmeden devam etti**:

```
[4b MEDIAL] BASARISIZ, landmarklar DEGISMEDI: too many values to unpack (expected 4)
```

`d` ve `mf`'nin NICP düzeltmesi sessizce atlanıyordu. Bu hâliyle ölçülen
olguların landmarkları, denek1–98'i üreten hattınkinden **farklı** olurdu
(`0K` §1 ihlali). Sebep `an/sablon.py:98`'de sabit 4'lü açma; `OLGULAR`
kayıtlarından biri (hasta6) 5 öğelidir. Düzeltildi:

```python
for k0 in OLGULAR:
    ad, _, _, kod = k0[:4]
```

**Kohorta bulaşmadı:** aynı gün denek98 kilitli kayda karşı yeniden ölçüldü,
**27/27 birebir** çıktı. Ders `orbita-hat-donmus-ayar` skill'ine §5f olarak
eklendi.

## 2. Sonuç

| denek | kesit | RED | UYARI | havuz | OW sağ/sol | OH sağ/sol | hacim sağ/sol |
|---|---|---|---|---|---|---|---|
| denek201 | 143 | 0 | 1 | evet | 41,87 / 41,26 | 35,94 / 36,96 | 25,53 / 25,31 |
| denek202 | 143 | 0 | 2 | evet | 37,87 / 40,31 | 35,77 / 37,76 | 20,43 / 20,48 |
| denek203 | 159 | 0 | 4 | evet | 40,02 / 39,90 | 35,91 / 36,67 | 22,64 / 23,17 |
| denek204 | 163 | — | — | — | **DURDU: rim eğrisi üretilemedi** | | |
| denek205 | 163 | koşuyor | | | | | |

UYARI'lar: `kesit_apertur_asimi` (hepsinde), `apeks_kesiti` (denek203).

## 3. ÜÇ DÜZLEM DENETİMİ — gözle, sayıya ek olarak

Araç: `an/uc_duzlem.py`. Aksiyel + koronal + sagital, 14 landmark üstte,
orbita kutusuna kırpılmış (yüz görünmez, `§0.2`), pencere W1000/L400.

**İki kendi hatam bulundu ve düzeltildi, bozuk denetim kullanılmadı:**

1. `.mrk.json` dosyaları **LPS**, origin de LPS; araya gereksiz bir
   RAS↔LPS işaret çevirmesi koymuştum. Koronal kesit 137 yerine 375'e,
   yani beynin içine düşüyordu.
2. Koronal ve sagital panellerde **üst–alt tersti** (`origin='lower'` yoktu):
   supraorbital `mso` altta, infraorbital `o` üstte görünüyordu. Böyle
   okunsaydı landmarklar yer değiştirmiş sanılırdı.

**Düzeltilmiş denetimin sonucu (üç olgu, gözle):**

- `mf` ve `d`: medial orbital duvarda, lakrimal bölgede — **doğru**
- `fmo` ve `ek`: lateral orbital kenarda — **doğru**
- `mso`: supraorbital kenarın üstünde · `o`: infraorbital kenarın altında — **doğru**
- `apex`: posterior, sfenoid/optik kanal bölgesinde — **makul**, ama apeks
  zaten `0AY`/`0AZ` ile teze girmiyor

**Hüküm: denek201, 202, 203 üç düzlemde temiz.**

## 4. denek204 — başarısız olgu

`DURDU: rim eğrisi üretilemedi`. `0K` §4.4 gereği **yerine yenisi konmaz**;
"ölçülemedi" diye kaydedilir. Tanısı ayrıca yapılacak.
