# 0BH — ÖN KAYIT: yerleştirme çerçevesinin anatomik MSP'ye geçirilmesi

Tarih: 2026-11-11 · **Koşudan ÖNCE yazıldı; hiçbir sonuca bakılmadı.**
Tam metin proje belgelerinde: `claude/0BH-ON-KAYIT-ANATOMIK-MSP-CERCEVESI-TUM-NOKTALAR.md`

## Özet

`landmark._duzlem_cerceve` düzlem içi "yukarı" eksenini dünya +z'den alıyor; baş yatıksa
bütün noktalar yanlış açıya konuyor (`0BE` §4, denek211'de medial oynama 29–37 mm).
Çerçeve sapması kohortta ort 3,50° / maks 11,72°, r=20 mm'de 4,09 mm'ye kadar kayma.

Literal Frankfort kapsamı %64,3 olduğu için (`0AR`) anatomik MSP çerçevesi seçildi
(tez sahibinin kararı, 2026-11-11). Kapsama %100.

## Yapılanlar (koşudan önce)

- `an/rimatlas_anatomik.py`: rim atlası anatomik çerçevede yeniden türetildi.
  Doğrulama 1: `mso` −2,0° (SS 9,9) ≡ bağımsız `mso_anatomik.json` (−2,043 / 9,869).
  Doğrulama 2: açı kayması altı noktada da −1,6° (katı dönme imzası).
  Dürüst gözlem: atlas olgularında ortalama açısal saçılım düzelmiyor (7,70 → 7,83);
  yalnız `mso` düzeliyor. Bu ölçüt listesine EKLENMEDİ.
- `an/apeksatlas_anatomik.py`: apeks atlası ölçüldü, **dokunulmamasına karar verildi**.
  Çerçeve etkisi dik +0,014 / yan −0,080 mm; bileşim etkisi (18→10 giriş, hasta13–16
  sahneleri hiçbir yerde yok) t −0,292 / dik +0,607 / yan −0,352 mm. Yani yeniden türetmek
  kazandırmadan kaybettirir. Geride kalan ≤0,08 mm tutarsızlık tezde bildirilecek.
- `ORBITA_CERCEVE` ortam değişkeni: varsayılan `dunya_z` (donmuş hat birebir korunur),
  `anatomik` seçilirse atlas açıları da anatomik dosyadan okunur. Atlas ile çerçeve
  AYRILAMAZ; ayrılırsa her nokta çerçeve dönmesi kadar kayar.

## Kabul ölçütleri (sonuçlara bakılmadan sabitlendi)

- **Ö1** kapsama kaybı yok · **Ö2** ort(MSP_yeni) ≤ ort(MSP_eski) · **Ö3** denek211'de dört
  medial oynamanın dördü de < 10 mm · **Ö4** sapma < 1° olan olgularda yer değiştirme
  < 0,50 mm · **Ö5** yakınsama kötüleşmez.
- Hepsi geçerse 123 olgu yeniden ölçülür (`0K` §1); biri düşerse mevcut hat korunur ve
  ön kayıt yanlışlanmış olarak kapanır. Ölçüt sonradan gevşetilmeyecek/eklenmeyecek.

Sınav betiği: `an/cerceve_sinav.py`.
