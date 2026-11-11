# 0BE — Orbita bulma yön ölçütü: tarayıcı ekseninden anatomik eksene

Tarih: 2026-11-10/11 · Durum: **ön kayıt yapıldı, nötrlük sınavı geçti, uygulandı**

## 1. Sorun

denek211'de hiçbir orbita bulunamadı. Neden tahmin edilmedi, kodda bulundu: `an/bul.py`
aday yüzeyin dışa bakıp bakmadığını **tarayıcı eksenine** göre sınıyordu.

```python
if nrm[1] <= 0.45:        # A bileseni; one bakmayanlari at
    continue
```

Hastanın başı yatık olduğunda yüzün normali artık `+A` ekseninde değildir, dolayısıyla
gerçek orbita yüzeyi de atılır. Yani kapı anatomiyi değil hasta pozisyonunu ölçüyordu.

## 2. Ön kayıt (sonuçlara bakılmadan yazıldı)

Yeni ölçüt: normal, kafa kütle merkezinden adaya doğru olan yöne bakmalı — eşik **aynı 0,45**
kalır, yalnızca karşılaştırılan eksen değişir.

```python
_d = np.asarray(p, float) - _KAFA_MERKEZI
_nd = np.linalg.norm(_d)
if _nd < 1e-9 or float(np.dot(nrm, _d / _nd)) < 0.45:   # DISA bakiyor mu
    continue
```

### 2.1 Nötrlük ölçütü — kendi kuralımı sınav öncesi SERTLEŞTİRDİM

İlk yazdığım ölçüt "yeni kapı en az eski kadar orbita bulsun" idi. Bunun zayıf olduğunu
gördüm: dışa bakan her yüzey ölçütü geçer, kulak kanalı ve nazal boşluk dahil. Bu yüzden
ölçütü sonucu görmeden şuna çevirdim: **seçilen orbitaların kendisi birebir aynı kalmalı** —
sayıları değil, konumları.

## 3. Sonuç

Eski ve yeni `orbita_bul`, dört olguda tam karşılaştırıldı:

| olgu | alan sayısı | ortak | en büyük fark |
|---|---|---|---|
| denek201 | 4/4 | 4 | 0,0000 mm |
| denek203 | 4/4 | 4 | 0,0000 mm |
| denek206 | 4/4 | 4 | 0,0000 mm |
| denek212 | 4/4 | 4 | 0,0000 mm |

**HÜKÜM: GEÇTİ** — seçilen orbitalar aynı. Bu yüzden 111 satırın hiçbiri yeniden ölçülmedi
(`0K` §1 korundu). Yedek: `an/bul.py.oncesi`.

## 4. denek211 bu değişiklikten sonra: ölçüldü ama REDDEDİLDİ

```
[4/8 LANDMARK] 14 nokta · MSP ort 3,12 maks 9,36 mm · mso-o 22,07 / 34,45 mm
[4b MEDIAL]  oynama {'d-r': 33,56, 'd-l': 36,61, 'mf-r': 29,56, 'mf-l': 34,62} mm
[8/8 DENETIM] RED 3 · UYARI 0 · havuz: False
   RED hacim_bandi     sag 35,897   (band 19,9–33,4)
   RED hacim_bandi     sol 42,728
   RED orbital_indeks  sol 150,3
```

Normal olgularda medial oynama 1–8 mm'dir; burada 29–37 mm. Yani orbitanın **bulunması**
düzeldi, ama nokta **yerleştirme çerçevesi** hâlâ tarayıcı eksenlerinde: `landmark._duzlem_cerceve`
`up=[0,0,1]` (dünya +z) kullanıyor. Yatık başta bu çerçeve yanlış döner.

Sonuç: `0K` §4.4 uyarınca olgu dışlanmadı ve yerine başkası konmadı; tabloya `havuz False`
olarak yazıldı (112. satır).

## 5. Açık karar — çerçeve değişikliği

Yatık başları düzeltmek için yerleştirme çerçevesi de değişmek zorunda. İki seçenek var ve
**ikisi de 112 olgunun tamamının yeniden ölçümünü gerektirir** (`0K` §1), yaklaşık 14 saat:

1. **Literal Frankfort** (iki porion + sol orbitale): kohortta kapsama yalnızca **9/14 = %64,3**.
   Kalan ~%36 olgu ölçülemez hale gelir.
2. **Anatomik MSP çerçevesi** (`_duzlem_cerceve_anatomik`, `d`/`mf` çiftlerinden MSP normali):
   kapsama %100, ama `0F` §21 / `0F2` §36 uyarınca şu an yalnızca `mso` için kullanılıyor;
   bütün noktalara yayılması ayrı bir ön kayıt ister.

Ölçülen çerçeve sapması: ortalama 3,50°, ortanca 2,51°, maksimum 11,72°; r=20 mm'de nokta
kayması **4,09 mm**'ye kadar. Yani sorun denek211'e özgü değil, derece derece bütün kohortta var.
