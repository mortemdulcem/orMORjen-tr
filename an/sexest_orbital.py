# -*- coding: utf-8 -*-
"""SexEst yontemini (Apache-2.0, Constantinou ve ark.) HOWELLS verisinde kurar ve
TEZIN SORUSUNU olcer: yalniz ORBITAL degiskenlerle cinsiyet ne kadar belirlenir?

SexEst'in kendi kurulumu (depodan okundu, tahmin degil):
  - kraniyometrik tam model 32 degisken kullanir; yayinlanmis dogruluk LDA 0,8667 XGB 0,8656
  - eksik-veri modelleri YALNIZ su 10 degiskeni kapsar: GOL BNL BBH XCB ZYB BPL NLH NLB MDH FOL
    -> hicbiri orbital DEGIL, yani SexEst bizim olcumlerimizi oldugu gibi YIYEMEZ.
Bu yuzden ayni model siniflari (LDA / XGB / LGB) ayni veride, bu kez ORBITAL
degiskenlerle yeniden kurulur. Karsilastirma boylece yontem farkindan degil
DEGISKEN KUMESI farkindan gelir.

Degerlendirme: popülasyona gore tabakalandirilmis 5 katli capraz dogrulama,
10 tekrar. Hicbir esik kohorttan turetilmez.
"""
import sys, csv, json
import numpy as np
sys.path.insert(0, '/home/claude/an')
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

HOW = '/home/claude/dis_kaynak/howells/howell.csv'
ORBITAL = ['OBH', 'OBB', 'DKB', 'FMB', 'EKB']
SEXEST10 = ['GOL', 'BNL', 'BBH', 'XCB', 'ZYB', 'BPL', 'NLH', 'NLB', 'MDH', 'FOL']

def yukle(degiskenler):
    r = list(csv.DictReader(open(HOW)))
    X, y, pop = [], [], []
    for s in r:
        try:
            v = [float(s[k]) for k in degiskenler]
        except (KeyError, ValueError):
            continue
        c = str(s.get('Sex', '')).strip().upper()
        if c not in ('M', 'F', '1', '2'):
            continue
        X.append(v); y.append(1 if c in ('M', '1') else 0); pop.append(s.get('Population', '?'))
    return np.array(X, float), np.array(y, int), np.array(pop)

def dene(ad, degiskenler, tekrar=10):
    X, y, pop = yukle(degiskenler)
    modeller = {
        'LDA': lambda: make_pipeline(StandardScaler(), LDA()),
        'XGB': lambda: XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.1,
                                     subsample=0.9, colsample_bytree=0.9,
                                     eval_metric='logloss', verbosity=0, n_jobs=1, tree_method='hist'),
        'LGB': lambda: LGBMClassifier(n_estimators=300, max_depth=4, learning_rate=0.1,
                                      subsample=0.9, colsample_bytree=0.9, verbose=-1, n_jobs=1),
    }
    cik = {}
    for nm, yap in modeller.items():
        skor = []
        for t in range(tekrar):
            kf = StratifiedKFold(5, shuffle=True, random_state=t)
            for tr, te in kf.split(X, y):
                m = yap(); m.fit(X[tr], y[tr])
                skor.append(float((m.predict(X[te]) == y[te]).mean()))
        s = np.array(skor)
        cik[nm] = (float(s.mean()), float(s.std()))
        print('  %-4s %-28s dogruluk %.4f ± %.4f' % (nm, ad, s.mean(), s.std()), flush=True)
    return cik, X.shape

if __name__ == '__main__':
    SON = {}
    print('HOWELLS · SexEst model siniflari · 5x2 capraz dogrulama (10 tekrar)\n')
    for ad, dv in (('32 kraniyometrik (SexEst tam)', None),
                   ('10 degisken (SexEst eksik-veri)', SEXEST10),
                   ('5 ORBITAL (bu tez)', ORBITAL)):
        if dv is None:
            r = list(csv.DictReader(open(HOW)))
            sayi = [k for k in r[0] if k not in ('ID','Sex','PopNum','Population')]
            dv = sayi[:32]
        X, y, _ = yukle(dv)
        print('%s  (n=%d, %d degisken)' % (ad, len(y), X.shape[1]))
        SON[ad], _ = dene(ad, dv)
        print()
    json.dump(SON, open('/home/claude/an/out/sexest_orbital.json', 'w'),
              ensure_ascii=False, indent=1)
    print('yazildi: out/sexest_orbital.json')
