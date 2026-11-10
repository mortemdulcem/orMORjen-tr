# -*- coding: utf-8 -*-
"""hasta9 (P08) — atlasta eksik kalan olcumler, kaynaktan.
1) Otomatik rim egrisi <-> arastirmacinin TAM ELLE cizdigi egri (serinin tek tam elle egrisi)
2) Altigen turevli apertur <-> elle egri (katsayi dogrulamasi)
3) Isin yontemi hacmi + Dice (tez maskesine karsi)
"""
import sys, json
sys.path.insert(0, '/home/claude/an')
import numpy as np, nrrd, params, rayseg, rimcurve

F = '/home/claude/h9m/ham/ölçüm5'
ORD = ('d', 'mf', 'mso', 'fmo', 'ek', 'o')   # CEVRESEL sira (00 §3 / §12) — alan icin zorunlu

lm, egri = params.load_scene(F)
for a, b in (('fso-r', 'mso-r'), ('fso-l', 'mso-l')):
    if a in lm and b not in lm:
        lm[b] = lm[a]
ct, rows, org = rayseg.load_ct(F + '/4 1.25MM BONE.nrrd')
vox = abs(float(np.linalg.det(rows)))

d, h = nrrd.read(F + '/Segmentation.seg.nrrd')
sub = d if d.ndim == 3 else d[0]
TEZ = {'r': (sub == 1), 'l': (sub == 2)}

# n=8 (guncel) ve n=6 (olcum_zinciri.py'de duran eski) katsayilar
K8 = dict(alan=1.4015, cevre=1.0974, derinlik=1.539, kaydir=1.39)
K6 = dict(alan=1.4243, cevre=1.1006, derinlik=1.523, kaydir=1.30)

OUT = {}

def metr(P, apex):
    c, n, rr, dev = params.plane(np.asarray(P, float))
    if np.dot(apex - c, n) > 0:
        n = -n
    return dict(alan=params.newell_area(P), cevre=params.perim(P),
                s31=rr, sapma=dev, derinlik=abs(float((apex - c) @ n)), c=c, n=n)

def en_yakin(A, B):
    """A'nin her noktasinin B poligon KOSELERINE en kisa uzakligi (mm)."""
    A = np.asarray(A, float); B = np.asarray(B, float)
    return np.array([np.min(np.linalg.norm(B - a, axis=1)) for a in A])

def poli_uzaklik(A, B):
    """A'nin her noktasinin B kapali POLIGON KENARLARINA en kisa uzakligi."""
    A = np.asarray(A, float); B = np.asarray(B, float)
    out = []
    for a in A:
        best = 1e9
        for i in range(len(B)):
            p, q = B[i], B[(i + 1) % len(B)]
            v = q - p; L2 = float(v @ v)
            t = 0.0 if L2 == 0 else max(0.0, min(1.0, float((a - p) @ v) / L2))
            best = min(best, float(np.linalg.norm(a - (p + t * v))))
        out.append(best)
    return np.array(out)

print('=' * 78)
print('1) OTOMATIK RIM EGRISI  <->  ARASTIRMACININ TAM ELLE CIZDIGI EGRI')
print('=' * 78)
for s, S in (('r', 'sag'), ('l', 'sol')):
    apex = np.asarray(lm['apex-' + s], float)
    man = np.asarray(egri[S], float)
    oto, bilgi = rimcurve.auto_rim(ct, rows, org, lm, s, win=0.75, n_out=20)
    M, A = metr(man, apex), metr(oto, apex)
    dk = poli_uzaklik(oto, man)      # otomatik nokta -> elle poligon
    dk2 = poli_uzaklik(man, oto)     # elle nokta -> otomatik poligon
    OUT['oto_egri_' + S] = dict(
        alan=round(A['alan'], 1), cevre=round(A['cevre'], 2),
        derinlik=round(A['derinlik'], 2), s31=round(A['s31'], 3),
        alan_hata=round(100 * (A['alan'] / M['alan'] - 1), 2),
        cevre_hata=round(100 * (A['cevre'] / M['cevre'] - 1), 2),
        derinlik_hata=round(A['derinlik'] - M['derinlik'], 2),
        sapma_ort=round(float(dk.mean()), 2), sapma_maks=round(float(dk.max()), 2),
        sapma_ort_ters=round(float(dk2.mean()), 2), sapma_maks_ters=round(float(dk2.max()), 2))
    print('--- %s' % S)
    print('  elle   : alan %7.1f  cevre %6.2f  derinlik %5.2f  s3/s1 %.3f'
          % (M['alan'], M['cevre'], M['derinlik'], M['s31']))
    print('  otomatik: alan %7.1f  cevre %6.2f  derinlik %5.2f  s3/s1 %.3f'
          % (A['alan'], A['cevre'], A['derinlik'], A['s31']))
    print('  hata   : alan %+6.2f%%  cevre %+6.2f%%  derinlik %+5.2f mm'
          % (OUT['oto_egri_' + S]['alan_hata'], OUT['oto_egri_' + S]['cevre_hata'],
             OUT['oto_egri_' + S]['derinlik_hata']))
    print('  nokta sapmasi (oto->elle kenar): ort %.2f  maks %.2f mm' % (dk.mean(), dk.max()))
    print('  nokta sapmasi (elle->oto kenar): ort %.2f  maks %.2f mm' % (dk2.mean(), dk2.max()))

print()
print('=' * 78)
print('2) ALTIGEN TUREVLI APERTUR  <->  ELLE EGRI  (katsayi dogrulamasi)')
print('=' * 78)
for s, S in (('r', 'sag'), ('l', 'sol')):
    apex = np.asarray(lm['apex-' + s], float)
    man = np.asarray(egri[S], float)
    H = np.array([lm[b + '-' + s] for b in ORD], float)
    M, Hm = metr(man, apex), metr(H, apex)
    r = dict(alan=M['alan'] / Hm['alan'], cevre=M['cevre'] / Hm['cevre'],
             derinlik=M['derinlik'] - Hm['derinlik'],
             duzlem=float((Hm['c'] - M['c']) @ M['n']))
    OUT['altigen_' + S] = {k: round(v, 4) for k, v in r.items()}
    print('--- %s   altigen ham: alan %7.1f  cevre %6.2f  derinlik %5.2f'
          % (S, Hm['alan'], Hm['cevre'], Hm['derinlik']))
    print('  hasta9\'un kendi katsayilari : alan x%.4f  cevre x%.4f  derinlik %+.3f mm'
          % (r['alan'], r['cevre'], r['derinlik']))
    print('  altigen duzlemi elle duzleme gore %+.3f mm (negatif = daha derin)' % r['duzlem'])
    for ad, K in (('n=8 (guncel)', K8), ('n=6 (olcum_zinciri.py)', K6)):
        a = Hm['alan'] * K['alan']; c = Hm['cevre'] * K['cevre']; dd = Hm['derinlik'] + K['derinlik']
        print('  %-22s -> alan %7.1f (%+5.2f%%)  cevre %6.2f (%+5.2f%%)  derinlik %5.2f (%+5.2f mm)'
              % (ad, a, 100 * (a / M['alan'] - 1), c, 100 * (c / M['cevre'] - 1),
                 dd, dd - M['derinlik']))

print()
print('=' * 78)
print('3) ISIN YONTEMI  ->  hacim ve Dice (tez maskesi = tam elle cizim)')
print('=' * 78)
sen = [('egri + kaydirma 0,0 mm', dict(rim=True, sh=0.0)),
       ('altigen + kaydirma 1,30 mm', dict(rim=False, sh=1.30)),
       ('altigen + kaydirma 1,39 mm', dict(rim=False, sh=1.39))]
for ad, cfg in sen:
    sat = []
    for s, S in (('r', 'sag'), ('l', 'sol')):
        rc = np.asarray(egri[S], float) if cfg['rim'] else None
        o = rayseg.ray_volume(ct, rows, org, lm, s, rim_curve=rc,
                              plane_shift=cfg['sh'], return_mask=True, acma_mm=1.5)
        mk = o['maske'] if 'maske' in o else o.get('mask')
        T = TEZ[s]
        hac = float(mk.sum()) * vox / 1000.0
        dice = 2 * float((mk & T).sum()) / float(mk.sum() + T.sum())
        tez = float(T.sum()) * vox / 1000.0
        sat.append((S, hac, tez, 100 * (hac / tez - 1), dice))
        OUT['isin_%s_%s' % (cfg['sh'], S)] = dict(
            hacim=round(hac, 3), sapma=round(100 * (hac / tez - 1), 2), dice=round(dice, 4))
    print('--- %s' % ad)
    for S, hac, tez, sp, dc in sat:
        print('  %-4s isin %7.3f  tez %7.3f cm3  sapma %+6.2f%%  Dice %.4f' % (S, hac, tez, sp, dc))

json.dump(OUT, open('/home/claude/h9m/atlas_eksik.json', 'w'), ensure_ascii=False, indent=1)
print('\nyazildi: /home/claude/h9m/atlas_eksik.json')
