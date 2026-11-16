# -*- coding: utf-8 -*-
"""ek ve fmo yerlesim kuralini arastirmacinin duzeltmelerinden ogren — 5 katli capraz dogrulama (0BQ).

Karsilastirilan kurallar (her biri ayni egri/cerceve uzerinde; egri ve diger noktalar ARASTIRMACININ):
  A  (bugunku hat): fmo = rim atlasi acisi (5 olgu/10 orbita, 74,5 deg); ek = alan-ikiye-bolme kurali
  B  : fmo = OGRENME katlarindaki arastirmaci fmo acilarinin ortalamasi (taraf basina); ek = alan kurali
  C  : fmo ve ek = OGRENME katlarindaki arastirmaci acilarinin ortalamasi (taraf basina)
Sinav: her olgu yalniz KENDI KATI disindaki olgulardan ogrenilen kuralla olculur (ezber yok).
Hata = kural noktasindan cikan olcu - arastirmacinin olcusu: OW (mf-ek), BOW_ek, BOW_fmo.
"""
import sys, os, json, glob
import numpy as np
sys.path.insert(0, '/home/claude/orbita_hat'); sys.path.insert(0, '/home/claude/an')
import params, landmark as L

EG = '/home/claude/egitim'
KAT = {}
for f in glob.glob('/home/claude/ormorjen-tr/kohort/elle_duzeltme/*_ELLE_OLCUM.json'):
    d = json.load(open(f)); KAT[d['kimlik']] = d.get('kume')
ATLAS = json.load(open('/home/claude/an/out/rimatlas.json'))['atlas']


def yukle(ad):
    lm, eg = params.load_scene(EG + '/' + ad)
    for s in 'rl':
        for a, b in (('apeks-', 'apex-'), ('fso-', 'mso-'), ('mfo-', 'fmo-')):
            if a + s in lm and b + s not in lm:
                lm[b + s] = lm.pop(a + s)
    E = {}
    for S in ('sag', 'sol'):
        k = [x for x in eg if x == S or x.endswith('_' + S) or x.endswith(S)]
        if k:
            E[S] = np.asarray(eg[sorted(k)[0]], float)
    return lm, E


def aci(P, c, u, v, s):
    sgn = 1.0 if s == 'r' else -1.0
    return float(np.degrees(np.arctan2(sgn * ((P - c) @ v), (P - c) @ u)))


V = {}
for ad in sorted(KAT):
    if not os.path.isdir(EG + '/' + ad):
        continue
    try:
        lm, E = yukle(ad)
    except Exception as e:
        print(ad, 'okunamadi', e); continue
    o = {}
    for s, S in (('r', 'sag'), ('l', 'sol')):
        need = ['mf-' + s, 'ek-' + s, 'fmo-' + s, 'apex-' + s]
        if S not in E or any(k not in lm for k in need):
            break
        c, n, u, v = L._duzlem_cerceve(E[S], np.asarray(lm['apex-' + s], float))
        o[s] = dict(E=E[S], c=c, u=u, v=v, mf=np.asarray(lm['mf-' + s], float),
                    ek=np.asarray(lm['ek-' + s], float), fmo=np.asarray(lm['fmo-' + s], float),
                    a_ek=aci(np.asarray(lm['ek-' + s], float), c, u, v, s),
                    a_fmo=aci(np.asarray(lm['fmo-' + s], float), c, u, v, s))
    if len(o) == 2:
        V[ad] = o
print('kullanilabilir olgu:', len(V))


def tahmin(o, s, kural, ogr):
    E, c, u, v = o['E'], o['c'], o['u'], o['v']
    if kural == 'A':
        fmo, _ = L._aci_yerlestir(E, c, u, v, s, ATLAS['fmo']['aci'], 1)
        ek = L._ek_alan(E, c, u, v, o['mf'])
    elif kural == 'B':
        fmo, _ = L._aci_yerlestir(E, c, u, v, s, ogr['fmo'][s], 1)
        ek = L._ek_alan(E, c, u, v, o['mf'])
    else:
        fmo, _ = L._aci_yerlestir(E, c, u, v, s, ogr['fmo'][s], 1)
        ek, _ = L._aci_yerlestir(E, c, u, v, s, ogr['ek'][s], 1)
    return fmo, ek


H = {k: {'OW': [], 'BOW_ek': [], 'BOW_fmo': [], 'fmo_nokta': [], 'ek_nokta': []} for k in 'ABC'}
ogr_son = None
for kat in sorted(set(KAT[a] for a in V)):
    tr = [a for a in V if KAT[a] != kat]; te = [a for a in V if KAT[a] == kat]
    ogr = {b: {s: float(np.mean([V[a][s]['a_' + b] for a in tr])) for s in 'rl'} for b in ('fmo', 'ek')}
    for a in te:
        o = V[a]
        for k in 'ABC':
            P = {s: tahmin(o[s], s, k, ogr) for s in 'rl'}
            for s in 'rl':
                H[k]['OW'].append(np.linalg.norm(P[s][1] - o[s]['mf']) - np.linalg.norm(o[s]['ek'] - o[s]['mf']))
                H[k]['fmo_nokta'].append(np.linalg.norm(P[s][0] - o[s]['fmo']))
                H[k]['ek_nokta'].append(np.linalg.norm(P[s][1] - o[s]['ek']))
            H[k]['BOW_ek'].append(np.linalg.norm(P['r'][1] - P['l'][1]) - np.linalg.norm(o['r']['ek'] - o['l']['ek']))
            H[k]['BOW_fmo'].append(np.linalg.norm(P['r'][0] - P['l'][0]) - np.linalg.norm(o['r']['fmo'] - o['l']['fmo']))
ogr_son = {b: {s: round(float(np.mean([V[a][s]['a_' + b] for a in V])), 2) for s in 'rl'} for b in ('fmo', 'ek')}
ogr_ss = {b: {s: round(float(np.std([V[a][s]['a_' + b] for a in V], ddof=1)), 2) for s in 'rl'} for b in ('fmo', 'ek')}
S = {}
print('\nSINAV (her olgu kendi katinda, gormedigi kuralla) — otomatik kural - arastirmaci')
print('%-6s %-10s %8s %8s %8s' % ('kural', 'olcu', 'ort', 'ort|.|', 'maks|.|'))
for k in 'ABC':
    S[k] = {}
    for m, x in H[k].items():
        x = np.array(x)
        S[k][m] = dict(n=len(x), ort=round(float(x.mean()), 3), mae=round(float(np.abs(x).mean()), 3), maks=round(float(np.abs(x).max()), 3))
        print('%-6s %-10s %8.2f %8.2f %8.2f' % (k, m, x.mean(), np.abs(x).mean(), np.abs(x).max()))
print('\nson model (butun duzeltmeler) ogrenilen acilar:', ogr_son, ' SS:', ogr_ss, ' eski atlas: fmo', ATLAS['fmo']['aci'], 'ek', ATLAS['ek']['aci'])
json.dump(dict(n_olgu=len(V), sinav=S, son_model=ogr_son, son_model_ss=ogr_ss,
               eski_atlas={'fmo': ATLAS['fmo']['aci'], 'ek': ATLAS['ek']['aci']}),
          open('/home/claude/ormorjen-tr/kohort/dogruluk/ogren_ek_fmo.json', 'w'), indent=1)
