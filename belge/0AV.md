# 0AV — ÖN KAYIT: bi-porion bandı dış kaynaktan yeniden türetildi

**Tarih:** 2026-11-10, saat 20:29 (Europe/Istanbul)
**Araştırmacı onayı:** *"Band evet, ölçüt 2 dursun"* (seçenek 1, açık onay)
**Karar:** bi-porion kabul bandı = **89,91 – 121,79 mm**
(`frankfort.py` 3. ölçütü; `0Z`'nin 97,3–114,4 bandı **iptal**)
**Ölçüt 2 (orta-MSP ≤ 3,00 mm): DEĞİŞMEDİ.** Gerekçesi §4'te.

---

## 1. ⚠ ÖNCE DÜRÜST KAYIT — bu türetme sayılar görüldükten sonra yapıldı

`00` §0.12 gereği, savunmada sorulmadan önce buraya yazılıyor:

Bu türetme yapıldığında **14 olgunun bi-porion değerlerinin tamamı görülmüştü**
(`0AU`, 2026-11-10). Bandın yeniden ele alınma **sebebi** o değerlerdi: dört olgu
(denek100 114,44 · denek94 115,11 · denek92 118,80 · denek95) ölçütlerden düşmüştü
ama karşı orbitaleleri 0,69–2,79 mm ve HU'ları 743–1183 ile `0F` §24'ün *doğru*
porion imzasının içindeydi.

Bandın **kuralı** ise bu kohorttan türemiyor: merkez `0Z`'nin öğrenme setinden,
yarı-genişlik Howells'ın 2524 kafatasından geliyor. Kohortun hiçbir sayısı türetmeye
girmedi. `00` §0.12'nin ikinci yasağı (bir parametreyi onu doğrulayan veriden
türetmek) çiğnenmedi. Birinci yasak (sonucu görüp kol seçmek) ise **kısmen**
geçerlidir ve bu paragraf onun kaydıdır.

## 2. `0Z`'NİN KUSURU — merkez değil, genişlik

`0Z` bandı n=8 öğrenme olgusundan kurdu: ortalama 105,85 · SS **2,85** mm → ±3SS.
Merkez savunulabilir (ASO altın standardı 104,2 mm ile 1,65 mm uyumlu). Kusur
yarı-genişlikte: **tek bir homojen öğrenme setinin SS'si, bir popülasyondaki
bireysel değişkenliğin tahmini değildir.**

Kohortta bunun bedeli ölçüldü: karşı orbitalesi ≤3 mm olan 11 olguda bi-porion
105,81–118,80 mm (ortanca 111,05). `0Z` bandının üst sınırı 114,4 bu dağılımın
**boşluğundan değil ortasından** kesiyor. Öğrenme setinde bandın üstünde 9,1 mm
boşluk vardı; kohortta yok — denek93 113,02'de geçiyor, denek100 114,44'te düşüyor,
arada **1,42 mm** var. İki grubu ayırdığı yerde 1,42 mm fark bulunan bir eşik
ayırıcı değildir.

## 3. YENİ BANDIN TÜRETİLMESİ

### 3.1 Merkez — değişmedi
**105,85 mm.** Kaynak `0Z` §2: öğrenme setinde kabul edilen 7 olgu + ASO altın
standardı (n=8). Bu sayı bu oturumda yeniden hesaplanmadı, `0Z`'den alındı.

### 3.2 Yarı-genişlik — Howells'tan
Dış kaynak: **Howells kraniyometrik veri seti** (`dis_kaynak/howells/howell.csv`),
2524 kafatası, 30 popülasyon, 1368 E / 1156 K.

Kullanılan değişken: **AUB (biauriküler genişlik)** — aurikular bölgedeki enine
kafa tabanı genişliği.

| tahmin | SS | serbestlik derecesi |
|---|---|---|
| AUB toplam SS (popülasyonlar arası dahil) | 7,39 mm | 2523 |
| **AUB popülasyon içi havuzlanmış SS** | **5,313 mm** | **2494** |
| AUB popülasyon × cinsiyet içi havuzlanmış SS | 4,279 mm | 2468 |
| Avrupa/Yakın Doğu havuzu (NORSE+ZALAVAR+BERG+EGYPT, n=428) | 6,14 mm | 427 |

**Seçilen: popülasyon içi havuzlanmış SS = 5,313 mm.** Gerekçe kural olarak önceden
yazıldı:

1. Kohort **tek bir popülasyondur** (Türk). Toplam SS (7,39) popülasyonlar arası
   farkı da içerir ve bu kohorta uygulanamaz.
2. Kohortun **cinsiyeti kapalıdır** (`0K` §3). Cinsiyete göre ayrıştırılmış tahmin
   (4,279) uygulanamaz; `0Z` §4'ün cinsiyetten bağımsızlık kararı sürüyor.
3. Alt küme havuzu (6,14) daha dar bir referans ama n=428; havuzlanmış tahmin
   n=2524 ile daha kararlıdır ve **daha muhafazakârdır** (5,313 < 6,14), yani
   bandı gereğinden fazla genişletmez.

**Band = 105,85 ± 3 × 5,313 = 89,91 – 121,79 mm.**

### 3.3 ⚠ VEKİL DEĞİŞKEN UYARISI — AUB bi-porion DEĞİLDİR

Bu, bandın en zayıf halkasıdır ve teze **bu haliyle** yazılacaktır.

Howells'ın 85 değişkeninde biporionik genişlik **yoktur**. AUB'nin tanımı:

> *"The least exterior breadth across the roots of the zygomatic processes (ra)."*
> — [CoRA, Cra_10 Biauricular Breadth](https://docs.coracore.org/en/v1.0.0/forensics-anthro-guide/measurements/)

İşaret noktası **ra** (zigomatik çıkıntı kökü), **po** (porion) değil. Martin
sisteminde M11 (biauriküler) ile M11b (biporionik) ayrı ölçümlerdir. Howells'ta
porion kullanan tek değişken MDH'dir (po–ms mastoid yüksekliği) ve bir genişlik
değildir. Howells'ın radii'leri (NAR, SSR, … BAR) transmeatal eksenden ölçülür ama
**eksenin uzunluğu kaydedilmemiştir.**

Bu yüzden Howells'tan alınan şey **ölçümün kendisi değil, değişkenliğidir.** Varsayım
açıkça şudur: *aurikular bölgedeki enine kafa tabanı genişliğinin bir popülasyon
içindeki değişkenliği, ra ile po arasındaki birkaç milimetrelik işaret noktası
farkından büyük ölçüde bağımsızdır.* Bu varsayım **sınanmamıştır** ve tezin
sınırlılıklar bölümünde bu cümleyle yer alacaktır.

Merkez bu varsayıma dayanmıyor (öğrenme setinden ve altın standarttan geliyor);
yalnız genişlik dayanıyor.

## 4. ÖLÇÜT 2 NİÇİN DEĞİŞMEDİ — araştırmacı kararı

Araştırmacı ilk turda orta-MSP eşiğinin 4,00 mm'ye çıkarılmasını seçti. Dış kaynak
arandı ve **4,00'ı desteklemediği** bulundu; bulgu araştırmacıya iletildi ve karar
**ölçüt 2'ye dokunmamak** yönünde değiştirildi. Kayıt:

Dış kaynak: 67 denekli 3B BT çalışması (22 normal kontrol + 45 yüz asimetrisi),
[Positional symmetry of porion and external auditory meatus in facial asymmetry](https://link.springer.com/article/10.1186/s40902-015-0033-1).

- Porionun MSP'ye göre **yatay** sağ-sol farkı normal grup ile asimetri grubu
  arasında **anlamlı değil** (p = 0,611).
- Dağılım: %36'sı |fark| < 1,0 mm; %21'i |fark| ≥ 3 mm.
- Bu iki yüzdeden normal dağılım varsayımıyla geri hesaplanan SS: 2,14 ve 2,39 mm
  (tutarlı). Orta nokta kayması bu farkın yarısı olduğundan SS ≈ 1,07–1,20 mm.
- **+3SS sınırı ≈ 3,21 – 3,59 mm.**

**Bu aralık denek92'nin (3,320) ve denek95'in (3,537) tam üstüne düşüyor.** Aralığın
içinden seçilecek her sayı bu iki olgunun hükmünü doğrudan belirler. `00` §0.12
gereği seçim yapılmadı; **eşik 3,00'de bırakıldı** ve iki olgu reddedilmiş kaldı.

### 4.1 Ölçüt 2 üzerine yapısal bulgu — raporlanır, uygulanmaz

Yukarıdaki p = 0,611, yatay porion asimetrisinin normal ile asimetrik yüzü
**ayırmadığını** söylüyor. Yani ölçüt 2, yanlış yerleştirilmiş porionun yatay
dedektörü olarak geçerli olmayabilir.

İkinci gözlem: bizim MSP'miz altı orbital açıklık çiftinin orta noktalarından
kuruluyor (`atlas-hasta7-8-9.md`) — yerel bir orbital yapı, kafatası orta düzlemi
değil. Porionlar orbital bölgeden ~70–80 mm arkada; MSP'de 2°'lik bir sapma orada
70 × sin2° ≈ 2,4 mm görünür orta nokta kayması üretir. denek92 ve denek95'te ölçülen
3,3–3,5 mm **anatomik asimetri değil, MSP kestirim hatası** olabilir.

Bu kohortta ölçüt 2 tek başına **hiçbir** kaba kusuru yakalamadı: yakaladığı üç
olguyu (denek10, denek11, denek78) ölçüt 6 zaten yakalıyordu. Kaba kusurları
yakalayan ölçüt 4 (HU 47–72) ve ölçüt 6'dır (karşı orbitale 24,8–67,7 mm).

**Ölçüt 2 sonucu görüldükten sonra kaldırılamaz veya gevşetilemez** (`00` §0.12).
Bu bulgu `0K` §1'in tam kohort yeniden ölçümüne taşınır; orada ölçüt 2'nin yerine
geçecek kural **ölçümden önce** sabitlenir.

## 5. BEKLENEN ETKİ — uygulamadan önce yazıldı

14 paketlik ön kümede, depolanmış sayılardan yeniden hesaplandığında:

| denek | bi-porion | eski hüküm | yeni hüküm |
|---|---|---|---|
| denek10 | 88,73 | ret (1,2,3,4,6) | **ret** (1,2,3,4,6) |
| denek78 | 105,16 | ret (2,6) | ret (2,6) |
| denek98 | 105,81 | kabul | kabul |
| denek101 | 107,44 | kabul | kabul |
| denek86 | 108,91 | kabul | kabul |
| denek95 | 110,17 | ret (2) | ret (2) |
| denek96 | 110,32 | kabul | kabul |
| denek99 | 111,05 | kabul | kabul |
| denek97 | 111,11 | kabul | kabul |
| denek93 | 113,02 | kabul | kabul |
| **denek100** | **114,44** | ret (3) | **KABUL** |
| **denek94** | **115,11** | ret (3) | **KABUL** |
| denek92 | 118,80 | ret (2,3) | ret (2) |
| denek11 | 123,82 | ret (2,3,4,6) | **ret** (2,3,4,6) |

**7/14 (%50) → 9/14 (%64,3).**

### 5.1 Ölçüt 3 ayırıcı gücünü koruyor
Genişletilmiş bandla bile ölçüt 3 **kendi başına** denek10'u (88,73 < 89,91) ve
denek11'i (123,82 > 121,79) reddediyor. Porionları yumuşak dokuda olan hiçbir olgu
banda girmiyor. Band genişlemesi hassasiyet kaybettirmedi.

## 6. KOŞU BAŞTAN ALINMIYOR
`frankfort_olcutler.json` her olgunun **sayısını** tutuyor, hükmünü değil. Hükümler
kaydedilmiş sayılardan yeniden hesaplandı; ALI koşusu, landmark çıkarımı ve porion
tespiti tekrarlanmadı. Yeni kabul edilen iki olgunun (denek100, denek94) koordinat
satırları `dok_2637.py` ile üretildi.

## 7. DEĞİŞMEYEN HER ŞEY
- Porion dedektörü (ALI_CBCT, IMAIOS e-Anatomy porion tanımı) **değişmedi**.
- Ölçüt 1, 2, 4, 5, 6 **değişmedi**.
- Çatı kurulumu (üç noktalı A kolu) ve rijitlik **değişmedi** (2,842 × 10⁻¹⁴ mm).
- 43 parametre **etkilenmiyor** (katı cisim dönüşümü).
- Hiçbir olgu değerine bakılarak dışlanmadı (`0K` §4.4); düşen olgular yerine
  yenisi konmadı.
- `o-l_z` sütununun özdeş sıfır olması (`0AU` §5) sürüyor.

---

## 8. ⭐ BAĞIMSIZ DOĞRULAMA — ASO'nun kendi toleransı (2026-11-10 21:05)

**Araştırmacı sorusu:** *"3D slicer uygulamasının frankfort kodları onları niye
çekmiyorsun sen"*

Çekildi. Bulgular:

### 8.1 Slicer çekirdeğinde Frankfort kodu YOK
`github.com/Slicer/Slicer` üzerinde arandı: sıfır sonuç. Frankfort,
**eklentide** — `DCBIA-OrthoLab/SlicerAutomatedDentalTools`, yani **ALI_CBCT ile
aynı laboratuvar** ve `0Z`'nin altın standardının geldiği yer. Depo okundu
(klon: `/home/claude/dcbia-ortholab/slicerautomateddentaltools`), **koşturulmadı.**

### 8.2 ASO düzlemi analitik kurmuyor — altın referansa KAYDEDİYOR
- `ASO/ASO_Method/CBCT.py:51` → referans: `Frankfurt_Horizontal_Midsagittal_Plane.zip`
- `ASO/ASO_Method/CBCT.py:249` → `["Ba", "S", "N", "RPo", "LPo", "ROr", "LOr"]`
- `ASO_CBCT/ASO_CBCT_utils/utils.py:527` `ICP_Transform` →
  `vtkIterativeClosestPointTransform`, `SetModeToRigidBody()`

Yani ASO, hastanın yedi landmarkını altın taramanın aynı yedi landmarkına katı
cisim olarak oturtur. Üç noktalı düzlem kurulumu hiç yoktur.

> **Bu, `0AU` §7c'nin açık sorusunu çözüyor.** Frankfort tanımı düzlem içi dönmeyi
> sabitlemez; biz koşudan önce bir kural yazmıştık. ASO'da böyle bir kurala gerek
> yok, çünkü yedi landmark altı serbestlik derecesinin hepsini belirler. Tezin
> §7c sınırlılığında bu yaklaşım kaynak gösterilebilir.

### 8.3 ⭐⭐ ASO'nun landmark denetim ölçütleri — ve bi-porion bandını doğrulaması

`ASO_CBCT/ASO_CBCT_utils/utils.py:341` `GetLandmarkToRemove`:

| ölçüt | ne yapar | eşik | satır |
|---|---|---|---|
| uzaklık | altın ile hastanın **bütün ikili landmark uzaklıklarının** farkı | **15 mm** | `:350` `GetCount(dist_diff, max_diff=15)` |
| yön | aynı çiftlerin **yön vektörleri arasındaki açı** | **0,4 rad (≈22,9°)**, alt sınır 0,1 rad | `:351` |
| hüküm | toplam sayım > landmark sayısı → landmark atılır | | `:353-362` |

Bi-porion çiftine uygulandığında, altın standardın bi-porion'u **104,2 mm**
(`0Z` §2'de kayıtlı) olduğuna göre kabul aralığı **104,2 ± 15 = 89,20–119,20 mm**.

| olgu | bi-porion | \|104,2 − b\| | ASO (±15) | `0AV` §3 (Howells) |
|---|---|---|---|---|
| denek10 | 88,73 | 15,47 | **ret** | **ret** |
| denek78 | 105,16 | 0,96 | geçer | geçer |
| denek98 | 105,81 | 1,61 | geçer | geçer |
| denek101 | 107,44 | 3,24 | geçer | geçer |
| denek86 | 108,91 | 4,71 | geçer | geçer |
| denek95 | 110,17 | 5,97 | geçer | geçer |
| denek96 | 110,32 | 6,12 | geçer | geçer |
| denek99 | 111,05 | 6,85 | geçer | geçer |
| denek97 | 111,11 | 6,91 | geçer | geçer |
| denek93 | 113,02 | 8,82 | geçer | geçer |
| denek100 | 114,44 | 10,24 | geçer | geçer |
| denek94 | 115,11 | 10,91 | geçer | geçer |
| denek92 | 118,80 | 14,60 | geçer | geçer |
| denek11 | 123,82 | 19,62 | **ret** | **ret** |

**14 olgunun 14'ünde iki band AYNI hükmü veriyor. Fark sıfır.**

### 8.4 Ne değişebilir — araştırmacı kararı
ASO toleransı `0AV` §3.3'teki **vekil değişken uyarısını gereksiz kılar**: AUB/ra
varsayımı yok, doğrudan bi-porion üzerine yayımlanmış bir eşik var. Hiçbir olgunun
hükmü değişmediği için bu bir **kol seçimi değildir** (`00` §0.12 anlamında ortada
değişen bir sonuç yok); yalnız bandın **dayanağı** güçlenir.

Seçenekler: (a) ASO toleransı birincil kaynak olur, Howells türetmesi bağımsız
doğrulama olarak kalır; (b) ikisi birlikte bildirilir; (c) hiçbir şey değişmez,
bu bölüm yalnız doğrulama kaydı olarak durur.

> ✅ **ARAŞTIRMACI KARARI (2026-11-10 21:1x): (b) — ikisi birlikte bildirilecek.**
> Band sayısal olarak **değişmedi** (89,91–121,79; `frankfort.py` dokunulmadı);
> tezde Howells türetmesi ile ASO toleransının örtüşmesi **birlikte** yazılacak.
> AUB vekil değişken uyarısı (§3.3) tezde **kalmaya devam ediyor**, yanında
> ASO'nun vekil değişken gerektirmeyen doğrulaması bildirilecek.

### 8.5 AÇIK — ölçüt 2'nin yerine geçecek kural bulundu
`0AV` §4.1 ölçüt 2'nin yerine geçecek kuralın tam kohort ölçümünden **önce**
sabitlenmesi gerektiğini yazmıştı. ASO'nun yön ölçütü (0,4 rad) + uzaklık ölçütü
(15 mm) bu kuraldır: yayımlanmış, dışarıdan, ve bizim altı ad hoc ölçütümüzün
tamamının yerine geçebilir. Gereken: ALI'nin **yedi** landmarkı da çıkarması
(`Ba, S, N` → CB grubu; `ROr, LOr` → U grubu; `GlobalVar.py` hepsini listeliyor).
Şu an yalnız `RPo, LPo` çıkarılıyor.

> ✅ **ARAŞTIRMACI KARARI (2026-11-10 21:1x): yedi landmark çıkarılacak.**

### 8.5.1 Uygulama — modeller tamamlandı
Eksik üç model (`Ba`, `S`, `N`) `lucanchling/ALI_CBCT` `models_v01` sürümünden
indirildi (her biri ~108 MB, iki ölçek). Yedi landmarkın tamamı artık
`/home/claude/ali/models/<LM>/{1,0-3}/` düzeninde. Koşucu: `porion/kos7.sh`.

**Düzeltilen tuzak:** ALI çıktıyı **grup başına ayrı dosyaya** yazar
(`GlobalVar.py`: `Ba,S,N,RPo,LPo` → CB grubu; `ROr,LOr` → U grubu). İlk koşuda
betik `find ... | head -1` ile yalnız **bir** dosyayı alıyordu ve sessizce iki
landmark döndürüyordu. `an/birlestir_mrk.py` bütün grup dosyalarını birleştirir;
koordinat sistemi uyuşmazlığında ve aynı etiketin iki dosyada farklı gelmesinde
**hata verir**, sessizce birini seçmez.

### 8.5.2 ⚠ NASİON BULUNAMIYOR — ölçülmüş
denek98'de yedi landmarktan **altısı** geldi (`Ba, S, RPo, LPo, ROr, LOr`);
**N bulunamadı.** ALI günlüğü:

```
Searching landmark : N
Landmark found at scale : 0
Agent pos =  [ 81.  68. 127.]
WARNING : Agent trying to go in a none existing space   (x3)
N landmark not found
Fails for N : 1/1
```

Etmen 0,3 mm ölçeğinde **hacmin dışına çıkıyor**. Bu bir **altyapı kusurudur**,
yöntem hükmü değildir (`0AU` §4 ayrımı).

**Görüş alanı sorunu DEĞİL — ölçüldü.** denek98'in hacmi LPS'te
x −151,0..150,4 · y −121,6..179,8 · z −194,8..−19,8 mm. Orbitale orta noktasının
en yakın kutu kenarına uzaklığı **50 mm**; nasion oradan birkaç cm ötede, rahatça
içeride. Nasion taramanın içindedir.

**Başarısızlığın ölçülen biçimi:** etmen kaba ölçekte (1 mm) noktayı buluyor
(`Agent pos = [81, 68, 127]`), 0,3 mm ölçeğine yükseliyor ve orada **üç kez**
sınır dışına çıkıp `search_atempt > 2` ile vazgeçiyor. Yani kusur ince ölçektedir.

### 8.5.3 ⚠ BULUNAN KOD HATASI — gerçek ama SEBEP DEĞİL (yama geri alındı)
`Agents_class.py:123` `Move()` sınır denetimi:
```python
if new_pos.all() > 0 and (new_pos < ...GetSize(...)).all():
```
`new_pos.all()` diziyi tek bir mantıksal değere indirip 0 ile karşılaştırıyor;
doğrusu `(new_pos > 0).all()`. Ölçülen etkisi: **negatif indisler alt sınırdan
geçiyor** (`[100,50,−30]` → yazılan `True`, doğrusu `False`) ve numpy'de negatif
indis dizinin öbür ucundan örnekler.

**Yama denendi ve SEBEP OLMADIĞI ölçüldü.** denek98 düzeltilmiş kodla yeniden
koşuldu:

| | yamasız | yamalı |
|---|---|---|
| gelen landmark | 6 (Ba, S, RPo, LPo, ROr, LOr) | **aynı 6** |
| ortak noktalarda en büyük fark | — | **0,000000 mm** |
| N geldi mi | hayır | **hayır** |

Yani hata gerçektir ama nasion kaybının sebebi değildir.

> ⛔ **YAMA GERİ ALINDI, özgün kod kullanılıyor.** Gerekçe: yamanın etkisizliği
> yalnız **bir** olguda gösterilebildi; bir sınır denetimi hatasının etkisi
> olguya göre değişebilir. `0K` §1 dondurulmuş hat kuralı gereği, bütün kohortta
> etkisizliği gösterilemeyen bir sapma koda sokulmaz. Hata üçüncü taraf kodun
> bilinen kusuru olarak buraya kaydedilir.

### 8.5.4 NASİON GEREKLİ DEĞİL
ASO kaydı katı cisim ICP'dir; eş-doğrusal olmayan **üç** nokta yeter. Elimizde
altı nokta var ve ikisi orta hatta (`Ba`, `S`), yani orta sagital düzlem hâlâ
belirleniyor. ASO'nun kendi `GetLandmarkToRemove`'u zaten landmark atmak üzere
yazılmıştır. **Yedi landmark planı altı landmarkla sürüyor**; N'in yokluğu
kayıt olarak bildirilir.

> ⭐ **YAN DOĞRULAMA:** yedi landmarklı koşuda denek98'in porionları, iki
> landmarklı koşunun ürettiğiyle **bit düzeyinde aynı** (fark 0,0000 mm; bi-porion
> 105,811 ↔ 105,811). Yani landmark listesini genişletmek mevcut noktaları
> değiştirmiyor — `0AD`'nin determinizm kaydı bir kez daha doğrulandı.

### 8.6 Çatı değiştirilmesi ÖNERİLMİYOR
`tez/10` §7 analitik üç noktalı tanımı yazıyor ve GPA zaten dönmeyi giderdiği için
ASO çatısına geçmek **morfometrik sonuçları değiştirmez**, yalnız ham bildirilen
koordinatları değiştirir. Çok iş, sıfır kazanç. ASO yaklaşımı §7c'de kaynak olarak
anılır, çatı olarak benimsenmez.

### 8.7 İZİN NOTU
Bu depo yalnız **okundu**. Araştırmacının 2026-11-09'daki *"İzin veriyorum"* izni
`ALI_CBCT` kodunu **koşturmak** içindi. ASO kodu koşturulacaksa ayrı izin gerekir.
