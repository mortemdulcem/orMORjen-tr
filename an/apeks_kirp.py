# 0BM: TotalSegmentator'i yalniz orbita+optik kanal bolgesinde kostur (bellek siniri).
# Kirpma kutusu hastanin KENDI landmarklarindan: 14 nokta + 20 mm pay (arkaya 35 mm).
# Kirpma yalniz ROI'dir, apeks tanimini degistirmez (0BM §2).
import sys, json, glob, numpy as np, SimpleITK as sitk
sys.path.insert(0,'/home/claude/an')
h=sys.argv[1]; ad='hasta'+h[1:]
img=sitk.ReadImage('/home/claude/atlas_nii/%s/%s.nii.gz'%(h,h))
R=json.load(open('/home/claude/orbita_hat/raporlar/%s_OTO.json'%ad))
P=np.array([v for k,v in R['landmark']['nokta'].items() if not k.startswith('apex')],float)  # RAS
L=P*np.array([-1,-1,1])  # LPS (SimpleITK fiziksel)
lo=L.min(0)-20; hi=L.max(0)+20
# arka yon: LPS'de +y posterior
hi[1]+=35
i0=np.array(img.TransformPhysicalPointToIndex(lo.tolist())); i1=np.array(img.TransformPhysicalPointToIndex(hi.tolist()))
a=np.minimum(i0,i1); b=np.maximum(i0,i1)
sz=np.array(img.GetSize()); a=np.clip(a,0,sz-1); b=np.clip(b,0,sz-1)
c=sitk.RegionOfInterest(img,(b-a+1).tolist(),a.tolist())
sitk.WriteImage(c,'/home/claude/apeks_ts/%s_kirp.nii.gz'%h)
print(h,'kirpildi',img.GetSize(),'->',c.GetSize())
