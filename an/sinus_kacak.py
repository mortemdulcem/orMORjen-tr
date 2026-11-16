# -*- coding: utf-8 -*-
"""Sinus kacagi: kohort maske yontemi (rayseg.kohort_maskesi), ARASTIRMACININ landmark ve
egrileriyle uretildiginde, arastirmacinin ELLE CIZDIGI segmentasyondan ne kadar sapiyor?
Landmark hatasi devre disi -> kalan fark maske yonteminin kendisidir.
Cikti: Dice, maske-disi hacim, maske-disi kismin hava (HU<-300) orani (= sinus/hava kacagi).
"""
import sys, os, json, glob
import numpy as np, nrrd
sys.path.insert(0, '/home/claude/orbita_hat'); sys.path.insert(0, '/home/claude/an')
import onisle, params, rayseg

OLG = [('hasta5', "/home/claude/gelen/bt_h5/ölçüm denemesi 1", '4 1.25MM BONE.nrrd'),
       ('hasta6', '/home/claude/gelen/bt_h6/hasta6', '4 1.25MM BONE_1.nrrd'),
       ('hasta7', '/home/claude/sahne/h7', '4 1.25MM BONE.nrrd'),
       ('hasta8', '/home/claude/sahne/h8m2', '4 1.25MM BONE.nrrd'),
       ('hasta9', '/home/claude/sahne/h9m5', '4 1.25MM BONE.nrrd'),
       ('hasta10', '/home/claude/sahne/h10m4', '4 1.25MM BONE.nrrd'),
       ('hasta11', '/home/claude/sahne/h11m3', '1.25MM BONE50.nrrd')]


def elle_seg(kl, shape, org, rows):
    """Segmentation.seg.nrrd -> {'sag','sol'} tam izgarada bool maske (kirpik kayit desteklenir)."""
    a, h = nrrd.read(kl + '/Segmentation.seg.nrrd')
    so = np.array(h['space origin'], float)
    off = np.round(np.linalg.solve(rows.T, so - org)).astype(int)
    out = {}
    i = 0
    while 'Segment%d_Name' % i in h:
        ad = h['Segment%d_Name' % i].lower()
        lv = int(h.get('Segment%d_LabelValue' % i, i + 1))
        ly = int(h.get('Segment%d_Layer' % i, 0))
        A = a[ly] if a.ndim == 4 else a
        m = np.zeros(shape, bool)
        sl = tuple(slice(max(o, 0), max(o, 0) + A.shape[k] - max(-o, 0)) for k, o in enumerate(off))
        src = tuple(slice(max(-o, 0), A.shape[k]) for k, o in enumerate(off))
        m[sl] = (A[src] == lv)
        key = 'sag' if ad.startswith('sa') else ('sol' if ad.startswith('so') else None)
        if key is None:      # terminoloji karisikligi: konuma gore (LPS x>0 = sol)
            c = np.argwhere(m).mean(0) if m.any() else None
            key = 'sol' if c is not None and (org + rows @ c)[0] > 0 else 'sag'
        out[key] = out.get(key, np.zeros(shape, bool)) | m
        i += 1
    return out


R = {}
for ad, kl, ct_ad in OLG:
    hacim, bilgi = onisle.nrrd_hacim(kl + '/' + ct_ad)
    ct = np.transpose(hacim, (2, 1, 0))
    org = np.array(bilgi['origin'], float)
    rows = np.diag([bilgi['PixelSpacing'][0], bilgi['PixelSpacing'][1], bilgi['kesit_araligi']])
    vox = abs(np.linalg.det(rows)) / 1000.
    lm, eg = params.load_scene(kl)
    for s in 'rl':
        for a_, b_ in (('apeks-', 'apex-'), ('fso-', 'mso-'), ('mfo-', 'fmo-')):
            if a_ + s in lm and b_ + s not in lm:
                lm[b_ + s] = lm.pop(a_ + s)
    for S in ('sag', 'sol'):
        if S not in eg:
            k = sorted(x for x in eg if x.endswith(S) or x in (('sağ', 'sa') if S == 'sag' else ()))
            if k: eg[S] = eg[k[0]]
    E = elle_seg(kl, ct.shape, org, rows)
    R[ad] = {}
    for s, S in (('r', 'sag'), ('l', 'sol')):
        if S not in E or S not in eg:
            R[ad][S] = 'eksik'; continue
        M = rayseg.kohort_maskesi(ct, rows, org, lm, s, rim_curve=np.asarray(eg[S], float))['maske']
        G = E[S]
        dis = M & ~G; eks = G & ~M
        R[ad][S] = dict(elle=round(G.sum() * vox, 3), oto=round(M.sum() * vox, 3),
                        dice=round(2. * (M & G).sum() / (M.sum() + G.sum()), 4),
                        fazla=round(dis.sum() * vox, 3), eksik=round(eks.sum() * vox, 3),
                        fazla_hava_orani=round(float((ct[dis] < -300).mean()) if dis.any() else 0., 3),
                        fazla_kemik_orani=round(float((ct[dis] > 160).mean()) if dis.any() else 0., 3))
        print(ad, S, R[ad][S], flush=True)
json.dump(R, open('/home/claude/an/out/elle/sinus_kacak.json', 'w'), indent=1)
print('BITTI')
