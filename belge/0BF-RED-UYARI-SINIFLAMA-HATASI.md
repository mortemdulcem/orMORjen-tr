# 0BF — Kohort tablosunda RED/UYARI sınıflama hatası, denetim ve düzeltme

Tarih: 2026-11-11 · Durum: **düzeltildi, doğrulandı**

## 1. Belirti

denek211 koşu kütüğü `RED 3 · UYARI 0` dedi; kohort satırı `RED 0 UYARI 3` yazıyordu.

## 2. Kök neden

`orbita_hat/olcum_zinciri.denetle` bütün kapı sonuçlarını tek listeye (`uyari`) yazar;
kırmızı/uyarı ayrımı her kaydın `sonuc` alanındadır. Kaydedilen JSON'da **ayrı bir `red`
anahtarı yoktur.** Tablo yazıcıları o olmayan anahtarı okuyordu:

```python
red, uya = den.get('red', []), den.get('uyari', [])   # 'red' her zaman bos
```

Sonuç: her kırmızı kapı UYARI sayıldı, `RED` kolonu daima 0. Hata iki dosyadaydı:
`kohort/tablo_kur.py` ve `an/satir_yeni.py`.

## 3. 112 satırın tamamı denetlendi

| | satırlar | yazıcı | durum |
|---|---|---|---|
| 1. nesil | 1–94 | kapı adını `kapi(taraf)` yazan eski kod | **hatasız** |
| 2. nesil | 95–112 | `tablo_kur.satir` / `satir_yeni.satir` | 2 satır hatalı |

Birinci nesil tutarlıdır: `kemik_kapisi == 'False'` olan 18 satırın 18'inde `havuz False`
(o neslin havuz kuralı kemik kapısını içeriyor), ve `kemik_kapisi True` + RED≥1 olan 5 satır
(denek24, 29, 36, 42, 81) doğru sayılmıştır.

### 3.1 Havuz kirlenmemiştir

`havuz` bayrağı tablo yazıcısından gelmez; `denetle()` içinde
`not any(u["sonuc"] == "RED" ...)` ile hesaplanır ve `sonuc` alanını doğru okur. 112 satırın
tamamında rapor ↔ tablo `havuz` sapması **0**'dır. Dolayısıyla **`0K` §4.4 ihlali yoktur**:
hiçbir reddedilmiş olgu havuza girmemiştir.

## 4. Düzeltme

İki dosyada aynı yama, eski biçimle geriye dönük uyumlu:

```python
den = R.get('denetim', {})
if 'red' in den:
    red, uya = den['red'], den['uyari']
else:
    hepsi = den.get('uyari', [])
    red = [g for g in hepsi if g.get('sonuc') == 'RED']
    uya = [g for g in hepsi if g.get('sonuc') != 'RED']
```

Ayrıca her iki yazıcıya çapraz denetim eklendi — uyuşmazsa satır **yazılmaz**:

```python
if (len(red) > 0) == bool(den.get('hacim_veri_setine_yazilabilir')):
    raise AssertionError('%s: RED=%d ile havuz=%s celisiyor — satir yazilmadi' % ...)
```

Yedekler: `kohort/tablo_kur.py.oncesi`, `an/satir_yeni.py.oncesi`.

Sonra yalnızca iki satırın dört alanı yeniden yazıldı; **hiçbir olgu yeniden ölçülmedi**,
`0K` §1 dokunulmadı:

| olgu | önce | sonra |
|---|---|---|
| denek208 | RED 0 / UYARI 2 | RED 2 / UYARI 0 · `hacim_bandi` |
| denek211 | RED 0 / UYARI 3 | RED 3 / UYARI 0 · `hacim_bandi;orbital_indeks` |

Kanıt: iki tablo bu dört alan dışarıda bırakılarak satır satır karşılaştırıldı → diğer bütün
alanlar birebir aynı.

## 5. Düzeltme sonrası

112 satır · `havuz True` 87 · `havuz False` 25 · RED>0: denek24, 29, 36, 42, 49, 74, 81, 208,
211 · açıklanamayan tutarsızlık **0**.

## 6. Ders

Koşu kütüğü ile tabloya yazılanı hiç karşılaştırmamıştım; `den.get('red', [])` sessizce boş
liste döndürüyordu. §4'teki çapraz denetim bunu artık sessiz bırakmıyor.
