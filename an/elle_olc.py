# -*- coding: utf-8 -*-
"""ARASTIRMACI LANDMARKLARIYLA OLCUM — donmus hattin 6-8. adimlari, AYNI cagrilarla.

Girdi: ham DICOM klasoru + arastirmacinin Slicer klasoru (14 nokta + sag/sol rim egrisi).
Hattin 1-5. adimlari (otomatik landmark/rim) ATLANIR; yerine arastirmacinin noktalari girer.
6) maske   : rayseg.kohort_maskesi (otomasyon2 ile ayni tek kaynak ayar)
7) olcum   : olcum_zinciri.olc(on_sinir_duzlemde=True), apeks_atlastan=False
             -> apeks ELLE isaretli oldugu icin DERINLIK OLCULUR
             kalinlik: kalinlik_bolgesel.measure_side (ayni eksen tanimi)
8) denetim : olc() icindeki kapilar + otomasyon2 ek kapilari
Kullanim: python3 elle_olc.py <denek> <dicom_klasoru> <slicer_klasoru>
"""
import sys, os, json
import numpy as np
sys.path.insert(0, '/home/claude/orbita_hat'); sys.path.insert(0, '/home/claude/an')
import onisle, params, rayseg, landmark as L
import olcum_zinciri as oz
import kalinlik_bolgesel as kb

denek, dcm, kl = sys.argv[1:4]
hacim, bilgi = (onisle.nrrd_hacim(dcm) if dcm.endswith('.nrrd') else onisle.dicom_hacim(dcm))
ct = np.transpose(hacim, (2, 1, 0))
org = np.array(bilgi["origin"], float)
rows = np.diag([bilgi["PixelSpacing"][0], bilgi["PixelSpacing"][1], bilgi["kesit_araligi"]])

lm, egri = params.load_scene(kl)
for s in ('r', 'l'):                      # Slicer adi 'apeks-*' -> hat adi 'apex-*'
    if 'apeks-' + s in lm:
        lm['apex-' + s] = lm.pop('apeks-' + s)
    if 'mfo-' + s in lm and 'fmo-' + s not in lm:   # hasta6 sahnesindeki yazim hatasi
        lm['fmo-' + s] = lm.pop('mfo-' + s)
    if 'fso-' + s in lm and 'mso-' + s not in lm:   # hasta8-11: fso = mso (manuel-olcum-yontemi-atlas §3)
        lm['mso-' + s] = lm.pop('fso-' + s)
if 'sag' not in egri:                     # 'sağ' / 'sa' (Turkce karakter) adlandirmasi
    for k in ('sağ', 'sa'):
        if k in egri:
            egri['sag'] = egri[k]; break
for S in ('sag', 'sol'):                  # 'hasta11_rim_sag' gibi adlar
    if S not in egri:
        ad = sorted(k for k in egri if k.endswith(S) or ('_%s_' % S) in k)
        if ad:
            egri[S] = egri[ad[0]]
gerek = [b + '-' + s for b in L.ORD for s in 'rl'] + ['apex-r', 'apex-l']
eksik = [k for k in gerek if k not in lm]
assert not eksik, 'eksik landmark: %s' % eksik
E = {'sag': np.asarray(egri['sag'], float), 'sol': np.asarray(egri['sol'], float)}

M = {}
for s, S in (('r', 'sag'), ('l', 'sol')):
    M[s] = rayseg.kohort_maskesi(ct, rows, org, lm, s, rim_curve=E[S])['maske']

R = oz.olc(ct, rows, org, lm, M['r'], M['l'], rim_r=E['sag'], rim_l=E['sol'],
           kaynak='ARASTIRMACI LANDMARK + EGRI (Slicer) · maske rayseg.kohort_maskesi',
           kimlik=denek + '_ELLE', on_sinir_duzlemde=True, apeks_atlastan=False)
for s, S in (('r', 'sag'), ('l', 'sol')):
    eks = np.asarray(lm['apex-' + s], float) - np.mean([lm[b + '-' + s] for b in L.ORD], axis=0)
    t = kb.measure_side(ct, rows, org, M[s], eks, s)
    for bol in ('superior', 'inferior', 'medial', 'lateral'):
        if t[bol]['durum'] == 'TAMAM':
            R['kal_%s_%s' % (bol[:3], S)] = round(t[bol]['medyan'], 2)
            R['kal_%s_%s_ince' % (bol[:3], S)] = round(t[bol]['p2'], 2)
            R['kal_%s_%s_kalin' % (bol[:3], S)] = round(t[bol]['p98'], 2)
den = R.pop('denetim')
ek = {}
for S in ('sag', 'sol'):
    kal = {b: R.get('kal_%s_%s' % (b, S)) for b in ('sup', 'inf', 'med', 'lat')}
    if all(v is not None for v in kal.values()):
        ek['medial_en_ince_' + S] = bool(kal['med'] == min(kal.values()))
    h = R.get('hacimK_' + S)
    ek['hacim_bandi_' + S] = bool(h is not None and 19.9 <= h <= 33.4)
    ek['OI_100_' + S] = bool(R.get('OI_' + S, 0) < 100)
rap = {'kimlik': denek, 'yontem': 'elle_olc.py (hat 6-8. adim, arastirmaci landmarklari)',
       'slicer_klasoru': kl, 'bt': bilgi, 'olcum': R, 'denetim': den, 'ek_kapilar': ek}
os.makedirs('/home/claude/an/out/elle', exist_ok=True)
json.dump(rap, open('/home/claude/an/out/elle/%s_ELLE_OLCUM.json' % denek, 'w'),
          ensure_ascii=False, indent=1, default=str)
print('BITTI', denek)
