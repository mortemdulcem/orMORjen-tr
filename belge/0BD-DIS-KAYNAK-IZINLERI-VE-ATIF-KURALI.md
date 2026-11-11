# 0BD — DIŞ KAYNAK İZİNLERİ VE TEZDE ATIF KURALI

**Tarih:** 2026-11-11 · **Kaynak:** araştırmacının 11:41 ve 11:42'deki bildirimleri

---

## 1. Araştırmacının verdiği izinler (kayıt)

| kaynak | lisans durumu | izin | tarih |
|---|---|---|---|
| `lucanchling/ALI_CBCT` | depo lisansı | *"İzin veriyorum"* | 2026-11-09 17:04 |
| `T-AbdelAlim/CraniumPy` | **Apache-2.0** (bağımsız doğrulandı) | araştırmacı izin aldığını bildirdi | 2026-11-09 |
| `SlicerMorph/SlicerMorph` (ALPACA) | **BSD 2-Clause** | lisans serbest, izne gerek yok | — |
| `cconsta1/SexEst` | **Apache-2.0** | lisans serbest, izne gerek yok | — |
| **`gennadyagre/cranial_sex_estimation`** (Toneva ve ark.) | **LİSANS DOSYASI YOK** | **araştırmacı izin aldığını bildirdi** | **2026-11-11 11:41** |
| **`pr0m1th3as/cranial-sex-estimation-code`** (Bertsatos) | LICENSE var | **araştırmacı izin aldığını bildirdi** | **2026-11-11 11:42** |

⚠ Toneva deposunun lisansı **yoktur**; varsayılan "tüm hakları saklıdır"dır.
Kullanım yalnız araştırmacının aldığını bildirdiği izne dayanır. **İznin
yazılı metni arşivlenmelidir** (IMAIOS ve Skeleton·ID taleplerinde olduğu gibi,
`tez/05`, `tez/08`). Yazılı belge olmadan tezin ek bölümüne konulamaz.

## 2. TEZDE ATIF KURALI — araştırmacının koyduğu kural

> *"Tezin hiçbir yerine GitHub repolarını yazmayacaksın, bu en büyük kural."*

**Uygulanacak biçim:**

- Tez metninde **hiçbir GitHub bağlantısı yer almaz.**
- Yöntemler **yayımlanmış makaleleriyle** anılır:
  - NICP → Amberg, Romdhani & Vetter 2007
  - ALPACA / geometrik medyan → SlicerMorph (Rolfe ve ark.) yayını
  - Cinsiyet tayini karşılaştırması → Constantinou ve ark., DOI 10.1002/oa.3109
  - BT tabanlı kraniyal cinsiyet tayini → Toneva ve ark.
  - 3B morfometrik özelliklerden cinsiyet tayini → Bertsatos
  - Dış referans veri → Howells kraniyometrik veri seti
- Yazılım adı ve sürümü yazılabilir (ör. *"CraniumPy"*), **adres yazılmaz.**

**Bu kural `00` §0.1 ile çelişmez ve onu ihlal etmez:** §0.1 kaynaksız bilgi
cümlesi yasaklar; burada kaynak **makaleye** verilir, depoya değil. Akademik
atıf zaten yazılımın kendisine değil yayınına yapılır.

**Lisans yükümlülükleri nerede karşılanır:** Apache-2.0 ve BSD-2 telif
bildiriminin **yazılımın dağıtımında** korunmasını ister. Tez bir yazılım
dağıtımı değildir; bildirimler `orMORjen-tr` kod deposundaki dosya
başlıklarında ve `YONTEM-KATALOGU.md`'de tutulmaktadır. Bu yüzden tez
metninden adreslerin çıkarılması **hiçbir lisansı ihlal etmez.**

## 3. Toneva ve ark. — ne için kullanılacak

BT tabanlı, Bulgar popülasyonu, SVM + lojistik regresyon. Ölçüm seti
`Attribute Description.pdf`'te tanımlı: doğrusal ölçüler, açılar ve **üçgen
alanları**; orbital yükseklik (`sk-zo`, suprakonchion–zygoorbitale) dahil,
`fmo` (frontomalare orbitale) nazomalar açıda kullanılıyor.

Türkiye'ye coğrafi olarak Howells'in 30 popülasyonundan daha yakın ve
**görüntüleme yöntemi bizimkiyle aynı (BT)** — bu yüzden `0BB`'nin kuru
kafatası kaynaklı kaymasını değerlendirmek için en uygun karşılaştırmadır.

## 4. SexEst bulgusu — tezin Tartışma omurgası

SexEst'in Howells kraniyal modeli 11 değişken kullanır:
`BBH · BNL · BPL · FOL · GOL · MDH · NLB · NLH · XCB · ZYB`.
**Hiçbiri orbital değildir.**

Bu, `0BB`'nin %72–76'sını açıklar ve tezin boşluğunu tanımlar: klasik
kraniyometri orbitayı kumpas ölçüleriyle değerlendirip zayıf bulmuş ve
dışarıda bırakmıştır. Bu çalışmanın ölçtüğü **hacim, apertür alanı ve çevresi,
duvar kalınlığı ve düzlemsizlik** Howells'de yoktur; dolayısıyla "orbita
cinsiyet ayırmaz" hükmü 3B BT değişkenleriyle **hiç sınanmamıştır.**
