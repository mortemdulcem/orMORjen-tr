# 0AZ — ÖN KAYIT: CRANIUMPY'NİN KENDİ NICP MOTORU (DÖRDÜNCÜ DENEME)

**Tarih:** 2026-11-11, 09:0x · **Durum:** ÖN KAYIT — tam koşu başlamadan yazıldı
**Bağlam:** `0AY` §6 (apeks kapandı) · `0AX` §8 · `YONTEM-KATALOGU` A5
**Cinsiyet:** körlü

---

## 1. Bu neden `0AY` §6.4'ün "dördüncü deneme yapılmaz" hükmünü ÇİĞNEMİYOR

`0AY` §6.4 çizelge taramasını yasakladı: *"çizelge taraması, ara değer, başka
depo: hiçbiri."* Bu koşu bir çizelge denemesi **değil**, farklı bir **algoritma**.

`0AY`'de yaptığım şey CraniumPy'nin **sayılarını** (katılık çizelgesini) alıp
BİZİM `an/nicp.py` motorumuza koymaktı. Araştırmacının *"kur onu"* talimatı
bunu değil, deponun **kendi kodunu çalıştırmayı** istiyordu. İkisi aynı şey
değil. CraniumPy'nin motorunda bizim motorumuzda **bulunmayan iki adım var:**

1. **`dist_threshold = 10 mm`** — bu uzaklıktan öteye düşen eşleşmeler
   ağırlık 0 alır, yani hedefte delik/kırpık olan yerler komşu tepeleri
   yanlış tarafa çekemez. Bizim `nicp.py`'de böyle bir eleme **yok**.
2. **SINIR–SINIRA eşleşme** — kaynağın **açık kenar** tepeleri yalnızca
   hedefin açık kenar tepeleriyle eşleşir. Bizim orbita meshlerimiz
   `yuzey.hazirla` ile kutu içinden kesilir, yani **açık kenarlıdır**; bizim
   motorumuzun sınır kavramı hiç olmadığı için kenar tepeleri hedefin **iç**
   yüzeyine kayabilir. `0AX` §8.2'de ölçtüğümüz yüksek saçılımın mekanik
   adayı budur.

Yani yasaklanan şey (aynı motoru farklı sayılarla tekrar koşmak) yapılmıyor;
kataloğun A5 satırında **zaten bekleyen** iş (*"bağımsız doğrulama olarak
kullanılacak"*) yapılıyor.

## 2. AMA `0M` §5.1'İN ÖLÇÜTLERİ TÜKENMİŞTİR — bu koşu apeksi AÇAMAZ

Üç ölçüt üç kez kullanıldı (ds=4, ds=2, dış çizelge). Dördüncü kullanım
çoklu-deneme sorunudur: yeterince yöntem denenirse biri eninde sonunda geçer.

**Bu nedenle, bu koşunun sonucu NE OLURSA OLSUN:**

- Üç ölçüt de geçse bile apeks sütunları **doldurulmaz**.
- `0M` §10.3'ün dört Cureus parametresi **teze girmez**.
- Sonuç **keşifsel** sayılır ve öyle raporlanır.

**Apeksi yalnızca tek bir kapı açabilir** ve o kapı zaten ön kayıtlıdır:
`0M` §5.4/4 ve §8'in **kör 30 olgu** doğrulaması —
`kohort/altkume.py` (HMAC ile seçilmiş 30 olgu) → `kohort/kor_paket.py` →
araştırmacının körlemesine 14 nokta işaretlemesi → `kohort/kor_karsilastir.py`.
Eşikleri 2026-11-07'de kilitlendi ve **hiç kullanılmadı**:

- **(A1)** apeks 3B hatası ortalama **< 5,14 mm**
- **(A2)** derinlik MAE kalibresiz **< 1,72 mm**

Bu koşunun tek meşru işlevi, o kör sınava **girmeye değer bir aday olup
olmadığını** göstermektir.

## 3. Sabitlenen ayarlar

- Motor: `an/cranium_nicp.py` — CraniumPy `nicp()`'in türevi, sayısal adımlar
  değiştirilmeden, donüş `(TV, X)` yapılarak (bizim `nokta_aktar` X ister).
  Apache-2.0, DOI 10.5281/zenodo.7430069, atıf dosya başlığında.
- `dist_threshold = 10.0` · `gamma = 1.0` · `alphalar = linspace(200,1,20)` ·
  `ic_tur = 3` — **hepsi CraniumPy'nin yayımlanmış varsayılanı**, hiçbiri
  bizim seçimimiz değil.
- `APEKS_DS = 4`; HEDEF/HİZALAMA `0M` §3 KOL B'deki gibi; LOO.
- `medial.py`'nin varsayılan yolu **değişmedi**: motor seçilmezse eski kod
  bire bir çalışır, `0J`/`0M`'in medial koşuları etkilenmez.

## 4. ÖNCEDEN GÖRÜLEN VERİ — dürüst bildirim

Bu ön kayıt yazılmadan önce **hasta8** tek olguluk bir deneme koşusunda
çalıştırıldı (motorun kurulduğunu doğrulamak için): sağ 1,11 / sol 1,70 mm.
Yani 7 olgunun 1'inin sonucu ön kayıttan önce görülmüştür. Bu, ön kaydı
zayıflatır ve §2'deki "apeksi açamaz" hükmünün ikinci gerekçesidir.

## 5. Ne raporlanacak

Üç ölçütün birleşik değeri (14 orbita), olgu bazında hata, yanlılık, saçılım,
r, ve süre. `0M`'in kayıtlı +1,110 / 1,787 / +0,542 üçlüsüyle karşılaştırma.
Hüküm cümlesi yalnız şu olabilir: *"kör 30 olgu sınavına aday / aday değil."*

---

## 6. SONUÇ — ÖLÇÜT 2 DÖRDÜNCÜ KEZ DÜŞTÜ, APEKS KAPALI KALIYOR

Koşu: `APEKS_MOTOR=cranium`, ds=4, iki paralel işçi, 66–89 sn/olgu.
Çıktı: `an/out/apeks_loo_cranium.json`.

| ölçüt | taban | `0M` | ds=4 | ds=2 | dış çizelge | **CraniumPy motoru** |
|---|---|---|---|---|---|---|
| 1 — apeks 3B hatası | < 5,14 | 2,69 | 3,49 | 3,47 | 3,41 | **3,16** E |
| 2 — derinlik MAE | < 1,72 | 1,65 | 2,24 | 2,05 | 2,05 | **2,03 RET** |
| 3 — sağ/sol farklı | ≥ 6/7 | 7/7 | 6/7 | 5/7 | 2/7 | **6/7** E |

yanlılık −0,685 · saçılım 2,571 · r +0,407 (`0M`: +1,110 / 1,787 / +0,542)

### 6.1 Sınır–sınıra eşleşme GERÇEKTEN işe yaradı

`0AY`'nin dış çizelgesi ölçüt 3'ü 2/7'ye düşürmüştü (sağ ve sol kestirimler
birbirine yapışıyordu). CraniumPy'nin motoru aynı çizelgeyle **6/7** veriyor.
Fark iki ek adımdan geliyor (sınır kısıtı + 10 mm eşiği) ve `0AZ` §1'in
hipotezini doğruluyor: bizim motorumuzun kenar tepeleri gerçekten kayıyordu.
Ölçüt 1 de dört koşunun en iyisi.

### 6.2 Ama DERİNLİK DUVARI kırılmadı — ve bu artık bir bulgu

Derinlik MAE dört bağımsız yapılandırmada **2,24 · 2,05 · 2,05 · 2,03 mm**.
Çözünürlük beş kat, katılık çizelgesi altı kat, motor tamamen değişti; sayı
değişmedi. Bu, ayarlanmamış bir parametre değil **yöntemin tavanı**.
`0M`'in 1,65'i bu tavanın altında ve dört denemeyle yeniden üretilemedi.

### 6.3 Dışlama gerekçesi ARANDI, BULUNAMADI

Hataların çoğu tek orbitada toplanıyor: hasta5 sol, dört koşuda da en kötü
(7,00 · 3,17 · 7,07 · 7,09 mm). hasta5 sol çıkarılsa MAE 1,68 mm'ye iner ve
ölçüt 2 geçerdi.

**Yapılmadı.** `0K` §4.4 sonuca bakarak olgu dışlamayı yasaklar. Bunun yerine
**sonuçtan bağımsız** bir girdi denetimi koşuldu: her olgunun ELLE apeksi
kendi altı rim landmarkının çerçevesinde (t, dik, yan) yazıldı ve kohort
içindeki z-skoru hesaplandı.

| olgu/taraf | t | dik | yan | z (t, dik, yan) |
|---|---|---|---|---|
| **hasta5 sol** | 42,10 | −3,67 | −1,57 | **+0,80 / +0,34 / +1,05** |
| hasta9 sağ | 42,44 | +1,94 | −4,25 | +0,99 / **+2,12** / +0,27 |

**hasta5 sol kusurlu DEĞİL** — üç bileşeni de normal aralıkta. Tek sapkın
orbita hasta9 sağ ve o sorunlu olan değil. Yani elle girdide dışlamayı haklı
çıkaracak bir kusur yok; hata **kestirimde**.

### 6.4 HÜKÜM

1. `0AY` §6.4'ün hükmü **ayakta**: apeks BT'den otomatik ölçülemedi.
2. `0AZ` §2 zaten bu koşunun apeksi açamayacağını yazmıştı; ölçüt 2 düştüğü
   için konu ayrıca kapanıyor.
3. **Kör 30 olgu sınavına aday DEĞİL.** O sınavın A2 eşiği de 1,72 mm'dir;
   2,03 ile girmek sınavı harcamak olur. A1 (<5,14) geçerdi, A2 geçmezdi.
4. Apeks sütunları kalıcı boş; `0M` §10.3'ün dört parametresi teze girmez.
5. **Kazanç:** `an/cranium_nicp.py` artık kurulu ve doğrulanmış bir bağımsız
   NICP motorudur. `YONTEM-KATALOGU` A5'in *"karşılaştırma bekliyor"* satırı
   kapandı. Bu motor d/mf kestirimi (`0J`, `0M` medial kolu) için de
   kullanılabilir — ayrı bir ön kayıt konusudur, burada yapılmadı.

### 6.5 Teze yazılacak ek cümle

*"Yöntem, biri yayımlanmış bağımsız bir uygulama (CraniumPy, Apache-2.0)
olmak üzere dört ayrı yapılandırmada sınanmış; derinlik ortalama mutlak
hatası dört koşuda da 2,03–2,24 mm aralığında kalarak sabit kestirici
tabanını (1,72 mm) geçememiştir."*
