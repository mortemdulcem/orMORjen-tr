# 0BI — Orbital değişkenlerin bilgi tavanı (SexEst yöntemi, Howells verisi)

SexEst'in kraniyometrik tam modeli 32 değişken ister ve bu 32'nin içinde beş orbital
değişkenimiz vardır; ama eksik-veri modelleri yalnızca GOL, BNL, BBH, XCB, ZYB, BPL,
NLH, NLB, MDH, FOL değişkenlerini kapsar — hiçbiri orbital değildir. Bu yüzden SexEst
bizim ölçümlerimizi olduğu gibi alamaz. Onun model sınıfları (LDA/XGB/LGB) aynı veride
yeniden kuruldu; tek değişen değişken kümesidir.

Doğrulama: 32 değişkenle LDA 0,8700 ± 0,0132 çıktı; deponun kendi kayıtlı değeri 0,8667.

| değişken kümesi | k | LDA | XGB | LGB |
|---|---|---|---|---|
| 32 kraniyometrik | 32 | 0,8700 ± 0,0132 | 0,8709 ± 0,0141 | 0,8685 ± 0,0126 |
| 10 değişken (SexEst eksik-veri) | 10 | 0,8451 ± 0,0130 | 0,8363 ± 0,0133 | 0,8341 ± 0,0102 |
| **5 orbital (bu tez)** | 5 | **0,7233 ± 0,0182** | 0,7040 ± 0,0181 | 0,7038 ± 0,0184 |

**Sonuç:** orbital değişkenlerin tavanı ≈ %72. Kohortta alınan %72–76 yöntemin zaafı
değil, değişken kümesinin bilgi içeriğidir. Tam metin: `claude/0BI-...md`.
