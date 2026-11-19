# -*- coding: utf-8 -*-
"""0BT — yontem secimi: BUGUNKU hat (A) ve C kurali, arastirmacinin duzeltmelerine (gercek) karsi, UCTAN UCA.
Girdi: an/out/erkekA/<denek>_OLCUM.json (+ TAMOTO klasoru) · egitim/<denek>/ (arastirmaci) · elle_duzeltme ELLE json.
C: ek/fmo, A'nin OTOMATIK rim egrisi + otomatik apeks uzerinde, OGRENME katlarindaki arastirmaci acilariyla.
Cikti: kohort/dogruluk/yontem_sinavi_0BT.json + .csv (olgu basina)
"""
import sys, os, json, glob, csv
import numpy as np
sys.path.insert(0, '/home/claude/orbita_hat'); sys.path.insert(0, '/home/claude/an')
import params, landmark as L

EG = '/home/claude/egitim'; EA = '/home/claude/an/out/erkekA'; REPO = '/home/claude/ormorjen-tr/kohort'
PTS = ['d', 'mf', 'mso', 'fmo', 'ek', 'o', 'apex']
PAR = ['OW_sag', 'OW_sol', 'OH_sag', 'OH_sol', 'OI_sag', 'OI_sol', 'APalan_sag', 'APalan_sol', 'APcevre_sag',
       'APcevre_sol', 'hacim_sag', 'hacim_sol', 'IOD_d', 'IOD_mf', 'BOW_ek', 'BOW_fmo', 'derinlik_sag', 'derinlik_sol']


def ad_duzelt(lm, eg):
    for s in 'rl':
        for a, b in (('apeks-', 'apex-'), ('fso-', 'mso-'), ('mfo-', 'fmo-')):
            if a + s in lm and b + s not in lm:
                lm[b + s] = lm.pop(a + s)
    E = {}
    for S in ('sag', 'sol'):
        k = sorted(x for x in eg if x == S or x.endswith('_' + S) or x.endswith(S))
        if not k and S == 'sag':
            k = [x for x in eg if x in ('sağ', 'sa')]
        if k:
            E[S] = np.asarray(eg[k[0]], float)
    return {k: np.asarray(v, float) for k, v in lm.items()}, E


def aci(P, c, u, v, s):
    sgn = 1.0 if s == 'r' else -1.0
    return float(np.degrees(np.arctan2(sgn * ((P - c) @ v), (P - c) @ u)))


def egri_hata(Ea, Eg):
    """A egrisinin her noktasinin arastirmaci egrisine (kapali, sik orneklenmis) en yakin uzakligi."""
    G = np.vstack([Eg, Eg[:1]])
    yog = np.vstack([G[i] + t * (G[i + 1] - G[i]) for i in range(len(G) - 1) for t in np.linspace(0, 1, 20, endpoint=False)])
    d = np.linalg.norm(Ea[:, None, :] - yog[None], axis=2).min(1)
    return float(d.mean()), float(d.max())


KAT = {}
for f in glob.glob(REPO + '/elle_duzeltme/*_ELLE_OLCUM.json'):
    d = json.load(open(f)); KAT[d['kimlik']] = (d.get('kume'), d['olcum'])

V = {}
for ad in sorted(KAT, key=lambda x: int(''.join(c for c in x if c.isdigit()) or 0)):
    fa = '%s/%s_OLCUM.json' % (EA, ad)
    if not (os.path.exists(fa) and os.path.isdir(EG + '/' + ad)):
        continue
    RA = json.load(open(fa))
    tam = RA.get('mrk_klasoru')
    try:
        g_lm, g_E = ad_duzelt(*params.load_scene(EG + '/' + ad))
        a_lm, a_E = ad_duzelt(*params.load_scene(tam))
    except Exception as e:
        print(ad, 'okunamadi', e); continue
    if len(g_E) < 2 or len(a_E) < 2 or any(p + '-' + s not in g_lm for p in PTS for s in 'rl'):
        print(ad, 'eksik veri'); continue
    V[ad] = dict(kat=KAT[ad][0], g=g_lm, gE=g_E, a=a_lm, aE=a_E, gO=KAT[ad][1], aO=RA.get('olcum', {}))
    for s, S in (('r', 'sag'), ('l', 'sol')):
        c, n, u, v = L._duzlem_cerceve(g_E[S], g_lm['apex-' + s])
        V[ad]['ga_ek_' + s] = aci(g_lm['ek-' + s], c, u, v, s)
        V[ad]['ga_fmo_' + s] = aci(g_lm['fmo-' + s], c, u, v, s)
print('sinava giren olgu:', len(V))

satirlar = []
for ad, o in V.items():
    tr = [x for x in V if V[x]['kat'] != o['kat']]
    ang = {(b, s): float(np.mean([V[x]['ga_%s_%s' % (b, s)] for x in tr])) for b in ('ek', 'fmo') for s in 'rl'}
    r = {'denek': ad, 'kat': o['kat']}
    C = {}
    for s, S in (('r', 'sag'), ('l', 'sol')):
        for p in PTS:
            r['nokta_%s-%s' % (p, s)] = round(float(np.linalg.norm(o['a'][p + '-' + s] - o['g'][p + '-' + s])), 3)
        r['egri_ort_' + S], r['egri_maks_' + S] = [round(x, 3) for x in egri_hata(o['aE'][S], o['gE'][S])]
        E = o['aE'][S]; c, n, u, v = L._duzlem_cerceve(E, o['a']['apex-' + s])
        C['fmo-' + s], _ = L._aci_yerlestir(E, c, u, v, s, ang[('fmo', s)], 1)
        C['ek-' + s], _ = L._aci_yerlestir(E, c, u, v, s, ang[('ek', s)], 1)
        C['fmo-' + s] = np.asarray(C['fmo-' + s], float); C['ek-' + s] = np.asarray(C['ek-' + s], float)
        r['C_nokta_ek-' + s] = round(float(np.linalg.norm(C['ek-' + s] - o['g']['ek-' + s])), 3)
        r['C_nokta_fmo-' + s] = round(float(np.linalg.norm(C['fmo-' + s] - o['g']['fmo-' + s])), 3)
    for p in PAR:
        a, g = o['aO'].get(p), o['gO'].get(p)
        r['A_' + p] = round(float(a) - float(g), 3) if a is not None and g is not None else None
    # C: OW ve BOW, A degerinden yalniz ek/fmo degisimiyle (tanim farki tasinmasin)
    for s, S in (('r', 'sag'), ('l', 'sol')):
        if r['A_OW_' + S] is not None:
            dA = np.linalg.norm(o['a']['ek-' + s] - o['a']['mf-' + s]); dC = np.linalg.norm(C['ek-' + s] - o['a']['mf-' + s])
            r['C_OW_' + S] = round(r['A_OW_' + S] + float(dC - dA), 3)
    for b in ('ek', 'fmo'):
        if r['A_BOW_' + b] is not None:
            dA = np.linalg.norm(o['a'][b + '-r'] - o['a'][b + '-l']); dC = np.linalg.norm(C[b + '-r'] - C[b + '-l'])
            r['C_BOW_' + b] = round(r['A_BOW_' + b] + float(dC - dA), 3)
    mx = max(r['nokta_%s-%s' % (p, s)] for p in PTS for s in 'rl')
    hv = max(abs(r['A_hacim_sag'] or 0), abs(r['A_hacim_sol'] or 0))
    r['felaket'] = bool(mx > 10 or hv > 3)
    satirlar.append(r)


def oz(key):
    x = np.array([r[key] for r in satirlar if r.get(key) is not None], float)
    if not len(x):
        return None
    return dict(n=int(len(x)), ort=round(float(x.mean()), 3), mae=round(float(np.abs(x).mean()), 3),
                medyan_mutlak=round(float(np.median(np.abs(x))), 3), maks=round(float(np.abs(x).max()), 3))


S = {'n_olgu': len(satirlar), 'felaket': [r['denek'] for r in satirlar if r['felaket']]}
S['nokta_A'] = {'%s-%s' % (p, s): oz('nokta_%s-%s' % (p, s)) for p in PTS for s in 'rl'}
S['nokta_C'] = {k: oz('C_nokta_' + k) for k in ('ek-r', 'ek-l', 'fmo-r', 'fmo-l')}
S['egri_A'] = {k: oz(k) for k in ('egri_ort_sag', 'egri_ort_sol', 'egri_maks_sag', 'egri_maks_sol')}
S['param_A'] = {p: oz('A_' + p) for p in PAR}
S['param_C'] = {p: oz('C_' + p) for p in ('OW_sag', 'OW_sol', 'BOW_ek', 'BOW_fmo')}
# 0BT §4 olcutleri
fel_C = S['felaket']   # C yalniz ek/fmo degistirir; felaket tanimi A noktalarindan; ayrica C ek/fmo >10 mm sayilir
fel_C2 = [r['denek'] for r in satirlar if r['felaket'] or max(r['C_nokta_ek-r'], r['C_nokta_ek-l'], r['C_nokta_fmo-r'], r['C_nokta_fmo-l']) > 10]
A_ = S['param_A']; C_ = S['param_C']
ekA = np.mean([S['nokta_A']['ek-r']['mae'], S['nokta_A']['ek-l']['mae']]); ekC = np.mean([S['nokta_C']['ek-r']['mae'], S['nokta_C']['ek-l']['mae']])
fA = np.mean([S['nokta_A']['fmo-r']['mae'], S['nokta_A']['fmo-l']['mae']]); fC = np.mean([S['nokta_C']['fmo-r']['mae'], S['nokta_C']['fmo-l']['mae']])
ol = {
    '1_OW_mae': bool(C_['OW_sag']['mae'] < A_['OW_sag']['mae'] and C_['OW_sol']['mae'] < A_['OW_sol']['mae']),
    '2_BOWek_mae': bool(C_['BOW_ek']['mae'] < A_['BOW_ek']['mae']),
    '3_nokta': bool(ekC < ekA and fC <= fA + 0.2),
    '4_maks': bool(all(C_[p]['maks'] <= A_[p]['maks'] + 1.0 for p in C_) and
                   all(S['nokta_C'][k]['maks'] <= S['nokta_A'][k]['maks'] + 1.0 for k in S['nokta_C'])),
    '5_felaket': bool(len(fel_C2) <= len(S['felaket'])),
}
S['olcut_0BT'] = ol; S['C_kabul'] = all(ol.values())
S['ek_nokta_ort'] = dict(A=round(float(ekA), 3), C=round(float(ekC), 3)); S['fmo_nokta_ort'] = dict(A=round(float(fA), 3), C=round(float(fC), 3))
os.makedirs(REPO + '/dogruluk', exist_ok=True)
json.dump(S, open(REPO + '/dogruluk/yontem_sinavi_0BT.json', 'w'), ensure_ascii=False, indent=1)
with open(REPO + '/dogruluk/yontem_sinavi_0BT_olgu.csv', 'w', newline='', encoding='utf-8') as fh:
    k = sorted({x for r in satirlar for x in r}, key=lambda x: (x != 'denek', x != 'kat', x))
    w = csv.DictWriter(fh, fieldnames=k); w.writeheader(); w.writerows(satirlar)
print(json.dumps({k: S[k] for k in ('n_olgu', 'felaket', 'olcut_0BT', 'C_kabul', 'ek_nokta_ort', 'fmo_nokta_ort')}, ensure_ascii=False))
print('NOKTA A (mae/maks):', {k: (v['mae'], v['maks']) for k, v in S['nokta_A'].items()})
print('EGRI A:', {k: v['mae'] for k, v in S['egri_A'].items()})
print('PARAM A (ort/mae/maks):', {k: (v['ort'], v['mae'], v['maks']) for k, v in A_.items() if v})
print('PARAM C:', {k: (v['ort'], v['mae'], v['maks']) for k, v in C_.items() if v})
