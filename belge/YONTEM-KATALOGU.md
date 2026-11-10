# YÖNTEM KATALOĞU — her kod, her depo, niçin ve nerede

**Tarih:** 2026-11-10 · **Araştırmacı talimatı:** *"Kullandığım her yöntem kodu ve
github repolarını niçin olduklarını kullanıldıklarını isim olarak dallar yapıp
github reposuna aktar; şu ana kadar en doğru hangi yöntemlerde"*

Her satırın bir **ölçülmüş** doğrulaması ya da açık bir *"doğrulanmadı"* notu var.
Doğrulaması olmayan hiçbir yöntem "çalışıyor" diye yazılmadı.

---

## A. DIŞARIDAN ALINAN KOD VE VERİ

| # | kaynak | lisans | niçin | nerede | durum |
|---|---|---|---|---|---|
| A1 | `lucanchling/ALI_CBCT` (`models_v01`) | depo | porion ve ASO landmarkları | `porion/kos.sh`, `kos7.sh` | **çalışıyor**, 14/14 |
| A2 | `DCBIA-OrthoLab/SlicerAutomatedDentalTools` | — | ASO'nun Frankfort yöntemi + landmark kapısı | `an/aso_kapi.py` | **okundu**, kapı koşuldu |
| A3 | `lucanchling/ASO_CBCT` (`v01_goldmodels`) | — | Frankfort altın referansı | `aso_gold/MAMP_0002_T1.mrk.json` | **doğrulandı** |
| A4 | Howells kraniyometrik veri seti | kamuya açık | bi-porion bandının dış türetmesi | `dis_kaynak/howells/howell.csv` | **kullanıldı** (`0AV` §3) |
| A5 | `T-AbdelAlim/CraniumPy` | **Apache-2.0** | NICP'in bağımsız uygulaması | doğrulama için | **kuruldu**, karşılaştırma bekliyor |
| A6 | `Slicer/Slicer` | — | arayüz/algoritma envanteri | `slicer-uygulama-envanteri.md` | tarandı; **Frankfort kodu YOK** |

**A1 — ALI_CBCT.** Çok ölçekli pekiştirmeli öğrenme etmeni. Porion hiçbir sahnede
elle işaretlenmemişti; `PO.bul` kohortta insan kafasında bulunmayan bi-porion
değerleri üretiyordu (`0AD`). Doğrulaması: ASO altın standardında nokta hatası
**0,39–0,61 mm**, bi-porion hatası **0,69 mm**, üç tekrarda birebir aynı sonuç.
Üç uyumluluk yaması gerekti (`0AU` §3); üçü de sayısal davranışı değiştirmiyor,
biri (bellek) ölçülerek gösterildi.
**Bilinen kusuru:** nasion 0,3 mm ölçeğinde bulunamıyor (`0AV` §8.5.2).

**A2 — ASO.** Frankfort düzlemini **analitik kurmuyor**: hastayı Frankfort'a zaten
oturtulmuş altın taramaya 7 landmarkla katı cisim ICP'siyle kaydediyor
(`ASO/ASO_Method/CBCT.py:249`). Kapı fonksiyonları (`GetLandmarkToRemove`)
birebir alındı, değiştirilmedi.
**Ölçülen sınırı:** kapı bizim altı ölçütümüzün yerine **geçemez** — 15 mm
toleransı tek bir kafatasına karşı mutlak uzaklık ölçüyor ve iyi olgularımızda
`LOr–ROr` farkı 16–20 mm çıkıyor (anatomik değişkenlik). `0AV` §9.4.

**A5 — CraniumPy.** `nicp.py` yazıldığında deponun LICENSE'ı **yoktu**, bu yüzden
kod kopyalanamadı ve NICP yayımlanmış formülasyondan (Amberg ve ark. 2007) kendimiz
yazıldı. Depo **2026-11-09'da Apache-2.0 aldı** (DOI `10.5281/zenodo.7430069`).
Engel kalktı ama **bizim kodumuz değiştirilmedi**: `0M`'in doğrulanmış sayıları
bizim uygulamamızla üretildi. CraniumPy bağımsız doğrulama olarak kullanılacak.

---

## B. KENDİ YÖNTEMLERİMİZ — doğrulamasıyla

| # | yöntem | dosya | doğrulaması | durum |
|---|---|---|---|---|
| B1 | Frankfort çatısı | `an/frankfort.py` | rijitlik **2,842×10⁻¹⁴ mm** = `0Y` §2 kaydı; det(R)=1,000000000000 | **en güçlü** |
| B2 | 43 parametre zinciri | `orbita_hat/olcum_zinciri.py` | denek98/99/100/101 kilitli kayıtla **birebir** | **en güçlü** |
| B3 | Altıgen apertür | `0T` tanımı | 3 olgu × 2 taraf: çevre birebir, alan ±0,02, düzlemsizlik ±0,0002 | **doğrulandı** |
| B4 | Derinlik tanımı | altıgen düzlemine dik | 7 olgunun 14 değerinin **13'ü birebir** | **doğrulandı** |
| B5 | Maske (ışın) | `an/rayseg.py` | `0AT` §3: 8/8 orbitada Dice 1,000, hacim farkı <%0,02 | **doğrulandı** |
| B6 | NICP | `an/nicp.py` | Amberg 2007; medial LOO `0M`'de | koşuyor |
| B7 | Apeks NICP | `an/apeks_nicp.py` | `0M` §5: hedef 2,69 mm / 1,65 mm | **doğrulanıyor** |
| B8 | Rim eğrisi | `an/rimcurve.py` | elle eğriye göre apertür alanı **+%0,5–7,4 büyük** | **kusurlu, biliniyor** |
| B9 | Ölçüt 2 (orta-MSP) | `an/frankfort.py` | iki bağımsız kanıt geçerliliğini sorguluyor | **şüpheli** |
| B10 | Lob temizliği | `an/rayseg.py` `lob_temizle` | denek10'un kayıtlı 0,2012 cm³'ünü **tutturamıyor** | ⛔ **BOZUK** |

---

## C. EN DOĞRU HANGİ YÖNTEMLER — kanıt sırasına göre

**1. Frankfort çatısı (B1).** Kayıp kod yeniden kuruldu ve rijitlik değeri
`0Y`'nin özgün kodla kaydettiğiyle **aynı çıktı** (2,842 vs 2,8 ×10⁻¹⁴ mm).
Bu tesadüf olamaz; yeniden kurulumun doğruluğunun en güçlü kanıtı.

**2. 43 parametre zinciri (B2).** Dört olgunun hacim, OW, OH, IOD, BOW ve APalan
değerleri kilitli kayıtla birebir örtüştü. Bir tuzağı var: `olcum_zinciri.py`'nin
komut satırı arayüzü rim eğrilerini geçirmiyor; geçirilmezse APalan altıgen
kolundan çıkıyor (denek98: 1016,9 yerine 1051,0). `orbita_hat/olc_paket.py` bunu
düzeltir.

**3. ALI porionu (A1).** Dış altın standartta 0,39–0,61 mm, determinist, ve
yedi landmarklı koşu iki landmarklı koşunun porionlarını **bit düzeyinde** aynı
üretti.

**4. Altıgen apertür ve derinlik tanımı (B3, B4).** İkisi de belgeden türetilip
kayıtlı sayılara karşı sınandı; tahminle değil **ölçümle** belirlendi (ör. alan
Newell değil izdüşüm, düzlemsizlik maks değil ortalama mutlak).

**En zayıf halkalar:**
- **Lob temizliği (B10) BOZUK** ve kapsamı bilinmiyor. `0AT`'nin *"hat
  değişmemiştir"* hükmü bu kolu hiç sınamamıştı (denek98–101'de lob yok).
- **Rim eğrisi (B8)** lateral korumasızdır; apertür alanını büyütür. `0T`'nin
  duyarlılık analizi tam da bunun için kuruldu.
- **Ölçüt 2 (B9)** muhtemelen anatomiyi değil MSP kestirim hatasını ölçüyor.

---

## D. ÖLÇÜM KALİTESİ — araştırmacının işaret ettiği olgular

Araştırmacı denek90–96 ve 98–100'ü *"çok güzel ölçümler, özellikle son üçü"*
diye işaret etti. Tablodan ölçülen:

| denek | RED | UYARI | havuz | not |
|---|---|---|---|---|
| denek90 | 0 | 4 | evet | |
| **denek91** | 0 | 3 | **HAYIR** | **kemik kapısı düştü** |
| denek92 | 0 | 3 | evet | ölçüt 2'den düştü (Frankfort) |
| **denek93** | 0 | 1 | **HAYIR** | **kemik kapısı düştü** |
| denek94 | 0 | 2 | evet | |
| **denek95** | 0 | **0** | evet | kohortun UYARI'sız **7 olgusundan biri** |
| denek96 | 0 | 2 | evet | |
| denek98 | 0 | 2 | evet | ⭐ bağımsız yeniden üretildi |
| denek99 | 0 | 2 | evet | ⭐ bağımsız yeniden üretildi |
| denek100 | 0 | 1 | evet | ⭐ bağımsız yeniden üretildi |

⚠ **denek91 ve denek93 havuzun DIŞINDA** — RED'leri yok ama kemik kapısı düştü,
yani bazı rim noktaları kemiğin üstünde değil. Veri setine girmiyorlar.

**Son üçünün (98–99–100) gerçekten örnek olmasının sebebi:** bunlar, tam 43
parametresi **bağımsız olarak yeniden ölçülüp kilitli kayıtla birebir
örtüştürülebilen tek olgulardır** (`0AW` §2.1). Yani "hat çalışıyor" iddiasının
kanıtı onlar. Örnek alınacak şey tarama kalitesi değil, **yeniden
üretilebilirlik**.

**denek95 ayrıca örnek:** kohortta UYARI'sı sıfır olan 7 olgudan biri — ama
Frankfort tarafında ölçüt 2'den düşüyor (orta-MSP 3,537). İki kapının birbirinden
bağımsız olduğunun iyi bir örneği.

---

## E. DALLAR

Her yöntem/depo için `yontem/<ad>` dalı açıldı; her dalın kökünde o yöntemin
`YONTEM.md` kartı var. Ana dal (`main`) bu kataloğu taşır.
