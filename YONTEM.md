# NICP — Amberg, Romdhani & Vetter 2007

**Dosya:** `an/nicp.py` · **Kaynak:** yayımlanmış formülasyon, depo değil

**NİÇİN KENDİMİZ YAZDIK:** yazıldığı sırada `T-AbdelAlim/CraniumPy`'nin LICENSE
dosyası **yoktu** (varsayılan: bütün hakları saklı). *(2026-11-09'da Apache-2.0
aldı — bkz. `yontem/craniumpy-nicp-dogrulama`.)*

**NİÇİN CPD DEĞİL:** `pycpd` yoğun M×M Gauss çekirdeği kuruyor; orbita kutusunun
izo-yüzeyi 328.891 tepe veriyor → G matrisi **806 GB**. Belleğe sığdırmak için
2.418 noktaya seyreltmek gerekti ve komşu uzaklığı 0,31 → 2,77 mm'ye çıktı,
yani sütürler nokta bulutundan silindi (`07` §7d). NICP seyrek çalışır.

**BAĞIMLILIK:** yalnız numpy + scipy.sparse (trimesh/open3d yok).
