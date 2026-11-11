# -*- coding: utf-8 -*-
"""Kohort etiketleriyle cinsiyet tayini — SIZINTISIZ kurulum.

Arastirmacinin onerdigi iskelet korundu (StratifiedKFold, LDA + Random Forest,
karisiklik matrisi), uc sizinti kapatildi:

  1. SENTETIK VERI YOK. Etiket dosyasi verilmezse betik CALISMAZ; uydurma dagilimdan
     uretilen veri %95+ dogruluk verir ve bu bir sonuc degildir.
  2. RAPOR EGITIM VERISINDE DEGIL. classification_report ve confusion_matrix
     `cross_val_predict` ciktisindan kurulur; model kendi gordugu satiri puanlamaz.
  3. OLCEKLEYICI PIPELINE ICINDE. StandardScaler her katta YENIDEN uydurulur; capraz
     dogrulamadan once butun veriyi gormez.

Oznitelik kumeleri ONCEDEN belirlenir ve HEPSININ sonucu bildirilir — en iyisi secilip
o rapor edilmez (`§0.12`).

Kullanim:
  python3 -I cinsiyet_kohort.py etiket.csv      # etiket.csv: denek,cinsiyet  (E/K)
"""
import sys, csv, json
import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (classification_report, confusion_matrix,
                             roc_auc_score, accuracy_score)

KOH = '/home/claude/ormorjen-tr/kohort/kohort_98.csv'

# --- oznitelik kumeleri: KOSUDAN ONCE sabit, hepsi bildirilecek ---
TEMEL   = ['OW_sag','OW_sol','OH_sag','OH_sol','OI_sag','OI_sol']
HACIM   = TEMEL + ['hacim_sag','hacim_sol']
APERTUR = HACIM + ['APalan6_sag','APalan6_sol','APcevre6_sag','APcevre6_sol']
GENIS   = APERTUR + ['IOD_d','IOD_mf','BOW_ek','BOW_fmo','centroid',
                     'kal_sup_sag','kal_sup_sol','kal_inf_sag','kal_inf_sol',
                     'kal_med_sag','kal_med_sol','kal_lat_sag','kal_lat_sol']
KUMELER = [('temel (OW/OH/OI)', TEMEL), ('+ hacim', HACIM),
           ('+ apertur', APERTUR), ('+ IOD/BOW/kalinlik', GENIS)]

def asimetri_ekle(satir, ad_listesi):
    """Sag-sol ciftlerinden ASIMETRI oznitelikleri turetir (`|R-L|`)."""
    ek = {}
    for a in ad_listesi:
        if a.endswith('_sag'):
            b = a[:-4] + '_sol'
            if b in satir and satir[a] not in ('', None) and satir[b] not in ('', None):
                ek['asim_' + a[:-4]] = abs(float(satir[a]) - float(satir[b]))
    return ek

def yukle(etiket_yolu, asimetri=False, kume=GENIS, disla=()):
    et = {}
    for r in csv.DictReader(open(etiket_yolu, encoding='utf-8-sig')):
        d = (r.get('denek') or r.get('Denek') or '').strip()
        c = (r.get('cinsiyet') or r.get('Cinsiyet') or r.get('sex') or '').strip().upper()
        if d and c in ('E', 'K', 'M', 'F'):
            et[d] = 1 if c in ('E', 'M') else 0
    X, y, adlar, kullanilan = [], [], [], []
    for s in csv.DictReader(open(KOH)):
        d = s['denek']
        if d not in et or d in disla:
            continue
        if s.get('havuz') != 'True':          # kalite kapisindan gecmeyen olgu modele girmez
            continue
        try:
            v = [float(s[k]) for k in kume]
        except (KeyError, ValueError):
            continue
        if asimetri:
            ek = asimetri_ekle(s, kume)
            v = v + [ek[k] for k in sorted(ek)]
            if not adlar:
                adlar = list(kume) + sorted(ek)
        elif not adlar:
            adlar = list(kume)
        X.append(v); y.append(et[d]); kullanilan.append(d)
    return np.array(X, float), np.array(y, int), adlar, kullanilan

def degerlendir(X, y, ad):
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    modeller = {
        'LDA': make_pipeline(StandardScaler(), LDA()),
        'Lojistik': make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
        'RF': make_pipeline(StandardScaler(),
                            RandomForestClassifier(n_estimators=300, max_depth=5,
                                                   random_state=0, n_jobs=1)),
    }
    cik = {}
    for nm, m in modeller.items():
        # KAT DISI tahmin: her satir, kendisini gormemis bir modelden puan alir
        p  = cross_val_predict(m, X, y, cv=cv, method='predict')
        pr = cross_val_predict(m, X, y, cv=cv, method='predict_proba')[:, 1]
        dg = accuracy_score(y, p)
        # %95 guven araligi (Wilson)
        n = len(y); z = 1.96
        mrk = z * np.sqrt(dg * (1 - dg) / n)
        km = confusion_matrix(y, p)
        cik[nm] = dict(dogruluk=float(dg), alt=float(dg-mrk), ust=float(dg+mrk),
                       auc=float(roc_auc_score(y, pr)), karisiklik=km.tolist())
        print('  %-9s %-22s dogruluk %.3f  [%.3f, %.3f]  AUC %.3f'
              % (nm, ad, dg, dg-mrk, dg+mrk, cik[nm]['auc']), flush=True)
        print('            karisiklik [[KK %d, KE %d], [EK %d, EE %d]]'
              % (km[0,0], km[0,1], km[1,0], km[1,1]), flush=True)
    return cik

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit('KULLANIM: python3 -I cinsiyet_kohort.py etiket.csv\n'
                         'Sentetik veri URETILMEZ — etiket dosyasi zorunludur.')
    DISLA = ('denek250',)   # cinsiyeti ekran goruntusunde gorulduğu icin kor sinavdan cikarildi
    SON = {}
    for ad, kume in KUMELER:
        for asim in (False, True):
            X, y, adlar, kull = yukle(sys.argv[1], asimetri=asim, kume=kume, disla=DISLA)
            if len(y) < 20:
                print('%s%s: yeterli etiketli olgu yok (%d)' % (ad, ' + asimetri' if asim else '', len(y)))
                continue
            etiket = ad + (' + asimetri' if asim else '')
            print('\n%s  (n=%d · E %d / K %d · %d oznitelik)'
                  % (etiket, len(y), int(y.sum()), int(len(y)-y.sum()), X.shape[1]), flush=True)
            SON[etiket] = degerlendir(X, y, etiket)
    json.dump(SON, open('/home/claude/an/out/cinsiyet_kohort.json', 'w'),
              ensure_ascii=False, indent=1)
    print('\nyazildi: out/cinsiyet_kohort.json')
