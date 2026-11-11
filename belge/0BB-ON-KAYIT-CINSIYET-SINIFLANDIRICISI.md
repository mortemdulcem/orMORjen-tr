# 0BB — ÖN KAYIT: CİNSİYET SINIFLANDIRICISI, DIŞ ETİKETLE EĞİTİM / KÖR PUANLAMA

**Tarih:** 2026-11-11 · **Durum:** ÖN KAYIT — model kurulmadan, tahmin üretilmeden yazıldı
**Araştırmacının tasarımı (10:19):** *"Senin doğruluk oranını ölçeceğim bendeki
cinsiyetlerle"* — etiketler araştırmacıda kalır, bana verilmez.

---

## 1. Tasarım ve niçin güçlü

| | |
|---|---|
| **Eğitim** | Howells kraniyometrik veri seti — 2524 kafatası, **cinsiyeti belgeli** (1368 E / 1156 K), 30 popülasyon |
| **Tahmin** | bizim 98 olgumuz; etiketleri **görmüyorum** |
| **Puanlama** | araştırmacı, kendi elindeki cinsiyetlerle |

Bu düzen kör yarışma düzenidir ve ezberlemeyi **fiziksel olarak imkânsız**
kılar: kohortun etiketleri hiçbir aşamada modele girmez. `0M` §4'ün
olgu-bırak-bir ilkesinin daha güçlü biçimidir.

## 2. Değişken eşleşmesi — ÖLÇÜLEN, varsayılan değil

| Howells | bizdeki | eşleşme |
|---|---|---|
| **DKB** (interorbital, dakriyon–dakriyon) | `IOD_d` | **birebir** |
| **EKB** (biorbital, ektokonkion–ektokonkion) | `BOW_ek` | **birebir** |
| OBH (orbita yüksekliği) | `OH_sag`+`OH_sol` ortalaması | yakın (Howells OBB’ye dik ölçer) |
| OBB (orbita genişliği) | `OW` | **farklı** (Howells dakriyon→ek; bizim ek–mf) |
| FMB (bifrontal) | `BOW_fmo` | **farklı** (Howells frontomalare *temporale*) |

**MODEL 1 (birincil):** yalnız **birebir** eşleşen ikisi — `DKB`, `EKB`.
**MODEL 2 (ikincil):** beşi birden; tanım farkları Tartışma'ya sınırlılık yazılır.

Howells'de ölçülen cinsiyet ayırma gücü (Cohen d): FMB 1,18 · EKB 1,07 ·
OBB 0,79 · DKB 0,46 · OBH 0,26.

## 3. Popülasyon farkı — ölçülmüş çözüm

Howells'de **Türk/Anadolu popülasyonu YOK** ve ölçümü kuru kafatası kumpasıdır,
bizimki BT. İkisi arasında sistematik kayma beklenir.

**Çözüm (`0AV`'nin Howells ilkesiyle aynı): popülasyon içi z-skor.**
Howells her popülasyonun **kendi** ortalama/SS'siyle, bizim kohort **kendi**
ortalama/SS'siyle standartlaştırılır. Boy kayması düşer, kalan şey biçimdir.
Etiket gerekmez; kohortun kendi ortalaması etiketsiz hesaplanır.

⚠ **VARSAYIM:** kohortun cinsiyet oranı kabaca dengeli. Araştırmacı oranı
bildirmedi. Dengeli varsayılmıştır; oran 70/30'dan sapkınsa merkezleme kayar ve
**bu, doğruluk düşerse ilk şüphelidir.** Araştırmacı oranı sonradan bildirirse
model yeniden merkezlenir ve **o da ayrıca raporlanır**.

## 4. Modeller — üçü de koşar, hiçbiri sonuca göre seçilmez

1. **LDA** (doğrusal ayırıcı analiz) — adli antropolojinin standardı
2. **Lojistik regresyon** (L2)
3. **Sinir ağı (MLP)** — 2 gizli katman, `sklearn.MLPClassifier`

Üçünün de Howells üzerindeki çapraz-doğrulanmış doğruluğu **önce** raporlanır;
kohort tahmini **üçü için ayrı ayrı** verilir. Araştırmacı hepsini puanlar.
Sonuç görüldükten sonra "en iyi model" seçilmez.

## 5. Önceden yazılan beklentiler

Howells 5-katlı çapraz doğrulamada beklenen doğruluk **%65–80** (d=0,46–1,18
düzeyindeki iki-beş değişkenle). Kohortta bundan **daha düşük** çıkması
beklenir, çünkü popülasyon ve görüntüleme farkı var.

- **%90'ın üstü çıkarsa:** sızıntı şüphesi. Durulur, aranır, raporlanır.
- **%50 civarı çıkarsa:** model aktarılamamıştır; bu da bir bulgudur
  (Türk popülasyonu için kendi formülü gerekir — tezin özgün katkı iddiası).

## 6. Bu modelin teze giriş biçimi

Bu, tezin **ana** cinsiyet analizi DEĞİLDİR; ana analiz kohortun kendi
etiketleriyle, kendi formülüyle yapılır (araştırmacı etiketleri açtığında).
Bu koşu iki şey verir: (a) dış formülün bu kohorttaki aktarılabilirliği,
(b) ölçümlerimizin cinsiyet bilgisi taşıyıp taşımadığının **bağımsız** sınavı.

## 7. GPU yok — ne yapılmadığının kaydı

Konteynerde GPU yoktur (`torch 2.15.0+cpu`, 2 çekirdek). 3B evrişimli ağ
(landmark ısı haritası, nnU-Net) bu ortamda eğitilemez. Buradaki "sinir ağı"
tablo verisi üzerinde **çok katmanlı algılayıcıdır**, 3B CNN değildir, ve
öyle raporlanır.

---

## 8. SONUÇ — MODELLER KURULDU, TAHMİNLER ÜRETİLDİ (2026-11-11)

Kod: `an/cinsiyet.py` · çıktı `an/out/cinsiyet_tahmin.json` ve
`cinsiyet_tahminleri_2026-11-11.csv`.

### 8.1 Howells üzerinde 5-katlı çapraz doğrulama

| model | MODEL 1 (`DKB`,`EKB`) | MODEL 2 (beş değişken) |
|---|---|---|
| LDA | 0,726 ± 0,017 | **0,760 ± 0,009** |
| Lojistik | 0,724 ± 0,018 | 0,759 ± 0,007 |
| Sinir ağı (MLP 16-8) | 0,725 ± 0,016 | 0,756 ± 0,005 |

Eğitim n=2524 (1368 E / 1156 K), 30 popülasyon, popülasyon içi z-skor.

**§5'in ön kayıtlı beklentisi %65–80 idi; sonuç %72,4–76,0 ile bandın içinde.**
%90 üstü çıkmadı, yani sızıntı işareti yok. Üç model birbirine çok yakın —
ilişkinin doğrusal olduğunu ve MLP'nin ek bir şey öğrenmediğini gösterir.

### 8.2 Kohort tahmini (n=75, havuz içi)

Altı modelin **61'inde (%81) oy birliği** var. Çoğunluk dağılımı: **45 E / 30 K**.
Bu, §3'ün "kabaca dengeli" varsayımıyla tutarlı — ama varsayımı doğrulamaz,
çünkü dağılım merkezlemeden gelir.

### 8.3 Araştırmacının puanlaması

`cinsiyet_tahminleri_2026-11-11.csv`: her denek için altı modelin tahmini,
oy birliği bayrağı ve çoğunluk. Araştırmacı kendi etiketleriyle puanlar.
**Puan gelmeden hiçbir model "en iyi" seçilmez** (§4).

Beklenen: kohort doğruluğu Howells'inkinden **düşük** çıkacaktır (popülasyon ve
görüntüleme farkı). %50 civarı çıkarsa bu bir başarısızlık değil **bulgudur**:
dış formül Türk BT kohortuna aktarılamıyor demektir ve tezin özgün katkı
iddiasını güçlendirir.

### 8.4 Sınırlılıklar — teze yazılacak

1. Howells'de **Türk popülasyonu yok**; en yakınları ZALAVAR, BERG, NORSE, EGYPT.
2. Howells **kuru kafatası kumpas** ölçümü, bizimki **BT**.
3. `OBB` ve `FMB` tanımları birebir değil (§2); MODEL 1 bu yüzden birincildir.
4. `OBH`/`OBB` bizde taraflıdır, **iki taraf ortalaması** alınmıştır.
5. Kohort merkezlemesi **cinsiyet oranının dengeli olduğunu varsayar** (§3).
6. GPU yokluğu nedeniyle 3B CNN denenmemiştir (§7); buradaki sinir ağı tablo
   verisi üzerinde çok katmanlı algılayıcıdır.
