# 0AX — APEKS NICP YENİDEN KURULUMU İKİ ÇÖZÜNÜRLÜKTE YANLIŞLANDI

**Tarih:** 2026-11-11
**Bağlam:** `0AT` (konteyner sonrası hat yeniden kurulumu) · `0M` §3 KOL B, §5.1 · `0AW` (98 satırlık kohort tablosu)
**Durum:** apeks adımı GERİ KURULAMADI. `kohort_98.csv`'nin 10 apeks sütunu BOŞ bırakıldı.

---

## 1. Neden yeniden kurulmaya çalışıldı

Konteyner kaybı sonrası `0M`'in apeks NICP sürücüsü diskte yoktu. `0AT` §3 üç adımın
kayıp olduğunu saptamıştı. Bunlardan apeks adımı, `0M` §3 KOL B'nin tarifinden
(HEDEF = apex-r/apex-l, HİZALAMA = diğer 12 nokta, apeks hizalamaya KATILMAZ)
yeniden yazıldı: `an/apeks_nicp.py` + `an/apeks_loo.py`.

Yeniden kurulumun geçerli sayılması için `0M` §5.1'in **sonuç görülmeden
kilitlenmiş** üç ölçütünü tutturması gerekiyordu:

| ölçüt | ön kayıtlı taban | `0M`'in kaydettiği ölçüm |
|---|---|---|
| 1 — apeks 3B hatası ortalaması | < 5,14 mm | 2,69 mm |
| 2 — derinlik MAE (kalibresiz) | < 1,72 mm | 1,65 mm |
| 3 — sağ/sol derinlik farklı (≥0,50 mm) | ≥ 6/7 olgu | 7/7 |

## 2. İki koşu, iki ret

Tek değişken: şablon örnekleme adımı `APEKS_DS`.

| ölçüt | taban | `0M` kaydı | ds=4 | ds=2 | sonuç |
|---|---|---|---|---|---|
| 1 — apeks 3B hatası ort. | < 5,14 mm | 2,69 | 3,49 | 3,47 | taban geçildi, kayıt tutmadı |
| 2 — derinlik MAE | < 1,72 mm | 1,65 | 2,24 | 2,05 | **RET** |
| 3 — sağ/sol farklı | ≥ 6/7 | 7/7 | 6/7 | 5/7 | **RET** |

Şablon tepe sayısı ds=4'te 8.372, ds=2'de 36.810–49.753 (beş kat).
Süre: ds=4 ~100 sn/olgu, ds=2 ~1.550 sn/olgu. `0M` §5 **~800 sn/olgu** kaydetmiş,
yani `0M`'in koşusu ikisinin arasında.

### 2.1 Olgu bazında (apeks 3B hatası, mm)

| olgu | ds=4 sağ | ds=4 sol | ds=2 sağ | ds=2 sol |
|---|---|---|---|---|
| hasta5 | 3,44 | 7,00 | 4,15 | 3,17 |
| hasta6 | 3,42 | 3,97 | 3,22 | 3,70 |
| hasta7 | 1,98 | 1,39 | 2,24 | 1,44 |
| hasta8 | 0,92 | 1,89 | 1,00 | 1,91 |
| hasta9 | 3,39 | 3,10 | 3,95 | 2,31 |
| hasta10 | 4,25 | 5,80 | 5,82 | 5,46 |
| hasta11 | 4,37 | 3,96 | 5,02 | 5,16 |

## 3. Çözünürlük eksik değişken DEĞİL

Beş kat ince şablon ortalama hatayı 3,49'dan 3,47 mm'ye getirdi — ölçüm
belirsizliğinin içinde. Olgu bazında bakıldığında bunun bir durağanlık değil
**birbirini silen iki etki** olduğu görülüyor: hasta5 sol apeksi 7,00 → 3,17 mm
düzeldi, hasta10 ve hasta11 ise belirgin kötüleşti. Dolayısıyla `0M`'in 2,69 mm'si
şablon çözünürlüğünden gelmiyor; eksik olan başka bir ayar ya da başka bir
yöntem ayrıntısıdır.

## 4. ds=3 ve diğer ara değerler DENENMEDİ — gerekçe

İki sebeple:

1. **§0.12.** `0M` §5.1'in üç ölçütü sonuç görülmeden kilitlenmiş ön kayıttır.
   Onları ds seçmek için art arda kullanmak, doğrulama ölçütünü uydurma hedefine
   çevirir. İki koşu zaten bu ölçütleri tüketmeye başlamıştır; bu kayıt, o iki
   koşunun da yapıldığını açıkça bildirmek içindir.
2. **Olgusal.** §3'teki bulgu ds'nin etkisiz olduğunu gösteriyor. Ara değer
   denemenin bilimsel gerekçesi yok, yalnızca hedefe yaklaşma umudu var.

## 5. Sonuç ve tablonun durumu

- `kohort_98.csv`'nin 10 apeks sütunu **boştur** ve bu oturumda doldurulmamıştır.
- Doldurma, ancak `0M`'in özgün sürücüsü/ayarları bulunduğunda ve ölçütler
  tutturulduğunda yapılacaktır.
- `0AW`'nin 98 satırı ve SHA-256'sı bu karardan etkilenmez.
- Hâlâ eksik ikinci sütun çifti: `lob_cikan_sag/sol` (bkz. `0AT` §3, `0R` §2).

## 6. Sıradaki doğru adım (parametre taraması DEĞİL)

`0M`'in özgün kodunu aramak: konuşma geçmişi, Drive `bellek yetmeyenler` klasörü
ve `parametre tablosu` klasörü. Parametre uzayını doğrulama ölçütlerine karşı
taramak, ölçütleri harcar ve yanlış bir "geri kurulum" üretir.

## 7. Üretilen dosyalar

- `an/apeks_nicp.py` — HEDEF/HİZALAMA ayrımı `0M` §3 KOL B'ye göre
- `an/apeks_loo.py` — olgu-bırak-bir doğrulaması, `APEKS_DS` ortam değişkeni
- `an/out/apeks_loo_ds4.json`, `an/out/apeks_loo_ds2.json` — iki koşunun ham çıktısı
- `an/medial.py` — `hedef_nokta` / `hiza_nokta` seçimlik parametreleri eklendi
  (varsayılanlar DEĞİŞMEDİ, `0J`/`0M` koşuları etkilenmez)
