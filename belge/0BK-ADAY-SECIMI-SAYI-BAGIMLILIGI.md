# 0BK — orbita aday seçimindeki sayı bağımlılığı: düzeltildi

**Kök neden (ölçüldü):** `bul.orbita_bul` aday tepeleri D'ye göre sıralayıp ilk **600**'ünü
alıyordu. Voksel küçüldükçe tepe sayısı artıyor ve kontenjanı beyin bölgeleri (D maks
~39 mm) dolduruyor; orbitalar listeye giremiyor.

| | denek250 (düştü) | denek249 (geçti) |
|---|---|---|
| düzlem içi aralık | 0,488 mm | 0,561 mm |
| kafa voksel | 11,74 M | 8,10 M |
| tepe voksel | 917 | 200 |
| 14 mm'de teke inince | **7** | yeterli |
| açıklık testini geçen | **1** | ≥2 |

Yani kapı hastayı değil tarayıcı çözünürlüğünü eliyordu — `0BE`'nin kardeşi.

**Değişiklik:** `srt = np.argsort(dv)[::-1][:600]` → `srt = np.argsort(dv)[::-1]`.
14 mm teklestirme ve 60 küme sınırı aynen kaldı (fiziksel ölçütler).

**Nötrlük sınavı GEÇTİ:** denek201/206/212/226/236/249'da seçilen orbita konumu farkı
**0,0000 mm**. Bu yüzden 145 satırın hiçbiri yeniden ölçülmedi.

**denek250 artık ölçülüyor:** MSP 0,31 mm, hacim 24,3/23,2 cm³, RED 0, havuz True →
kohort **146 satır**.

**denek248 düzelmedi:** farklı kapı (rim eğrisi, `0BG`). Ön kayıt bunu vaat etmiyordu.

**Açık:** `maximum_filter(D, size=(9,9,5))` penceresi hâlâ vokselde tanımlı — ayrı ön kayıt.
