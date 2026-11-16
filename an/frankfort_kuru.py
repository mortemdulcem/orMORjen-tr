# -*- coding: utf-8 -*-
"""0BP kuru deneme: ALI (RPo LPo ROr LOr) -> hizalama -> gorsel denetim. OLCUM YAPILMAZ."""
import sys, os, json, glob, subprocess, shutil
import numpy as np, SimpleITK as sitk, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, '/home/claude/an'); import frankfort_hizala as FH
ad, kaynak = sys.argv[1], sys.argv[2]
O = '/home/claude/an/out/frankfort_kuru'; os.makedirs(O, exist_ok=True)
AG = '/home/claude/gelen/ali_zip/ALI_CBCT-main/src/AGENT'
if os.path.isdir(kaynak):
    r = sitk.ImageSeriesReader(); r.SetFileNames(r.GetGDCMSeriesFileNames(kaynak)); img = r.Execute()
else:
    img = sitk.ReadImage(kaynak)
st = os.statvfs('/home/claude')
assert st.f_bavail * st.f_frsize / 1e6 > 900, 'DUR: disk az'
T = '/home/claude/porion/temp_fh'; shutil.rmtree(T, ignore_errors=True); os.makedirs(T + '/tek')
sitk.WriteImage(img, T + '/tek/%s_CT.nrrd' % ad)
pj = O + '/%s_ali.json' % ad
if not os.path.exists(pj):
    subprocess.run('cd "%s" && PYTHONPATH="%s" timeout 1500 python3 predict_landmarks.py --dir_scans %s/tek '
                   '--dir_models /home/claude/ali/models -lm RPo LPo ROr LOr --dir_temp %s/t > %s/log.txt 2>&1'
                   % (AG, AG, T, T, T), shell=True)
    P = {}
    for f in glob.glob(T + '/tek/*_lm_Pred_*.mrk.json'):
        for c in json.load(open(f))['markups'][0]['controlPoints']:
            P[c['label']] = c['position']      # LPS
    if not P:
        shutil.copy(T + '/log.txt', O + '/%s_ali_HATA.log' % ad); print(ad, 'ALI CIKTI YOK'); sys.exit()
    json.dump(P, open(pj, 'w'), indent=1)
shutil.rmtree(T, ignore_errors=True)
A = json.load(open(pj))
P = {'Po-R': A['RPo'], 'Po-L': A['LPo'], 'Or-R': A['ROr'], 'Or-L': A['LOr']}
yeni, R, m, k = FH.hizala(img, P)
dn = np.degrees(np.arccos(np.clip(R[2] @ np.array([0, 0, 1.]), -1, 1)))
yaw = np.degrees(np.arctan2(R[0][1], R[0][0]))
print(ad, 'kapi', k, 'egim(z ekseni) %.1f deg, yaw %.1f deg' % (dn, yaw))
a0 = sitk.GetArrayFromImage(img); a1 = sitk.GetArrayFromImage(yeni)
# orbita seviyesi: orbitale orta noktasinin 10 mm ustu
orm = 0.5 * (np.asarray(P['Or-R']) + np.asarray(P['Or-L']))
z0 = img.TransformPhysicalPointToIndex((orm + [0, 0, 10]).tolist())[2]
q = FH.eski_to_yeni(orm, R, m) + [0, 0, 10]; z1 = yeni.TransformPhysicalPointToIndex(q.tolist())[2]
fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].imshow(np.clip(a0[min(max(z0, 0), a0.shape[0] - 1)], -200, 1500), cmap='gray'); ax[0].set_title('%s ONCE (aksiyel, Or+10mm)' % ad)
ax[1].imshow(np.clip(a1[min(max(z1, 0), a1.shape[0] - 1)], -200, 1500), cmap='gray'); ax[1].set_title('SONRA Frankfort hizali  egim %.1f°' % dn)
for x in ax: x.axis('off')
fig.tight_layout(); fig.savefig(O + '/%s_once_sonra.png' % ad, dpi=70)
json.dump(dict(kapi=k, egim_deg=round(float(dn), 2), yaw_deg=round(float(yaw), 2), P=P), open(O + '/%s_kuru.json' % ad, 'w'), indent=1)
