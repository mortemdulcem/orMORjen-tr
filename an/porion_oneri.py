# -*- coding: utf-8 -*-
"""Arastirmaciya ELLE porion isaretlemesi icin KESIT ONERISI (olcum degil, yon gosterme).
Kaynak: hasta7 ALI porionu (0BJ: gecerli). Diger olgulara hasta7 BT'sinden katı (rigid) kayitla
tasinir; hasta8'de ALI de karsilastirma icin yazilir. Cikti: LPS/RAS koordinat + Slicer kesit
konumlari + sagital/koronal goruntu.
"""
import json, numpy as np, SimpleITK as sitk, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
SP = '/tmp/claude-0/-home-claude/9f46a888-8a38-562b-887d-ad413187b1aa/scratchpad/porion'
import os; os.makedirs(SP, exist_ok=True)
CT = {'hasta7': '/home/claude/sahne/h7/4 1.25MM BONE.nrrd',
      'hasta8': '/home/claude/sahne/h8m2/4 1.25MM BONE.nrrd',
      'hasta9': '/home/claude/sahne/h9m5/4 1.25MM BONE.nrrd',
      'hasta10': '/home/claude/sahne/h10m4/4 1.25MM BONE.nrrd',
      'hasta11': '/home/claude/sahne/h11m3/1.25MM BONE50.nrrd'}

def ali(h):
    cp = json.load(open('/home/claude/porion/atlas/%s_aso6.json' % h))['markups'][0]['controlPoints']
    return {c['label']: np.array(c['position'], float) for c in cp}

def oku(f):
    im = sitk.Cast(sitk.ReadImage(f), sitk.sitkFloat32)
    return im

ref = oku(CT['hasta7']); P7 = ali('hasta7')
def kucult(im):
    return sitk.Resample(im, [int(s * sp / 2.0) for s, sp in zip(im.GetSize(), im.GetSpacing())],
                         sitk.Transform(), sitk.sitkLinear, im.GetOrigin(), [2.0] * 3, im.GetDirection(), -1024)
def kemik(im):
    return sitk.Cast(sitk.Clamp(im, sitk.sitkFloat32, 0, 1500), sitk.sitkFloat32)

out = {}
for h, f in CT.items():
    im = oku(f)
    if h == 'hasta7':
        P = {k: P7[k] for k in ('RPo', 'LPo')}
    else:
        fx, mv = kemik(kucult(im)), kemik(kucult(ref))
        T0 = sitk.CenteredTransformInitializer(fx, mv, sitk.Euler3DTransform(),
                                               sitk.CenteredTransformInitializerFilter.MOMENTS)
        R = sitk.ImageRegistrationMethod()
        R.SetMetricAsMattesMutualInformation(32); R.SetMetricSamplingStrategy(R.RANDOM)
        R.SetMetricSamplingPercentage(0.2, 7); R.SetInterpolator(sitk.sitkLinear)
        R.SetOptimizerAsRegularStepGradientDescent(2.0, 1e-3, 300)
        R.SetOptimizerScalesFromPhysicalShift(); R.SetShrinkFactorsPerLevel([4, 2, 1])
        R.SetSmoothingSigmasPerLevel([2, 1, 0]); R.SetInitialTransform(T0, inPlace=False)
        T = R.Execute(fx, mv)
        Ti = T.GetInverse()            # T: sabit(h) -> hareketli(hasta7) noktasi; hasta7 noktasini h'ye tasimak icin ters
        P = {k: np.array(Ti.TransformPoint(tuple(P7[k]))) for k in ('RPo', 'LPo')}
        out[h + '_kayit_metrik'] = float(R.GetMetricValue())
    A = ali(h)
    out[h] = {}
    a = sitk.GetArrayFromImage(im)
    fig, ax = plt.subplots(2, 2, figsize=(10, 10))
    for j, k in enumerate(('RPo', 'LPo')):
        p = P[k]; idx = im.TransformPhysicalPointToIndex(tuple(p))
        ras = [-p[0], -p[1], p[2]]
        out[h][k] = dict(LPS=[round(x, 1) for x in p], RAS=[round(x, 1) for x in ras],
                         Slicer_sagital_R=round(ras[0], 1), Slicer_koronal_A=round(ras[1], 1),
                         Slicer_aksiyel_S=round(ras[2], 1), voksel_ijk=list(idx),
                         ALI_RAS=[round(x, 1) for x in [-A[k][0], -A[k][1], A[k][2]]])
        i, jj, kk = idx
        sag = a[::-1, :, i]; kor = a[::-1, jj, :]
        sp = im.GetSpacing()
        ax[j, 0].imshow(np.clip(sag, -200, 1500), cmap='gray', aspect=sp[2] / sp[1])
        ax[j, 0].plot(jj, a.shape[0] - 1 - kk, 'r+', ms=18, mew=2)
        ax[j, 0].set_title('%s %s SAGITAL  R=%.1f' % (h, k, ras[0]))
        ax[j, 1].imshow(np.clip(kor, -200, 1500), cmap='gray', aspect=sp[2] / sp[0])
        ax[j, 1].plot(i, a.shape[0] - 1 - kk, 'r+', ms=18, mew=2)
        ax[j, 1].set_title('%s %s KORONAL  A=%.1f' % (h, k, ras[1]))
        for x in ax[j]: x.axis('off')
    fig.tight_layout(); fig.savefig('%s/%s_porion_oneri.png' % (SP, h), dpi=80); plt.close(fig)
    print(h, json.dumps(out[h]), flush=True)
json.dump(out, open(SP + '/porion_oneri.json', 'w'), indent=1)
