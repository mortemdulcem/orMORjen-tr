# ALI_CBCT — porion ve ASO landmarkları

**Kaynak:** `github.com/lucanchling/ALI_CBCT`, sürüm `models_v01`
**Tür:** dışarıdan alınan kod + eğitilmiş ağırlıklar (bu çalışmada eğitilmedi)
**Araştırmacı izni:** 2026-11-09 17:04 — *"İzin veriyorum"* (koşturmak için)

**NİÇİN:** Frankfort düzlemini tanımlayan porion hiçbir sahnede elle
işaretlenmemişti. Proje içinde yazılan `PO.bul` dedektörü kohortta insan
kafasında bulunmayan bi-porion değerleri üretiyordu; ölçülerek bırakıldı (`0AD`).

**NEREDE:** `porion/kos.sh` (RPo, LPo) · `porion/kos7.sh` (altı ASO landmarkı)

**DOĞRULAMASI:** ASO altın standardında nokta hatası **0,39–0,61 mm**,
bi-porion hatası **0,69 mm**; aynı tarama üzerinde üç tekrarda **birebir aynı**.
Altı landmarklı koşu, iki landmarklı koşunun porionlarını **0,0000 mm** farkla
üretti.

**UYUMLULUK YAMALARI (3):** `AddChannel` kaldırılmış · `BorderPad` artık
MetaTensor dönüyor · `LoadImages` bellek yığılması. Üçü de sayısal davranışı
değiştirmiyor; bellek yaması `np.pad`'in bit düzeyinde aynı olduğu ölçülerek
gösterildi (`0AU` §3).

**BİLİNEN KUSUR:** **nasion bulunamıyor** — etmen 0,3 mm ölçeğinde hacmin dışına
çıkıyor. Görüş alanı sorunu değil, ölçüldü. Bulunan bir kod hatası
(`new_pos.all() > 0`) sebep DEĞİL; yama denendi, N yine gelmedi, yama geri
alındı (`0AV` §8.5.2–4).
