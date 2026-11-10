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
