# -*- coding: utf-8 -*-
"""hasta16'yi APEKS ATLASINA ekle — once TANIMI 16 girisin HEPSINDE dogrula.

Dogrulama ekleme oncesi SARTtir (atlas §BD, §BG). Sebebi §BA'daki ISARET DUZENI
TUZAGI: atlas `yan` bilesenini SOL icin AYNALI saklar, `landmark.tespit` onu
`v * (sgn * yan)` ile geri cevirir. Dogrulamasaydim hasta13 yanlis isaretle
girip atlasi bozacakti.

hasta16 GIRDISI: apeks ve egriler 1. DUZELTMEDEN gelir (2. duzeltmede apeks ve
egri YENIDEN GONDERILMEDI, yani 1. turun degerleri gecerli). Ikisi de
ARASTIRMACININ elle verisidir -> olcutu karsiliyor.

BEKLENTI: hasta16'nin `t` degerleri (39,95 / 39,34) atlasin ALT SINIRININ
ALTINDA (su anki aralik 40,85-46,13) -> araligi ASAGIDAN genisletir.
hasta14 yukaridan genisletmisti. §BA'daki aralik-sinirli ekstrapolasyon
sorununa dogrudan katki.
"""
import sys, json, shutil
sys.path.insert(0, '/home/claude/an'); sys.path.insert(0, '/home/claude/orbita_hat')
import numpy as np, params, sablon as S, landmark as L

AA_YOL = '/home/claude/an/out/apeks_atlas.json'
AA = json.load(open(AA_YOL, encoding='utf-8'))
KAYNAK = {
    'hasta7':  (None, 'sag', 'sol'),
    'hasta8':  (None, 'sag', 'sol'),
    'hasta9':  (None, 'sag', 'sol'),
    'hasta10': (None, 'hasta10_sag_rim_otomatik', 'hasta10_sol_rim_otomatik'),
    'hasta11': (None, 'hasta11_rim_sag', 'hasta11_rim_sol'),
    'hasta13': ('/home/claude/h13m2/ham/ölçüm2', 'oto_rim_sag_1', 'oto_rim_sol_1'),
    'hasta14': ('/home/claude/h14m/ham/hasta14 otomatik ölçüm düzeltme', 'oto_rim_sag', 'oto_rim_sol'),
    'hasta15': ('/home/claude/h15m/ham/hasta15 düzeltme', 'oto_rim_sag', 'oto_rim_sol'),
}
H16 = '/home/claude/h16m/ham/hasta16 ototmatik ölçüm düzeltmesi'   # 1. duzeltme


def giris(apeks, egri, s):
    c, n, u, v = L._duzlem_cerceve(np.asarray(egri, float), np.asarray(apeks, float))
    d = np.asarray(apeks, float) - c
    sgn = 1.0 if s == 'r' else -1.0
    return float(-(d @ n)), float(d @ u), float(sgn * (d @ v))


print('TANIM DOGRULAMASI — %d kayitli girisin HEPSI yeniden uretiliyor' % len(AA))
print('%-14s %8s %8s %8s | %8s %8s %8s  %s'
      % ('anahtar', 't', 'dik', 'yan', 'kayit t', 'kayit dik', 'kayit yan', 'durum'))
tamam, bakilan = 0, 0
for ad, (kls, ks, kl) in KAYNAK.items():
    if kls is None:
        kls = [o[1] for o in S.OLGULAR if o[0] == ad][0]
        yed = [o[4] for o in S.OLGULAR if o[0] == ad][0]
        lm = S.landmarklar(kls, yed)
    else:
        lm, _ = params.load_scene(kls)
    _, egri = params.load_scene(kls)
    for s, k in (('r', ks), ('l', kl)):
        anah = '%s_%s' % (ad, 'sag' if s == 'r' else 'sol')
        kay = AA.get(anah)
        if kay is None or k not in egri or ('apex-' + s) not in lm:
            print('%-14s ATLANDI (egri/apeks/kayit yok)' % anah); continue
        t, dik, yan = giris(lm['apex-' + s], egri[k], s)
        ok = all(abs(x - kay[nm]) < 0.02 for x, nm in ((t, 't'), (dik, 'dik'), (yan, 'yan')))
        tamam += ok; bakilan += 1
        print('%-14s %8.3f %8.3f %8.3f | %8.3f %8.3f %8.3f  %s'
              % (anah, t, dik, yan, kay['t'], kay['dik'], kay['yan'],
                 'AYNI' if ok else '>>> FARKLI'))
print('\n  %d/%d giris birebir uretildi (atlasta %d giris var)' % (tamam, bakilan, len(AA)))
if tamam != len(AA):
    raise SystemExit('DURDU: tanim dogrulanmadi — hasta16 EKLENMEZ')
print('  -> tanim DOGRULANDI (cerceve yalniz egriden, landmarklardan bagimsiz)')

print('\n' + '=' * 72)
print('hasta16 GIRISI (arastirmacinin elle apeksi + duzelttigi egri, 1. duzeltme)')
print('=' * 72)
el, egri_el = params.load_scene(H16)
yeni = {}
for s, k in (('r', 'oto_rim_sag'), ('l', 'oto_rim_sol')):
    t, dik, yan = giris(el['apex-' + s], egri_el[k], s)
    anah = 'hasta16_%s' % ('sag' if s == 'r' else 'sol')
    yeni[anah] = dict(t=round(t, 3), dik=round(dik, 3), yan=round(yan, 3))
    print('  %-14s t=%.3f  dik=%.3f  yan=%.3f' % (anah, t, dik, yan))
es = {k: [v[k] for v in AA.values()] for k in ('t', 'dik', 'yan')}
hep = {k: es[k] + [v[k] for v in yeni.values()] for k in ('t', 'dik', 'yan')}
print('\n%-5s %28s %28s' % ('', 'MEVCUT (%d orbita)' % len(AA),
                            'hasta16 EKLENINCE (%d)' % (len(AA) + 2)))
for k in ('t', 'dik', 'yan'):
    a, b = np.array(es[k]), np.array(hep[k])
    print('%-5s ort %7.3f SS %5.3f [%6.2f,%6.2f]  ort %7.3f SS %5.3f [%6.2f,%6.2f]'
          % (k, a.mean(), a.std(ddof=1), a.min(), a.max(),
             b.mean(), b.std(ddof=1), b.min(), b.max()))
print('\n  t = otomatik hattin DERINLIK sabiti')
print('  mevcut %.3f mm -> hasta16 eklenince %.3f mm (%+.3f)'
      % (np.mean(es['t']), np.mean(hep['t']), np.mean(hep['t']) - np.mean(es['t'])))
print('  ARALIK: alt sinir %.2f -> %.2f mm · ust sinir %.2f -> %.2f mm'
      % (min(es['t']), min(hep['t']), max(es['t']), max(hep['t'])))

if any(k.startswith('hasta16') for k in AA):
    print('\nhasta16 ZATEN VAR — eklenmiyor')
else:
    shutil.copy(AA_YOL, AA_YOL + '.yedek_hasta16oncesi')
    AA.update(yeni)
    json.dump(AA, open(AA_YOL, 'w'), ensure_ascii=False, indent=1)
    print('\nEKLENDI -> %d giris / %d hasta'
          % (len(AA), len(set(k.rsplit('_', 1)[0] for k in AA))))
json.dump(yeni, open('/home/claude/an/out/apeks_hasta16.json', 'w'),
          ensure_ascii=False, indent=1)
print('yazildi: out/apeks_hasta16.json · yedek: apeks_atlas.json.yedek_hasta16oncesi')
