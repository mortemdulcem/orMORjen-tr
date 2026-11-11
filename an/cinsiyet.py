# -*- coding: utf-8 -*-
"""CINSIYET SINIFLANDIRICISI — `0BB` on kaydi.

Egitim: Howells (cinsiyeti BELGELI, 2524 kafatasi, 30 populasyon)
Tahmin: bizim kohort (etiketleri GORULMEZ)
Standartlastirma: POPULASYON ICI z-skor -- `0AV`'nin Howells ilkesiyle ayni.
"""
import csv
import json
import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold

HOW = '/home/claude/dis_kaynak/howells/howell.csv'
KOH = '/home/claude/ormorjen-tr/kohort/kohort_98.csv'
# Howells tek deger verir; bizde tarafli olanlarin IKI TARAF ORTALAMASI alinir
ESLES = {'DKB': ('IOD_d',), 'EKB': ('BOW_ek',), 'FMB': ('BOW_fmo',),
         'OBH': ('OH_sag', 'OH_sol'), 'OBB': ('OW_sag', 'OW_sol')}
MODEL1 = ['DKB', 'EKB']                       # birebir eslesen
MODEL2 = ['DKB', 'EKB', 'OBH', 'OBB', 'FMB']  # hepsi


def howells(var):
    r = list(csv.DictReader(open(HOW)))
    X, y, pop = [], [], []
    for x in r:
        try:
            v = [float(x[k]) for k in var]
        except (ValueError, KeyError):
            continue
        if any(t <= 0 for t in v) or x['Sex'] not in ('M', 'F'):
            continue
        X.append(v); y.append(1 if x['Sex'] == 'M' else 0); pop.append(x['Population'])
    return np.array(X), np.array(y), np.array(pop)


def pop_z(X, pop):
    """POPULASYON ICI z-skor: her populasyon kendi ort/ss'sine gore."""
    Z = np.empty_like(X, dtype=float)
    for p in np.unique(pop):
        m = pop == p
        mu, sd = X[m].mean(0), X[m].std(0, ddof=1)
        sd[sd == 0] = 1.0
        Z[m] = (X[m] - mu) / sd
    return Z


def kohort(var):
    r = list(csv.DictReader(open(KOH)))
    ad, X = [], []
    for x in r:
        if x.get('havuz') != 'True':          # `0K` havuz disi olgu girmez
            continue
        try:
            v = [float(np.mean([float(x[c]) for c in ESLES[k]])) for k in var]
        except (ValueError, KeyError):
            continue
        ad.append(x['denek']); X.append(v)
    X = np.array(X)
    return ad, (X - X.mean(0)) / X.std(0, ddof=1)   # kendi ort/ss'si


def modeller():
    return [('LDA', LinearDiscriminantAnalysis()),
            ('Lojistik', LogisticRegression(max_iter=2000)),
            ('Sinir agi (MLP)', MLPClassifier(hidden_layer_sizes=(16, 8),
                                              max_iter=3000, random_state=0))]


def kos(var, etiket):
    Xh, yh, pop = howells(var)
    Zh = pop_z(Xh, pop)
    ad, Zk = kohort(var)
    print('--- %s : %s ---' % (etiket, ', '.join(var)))
    print('Howells egitim n=%d (E %d / K %d, %d populasyon) · kohort n=%d'
          % (len(yh), yh.sum(), len(yh) - yh.sum(), len(np.unique(pop)), len(ad)))
    cik = {'degiskenler': var, 'kohort': ad, 'tahmin': {}, 'howells_dogruluk': {}}
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    for nm, m in modeller():
        s = cross_val_score(m, Zh, yh, cv=cv, scoring='accuracy')
        m.fit(Zh, yh)
        p = m.predict(Zk)
        cik['howells_dogruluk'][nm] = [round(float(s.mean()), 4), round(float(s.std()), 4)]
        cik['tahmin'][nm] = ['E' if t else 'K' for t in p]
        print('  %-16s Howells 5-kat dogruluk %.3f (+-%.3f) · kohort tahmini E %d / K %d'
              % (nm, s.mean(), s.std(), int(p.sum()), int(len(p) - p.sum())))
    return cik


if __name__ == '__main__':
    out = {'MODEL1': kos(MODEL1, 'MODEL 1 — birebir eslesen'),
           'MODEL2': kos(MODEL2, 'MODEL 2 — hepsi')}
    json.dump(out, open('/home/claude/an/out/cinsiyet_tahmin.json', 'w'),
              ensure_ascii=False, indent=1)
