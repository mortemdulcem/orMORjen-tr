# 0AU — 26–37 Frankfort çıktısı üretildi; `frankfort.py` yeniden kuruldu

**Tarih:** 2026-11-10 · **Araştırmacı talimatı:** *"b)'yi, yani tezi bloklayan
26–37 çıktısını halleT"*

> 🔄 **BU BELGE KISMEN GÜNCELLENDİ (2026-11-10 20:40).** §6'da araştırmacı
> kararına bırakılan band sorunu `0AV` ön kaydıyla **çözüldü**: bi-porion bandı
> dış kaynaktan (Howells) yeniden türetildi, 89,91–121,79 mm oldu ve kapsama
> 9/14'e çıktı. §4 ve §6 bu sonuca göre düzeltilmiştir. Ölçüt 2 değişmedi.

---

## 1. NE ÇÖZÜLDÜ

`0F` §25d'nin kararı şuydu: *"Kapsama tamamlandığında karar A'ya döner ve
`an/dok_2637.py` tek koşuda yeniden döker."* Bugün o hat kuruldu, koştu ve
çıktı üretti. Tıkanıklık porion kapsamasıydı; `PO.bul` zaten bırakılmıştı
(`0AD`), ALI ise konteyner sıfırlanmasıyla kurulumunu kaybetmişti.

**Üretilen:** `veri_disk/26-37_landmark_FRANKFORT.csv` — 36 sütun + `denek`.

## 2. KAYBOLAN DOSYALAR — ve ne yapıldı

`an/frankfort.py`, `an/porion.py`, `an/dok_2637.py` konteyner sıfırlanmasında
kayboldu. **Drive'daki `bellek yetmeyenler` klasörüne bakıldı — orada da yok**
(klasör bugün açılmış, henüz boş). Proje belgelerinde de kaynak kodları yok.

Yeniden kuruldu, ama tahminle değil: `an/frankfort.py`'nin içinde altı ölçütün
her birinin eşiği, **yanında kaynağı yazılı** olarak duruyor. Belgede sayısı
bulunmayan hiçbir eşik koda konmadı.

> ⭐ **YENİDEN KURULUMUN BAĞIMSIZ DOĞRULAMASI.** Dönüşümün rijitliği
> **2,842 × 10⁻¹⁴ mm**; `0Y` §2'nin kaybolan özgün kodla kaydettiği değer
> **2,8 × 10⁻¹⁴ mm**. Aynı. det(R) = 1,000000000000, R ortogonalliği 2,2×10⁻¹⁶.
> Ayrıca iki porion Frankfort çatısında z = 10⁻¹⁴ mertebesinde, yani tam düzlem
> üzerinde; x'te simetrik.

Kurulum `tez/10` §7'nin teze yazılacak tanımıyla birebir örtüşüyor:
*"her iki porion ile **sol** orbitaleden geçen düzlem"*.

## 3. ALI UYUMLULUK — `0AD` §3'ün aynısı + bir bellek yaması

| eksik | çözüm | sayısal davranış |
|---|---|---|
| `AddChannel` monai ≥1.0'da kaldırılmış | özgün davranışı (`img[None]`) veren eşdeğer sınıf | değişmez |
| `BorderPad` artık `MetaTensor` dönüyor | Compose'un sonuna `_ToNumpy` | değişmez |
| `LoadImages` bellek yığılması (~5,4 GB, kap 7 GB) | **saf yeniden sıralama** + ara kopyaların serbest bırakılması | değişmez |

`np.pad`'in `BorderPad` ile **bit düzeyinde aynı** olduğu küçük bir dizide
ölçülerek doğrulandı (fark 0,0). `torchvision` ABI sorunu bu ortamda çıkmadı.

## 4. KAPSAMA — iki sebep AYRI tutuldu

Bellek yaması uygulandıktan sonra denek11 de koştu; **altyapı kusuru sıfıra
indi.** Nihai durum:

| durum | n | not |
|---|---|---|
| paket | 14 | CT'si hazır denekler |
| ALI koşamadı (**altyapı**) | **0** | bellek yaması sonrası |
| ölçüldü (**yöntem hükmü**) | 14 | |
| — altı ölçütü geçen (`0Z` bandı) | 7 | %50 |
| — altı ölçütü geçen (**`0AV` bandı, geçerli**) | **9** | **%64,3** |

Ayrım şart: altyapı kusuru tarama alanının büyüklüğüyle ilişkilidir
(denek11 0,3 mm'de 839 milyon voksel) ve karıştırılırsa kapsamaya **sistematik
yanlılık** sokar.

## 5. KAPI ÇALIŞIYOR — ölçülmüş kanıt

| denek | düşen ölçüt(ler) | karşı orbitale | min maks HU |
|---|---|---|---|
| denek10 | 1 + 2 (5,62) + 3 (88,73) + 4 + 6 | **67,70** | **47** |
| denek11 | 2 (8,39) + 3 (123,82) + 4 + 6 | **50,51** | **72** |
| denek78 | 2 (10,29) + 6 | **24,83** | 882 |

denek10'un her iki porionu da kafatasının **dışında, yumuşak dokuda** —
üç düzlem görsel denetimiyle (`00B` §T9) doğrulandı. HU 47–72, `0F` §24'ün
yanlış porionlar için kaydettiği **58–75** aralığının içi. denek78'in karşı
orbitalesi 24,83 mm, aynı belgenin kaydettiği **24–30 mm** imzası.

Üçü de `0AV`'nin genişletilmiş bandıyla da reddedilmeye devam ediyor; denek10
ve denek11 **yalnız ölçüt 3 tarafından** bile düşüyor.

## 6. ✅ ÇÖZÜLDÜ — `0Z` bandı bu kohorta oturmuyordu

Bu bölüm dört reddi araştırmacı kararına bırakmıştı. Karar alındı ve `0AV` ön
kaydıyla uygulandı. Sorunun kendisi aşağıda olduğu gibi duruyor:

| denek | düşen ölçüt (`0Z`) | karşı orbitale | min maks HU | `0AV` sonrası |
|---|---|---|---|---|
| denek100 | 3 — bi-porion 114,44 (**+0,04 mm**) | 2,22 | 743 | **KABUL** |
| denek94 | 3 — bi-porion 115,11 (+0,71) | 2,79 | 1051 | **KABUL** |
| denek92 | 2 (3,32) + 3 — bi-porion 118,80 | **0,69** | 1183 | ret (2) |
| denek95 | 2 — orta-MSP 3,54 (eşik 3,00) | 1,13 | 999 | ret (2) |

`0F` §24'ün bandları: **doğru** porionlarda karşı orbitale 0,55–2,83 mm ·
maks HU 1298–1757; **yanlış** olanlarda 24–30 mm · 58–75 HU. Dördünün de
karşı orbitalesi doğru aralığın **tam içinde**. denek92'nin karşı orbitalesi
**0,69 mm** ile bütün kohortun en iyisi ve üç düzlem denetiminde her iki
porion da dış akustik meatusta, temporal kemikle çevrili (görüntü incelendi).

**Dağılım kanıtı:** karşı orbitalesi ≤3 mm olan 11 olguda bi-porion
**105,81–118,80 mm**, ortanca **111,05**. `0Z` bandının üst sınırı (114,4) bu
dağılımın ortasından kesiyordu. Öğrenme setinde kabul edilenler **102,8–110,6**
idi — bu kohort sistematik olarak daha geniş.

### 6.1 Nasıl çözüldü — `0AV`
Band **kohorttan değil dışarıdan** yeniden türetildi: merkez `0Z`'den
değişmeden alındı (105,85), yarı-genişlik Howells'ın popülasyon içi havuzlanmış
AUB standart sapmasından (5,313 mm; n=2524, 30 popülasyon) kuruldu.
**Band = 89,91–121,79 mm.** Ayrıntı, vekil değişken uyarısı ve §0.12 dürüst
kaydı `0AV`'de.

### 6.2 Ölçüt 2 DEĞİŞMEDİ
Araştırmacı önce 4,00 mm'yi seçti; dış kaynak arandı ve **desteklemediği**
bulundu (+3SS sınırı 3,21–3,59 mm) — üstelik o aralık denek92 ve denek95'in
değerlerinin üstüne düşüyor, yani aralıktan seçim doğrudan bu iki olgunun
hükmünü belirlerdi. Bulgu araştırmacıya iletildi, karar **ölçüt 2'ye
dokunmamak** yönünde değiştirildi. Eşik 3,00'de kaldı. Ölçüt 2'nin geçerliliği
üzerine yapısal bulgu `0AV` §4.1'de; `0K` §1'in tam kohort ölçümüne taşındı.

## 7. İKİ YAPISAL BULGU — teze yazılmalı

**a) Ölçüt 5 üç noktalı kurulumda boşa düşer.** Düzlem po-r/po-l/**o-l**'den
geçtiği için `o-l`'nin uzaklığı yapı gereği sıfırdır (ölçüldü: 6,9×10⁻¹⁶ mm).
`0F` §24'te olguların yalnız birinin *"altı ölçütün hepsini"* geçmesi bu
okumayla uyuşmuyor ve hangi ölçütün düştüğü belgede **yazılı değil**.
Uydurulmadı: altı sayının hepsi olgu başına kaydediliyor, ayrıca **dört noktalı
en küçük kareler** teşhis kurulumu da hesaplanıyor (denek97: sol 0,344 ·
karşı 0,361 mm).

**b) 36 sütunun biri sıfır varyanslıdır.** Aynı sebeple `o-l_z` her olguda
özdeş olarak 0. Procrustes için zararsız, ama *"12 landmarkın 3B koordinatı"*
denirken bu sütunun bilgi taşımadığı **yazılmalı**.

**c) Düzlem içi dönme Frankfort tanımıyla sabitlenmez.** Ön eksen, porion orta
noktasından orbitale orta noktasına uzanan doğrultuyla tanımlandı ve bu kural
**koşudan önce** yazıldı. Alternatif kural (yanal eksen doğrudan porion
doğrusuna) koordinatları düzlem içinde birkaç derece döndürür; kabul edilen
olgularda porion doğrusunun ön eksendeki artığı 0,46–3,26 mm ölçüldü.
Procrustes döndürmeyi giderdiği için GM sonuçları etkilenmez; yalnız ham
bildirilen koordinatlar değişir.

## 8. `00` §0e'NİN BEKLEYEN MADDESİ KAPANDI

*"⏳ HÂLÂ BEKLEYEN: metin artık doğru ama 2. maddedeki koordinat çıktısı henüz
üretilmemiştir."* — Çıktı üretildi. Tez §3.5 artık veriden doğrulanabilir
durumda (kabul edilen olgular için).

## AÇIK İŞ
- [x] ~~denek100 / denek92 / denek94 / denek95 kararı~~ → `0AV` (2026-11-10)
- [ ] Kohortun tamamı: 26–37, `0K` §1 yeniden ölçümüyle aynı koşuda dökülecek
- [ ] **Ölçüt 2'nin yerine geçecek kural**, tam kohort ölçümünden ÖNCE
      sabitlenecek (`0AV` §4.1)
- [ ] Porion güvenilirlik alt çalışması (`0K` §9) — porion kendi ICC'siyle
- [ ] `o-l_z` sıfır varyansı tez metnine yazılacak (§7b)
- [ ] AUB vekil değişken varsayımı tez sınırlılıklarına yazılacak (`0AV` §3.3)
