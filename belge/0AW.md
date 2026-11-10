# 0AW — Kilit sonrası kohort tablosunun geri kurulması (94 → 98 satır)

**Tarih:** 2026-11-10 23:0x (Europe/Istanbul)
**Araştırmacı talimatı:** *"ölçüm sırası hangi denekte"* → *"1 inhemen başla"* → *"B"* → *"A"*
**Çıktı:** `kohort/kohort_98.csv`
**SHA-256:** `ecc02aa7439f828d4427e4a094e1f170b3d61c149c3be7f2c90848f1ef340354`

---

## 1. SORUN

`0AS` kilit zinciri kohortu **97 olguya** kadar getirmişti (denek98 → 95,
denek99 → 96, denek100 → 97) ve denek101 de ölçülmüştü (`0AT` §3). Ama
konteyner sıfırlanmasında:

| kaybolan | sonuç |
|---|---|
| `kohort/kohort.csv`'nin güncel sürümü | diskte kalan kopya **94 satır** — yeni dördü yok |
| `kohort/tablo_uret.py` | tabloyu raporlardan kuran betik |
| `kohort/giris_denetimi.py` (T11) | yeni olgu giriş denetimi |
| `kohort/olc.py`, `uc_duzlem.py`, `lob_testi.py`, `apeks_gecir.py` | T12'nin beş adımı |
| `kohort/denetim/mukerrer_tam.json` | parmak izi veritabanı |
| `orbita_hat/raporlar/` | **tek** rapor kaldı (denek97) |

Drive'daki kopya da 94'lüktü (`kohort_2026-11-09_KILITLI_94olgu.csv`).
**Güncel tablo hiçbir yerde yoktu.**

## 2. GERİ KURULAN VE DOĞRULANAN

### 2.1 Ölçüm zinciri — 29 sütun
`orbita_hat/olcum_zinciri.py` hayatta kalmıştı ama **komut satırı arayüzü rim
eğrilerini `olc()`'ye geçirmiyor**; kohort `otomasyon2.calistir()` üzerinden
ölçülmüştü. Eğrisiz koşunca APalan altıgen yedek kolundan hesaplanıyor ve
kayıttan sapıyor (denek98: 1016,9 yerine 1051,0 olmalıydı). `orbita_hat/olc_paket.py`
eğrileri geçirir ve `on_sinir_duzlemde=True` kullanır (`0AT` §2'nin kaydettiği
kohort ayarı *"eğri varsa plane_shift=0"* — kodun belge dizesindeki karşılığı).

**Dört olgu da kilitli kayıtlarla örtüştü:**

| denek | hacim sağ/sol | APalan sağ/sol | RED/UYARI | kaynak |
|---|---|---|---|---|
| denek98 | 22,246 / 22,746 | **1051,0 / 1057,0** | 0 / 2 | `0AS` ile aynı |
| denek99 | 29,929 / 29,458 | **1161,2 / 1211,4** | 0 / 2 | `0AS` ile aynı |
| denek100 | 24,850 / 26,094 | **1337,7 / 1426,8** | 0 / 1 | `0AS` ile aynı |
| denek101 | 26,825 / 26,315 | 1177,5 / 1188,7 | 0 / 2 | `0AT` §3 ile aynı |

Tek fark denek100 sağ hacminde: `0AS` 24,854 yazıyor, ölçülen 24,850 — ama
`0AT` §3'ün "KAYITLI" sütunu da **24,850**. `0AS` tablosundaki yazım farkı.

### 2.2 Altıgen apertür — 6 sütun, GERİ KURULDU
`0T` tanımı: altı rim landmarkının (`ORD = d,mf,mso,fmo,ek,o`) çokgeni,
**kalibrasyon katsayısı uygulanmadan** (`0T` §3 bunu açıkça yasaklıyor).

Hayatta kalan `olcum_zinciri.py`'de `APalan6` **yoktu** (oradaki altıgen yalnız
eğri bulunamazsa devreye giren yedek kol). Tanım belgeden alındı, **üç olguda
× iki tarafta** kilitli değerlere karşı sınandı:

| büyüklük | formül | sonuç |
|---|---|---|
| `APcevre6` | `params.perim(H)` | **6/6 birebir** |
| `APalan6` | en iyi uyan **düzleme izdüşürülmüş** çokgen alanı (Newell DEĞİL) | 6/6, ±0,02 |
| `APduzlemsizlik6` | düzleme **ortalama mutlak** uzaklık (maks ya da oran değil) | 6/6, ±0,0002 |

Newell alanı %0,1 yüksek çıkıyordu; izdüşüm alanı tutturdu. Bu, formülün
belgeden değil **ölçümden** belirlendiği bir karardır ve üç bağımsız olguda
altı kez doğrulanmıştır.

## 3. ⛔ GERİ KURULAMAYAN İKİ ADIM

### 3.1 Lob (`lob_cikan_sag/sol`) — kod sessizce inert
`rayseg.lob_temizle` hayatta (`0AT`'de `0R` §2'den kurulmuş) ama **çalışmıyor.**
denek10 sağda üç yarıçapın üçünde de açma **tek bileşen** veriyor
(54325 · 52796 · 52111 voksel) → `if nl_ == 1: continue` → sıfır voksel çıkarılıyor.
`0R` §1 ise aynı olgu için **r=2,0 → 0,201 cm³** kaydetmişti.

Maske doğru: kurulan 26,526 cm³, kayıtlı temiz 26,331 + kayıtlı lob 0,2012 =
26,532. Fark **12 voksel (%0,02)**. Lob maskenin içinde, ayrılmıyor.

**Beş yapısal varyant denendi, hiçbiri hedefi (412 voksel) tutturmadı:**
mevcut `>`/`<=` · `>=`/`<` · örneklemesiz voksel birimi · maskeyle
sınırlandırılmamış açma · 26-bağlantılı etiketleme. **Beşi de üç yarıçapta tek
bileşen.** Sorun açma uygulamasında değil, maskenin boyun bölgesinde.

> **Durma gerekçesi:** elde düşülecek **tek** hedef sayı var (denek10 sağ,
> 0,2012). Diğer iki doğrulama olgusunun (denek11, denek78) kayıtlı lobu zaten 0,
> yani ayırt edici değiller. Tek sayıyı tutturana kadar kod değiştirmek, `00`
> §0.12'nin yasakladığı şeyin kod tarafındaki karşılığıdır.

> ### ⚠ `0AT` §3'ÜN HÜKMÜ DARALTILDI
> *"Hat değişmemiştir"* hükmü denek98–101'de Dice 1,000 ile verilmişti — ama o
> dört olguda **lob yok**. Sadakat sınavı maske kurulumunu doğruladı, **lob
> kolunu hiç sınamadı.** Bugünkü kodla ölçülecek yeni bir olguda lob varsa
> sessizce maskede kalır: `0Q` EK 4'ün SINAV 4 ile kapatılan kusuru, fark
> edilmeden geri gelmiş durumda. **Kapsamı bilinmiyor** (94 olgunun paketi yok,
> 14'ü var).

### 3.2 Apeks (10 sütun) — iki şablon eksik
`0M` §10.3: dört parametre (`mf`, `ek`, `mso`, `o` → apeks, 3B Öklid) kohortun
**atlas apeksiyle hesaplanamaz**; NICP apeksi gerekir. `0M` §5 yöntemi
**7 şablonlu** NICP ile doğruladı ve 2. ölçütün payı yalnız **%4,1** idi
(MAE 1,65 · eşik 1,72).

Diskte **5 şablon** var (hasta7, 8, 9, 10, 11). **Eksik: hasta5
(`ölçüm denemesi 2`) ve hasta6 (`hasta6 ölçüm 3`, yedek `ölçüm 2`).**
Drive'daki `bellek yetmeyenler` klasörüne bakıldı — **boş**.

Beş şablonla koşmak doğrulanmış yöntem değil **başka bir kestirici** olur.
`0M` §4 bu durumu zaten karara bağlamış: *"Sağlanmazsa: derinlik `None` kalır…
Eşik oynatılmaz, yeniden koşulmaz."* **Koşulmadı.**

## 4. TABLO — `kohort/kohort_98.csv`

94 eski satır **değiştirilmeden** korundu; dört yeni satır eklendi.
Betik: `kohort/tablo_kur.py` (her sütunun kaynağı belge dizesinde yazılı).

| sütun kümesi | n | kaynak |
|---|---|---|
| ölçüm | 29 | `orbita_hat/raporlar/<denek>_OLCUM.json` (§2.1) |
| altıgen | 6 | `0T` tanımı, §2.2'de doğrulandı |
| kesit, voksel_mm | 2 | paketin CT nrrd başlığı (`0AS` ile örtüştü) |
| RED, UYARI, uyari_kapilari, havuz | 4 | raporun `denetim` bölümü |
| cekirdek, kemik_kapisi | 2 | `0AS` kilit zinciri — **denek101 için kaynak yok, boş** |
| denek, olcum_tarihi | 2 | ad + **yeniden kurulma damgası** (özgün ölçüm tarihi değil) |

**Dört yeni satırda BOŞ bırakılanlar ve sebepleri:**

| sütun | sebep |
|---|---|
| `apeks_*` (10) | §3.2 — iki şablon eksik |
| `lob_cikan_*` (2) | §3.1 — kod inert, uydurma 0 yazılmadı |
| `mukerrer_uyari` | parmak izi veritabanı kayıp (T11 1. sorusu yanıtlanamıyor) |
| `sure_sn` | yeniden kurmanın süresi özgün ölçümün süresi değildir |
| `red_kapilari` | RED = 0, yani **boş olması doğru** |

**Havuz:** 75 / 98 (önce 71 / 94). Dört yeni olgunun dördü de havuzda —
`0AS` kilit #4'ün "74 / 148 orbita"sına denek101 eklenince 75 / 150.

> ⚠ **`0AS`'nin SHA zincirine BAĞLANAMAZ.** Kilit özetleri dosyanın baytlarının
> özetidir ve `tablo_uret.py`'nin biçimlendirmesi kayıp. Doğrulama **değer
> bazında** yapıldı (§2.1), bayt bazında yapılamadı. Yeni dosya kendi özetiyle
> kaydedilir; zincire yeni bir satır olarak girer, eskisinin yerine geçmez.

## 5. AÇIK İŞ
- [ ] **hasta5 ve hasta6 arşivleri** → apeks adımı aynı turda kurulur (§3.2)
- [ ] **Lob kusuru** — kapsamı ölçülmeli; `lob_temizle` neden ayırmıyor (§3.1)
- [ ] `kohort/giris_denetimi.py` + parmak izi veritabanı (T11) geri kurulmalı;
      denek102 bekliyor (pencere ve `ImageType` kapıları geçti, mükerrerlik
      denetimi yapılamadı)
- [ ] `0AS`'ye yeni kilit satırı — araştırmacı onayından sonra
