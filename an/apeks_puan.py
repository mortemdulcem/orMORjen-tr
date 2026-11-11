# -*- coding: utf-8 -*-
"""0BM puanlama. Tanim ve olcutler on kayittan AYNEN (sonuc gorulmeden sabit).
apeks = optik sinir maskesinin EN ARKA 2 mm diliminin agirlik merkezi;
'arka' = glob agirlik merkezinden sinir agirlik merkezine dogru birim vektor.
Derinlik = apeks -> ELLE cizilmis apertur egrisinin duzlemi (her iki kol icin AYNI duzlem;
fark yalniz apeksten gelsin). Koordinat: RAS (sahne ile ayni)."""
import sys, json, numpy as np, SimpleITK as sitk
sys.path.insert(0,'/home/claude/an')
import params
SAHNE={'hasta5':'/home/claude/h5m/ham/ölçüm denemesi 2','hasta6':'/home/claude/h6m3/ham/hasta6 ölçüm 3',
       'hasta7':'/home/claude/h7/ham/ölçüm1','hasta8':'/home/claude/h8m/ham/ölçüm2',
       'hasta9':'/home/claude/h9m/ham/ölçüm5','hasta10':'/home/claude/h10m/ham/ölçüm4',
       'hasta11':'/home/claude/h11m3/ham/ölçüm3'}
EGRI={'hasta10':('hasta10_sag_rim_otomatik','hasta10_sol_rim_otomatik'),
      'hasta11':('hasta11_rim_sag','hasta11_rim_sol')}
def ras_noktalar(yol):
    m=sitk.ReadImage(yol); a=sitk.GetArrayFromImage(m)          # z,y,x
    idx=np.argwhere(a>0)
    if len(idx)==0: return np.zeros((0,3))
    P=np.array([m.TransformIndexToPhysicalPoint((int(i[2]),int(i[1]),int(i[0]))) for i in idx],float)
    return P*np.array([-1,-1,1.])                                # LPS -> RAS
def duzlem(E):
    c=E.mean(0); n=np.linalg.svd(E-c)[2][2]; return c,n/np.linalg.norm(n)
def egri_bul(egri, S, ad):
    if ad in EGRI:
        k=EGRI[ad][0 if S=='sag' else 1]
        if k in egri: return np.asarray(egri[k],float)
    for k,v in egri.items():
        kl=k.lower().replace('ğ','g')
        if kl.endswith('_1'): kl=kl[:-2]
        if kl==S or kl.endswith('_'+S) or kl.endswith(S):
            a=np.asarray(v,float)
            if a.ndim==2 and len(a)>=10: return a
    return None
sat=[]; kapsama=0
for ad,yol in SAHNE.items():
    h='h'+ad[5:]
    try: lm,egri=params.load_scene(yol)
    except Exception as e: print(ad,'sahne yok',e); continue
    for s,S,tr in (('r','sag','right'),('l','sol','left')):
        sin=ras_noktalar('/home/claude/apeks_ts/%s/optic_nerve_%s.nii.gz'%(h,tr))
        glb=ras_noktalar('/home/claude/apeks_ts/%s/eyeball_%s.nii.gz'%(h,tr))
        el=np.asarray(lm['apex-'+s],float)
        E=egri_bul(egri,S,ad)
        if len(sin)>=50: kapsama+=1
        if len(sin)<50 or len(glb)==0 or E is None:
            print('%-8s %-3s sinir %d voksel · ATLANDI'%(ad,S,len(sin))); sat.append((ad,S,None,None,None)); continue
        yon=sin.mean(0)-glb.mean(0); yon/=np.linalg.norm(yon)
        t=sin@yon; dil=sin[t>=t.max()-2.0]; ap=dil.mean(0)
        c,n=duzlem(E)
        d_k=abs(float((ap-c)@n)); d_e=abs(float((el-c)@n))
        hata=float(np.linalg.norm(ap-el))
        sat.append((ad,S,hata,d_k,d_e))
        print('%-8s %-3s sinir %5d vx · 3B hata %5.2f mm · derinlik kes %5.2f / elle %5.2f · fark %+5.2f'%(ad,S,len(sin),hata,d_k,d_e,d_k-d_e))
ok=[x for x in sat if x[2] is not None]
H=np.array([x[2] for x in ok]); DM=np.array([abs(x[3]-x[4]) for x in ok])
fark=0; n7=0
for ad in SAHNE:
    r=[x for x in ok if x[0]==ad]
    if len(r)==2: n7+=1; fark+= abs(r[0][3]-r[1][3])>=0.5
print()
print('Olcut 1  apeks 3B hatasi ort  %.2f mm  (taban < 5,14)  -> %s'%(H.mean(),'GECTI' if H.mean()<5.14 else 'DUSTU'))
print('Olcut 2  derinlik MAE         %.2f mm  (taban < 1,72)  -> %s'%(DM.mean(),'GECTI' if DM.mean()<1.72 else 'DUSTU'))
print('Olcut 3  sag/sol farkli       %d/%d      (taban >= 6/7)  -> %s'%(fark,n7,'GECTI' if fark>=6 else 'DUSTU'))
print('Olcut 4  kapsama              %d/14     (taban >= 12)   -> %s'%(kapsama,'GECTI' if kapsama>=12 else 'DUSTU'))
json.dump(sat,open('/home/claude/an/out/apeks_0BM.json','w'),indent=1)
