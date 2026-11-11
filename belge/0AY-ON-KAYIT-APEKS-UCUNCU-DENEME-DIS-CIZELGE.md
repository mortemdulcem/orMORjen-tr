# 0AY — ÖN KAYIT: APEKS NICP ÜÇÜNCÜ VE SON DENEME, DIŞ KATILIK ÇİZELGESİ

**Tarih:** 2026-11-11, sabah · **Durum:** ÖN KAYIT — koşu BAŞLAMADAN yazıldı
**Bağlam:** `0AX` (iki çözünürlükte ret) · `0M` §3 KOL B, §4, §5.1 · `0AV` (dış türetme ilkesi)
**Cinsiyet:** körlü, sınav cinsiyetten bağımsız

---

## 1. Neden üçüncü deneme meşru

`0AX` §4'te *"ds=3 ve ara değerler denenmedi"* diye kayıt düşmüştüm, gerekçe
§0.12: ön kayıtlı ölçütler parametre seçmek için kullanılamaz. **Bu deneme o
yasağa girmiyor**, çünkü denenecek değer bizim seçtiğimiz bir değer değil:

**`T-AbdelAlim/CraniumPy`'nin yayımlanmış varsayılanı** (Apache-2.0,
DOI 10.5281/zenodo.7430069, `src/craniumpy_core/registration/nicp.py`):

```
DEFAULT_ALPHAS = np.linspace(200, 1, 20)      # 20 kademe
inner_iters    = 3
gamma          = 1.0
```

Bu, `0AV`'de bi-porion bandı için Howells'in dış SS'sini kullanmakla **aynı
ilkedir**: parametre dışarıdan, bizim sonuçlarımıza bakılmadan sabitlenmiş bir
kaynaktan alınır. Kendi öğrenme kümemizden ya da hedefe yakınlıktan
türetilmiyor. Depo dün kuruldu ve lisansı Apache-2.0'dır, kullanımı serbesttir.

Karşılaştırma:

| | çizelge | iç tur | toplam çözüm |
|---|---|---|---|
| CraniumPy (dış, yayımlanmış) | `linspace(200, 1, 20)` | 3 | **60** |
| bizim `medial.py` (`0AX`'te koşan) | `(200, 80, 30, 10, 3)` | 2 | 10 |
| bizim `nicp.py` varsayılanı | `(200,120,70,40,20,10,5,2)` | 3 | 24 |

## 2. Hipotez — iki ayrı ve bağımsız öngörü

`0AX` §8.2 saptadı: `0M`'in kestirimi **daha yanlı (+1,11 mm) ama daha az
saçılımlı (ss 1,787)**; benim yeniden kurulumum daha az yanlı (+0,26) ama çok
daha saçılımlı (ss 2,559). Bu, katılığın kademeli inişinin imzasıdır: ince
çizelge sıkı ve tutarlı, kaba çizelge gevşek ve gürültülü oturur.

### 2.1 ÖNGÖRÜ A — SÜRE (hata ölçütlerinden BAĞIMSIZ, önce bakılacak)

60 çözüm / 10 çözüm = 6 kat. ds=4'te ölçülen süre ~100 sn/olgu idi.

**Öngörü: 600–900 sn/olgu.** `0M` §5 **~800 sn/olgu** kaydetmiştir.

Bu öngörü hata sayılarına bakılmadan denetlenir ve §0.12'ye girmez, çünkü
süre bir doğrulama ölçütü değildir. **Süre bu aralığın dışına düşerse çizelge
hipotezi yanlıştır** ve hata sonuçları ne olursa olsun yöntem "`0M`'in
sürücüsü bulundu" sayılmaz.

### 2.2 ÖNGÖRÜ B — ÖLÇÜTLER (`0M` §5.1, DEĞİŞTİRİLMEDEN)

| # | ölçüt | taban | `0M` kaydı |
|---|---|---|---|
| 1 | apeks 3B hatası ortalama | < 5,14 mm | 2,69 mm |
| 2 | derinlik MAE kalibresiz | < 1,72 mm | 1,65 mm |
| 3 | sağ/sol farklı (≥0,50 mm) | ≥ 6/7 olgu | 7/7 |
| 4 | olgu-bırak-bir | şart | her şablon diğer 6 ile |

**Eşikler oynatılmadı.** Bu, bu ölçütlerin **ÜÇÜNCÜ ve SON** kullanımıdır.

## 3. Sabitlenen ayarlar (koşu öncesi, değiştirilemez)

- `alphalar = np.linspace(200, 1, 20)` — CraniumPy varsayılanı, aynen
- `ic_tur = 3` — CraniumPy varsayılanı, aynen
- `APEKS_DS = 4` — `0M`'in süre kuşağı; `0AX` §3 çözünürlüğün etkisiz
  olduğunu ölçtü, bu yüzden ds oynatılmaz
- HEDEF = `apex-r`, `apex-l`; HİZALAMA = kalan 12 nokta (apeks YOK) — `0M` §3 KOL B
- Derinlik tanımı: altıgen düzlemine dik — `0AX` §8.1'de elle ölçümle
  birebir doğrulandı (40,692 ± 1,760 = `0M` §9'un 40,69 ± 1,75)
- Olgular: hasta5–hasta11, LOO

## 4. SONUÇ NE OLURSA NE OLACAK (şimdi yazıldı)

**Dördü de sağlanır VE süre 600–900 sn ise:** sürücü `0M`'in yöntemi sayılır.
`kohort_98.csv`'nin 10 apeks sütunu doldurulur. `0M` §10.3'ün dört Cureus
parametresi (`mf/ek/mso/o–apeks`) askıdan iner ve hesaplanır.

**Ölçütlerden biri bile sağlanmazsa:** apeks **BT'den otomatik ölçülemedi**
diye teze yazılır. Apeks sütunları kalıcı olarak boş kalır. `0M` §10.3'ün dört
parametresi kalıcı olarak teze **girmez** (`0AX` §9). **Dördüncü deneme
yapılmaz** — çizelge taraması, ara değer, başka depo: hiçbiri. Bu ölçütler
tükenmiştir.

**Ölçütler geçer ama süre aralık dışına düşerse:** değerler raporlanır, ancak
teze *"`0M`'in özgün ayarı bulunamadı; yöntem bağımsız bir dış çizelgeyle
yeniden kuruldu"* diye yazılır ve `0AX` §8'in kayıp-kod kaydı sınırlılık
olarak durur.

**Her durumda:** `0K` §1 geçerli — kohorta geri işleme ayrı ön kayıt ve 50
olgunun yeniden ölçülmesini gerektirir, kohort toplanması bitene kadar
yapılmaz. `0M` §5.3c de geçerli: dik izdüşüm derinliği cinsiyet çıkarımına
**girmez**, bu koşu o kapıyı açmaz.

## 5. Araştırmacının izni

Araştırmacı CraniumPy için izin verdiğini bildirdi (2026-11-09) ve depo
bağımsız olarak **Apache-2.0** taşıdığı doğrulandı. Bu koşuda CraniumPy'nin
**kodu kopyalanmıyor**; yalnızca yayımlanmış varsayılan sayı değerleri dış
referans olarak alınıyor. Atıf tezin yöntem bölümüne girer.

---

## 6. SONUÇ — İKİ ÖNGÖRÜ DE TUTMADI, APEKS KAPANDI (2026-11-11, 08:4x)

Koşu: `an/apeks_loo.py`, `APEKS_CIZELGE=dis`, ds=4, iki paralel işçi
(hasta5–8 / hasta9–11), çıktı `an/out/apeks_loo_dis.json`.

### 6.1 Öngörü A — SÜRE: TUTMADI

Ölçülen **166–306 sn/olgu, ortanca 265 sn.** Öngörü 600–900 sn idi;
`0M` §5 ~800 sn kaydetmişti. Çizelgeyi 10 çözümden 60 çözüme çıkarmak süreyi
altı kat değil yalnız ~2,6 kat artırdı. **Çizelge hipotezi süre tarafından
yanlışlandı** — ve bu, hata sayılarına bakılmadan saptandı.

### 6.2 Öngörü B — ÖLÇÜTLER: İKİSİ RET

| # | ölçüt | taban | `0M` | ds=4 | ds=2 | **dış çizelge** |
|---|---|---|---|---|---|---|
| 1 | apeks 3B hatası ort | < 5,14 mm | 2,69 | 3,49 | 3,47 | **3,41** E |
| 2 | derinlik MAE | < 1,72 mm | 1,65 | 2,24 | 2,05 | **2,05 RET** |
| 3 | sağ/sol farklı | ≥ 6/7 | 7/7 | 6/7 | 5/7 | **2/7 RET** |

### 6.3 Mekanizma — ince çizelge YANLIŞ YÖNDE

| | yanlılık | saçılım (ss) | r |
|---|---|---|---|
| `0M` | +1,110 | 1,787 | +0,542 |
| ds=4 | −0,308 | 2,901 | +0,364 |
| ds=2 | +0,260 | 2,559 | +0,446 |
| dış çizelge | **−1,095** | 2,570 | **+0,286** |

Ölçüt 3, kademe sayısı arttıkça **6/7 → 5/7 → 2/7** diye çöktü. Sağ ve sol
kestirimler birbirine yapışıyor (hasta6'da 0,075 mm, hasta7'de 0,294 mm).
Sebep anlaşılır: daha sıkı ve daha kademeli bir oturma şablonun KENDİ
apeksine yakın kalır, hedefin yüzeyine esnemez — yani `0M` §3'ün atlas
formülüne yaptığı eleştirinin aynısı burada NICP'in içinde yeniden üretiliyor.
Ölçüt 3 tam olarak bu batma biçimini yakalamak için konmuştu ve yakaladı.

**Sonuç: `0M`'in 7/7 + düşük saçılımı çizelgeyi inceltmekle elde edilemez.
Yön yanlış.** Dördüncü deneme için bir hipotez de kalmadı.

### 6.4 HÜKÜM — `0AY` §4'ün yazdığı gibi

1. Apeks **BT'den otomatik ölçülemedi.** Teze bu cümleyle girer.
2. `kohort_98.csv`'nin 10 apeks sütunu **kalıcı olarak boş** kalır.
3. `0M` §10.3'ün dört Cureus parametresi (`mf/ek/mso/o–apeks`) teze **girmez.**
4. **Dördüncü deneme yapılmaz.** `0M` §5.1'in üç ölçütü tükenmiştir.
5. `0M` §5.3c değişmez: dik izdüşüm derinliği cinsiyet çıkarımına zaten
   girmiyordu. Bu kapanış **cinsiyet analizinde hiçbir kayıp yaratmaz** —
   yalnız §10.3'ün dört betimleyici ölçüsünü ve apeks sütunlarını kaybettirir.
6. Özgün kod (`an/derinlik/apeks_nicp.py`) bulunursa hüküm yeniden açılabilir;
   yeniden kurulumla değil, yalnız özgün kodla.

### 6.5 Teze yazılacak sınırlılık metni (taslak)

*"Orbital apeks (optik kanalın kemik ağzı), bu çalışmanın tam otomatik
hattında güvenilir biçimde ölçülememiştir. Üç bağımsız yöntem denenmiştir:
kesitte kapalı kemik halka arama, kemik koninin daralma profili ve çok
şablonlu doğrusal olmayan yüzey kaydı (NICP). Yedi elle işaretlenmiş olguda
olgu-bırak-bir doğrulamasında derinlik ortalama mutlak hatası 2,05 mm'de
kalmış ve sabit kestirici tabanını (1,72 mm) geçememiştir. Apeksten türetilen
parametreler bu nedenle raporlanmamıştır."*
