# 3D Slicer — kaynak ve arayüz envanteri

**Kaynak:** `github.com/Slicer/Slicer` (sparse-shallow klon)
**Belge:** `claude/slicer-uygulama-envanteri.md`

**NİÇİN:** Araştırmacının öğrettiği ayarların (CT_BONE, W:1000 L:400,
Threshold 226–3071, CT-AAA + Shift 25) kaynak koddaki tam karşılığını bulmak.
Her biri kaynakta bulundu **ve Slicer'ın içinde koşturulup geri okundu** —
10/10 ayar tuttu.

**ÇIKARILAN:** 62 modül · 122 panel · 996 etkileşimli öğe · 575 C++ logic
işlevi · 793 Python metodu.

**EN ÖNEMLİ İKİ BULGU:**
1. **`CT_BONE` ile `W:1000 L:400` aynı şeydir** — iki talimat birbirini
   doğruluyor, çelişmiyor.
2. **Bir landmark tıklamasının tam tanımı** bulundu: `vtkVolumePicker`
   ışın boyunca skaler opaklığın **0,05**'e ulaştığı ilk noktayı döndürür;
   CT-AAA + Shift 25 ile bu ≈ **170 HU**. Teze yazılabilir bir landmark tanımı.

**FRANKFORT:** Slicer çekirdeğinde **yok** — arandı, sıfır sonuç. Eklentide
(bkz. `yontem/aso-frankfort-kapisi`).
