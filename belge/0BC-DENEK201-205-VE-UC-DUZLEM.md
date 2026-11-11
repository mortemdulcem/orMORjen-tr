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
| denek204 | 163 | — | — | — | **ÖLÇÜLEMEDİ** (bkz. §4) | | |
| denek205 | 163 | 0 | 1 | evet | 46,86 / 47,82 | 38,77 / 44,90 | 26,87 / 29,59 |

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


---

## 5. TABLOYA YAZILDI — 98 → 102 OLGU

denek201, 202, 203, 205 `kohort_98.csv`'ye eklendi. Satırlar `an/satir_yeni.py`
ile kuruldu: `tablo_kur.satir` ile **birebir aynı kurallar**, tek fark `kesit`
ve `voksel_mm`'nin NRRD başlığı yerine raporun `bt` bloğundan alınması (bu
olgular DICOM'dan ölçüldü, NRRD yok). Altıgen yine `tablo_kur.altigen`.

### 5.1 Aykırı değer denetimi — yazmadan önce

Dört yeni olgunun on temel ölçüsü, 98 olgunun dağılımına göre z-skorlandı.

| sütun | kohort ort ± ss | 201 | 202 | 203 | 205 |
|---|---|---|---|---|---|
| OW_sag | 43,22 ± 3,48 | −0,39 | −1,54 | −0,92 | +1,05 |
| OH_sol | 37,75 ± 3,13 | −0,25 | 0,00 | −0,35 | +2,28 |
| BOW_ek | 99,53 ± 5,89 | −0,15 | −1,43 | −1,05 | +1,76 |
| hacim_sag | 28,28 ± 3,10 | −0,89 | **−2,53** | −1,82 | −0,46 |
| hacim_sol | 27,93 ± 2,88 | −0,91 | **−2,59** | −1,65 | +0,58 |
| APalan6_sol | 882,82 ± 140,59 | −0,26 | −0,43 | −0,29 | +2,18 |

Tek işaretlenen **denek202'nin hacimleri** (20,43 / 20,48 cm³). Hacim bandı
kapısından (19,9–33,4) geçiyor; n=98'de |z|=2,5 doğal değişkenlik sınırındadır.
**Hiçbiri dışlanmadı.**

⚠ denek205 için ilk bakışta "aralık dışı" dedim; kohortun gerçek ortalamasına
bakınca z=+1,05 çıktı. Dağılıma bakmadan "aykırı" demek, karar tablosu B1'in
uyardığı hatadır.

### 5.2 Yeni satırlarda boş kalan 17 sütun

`kemik_kapisi` ve `red_kapilari` (`0AS` kilit zinciri bu olguları kapsamıyor),
`mukerrer_uyari`, `derinlik_*` ve 10 apeks sütunu (apeks kapalı — `0AY`/`0AZ`),
`lob_cikan_*` (kod bozuk — `YONTEM-KATALOGU` B10).

## 6. denek204 — ÖLÇÜLEMEDİ olarak kaydedildi

Tanı: rim eğrisi **yalnız sağ tarafta** düştü (başarı %43–46; sol %79).
Üç düzlem denetiminde sağ orbitanın lateral-posterior duvarındaki kemik
kalın, yoğun ve düzensiz; solda aynı yerde ince ve düzgün bir duvar var.

**Araştırmacının hükmü (11:35):** patolojik değil, varyasyon ya da yaşa bağlı
değişiklik. Olgu kohorta uygundur; dışlama gerekçesi hastalık değildir.

**Ama ölçülemedi.** Araştırmacı önce tek olgu için eşik değiştirilmesini
istedi, sonra vazgeçti (11:38). Eşik değiştirilmedi:

1. `0K` §1 — hat kohort boyunca donmuştur.
2. `§0.12` — eşik, olgunun düştüğü **görüldükten sonra** seçilemez.
3. Ölçülmüş gerekçe: %43 başarı, eğri noktalarının yarısından fazlasının
   boşluktan geçirilmesi demektir; çıkan alan/hacim yanlış olur ve **sessizce**
   yanlış olur.

Kısmi ölçüm de yapılmadı: denetimde görüldü ki **98 olgunun hiçbirinde
rim-bağımlı sütun eksik değil**, yani kısmi ölçüm bu kohortta yerleşik bir
uygulama değildir; denek204 tek farklı kuralla üretilmiş satır olurdu.
