# -*- coding: utf-8 -*-
"""E KOLU — `mso` ANATOMIK CERCEVE.

`0F` §21 hukmu: GENEL kapsamda BENIMSENMEZ. `0F2` §36: `mso` icin kabul.
Bu yuzden YALNIZ `mso` yeniden konur; diger bes nokta D kolundan gelir.

Atlas acisi AYNI cercevede turetilir (bes atlas olgusundan) — yoksa aci ile
cerceve uyusmaz. OLCUT (kosmadan once): `mso` sapmasi DUSMELI ve genel
ortalama YUKSELMEMELI; aksi halde geri alinir.
"""
import sys, os, glob, json
sys.path.insert(0, '/home/claude/an')
import numpy as np, rayseg, params, otomasyon2 as O, landmark as L, kemik_kapisi as kk

AD = ['d','mf','fmo','ek','mso','o','apex']
PAK = '/home/claude/kurtarma/paket'
EGRI_AD = {'hasta7':('sag','sol'),'hasta8':('sag','sol'),'hasta9':('sag','sol'),
           'hasta10':('hasta10_sag_rim_otomatik','hasta10_sol_rim_otomatik'),
           'hasta11':('hasta11_rim_sag','hasta11_rim_sol')}
YOL = {'hasta7':'/home/claude/sahne/h7','hasta8':'/home/claude/sahne/h8m2',
       'hasta9':'/home/claude/sahne/h9m5','hasta10':'/home/claude/sahne/h10m4',
       'hasta11':'/home/claude/sahne/h11m3'}

def mrk(f):
    j = json.load(open(f, encoding='utf-8')); out = []
    for m in j.get('markups', []):
        fl = np.array([-1,-1,1.0]) if (m.get('coordinateSystem') or 'LPS').upper()=='LPS' else np.ones(3)
        for cp in m.get('controlPoints', []):
            out.append(np.array(cp['position'], float) * fl)
    return np.array(out)

# --- 1) mso atlas acisi, ANATOMIK cercevede, bes atlas olgusundan ---
aci, rr = [], []
for ad in EGRI_AD:
    lm, egri = params.load_scene(YOL[ad])
    for a_, b_ in (('fso-r','mso-r'), ('fso-l','mso-l'),
                   ('mfo-r','fmo-r'), ('mfo-l','fmo-l')):   # `00` §2 takma adlar
        if a_ in lm and b_ not in lm:
            lm[b_] = lm[a_]
    for (s, S), k in zip((('r','sag'), ('l','sol')), EGRI_AD[ad]):
        E = np.asarray(egri[k], float)
        c, n, u, v = L._duzlem_cerceve_anatomik(E, np.asarray(lm['apex-'+s], float), lm)
        P = np.asarray(lm['mso-'+s], float)
        p2 = np.array([(P-c) @ u, (P-c) @ v])
        sgn = 1.0 if s == 'r' else -1.0
        aci.append(float(np.degrees(np.arctan2(sgn*p2[1], p2[0]))))
        E2 = np.stack([(E-c) @ u, (E-c) @ v], 1)
        rr.append(float(np.linalg.norm(p2) / np.linalg.norm(E2, axis=1).mean()))
a = np.array(aci)
if a.max() - a.min() > 180: a = np.where(a < 0, a+360, a)
MSO_ANAT = dict(aci=float(a.mean()), r=float(np.mean(rr)))
print('mso atlas acisi (anatomik) : %.1f° · SS %.1f · r %.3f   [dunya +z: %.1f°]'
      % (MSO_ANAT['aci'], a.std(ddof=1), MSO_ANAT['r'], 0.0), flush=True)

ort, ra, apa, kull = O.atlas_yukle()
print('mso atlas acisi (dunya +z) : %.1f° · r %.3f'
      % (ra['mso']['aci'], ra['mso']['r']), flush=True)
print()
print('%-9s %9s %9s %9s %9s' % ('olgu','D mso','E mso','D ort','E ort'), flush=True)
dm=[]; em=[]; do=[]; eo=[]
for ad in sorted(os.listdir(PAK)):
    d = os.path.join(PAK, ad)
    if not os.path.isdir(d): continue
    ct, rows, org = rayseg.load_ct(os.path.join(d, '%s_CT.nrrd' % ad))
    ref = {}
    for f in glob.glob(os.path.join(d, 'OTO_*.mrk.json')):
        b = os.path.basename(f)[4:].replace('.mrk.json','')
        if b.startswith('rim_'): continue
        P = mrk(f)
        if len(P): ref[b] = P[0]
    lm, bil = L.tespit(ct, rows, org, ort, ra, apeks_atlas=apa, tur=3)
    if lm is None: continue
    lm, _ = kk.uygula(ct, rows, org, lm)          # D kolu
    lm2 = dict(lm)
    for s, S in (('r','sag'), ('l','sol')):
        E = bil['egri'].get(S)
        if not isinstance(E, list): continue
        E = np.asarray(E, float)
        c, n, u, v = L._duzlem_cerceve_anatomik(E, np.asarray(lm['apex-'+s], float), lm)
        P, _ = L._aci_yerlestir(E, c, u, v, s, MSO_ANAT['aci'], MSO_ANAT['r'])
        lm2['mso-'+s] = P
    f = lambda L_: np.array([float(np.linalg.norm(np.asarray(L_[b+'-'+s],float)-ref[b+'-'+s]))
                             for b in AD for s in ('r','l') if (b+'-'+s) in L_ and (b+'-'+s) in ref])
    g = lambda L_: np.array([float(np.linalg.norm(np.asarray(L_['mso-'+s],float)-ref['mso-'+s]))
                             for s in ('r','l') if 'mso-'+s in ref])
    a1,a2,b1,b2 = g(lm), g(lm2), f(lm), f(lm2)
    dm.extend(a1.tolist()); em.extend(a2.tolist()); do.extend(b1.tolist()); eo.extend(b2.tolist())
    print('%-9s %9.3f %9.3f %9.3f %9.3f' % (ad, a1.mean(), a2.mean(), b1.mean(), b2.mean()), flush=True)
dm,em,do,eo = map(np.array,(dm,em,do,eo))
print('\n' + '='*52)
print('mso    : D %.3f -> E %.3f   (%+.3f mm)' % (dm.mean(), em.mean(), em.mean()-dm.mean()))
print('genel  : D %.3f -> E %.3f   (%+.3f mm)' % (do.mean(), eo.mean(), eo.mean()-do.mean()))
print('\nHUKUM: %s' % ('ALINIR' if (em.mean() < dm.mean() and eo.mean() <= do.mean()+1e-9) else 'GERI ALINIR'))
