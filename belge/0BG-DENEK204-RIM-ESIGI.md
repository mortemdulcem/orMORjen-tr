# 0BG — denek204: rim eşiği ölçüldü, değiştirilmedi

Tarih: 2026-11-11 · Durum: **olgu ölçülemez olarak kayıtlı; eşik değiştirilmedi**

## 1. İstek ve neden yerine getirilmediği

"Sadece denek204 için rim eşiğini değiştir" — bu, sonucu gördükten sonra tek olgu için eşik
seçmek olur (`§0.12`) ve donmuş hattı bozar (`0K` §1). Kuralı öne sürmekle yetinmedim,
eşiğin ne yaptığını ölçtüm.

## 2. Ölçüm

`rimcurve.auto_rim` tek bir yerde `None` döner: 72 ışından yarısından azı rim bulursa
(`ok.sum() < n_ang * 0.5`). Söz konusu "eşik" budur.

| olgu | sağ | sol | eğri |
|---|---|---|---|
| **denek204** | **0,472** | **0,500** | sağ YOK |
| denek212 | 1,000 | 1,000 | var |
| denek206 | 1,000 | 1,000 | var |

Normal **1,000**'dir. Eşiği 0,47'ye indirmek, çevrenin yarısından çoğu `np.interp` ile eksik
veriden üretilmiş bir eğriyi kabul etmek olurdu; o eğri sonra alan, çevre, hacim ve altıgen
katsayılarını besler.

## 3. İki varsayımım sınandı, ikisi de çürütüldü

**(a) `cross(n,[0,0,1])` yozlaşması** (`0BE`'deki hatanın aynı sınıfı): n–z açısı denek204'te
79,0°/80,9°, başarılı olgularda 74–85°; `|cross(n,z)|`=0,98. **Yozlaşma yok.**

**(b) Tarama alanı kesilmesi:** rim ışınlarının hacim dışına taşma oranı **0,000**.
(İlk denemede %89 çıktı — benim hatamdı, sınır denetiminde `ct.shape`'i tersine çevirmiştim;
`rimcurve.hu` ijk'yi doğrudan `ct` eksen sırasıyla indeksliyor.)

## 4. Gerçek neden

Bir ışın, kemiğin en öndeki iki ardışık voksellik koşusu `s_min_front = -4.0` mm'den geride
kalırsa düşer. denek204'te çevrenin yarısından çoğunda rimin ön yüzü landmark düzleminin
4 mm'den fazla gerisindedir. Landmarklar tutarlıdır (MSP 0,27 mm); landmark düzlemi ile
gerçek rim düzlemi bu olguda uyuşmuyor.

## 5. Karar

Eşik değiştirilmedi. denek204 `0K` §4.4 uyarınca dışlanmadı, yerine başka olgu konmadı;
"ölçülemedi" olarak kayıtlıdır ve tezde öyle bildirilecektir. Genel bir düzeltme ancak ayrı
ön kayıt ve `0BE`'dekine benzer nötrlük sınavıyla yapılabilir.

Tanı betikleri: `an/tani204.py`, `an/tani204b.py`.
