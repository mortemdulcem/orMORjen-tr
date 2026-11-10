# orMORjen-tr

Türk popülasyonunda 3B BT ile orbital morfometriden cinsiyet tayini tezinin
ölçüm hattı. Bu depo **kodu ve yöntem verisini** tutar.

> ⚠ **Hasta verisi bu depoya ASLA girmez** (tez kural kitabı §0.2).
> BT hacimleri, DICOM, segmentasyon maskeleri, denetim paketleri ve sahneler
> `.gitignore` ile dışarıda tutulur.

## Yapı

| yol | içerik |
|---|---|
| `an/` | ölçüm hattı modülleri |
| `an/out/rimatlas.json` | rim atlası — 10 orbita / 5 olgu |
| `an/out/apeks_atlas.json` | apeks atlası — 18 orbita / 9 olgu |
| `kurtarma/` | sadakat sınavı betikleri |
| `belge/0AT.md` | 2026-11-10 konteyner kaybı ve hattın yeniden kurulması |

## Doğrulanmış durum (2026-11-10)

| parça | sınav | sonuç |
|---|---|---|
| `rayseg.py` (maske + hacim) | hacim farkı < %1 **ve** Dice > 0,95, ölçülmüş paketlere karşı | **10/10 orbita, Dice 1,000** |
| `params.py` | sahne değerleri ana veri setiyle birebir | 5 olguda geçti |
| apeks atlası | kayıtlı istatistik `t` ort 42,799 · SS 1,812 · [39,34–46,13] | **birebir** |
| rim atlası | 10 orbita / 5 olgu | kuruldu |

## Yeniden kurulmayı bekleyen

`landmark.py`'nin dört adımı (eğri yinelemesi · apeks atlası adımı ·
`mso` anatomik çerçevesi · kemik kapısı) ve `kemik_kapisi.py`.
Tarifleri proje belgelerinde yazılı, kodları kayıp.

## Neden bu depo var

2026-11-10'da çalışma alanı sıfırlandı ve beş modül kayboldu. Kayıtlar duruyordu
ama **kod hiçbir kalıcı yerde değildi**. Bu depo o hatayı kapatır: her kod
değişikliği aynı turda buraya push edilir.
