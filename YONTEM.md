# Lob temizliği — BOZUK, kapsamı bilinmiyor

**Dosya:** `an/rayseg.py` → `lob_temizle` · **Tanım:** `0R` §2 KOL B

**NE:** Orbita apeksi çevresinde kemik yarıklarından (fissura orbitalis
superior/inferior) maske dışarı sızıp ince boyunlu bir lob oluşturuyor.
`0Q` EK 4: havuzun **18/118 orbitasında (%15,3)**, büyüklük 0,03–0,85 cm³.
En büyüğü denek15 sol **0,852 cm³ (%2,77)** — literatürdeki hacim cinsiyet
farkının dörtte birine yakın.

**YÖNTEM:** r ∈ {1,5 · 2,0 · 2,5} mm küreyle açma → bileşen etiketleme → en
büyüğü kavite → her voksel en yakın bileşene → ana bileşene atanmayanların
**üç yarıçaptaki birleşimi** çıkarılır. Ayarlanmış parametre yok.

⛔ **BUGÜN BOZUK OLDUĞU ÖLÇÜLDÜ** (`0AW` §3.1). denek10 sağda üç yarıçapın
üçünde de açma **tek bileşen** veriyor (54325 · 52796 · 52111 voksel) →
`if nl_ == 1: continue` → **sıfır voksel** çıkarılıyor. `0R` §1 ise aynı olgu
için **r=2,0 → 0,201 cm³** kaydetmişti.

Maske doğru: kurulan 26,526 cm³ = kayıtlı temiz 26,331 + kayıtlı lob 0,2012
(fark 12 voksel, %0,02). Lob maskenin **içinde**, ayrılmıyor.

**BEŞ VARYANT DENENDİ, HİÇBİRİ TUTTURMADI:** `>`/`<=` · `>=`/`<` · örneklemesiz
voksel birimi · maskeyle sınırlandırılmamış açma · 26-bağlantılı etiketleme.
Sorun açma uygulamasında değil, maskenin boyun bölgesinde.

⚠ **`0AT` §3'ÜN HÜKMÜ DARALTILDI:** sadakat sınavı denek98–101'de Dice 1,000
verdi ama o dört olguda **lob yok** — sınav bu kolu hiç çalıştırmadı.
Bugünkü kodla ölçülecek yeni bir olguda lob varsa **sessizce maskede kalır**.
Kapsamı bilinmiyor (94 olgunun paketi elde yok, 14'ü var).
