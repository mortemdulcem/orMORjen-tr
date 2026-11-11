# -*- coding: utf-8 -*-
"""`0BH` kabul olcutleri Ö2/Ö4 sinavi: ayni olguda IKI cercevede landmark tespiti.

Her olgu icin olculenler:
  - cerceve sapmasi: dunya +z ile turetilen u ekseni ile ANATOMIK u arasindaki aci
    (her iki orbita, her yineleme turunun SONUNCUSU)
  - 14 noktanin yer degistirmesi (mm): maks ve ortalama
  - MSP sapmasi (ort/maks) her iki cercevede  -> Ö2
  - Ö4: cerceve sapmasi < 1 derece olan olgularda yer degistirme < 0,50 mm olmali

Kullanim:  python3 -I cerceve_sinav.py denek201 denek203 ...
Olcum hatti CAGRILMAZ; yalniz landmark tespiti kosar (hafif).
"""
import sys, os, json
import numpy as np
sys.path.insert(0, '/home/claude/an'); sys.path.insert(0, '/home/claude/orbita_hat')
import onisle, params

AD14 = None

def kaynak_bul(denek):
    n = denek.replace('denek', '')
    for p in ('/home/claude/gelen3/d%s/se' % n, '/home/claude/gelen/%s' % denek,
              '/home/claude/gelen2/d%s' % n):
        if os.path.isdir(p):
            return p
    return None

def tespit_et(ct, rows, org, cerceve):
    """Modulleri istenen cerceveyle TAZE yukle (modul duzeyi bayragi var)."""
    os.environ['ORBITA_CERCEVE'] = cerceve
    for m in ('landmark', 'otomasyon2'):
        sys.modules.pop(m, None)
    import landmark as L, otomasyon2 as O
    assert L._CERCEVE == cerceve, (L._CERCEVE, cerceve)
    ort, ra, apa, _ = O.atlas_yukle(None)
    try:
        msoa = json.load(open('/home/claude/an/out/mso_anatomik.json', encoding='utf-8'))
    except Exception:
        msoa = None
    lm, bil = L.tespit(ct, rows, org, ort, ra, apeks_atlas=apa, mso_anat=msoa)
    return lm, bil, L, O

def msp_sapma(lm, L):
    import olcum_zinciri as oz
    cm, nv = oz._msp(lm)
    s = [abs(float(((lm[b+'-r'] + lm[b+'-l'])/2 - cm) @ nv))
         for b in ('d','mf','mso','fmo','ek','o')]
    return float(np.mean(s)), float(max(s))

def cerceve_acisi(lm, bil, L):
    """Son egriden iki cerceveyi kurup u eksenleri arasindaki aciyi ver."""
    acilar = []
    for s, S in (('r','sag'), ('l','sol')):
        E = bil.get('egri', {}).get(S)
        if not isinstance(E, (list, tuple)) or len(E) < 10:
            continue
        E = np.asarray(E, float)
        mrk = np.asarray(lm['apex-'+s], float)
        _, _, u1, _ = L._duzlem_cerceve(E, mrk)
        _, _, u2, _ = L._duzlem_cerceve_anatomik(E, mrk, lm)
        acilar.append(float(np.degrees(np.arccos(np.clip(np.dot(u1, u2), -1, 1)))))
    return acilar

if __name__ == '__main__':
    print('%-10s %7s %8s %8s %8s %8s %8s  %s' %
          ('olgu','sapma°','yer_maks','yer_ort','MSP_esk','MSP_yen','Ö4','hukum'))
    satir = []
    for d in sys.argv[1:]:
        k = kaynak_bul(d)
        if k is None:
            print('%-10s KAYNAK YOK' % d); continue
        hacim, bilgi = onisle.dicom_hacim(k)
        ct = np.transpose(hacim, (2, 1, 0))
        org = np.array(bilgi['origin'], float)
        rows = np.diag([bilgi['PixelSpacing'][0], bilgi['PixelSpacing'][1],
                        bilgi['kesit_araligi']])
        lmA, bilA, LA, _ = tespit_et(ct, rows, org, 'dunya_z')
        if lmA is None:
            print('%-10s ESKI CERCEVEDE TESPIT YOK' % d); continue
        lmB, bilB, LB, _ = tespit_et(ct, rows, org, 'anatomik')
        if lmB is None:
            print('%-10s >>> Ö1 DUSTU: yeni cercevede tespit YOK' % d)
            satir.append((d, None)); continue
        ad = [k2 for k2 in lmA if k2 in lmB]
        far = np.array([np.linalg.norm(np.asarray(lmA[k2], float) - np.asarray(lmB[k2], float))
                        for k2 in ad])
        aci = cerceve_acisi(lmA, bilA, LA)
        a_ort = float(np.mean(aci)) if aci else float('nan')
        mA = msp_sapma(lmA, LA); mB = msp_sapma(lmB, LB)
        o4 = '-' if a_ort >= 1.0 else ('GECTI' if far.max() < 0.50 else 'DUSTU')
        print('%-10s %7.2f %8.3f %8.3f %8.2f %8.2f %8s  %s'
              % (d, a_ort, far.max(), far.mean(), mA[0], mB[0], o4,
                 'MSP %s' % ('iyilesti' if mB[0] < mA[0] else 'kotulesti' if mB[0] > mA[0] else 'ayni')),
              flush=True)
        satir.append((d, dict(sapma=a_ort, yer_maks=float(far.max()), yer_ort=float(far.mean()),
                              msp_eski=mA[0], msp_yeni=mB[0])))
    json.dump(satir, open('/home/claude/an/out/cerceve_sinav.json','w'),
              ensure_ascii=False, indent=1)
    print('\nyazildi: out/cerceve_sinav.json')
