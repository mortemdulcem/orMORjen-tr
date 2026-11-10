# Apeks — 7 şablonlu NICP (`0M` KOL B)

**Dosya:** `an/apeks_nicp.py` · **Tanım:** `0M` §3 KOL B

*"`d` ve `mf` için **zaten çalışan** makine apekse çevrilir — `an/medial.py`.
Tek fark hedef ve hizalama kümeleri: HEDEF = `apex-r`, `apex-l`;
HİZALAMA = kalan 12 nokta — **apeks yok**."*

Apeksin hizalamadan çıkarılması **şart**: hedefi hizalamada kullanmak cevabı
cevapla bulmaktır.

**UYGULAMA:** `medial.py` **bozulmadı** — hedef/hizalama kümeleri seçimlik
parametre yapıldı; varsayılan çağrılar (`d`/`mf` yolu) aynen eski davranışı
verir.

**NİÇİN GEREKLİ:** kohortun apeksi **atlas formülüyle** konuyor ve derinlik
bileşeni özdeş sabit (`c − n·t + u·dik + v·yan`, u·n = v·n = 0 → derinlik ≡ t).
Dört yeni parametre (`mf`, `ek`, `mso`, `o` → apeks, 3B Öklid) bu apeksle
**hesaplanamaz** (`0M` §10.3).

**TUTTURULMASI GEREKEN (`0M` §5.1):** apeks 3B hatası ort **2,69 mm** ·
derinlik MAE **1,65 mm** · sağ/sol farklı **7/7**.

**ŞABLONLAR:** hasta5–hasta11, yedisi de kuruldu. hasta6'nın `o-r`'si hiçbir
pakette yok; `atlas-hasta7-8-9.md` §AM'in kaydettiği ölçüm2 değerinden
(16,669 / 84,908 / −147,649 RAS) geri konuldu — veri setinin kendisi de aynı
değeri kullanmış.
