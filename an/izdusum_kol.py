# -*- coding: utf-8 -*-
"""IZDUSUM KURALI — ALPACA'nin NORMAL-ISIN kurali mi, bizim EN-YAKIN kuralimiz mi?

NEDEN: elle isaretlenmis `mf` noktalarinin 10/10'u kemigin tam BIR VOKSEL
DISINDA duruyor (SS 0,11 mm, atlas §BL); otomatik kestirimler ise iceride
kaliyordu. Yani kestirimi yuzeye oturtmak bir "suslemeden" fazlasi: olculmus
bir yanliligi duzeltiyor. Iki kural var ve hangisinin daha iyi oldugu
OLCULMEMISTI:
  (a) BIZIM  (`otomasyon2._yuzeye_izdusur`): en yakin DIS vokesle git.
  (b) ALPACA (`alpaca.yuzeye_izdusur_normal` <- ALPACA.projectPointsPolydata):
      kaynak yuzeyin NORMALI boyunca isin at, EN DISTAKI kesisimi al.

YONTEM: NICP yeniden kosmaz. `medial_loo_dok.json`'daki sablon kestirimleri
geometrik medyanla birlestirilir (hattin yeni birlestiricisi), sonra ucu de
AYNI noktalar uzerinde olculur. Boylece ayrim yalniz izdusum kuralindan gelir.

ON KAYIT — SONUCLAR GORULMEDEN YAZILDI (2026-10-26, `00` §0.12):
  TABAN: izdusum YOK (geometrik medyan cikti, oldugu gibi).
  KABUL (bir kural hatta alinir) UC KOSULUN HEPSI gerekir:
    1. ortalama hata DUSER (en az 0,05 mm; altinda "AYRIM YOK", `00` §14c),
    2. en kotu hata ARTMAZ,
    3. iyilesen nokta sayisi kotulesenden FAZLA.
  Iki kural da gecerse ortalamasi daha dusuk olan alinir; ikisi de gecmezse
  izdusum adimi `d`/`mf` icin HATTA ALINMAZ.

SADAKAT NOTU — BIREBIR DEGIL: ALPACA isin yonunu DEFORME EDILMIS SABLON
yuzeyinin normalinden alir. Burada o yuzey yok (dokumde saklanmiyor), bu yuzden
normal HEDEF yuzeyinden aliniyor. Fark kaydedilmelidir: bu kol "ALPACA'nin
izdusum kurali" degil, "normal-isin kurali"dir. Birebir sinama NICP'in yeniden
kosulmasini ve deforme yuzeyin saklanmasini gerektirir.
"""
import sys, json, argparse
sys.path.insert(0, '/home/claude/an')
import numpy as np
import sablon as S, medial as M, alpaca as AL

ap = argparse.ArgumentParser()
ap.add_argument('--ds', type=int, default=4)
ap.add_argument('--dok', default='/home/claude/an/out/medial_loo_dok.json')
ap.add_argument('--cikti', default='/home/claude/an/out/izdusum_kol.json')
a = ap.parse_args()


def polydata(v, f):
    import vtk
    from vtk.util import numpy_support as ns
    pts = vtk.vtkPoints()
    pts.SetData(ns.numpy_to_vtk(np.ascontiguousarray(v, dtype=np.float64)))
    # VTK 9 API (offsets + connectivity). ESKI `SetCells(n, [3,i,j,k, ...])`
    # cagrisi bu surumde hucre SAYISINI dogru veriyor ama BAGLANTIYI bozuyor:
    # 16.406 hucre "var" gorunurken yuzeyin tam capindan gecen bir isin bile
    # 0 kesisim donduruyordu (2026-10-26'da bu hata yapildi ve yakalandi —
    # `00` §G: hicbir sey kesmeyen bir isin sonuc degil suphedir).
    f = np.asarray(f, np.int64)
    off = np.arange(0, 3 * len(f) + 1, 3, dtype=np.int64)
    cells = vtk.vtkCellArray()
    cells.SetData(ns.numpy_to_vtkIdTypeArray(np.ascontiguousarray(off)),
                  ns.numpy_to_vtkIdTypeArray(np.ascontiguousarray(f.ravel())))
    pd = vtk.vtkPolyData(); pd.SetPoints(pts); pd.SetPolys(cells)
    assert pd.GetNumberOfCells() == len(f), 'hucre sayisi uyusmuyor'
    nf = vtk.vtkPolyDataNormals(); nf.SetInputData(pd)
    nf.ComputePointNormalsOn(); nf.SplittingOff(); nf.ConsistencyOn(); nf.Update()
    return nf.GetOutput()


D = json.load(open(a.dok, encoding='utf-8'))
print('ON KAYIT: kabul icin (1) ort duser >=0,05 (2) en kotu artmaz (3) yon tutarli.')
print('TABAN: izdusum yok (geometrik medyan cikti). kaynak: %s\n' % a.dok)

rows = []
for olgu in sorted(D['olgu']):
    r = D['olgu'][olgu]
    hd = S.yukle(olgu, ds=a.ds)
    pd = polydata(hd['v'], hd['f'])
    kosegen = float(np.linalg.norm(hd['v'].max(0) - hd['v'].min(0)))
    isin = kosegen * 0.05          # 5% — ALPACA'nin kaydirgaci yuzde olarak tanimli
    ad = [k for k in M.HEDEF_NOKTA if k in r['gercek'] and r['tek'].get(k)]
    P0 = np.array([AL.geometrik_medyan(np.array(r['tek'][k], float)) for k in ad])
    G = np.array([r['gercek'][k] for k in ad], float)

    import vtk
    loc = vtk.vtkPointLocator(); loc.SetDataSet(pd); loc.BuildLocator()
    P1 = np.array([pd.GetPoint(loc.FindClosestPoint(p.tolist())) for p in P0])
    P2, kural = AL.yuzeye_izdusur_normal(pd, pd, P0, isin)

    for i, k in enumerate(ad):
        rows.append(dict(olgu=olgu, nokta=k,
                         taban=float(np.linalg.norm(P0[i] - G[i])),
                         en_yakin=float(np.linalg.norm(P1[i] - G[i])),
                         normal_isin=float(np.linalg.norm(P2[i] - G[i])),
                         kural=kural[i],
                         kaydirma_en_yakin=float(np.linalg.norm(P1[i] - P0[i])),
                         kaydirma_normal=float(np.linalg.norm(P2[i] - P0[i]))))
    print('%-8s %s' % (olgu, '  '.join(
        '%s %.2f/%.2f/%.2f' % (k, rows[-len(ad) + i]['taban'],
                               rows[-len(ad) + i]['en_yakin'],
                               rows[-len(ad) + i]['normal_isin'])
        for i, k in enumerate(ad))), flush=True)

t = np.array([x['taban'] for x in rows])
y = np.array([x['en_yakin'] for x in rows])
n = np.array([x['normal_isin'] for x in rows])
print('\n' + '=' * 72)
print('%-26s %10s %10s' % ('kural', 'ort mm', 'en kotu'))
for nm, v in (('TABAN — izdusum yok', t), ('bizim: en yakin yuzey', y),
              ('ALPACA: normal-isin', n)):
    print('%-26s %10.3f %10.3f' % (nm, v.mean(), v.max()))
print('-' * 72)
sonuc = {}
for nm, v in (('en_yakin', y), ('normal_isin', n)):
    iyi = int((v < t - 1e-9).sum()); kot = int((v > t + 1e-9).sum())
    k1 = v.mean() <= t.mean() - 0.05
    k2 = v.max() <= t.max() + 1e-9
    k3 = iyi > kot
    sonuc[nm] = dict(ort=round(float(v.mean()), 3), kotu=round(float(v.max()), 3),
                     iyilesen=iyi, kotulesen=kot,
                     kosul=dict(ort_duser=bool(k1), kotu_artmaz=bool(k2),
                                yon=bool(k3)), gecti=bool(k1 and k2 and k3))
    print('%-14s fark %+.3f mm · iyilesen %d / kotulesen %d · (1)%s (2)%s (3)%s -> %s'
          % (nm, v.mean() - t.mean(), iyi, kot,
             'E' if k1 else 'H', 'E' if k2 else 'H', 'E' if k3 else 'H',
             'GECTI' if (k1 and k2 and k3) else 'GECMEDI'))
gec = [k for k in sonuc if sonuc[k]['gecti']]
if not gec:
    karar = 'IZDUSUM ADIMI d/mf ICIN HATTA ALINMAZ — iki kural da on kaydi gecmedi'
elif len(gec) == 1:
    karar = '%s hatta alinir' % gec[0]
else:
    karar = '%s hatta alinir (iki kural da gecti, ortalamasi dusuk olan)' % min(
        gec, key=lambda k: sonuc[k]['ort'])
print('\nKARAR: %s' % karar)
print('\nisin kurallarinin dagilimi:', {k: sum(1 for x in rows if x['kural'] == k)
                                        for k in set(x['kural'] for x in rows)})
print('ortalama kaydirma: en_yakin %.2f mm · normal %.2f mm'
      % (np.mean([x['kaydirma_en_yakin'] for x in rows]),
         np.mean([x['kaydirma_normal'] for x in rows])))
json.dump(dict(ayar=dict(ds=a.ds, dok=a.dok, isin_yuzdesi=0.05,
                         sadakat='normal HEDEF yuzeyinden; ALPACA deforme SABLONDAN alir'),
               taban=dict(ort=round(float(t.mean()), 3), kotu=round(float(t.max()), 3),
                          n=len(rows), yontem='geometrik medyan, izdusum yok'),
               kol=sonuc, karar=karar, satir=rows),
          open(a.cikti, 'w'), ensure_ascii=False, indent=1)
print('\nyazildi: %s' % a.cikti)
