# ASO — Frankfort yöntemi ve landmark kapısı

**Kaynak:** `github.com/DCBIA-OrthoLab/SlicerAutomatedDentalTools`
(ALI ile **aynı laboratuvar**)
**Tür:** okundu ve çağrıldı; ASO modülü koşturulmadı

**NİÇİN:** Araştırmacı sordu: *"3D slicer uygulamasının frankfort kodları onları
niye çekmiyorsun"*. Slicer çekirdeğinde Frankfort kodu **yok** (arandı); eklentide.

**ÖNEMLİ BULGU — ASO düzlemi analitik KURMUYOR.** Hastayı Frankfort'a zaten
oturtulmuş altın referans taramaya **7 landmarkla katı cisim ICP'siyle
kaydediyor** (`ASO/ASO_Method/CBCT.py:249` → `Ba, S, N, RPo, LPo, ROr, LOr`;
`ASO_CBCT_utils/utils.py:527` → `vtkIterativeClosestPointTransform`,
`SetModeToRigidBody`). Bu, `0AU` §7c'nin düzlem içi dönme sorununu çözüyor:
yedi landmark altı serbestlik derecesini de belirler.

**NEREDE:** `an/aso_kapi.py` — `utils.py` satır 123–163 ve 250–365'ten **birebir**
alındı, hiçbir satır değiştirilmedi.

**KAPI ÖLÇÜTLERİ:** uzaklık 15 mm · yön 0,4 rad (≈22,9°) · atma eşiği
`toplam > landmark sayısı`.

**SONUÇ:** 14 olgunun **11'inde** bizim altı ölçütümüzle aynı hüküm. Kaba
kusurlarda porionu **adıyla** gösteriyor (denek10: LPo, RPo).

⚠ **YERİNE GEÇEMEZ** (`0AV` §9.4): (a) 15 mm toleransı **tek bir kafatasına**
karşı mutlak uzaklık ölçüyor — iyi olgularımızda `LOr–ROr` farkı 16–20 mm, bu
anatomik değişkenlik; (b) atma eşiği landmark sayısına göreli, nasion düştüğü
için kendi tasarımından katı. denek78'de doğru noktayı (RPo) en tepeye koyuyor
ama eşiği **bir puanla** kaçırıyor.
