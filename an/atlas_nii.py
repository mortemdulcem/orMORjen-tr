# -*- coding: utf-8 -*-
"""Atlas olgularinin BT hacimlerini ALI icin .nii.gz'ye cevirir (`0BJ` §4.2).

Kaynak karisik: bazi olgular DICOM serisi, bazilari Slicer sahnesi icinde .nrrd.
Ikisi de SimpleITK ile okunur. HICBIR yeniden ornekleme yapilmaz — ALI kendi
on islemesini yapar; burada yalniz bicim degisir.
Olgu basina AYRI dizin (ALI skill §5: ayni dizinde birden cok tarama zaman asimi verdi).
"""
import os, glob, sys
import SimpleITK as sitk

KOK = '/home/claude/atlas_bt'
CIK = '/home/claude/atlas_nii'

def oku(dizin):
    nrrd = sorted(glob.glob(os.path.join(dizin, '**', '*.nrrd'), recursive=True))
    if nrrd:
        buyuk = max(nrrd, key=os.path.getsize)
        return sitk.ReadImage(buyuk), 'nrrd:%s' % os.path.basename(buyuk)
    for kok, _, dosya in os.walk(dizin):
        dcm = [f for f in dosya if f.lower().endswith('.dcm')]
        if len(dcm) >= 50:
            r = sitk.ImageSeriesReader()
            ids = r.GetGDCMSeriesIDs(kok)
            if not ids:
                continue
            en = max(ids, key=lambda i: len(r.GetGDCMSeriesFileNames(kok, i)))
            r.SetFileNames(r.GetGDCMSeriesFileNames(kok, en))
            return r.Execute(), 'dicom:%d kesit' % len(r.GetFileNames())
    return None, 'kaynak bulunamadi'

if __name__ == '__main__':
    os.makedirs(CIK, exist_ok=True)
    for h in sorted(os.listdir(KOK)):
        d = os.path.join(KOK, h)
        if not os.path.isdir(d):
            continue
        hedef_d = os.path.join(CIK, h)
        os.makedirs(hedef_d, exist_ok=True)
        hedef = os.path.join(hedef_d, '%s.nii.gz' % h)
        if os.path.exists(hedef):
            print('%-5s zaten var' % h, flush=True); continue
        img, kaynak = oku(d)
        if img is None:
            print('%-5s ATLANDI (%s)' % (h, kaynak), flush=True); continue
        sitk.WriteImage(img, hedef)
        print('%-5s %s · boyut %s · aralik %s -> %s (%.0f MB)'
              % (h, kaynak, img.GetSize(), tuple(round(x,3) for x in img.GetSpacing()),
                 os.path.basename(hedef), os.path.getsize(hedef)/1e6), flush=True)
