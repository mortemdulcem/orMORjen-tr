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

---

## 8. ÖZGÜN KOD ARANDI — BULUNAMADI (2026-11-11)

`0M` §5 kodun yerini açıkça yazmış: `an/derinlik/apeks_nicp.py`,
`an/derinlik/apeks_loo.py`, `an/derinlik/apeks_loo_olcut.py`; çıktılar
`an/out/apeks_nicp_loo.json`, `an/out/apeks_nicp_olcut.json`.

Beş kaynağın hepsi arandı:

| kaynak | sonuç |
|---|---|
| konteyner diski | `an/derinlik/` yok; `apeks_nicp_loo.json` yok; adı `derinlik` olan hiç klasör yok |
| GitHub `orMORjen-tr`, bütün dallar ve bütün geçmiş | `an/derinlik/*` **hiç gönderilmemiş** |
| Drive `bellek yetmeyenler` | klasör var, **boş** (2026-11-10'da açılmış) |
| Drive `parametre tablosu` | klasör var, apeks kodu yok |
| konuşma geçmişi | yalnız içinde bulunduğumuz sohbet görünüyor; 6 Kasım oturumu erişilemiyor |
| araştırmacının bilgisayarı | köprüye bağlı değil — denenemedi |

Geçmişte korunmuş apeks dosyaları `an/apeks.py` (13. yöntem, kemik koni
daralma profili = `0M` §10.3'ün "delik yöntemi") ve `an/apeksatlas16.py`
(KOL A atlası). **NICP kolunun sürücüsü bunların hiçbiri değil.**

### 8.1 Doğrulanan iki çapa — kaybolan yalnız kod

1. **Elle ölçüm aynı.** Yeniden kurulan hattın okuduğu elle apeks derinlikleri
   **40,692 ± 1,760 mm**; `0M` §9'un kaydı **40,69 ± 1,75**. Derinliğin tanımı,
   altıgen düzlemi ve elle koordinatlar sağlam.
2. **`0M`'in kendi sayıları §5.2 tablosundan birebir yeniden üretiliyor:**
   MAE 1,652 (kayıt 1,65) · yanlılık +1,110 (+1,11) · r +0,542 (0,543) ·
   R² 0,294 (0,295). `0M`'in koşusundan kayıp sayı yok.

### 8.2 İki sürücünün karakter farkı — aranacak yer

| | MAE | yanlılık | saçılım (ss) | r | R² |
|---|---|---|---|---|---|
| `0M` kaydı | 1,652 | **+1,110** | **1,787** | +0,542 | 0,294 |
| ds=4 | 2,237 | −0,308 | 2,901 | +0,364 | 0,133 |
| ds=2 | 2,049 | +0,260 | 2,559 | +0,446 | 0,199 |

Yeniden kurulan sürücü **daha az yanlı ama belirgin biçimde daha saçılımlı**.
`0M`'inki dizgesel olarak 1,11 mm derin ölçüyor ama tutarlıdır. Bu, mesh
çözünürlüğünün değil **NICP katılık çizelgesinin** (`ALPHA`, iç tur sayısı)
imzasıdır: daha kısıtlı bir oturma kaymış ama tutarlı cevap verir, daha gevşek
oturma merkezlenmiş ama gürültülü. `0M` §3 KOL B *"tek fark hedef ve hizalama
kümeleri"* diyordu, ama bu bir ÖN KAYIT cümlesidir — koşudan önce yazılmıştır
ve gerçekleşen kodun `medial.py`'nin `ALPHA = (200,80,30,10,3)`, `ic_tur=2`
çizelgesini kullandığını kanıtlamaz. Aranan fark burada olabilir.

**Çizelge taraması YAPILMAYACAK** — §4'teki gerekçe aynen geçerlidir.

## 9. SONUÇ — `0M` §10.3'ÜN DÖRT PARAMETRESİ ASKIYA ALINDI

`0M` §10.3 (Cureus 2023, Anadolu, n=126) dört yeni parametreyi ön kayda
bağlamıştı: `mf–apeks`, `ek–apeks`, `mso–apeks`, `o–apeks` (3B Öklid).
Hata/sinyal kapısı (eşik <0,70) hükmü **açıkça NICP'in 1,65 mm'sine**
dayandırıyordu. O sayı, artık var olmayan ve yeniden üretilemeyen bir koddan
geliyor.

| ölçü | Cureus cinsiyet farkı | hata/sinyal @ 1,65 | hata/sinyal @ 2,05 |
|---|---|---|---|
| medial (`mf`) | 3,01 mm | 0,549 ✓ | 0,681 ✓ |
| lateral (`ek`) | 2,77 mm | 0,596 ✓ | **0,740 ✗** |
| tavan (`mso`) | 2,92 mm | 0,566 ✓ | **0,702 ✗** |
| taban (`o`) | 2,68 mm | 0,616 ✓ | **0,765 ✗** |

**2,05 mm'de dördün üçünde kapı KAPANIYOR.**

⚠ 2,05 benim yeniden kurulumumun sayısıdır, yöntemin gerçek doğruluğu
olduğunu iddia etmiyorum. Hüküm şudur: **§10.3'ün kapısı artık doğrulanamayan
bir sayıya dayanıyor.** Bu yüzden:

1. Dört parametre **hesaplanmaz ve teze girmez** — ne özgün kod bulunana ne de
   yöntem yeni bir ön kayıtla yeniden doğrulanana kadar.
2. `kohort_98.csv`'nin 10 apeks sütunu **boş kalır.**
3. `0M` §5.3c'nin hükmü değişmez: dik izdüşüm derinliği cinsiyet çıkarımına
   zaten **girmiyordu** (hata/sinyal 2,43 > 0,70). Bu başarısızlık o kapıyı
   etkilemez; etkilediği tek şey §10.3'ün dört türetilmiş ölçüsüdür.
4. `0M` §5.3a'nın uyarısı doğru çıktı: *"2. ölçütün payı %4,1 (0,07 mm) …
   bu payın örneklemeye göre oynaması beklenir."* Oynadı.

### 9.1 Araştırmacıdan istenen

`an/derinlik/apeks_nicp.py` ve `apeks_loo.py` dosyaları, 6 Kasım akşamı
oturumunun indirilmiş paketlerinde, Replit projesinde ya da başka bir sohbetin
çıktısında olabilir. Bulunursa yeniden kurulum gereksiz kalır ve §10.3'ün dört
parametresi doğrudan hesaplanır. Yoksa yöntem **yeni bir ön kayıtla** (yeni
eşikler, eski eşikler harcanmıştır) sıfırdan doğrulanmalıdır.

### 9.2 Küçük bir kayıt düzeltmesi

`0M` §10.3'ün tablosunda NICP kolonu 0,55 / 0,58 / 0,62 / 0,62 yazılı;
1,65/fark hesabı 0,549 / 0,596 / 0,566 / 0,616 veriyor. Lateral ve tavan
satırları karışmış. Dördü de 0,70'in altında olduğu için **hüküm
etkilenmiyor**, ama kayıt düzeltilmiştir.
