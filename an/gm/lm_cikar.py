# -*- coding: utf-8 -*-
"""Arastirmacinin elle landmarklarini (sahnelerden) geomorph girdisine cevirir: 14 nokta x 3."""
import sys, csv
sys.path.insert(0, '/home/claude/orbita_hat'); sys.path.insert(0, '/home/claude/an')
import params
SAHNE = {'hasta5': ("/home/claude/gelen/bt_h5/ölçüm denemesi 1", 'K'),
         'hasta6': ('/home/claude/gelen/bt_h6/hasta6', 'K'), 'hasta7': ('/home/claude/sahne/h7', 'K'),
         'hasta8': ('/home/claude/sahne/h8m2', 'K'), 'hasta9': ('/home/claude/sahne/h9m5', 'E'),
         'hasta10': ('/home/claude/sahne/h10m4', 'E'), 'hasta11': ('/home/claude/sahne/h11m3', 'E'),
         'denek49': ('/home/claude/gelen_elle/d49/denek49 ölçüm 1', 'E'),
         'denek55': ('/home/claude/gelen_elle/d55/denek55 ölçüm1', 'E'),
         'hasta12': ('/home/claude/gelen_elle/hasta12', 'K'), 'hasta18': ('/home/claude/gelen_elle/hasta18', 'K')}
LM = ['d-r', 'mf-r', 'mso-r', 'fmo-r', 'ek-r', 'o-r', 'apex-r', 'd-l', 'mf-l', 'mso-l', 'fmo-l', 'ek-l', 'o-l', 'apex-l']
w = csv.writer(open('/home/claude/an/gm/elle_lm.csv', 'w'))
w.writerow(['olgu', 'cinsiyet'] + ['%s_%s' % (l, a) for l in LM for a in 'xyz'])
for ad, (kl, cs) in SAHNE.items():
    lm, _ = params.load_scene(kl)
    for s in 'rl':
        for a, b in (('apeks-', 'apex-'), ('fso-', 'mso-'), ('mfo-', 'fmo-')):
            if a + s in lm and b + s not in lm: lm[b + s] = lm.pop(a + s)
    eks = [l for l in LM if l not in lm]
    if eks: print(ad, 'EKSIK', eks); continue
    w.writerow([ad, cs] + [round(float(v), 4) for l in LM for v in lm[l]])
    print(ad, 'tamam')
