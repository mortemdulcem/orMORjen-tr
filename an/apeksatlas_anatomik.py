# -*- coding: utf-8 -*-
"""APEKS ATLASI, ANATOMIK CERCEVEDE yeniden turetilir (`0BH` §2.2).

`apeksatlas16.py`'nin `giris()` fonksiyonu `L._duzlem_cerceve` (dunya +z) kullanir.
Burada `L._duzlem_cerceve_anatomik` kullanilir; kaynaklar, isaret duzeni ve
`sgn` kurali AYNEN korunur (`§BA` isaret duzeni tuzagi).

Ic denetim: `t = -(d @ n)` cerceve donmesinden ETKILENMEZ (n degismiyor), bu yuzden
her girisin `t` degeri eski atlasla BIREBIR ayni cikmalidir. Cikmayan varsa durulur.

Cikti: out/apeks_atlas_anatomik.json (out/apeks_atlas.json'a DOKUNULMAZ).
"""
import sys, json
sys.path.insert(0, '/home/claude/an'); sys.path.insert(0, '/home/claude/orbita_hat')
import numpy as np, params, sablon as S, landmark as L

AA = json.load(open('/home/claude/an/out/apeks_atlas.json', encoding='utf-8'))
KAYNAK = {
    'hasta7':  (None, 'sag', 'sol'),
    'hasta8':  (None, 'sag', 'sol'),
    'hasta9':  (None, 'sag', 'sol'),
    'hasta10': (None, 'hasta10_sag_rim_otomatik', 'hasta10_sol_rim_otomatik'),
    'hasta11': (None, 'hasta11_rim_sag', 'hasta11_rim_sol'),
    'hasta13': ('/home/claude/h13m2/ham/ölçüm2', 'oto_rim_sag_1', 'oto_rim_sol_1'),
    'hasta14': ('/home/claude/h14m/ham/hasta14 otomatik ölçüm düzeltme', 'oto_rim_sag', 'oto_rim_sol'),
    'hasta15': ('/home/claude/h15m/ham/hasta15 düzeltme', 'oto_rim_sag', 'oto_rim_sol'),
    'hasta16': ('/home/claude/h16m/ham/hasta16 ototmatik ölçüm düzeltmesi', 'oto_rim_sag', 'oto_rim_sol'),
}

def giris_anatomik(apeks, egri, s, lm):
    c, n, u, v = L._duzlem_cerceve_anatomik(np.asarray(egri, float),
                                            np.asarray(apeks, float), lm)
    d = np.asarray(apeks, float) - c
    sgn = 1.0 if s == 'r' else -1.0
    return float(-(d @ n)), float(d @ u), float(sgn * (d @ v))

YENI = {}
print('%-14s %8s %8s %8s | %8s %8s %8s   t ayni mi' %
      ('anahtar', 't', 'dik', 'yan', 'eski t', 'eski dik', 'eski yan'))
t_sapma = []
for ad, (kls, ks, kl) in KAYNAK.items():
    if kls is None:
        # `OLGULAR` kayitlari esit uzunlukta DEGIL (yalniz hasta6'da 5 oge) — bu yuzden
        # o[4] kullanilmaz; sahne dogrudan okunur. Dogru kaynak oldugu, her girisin
        # `t` degerinin eski atlasla birebir cikmasiyla sinanir (asagida).
        kls = [o[1] for o in S.OLGULAR if o[0] == ad][0]
    lm, _ = params.load_scene(kls)
    _, egri = params.load_scene(kls)
    for a, b in (('fso-r', 'mso-r'), ('fso-l', 'mso-l')):
        if a in lm and b not in lm:
            lm[b] = lm[a]
    for s, k in (('r', ks), ('l', kl)):
        anah = '%s_%s' % (ad, 'sag' if s == 'r' else 'sol')
        if k not in egri or ('apex-' + s) not in lm:
            print('%-14s ATLANDI (egri/apeks yok)' % anah); continue
        t, dik, yan = giris_anatomik(lm['apex-' + s], egri[k], s, lm)
        YENI[anah] = dict(t=round(t, 3), dik=round(dik, 3), yan=round(yan, 3))
        kay = AA.get(anah)
        if kay:
            t_sapma.append(abs(t - kay['t']))
            print('%-14s %8.3f %8.3f %8.3f | %8.3f %8.3f %8.3f   %s'
                  % (anah, t, dik, yan, kay['t'], kay['dik'], kay['yan'],
                     'AYNI' if abs(t - kay['t']) < 0.02 else '>>> FARKLI %.4f' % abs(t - kay['t'])))
        else:
            print('%-14s %8.3f %8.3f %8.3f | %8s %8s %8s   (eski kayit yok)'
                  % (anah, t, dik, yan, '-', '-', '-'))

print('\nic denetim: t en buyuk sapma %.5f mm (beklenen 0 — n degismiyor)' % max(t_sapma))
if max(t_sapma) >= 0.02:
    raise SystemExit('DURDU: t degismemeliydi; cerceve turetmesinde hata var')
ort = {k: float(np.mean([v[k] for v in YENI.values()])) for k in ('t', 'dik', 'yan')}
eski = {k: float(np.mean([v[k] for v in AA.values()])) for k in ('t', 'dik', 'yan')}
print('ortalama  ANATOMIK t %.3f dik %.3f yan %.3f' % (ort['t'], ort['dik'], ort['yan']))
print('ortalama  DUNYA +z  t %.3f dik %.3f yan %.3f' % (eski['t'], eski['dik'], eski['yan']))
json.dump(YENI, open('/home/claude/an/out/apeks_atlas_anatomik.json', 'w'),
          ensure_ascii=False, indent=1)
print('\nyazildi: out/apeks_atlas_anatomik.json (%d giris)' % len(YENI))
