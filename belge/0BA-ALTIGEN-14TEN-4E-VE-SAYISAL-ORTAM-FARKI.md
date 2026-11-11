# 0BA — ALTIGEN SÜTUNLARI 14'TEN 4'E İNDİ · SAYISAL ORTAM FARKI SAPTANDI

**Tarih:** 2026-11-11 · **Bağlam:** `0AW` (98 satır), `0AT` (konteyner sonrası kurulum)

---

## 1. Doldurulan

| tarih | olgular | hücre |
|---|---|---|
| bugün, 1. tur | denek86, 92, 93, 94, 95, 96, 97 | 42 |
| bugün, 2. tur | denek83, 85, 90 | 18 |

Altıgen boşluğu **14 → 4**. Kalan: **denek84, denek87, denek89, denek91**
(Slicer paketleri henüz gelmedi).

`kohort_98.csv` SHA-256:
- dün `ecc02aa7439f828d4427e4a094e1f170b3d61c149c3be7f2c90848f1ef340354`
- 1. tur `2f730a624139883386453030ba69cce20a83bf9aef76b8a5ce883b18d56445f1`
- **şimdi `baaa21485761e93d4a7d3a1715749a39aac2fef0a6a099bc79135fd46ff285d6`**

Kod: `kohort/tablo_kur.altigen()` **aynen**, yeni kod yazılmadı.

## 2. SAYISAL ORTAM FARKI — `0AW`'nin "birebir" ölçütü için önemli

Zaten dolu dört olgu (denek10, 11, 78, 81) yeniden ölçülüp kilitli değerle
karşılaştırıldı. Hiçbiri 6/6 birebir çıkmadı:

| olgu | birebir | sapan değerler |
|---|---|---|
| denek81 | 3/6 | alan sağ 921,1 → 921,11 · alan sol 931,4 → 931,39 · dz sağ 2,525 → 2,5249 |
| denek10 | 3/6 | alan sağ 877,82 → 877,81 · alan sol 888,48 → 888,5 · dz sol 2,5312 → 2,5313 |
| denek11 | 2/6 | alan sağ 898,11 → 898,1 · alan sol 884,36 → 884,35 · dz sağ/sol son basamak |
| denek78 | 4/6 | alan sol 894,41 → 894,42 · dz sol 1,875 → 1,8748 |

**Desen:** sapma her zaman son basamakta — alanlarda ±0,01 mm² (**%0,001**),
düzlemsizlikte ±0,0002 mm. **Çevre hiçbir olguda sapmadı.**

**Sebep ölçüldü, tahmin edilmedi.** Çevre (`params.perim`) doğrudan nokta
mesafelerinden gelir; alan ve düzlemsizlik ise `np.linalg.svd` ile kurulan
en-iyi-uyum düzleminin izdüşümünden gelir. Konteyner yeniden kurulduğunda
BLAS/LAPACK sürümü değişti; SVD son bitlerde başka sonuç veriyor ve bu,
ayakkabı-bağı alanına 1e-5 bağıl düzeyde yansıyor.

**Doğrulayıcı kanıt:** bugün **bu ortamda** hesaplanan denek98 (`0AW`
sadakat sınavı) ve denek92–97 kendi değerleriyle **birebir** tuttu. Sapanların
hepsi **eski konteynerde** hesaplanmış satırlar. Yani fark olgularda değil,
ortamda.

### 2.1 Sonuç

1. Hat **sadıktır**; sapma 1e-5 bağıl düzeydedir ve hiçbir ölçüm anlamı taşımaz
   (alan ~900 mm², sapma 0,01 mm²).
2. `0AW` §2.1'in *"birebir yeniden üretildi"* ifadesi **aynı ortam içinde**
   geçerlidir. Konteyner değişiminden sonra ölçüt **son basamak toleransı**
   olmalıdır: alan ±0,02 mm², çevre ±0,01 mm, düzlemsizlik ±0,0005 mm.
3. Zaten dolu satırlar **değiştirilmedi** — eski değerler korundu, yalnız boş
   hücreler dolduruldu. Tablo içinde iki ortamdan değer bulunması bu tolerans
   düzeyinde sorun yaratmaz, ama tezin yöntem bölümünde **belirtilmelidir**.
4. Tezde yeniden üretilebilirlik iddiası *"bit düzeyinde"* değil
   *"ölçüm anlamı taşıyan her basamakta"* diye yazılmalıdır.

## 3. Hâlâ eksik olanlar

| sütun | eksik | sebep |
|---|---|---|
| `derinlik_sag/sol` | 76 / 69 | apeks ölçülemiyor (`0AY`, `0AZ`) — kalıcı |
| 10 apeks sütunu | 4 | aynı — kalıcı |
| `lob_cikan_sag/sol` | 19 | `lob_temizle` bozuk (`YONTEM-KATALOGU` B10) |
| altıgen (6 sütun) | 4 | denek84, 87, 89, 91 paketi gelmedi |
