# -*- coding: utf-8 -*-
"""ON SINIR CAKISMASI — tez metni YELPAZE YUZEYI yaziyor, kod SVD DUZLEMI uyguluyor.

`gerec-yontem-tasarim-kararlari.md`: "On sinir: orbita kenari landmarklari + AGIRLIK
MERKEZI ile kurulan apertur duzlemi (Jansen; gozlemciler arasi ICC 0,992)."
Jansen ve ark. 2016 (Int J CARS 11:11-18, §1a) bunu soyle tarif ediyor:
  "From these indicated landmarks, a surface was reconstructed connecting all landmarks
   AS WELL AS THE CENTER OF GRAVITY of these landmarks, creating the anterior plane."
Yani on sinir, rim noktalarini agirlik merkezine baglayan UCGEN YELPAZEDIR; kenarin
gercek 3B kivrimini IZLER.

Bizim kodumuz (`params.plane`) egriye SVD ile DUZLEM uyduruyor; agirlik merkezini
yalnizca duzlem uzerindeki bir nokta olarak kullaniyor. Kenarimiz duzlemsel DEGIL:
kayitli duzlem disi sapma 2,71-4,84 mm (atlas, olcum degerleri tablosu).

BU BETIK FARKI OLCER. Hangisinin DOGRU oldugunu soylemez — onu arastirmaci karar verir;
ama "ne kadar fark eder" sorusunu sayiya cevirir.

YONTEM (yelpaze ile kirpma): c = rim noktalarinin agirlik merkezi, n = SVD normali,
u,v duzlem ici eksenler. Her voksel icin aci t = atan2((x-c)·v, (x-c)·u); t'nin dustugu
sektorun ucgeni (c, P_i, P_i+1) bulunur; voksel O UCGENIN duzlemine gore onde mi arkada mi
diye bakilir. Duzlemle kirpmada ise tek bir duzlem kullanilir.
"""
import sys, json, os
sys.path.insert(0, '/home/claude/an'); sys.path.insert(0, '/home/claude/orbita_hat')
import numpy as np
import params, onisle

OLG = {
    'hasta15': ('/home/claude/an/out/h15_el_maske.npy',
                '/home/claude/h15m/ham/hasta15 düzeltme', '/home/claude/h15d_2/ham',
                'oto_rim_sag', 'oto_rim_sol'),
    'hasta16': ('/home/claude/an/out/h16_el_maske2.npy',
                '/home/claude/h16m/ham/hasta16 ototmatik ölçüm düzeltmesi', '/home/claude/h16d/ham',
                'oto_rim_sag', 'oto_rim_sol'),
}


def cerceve(P):
    """Rim noktalarindan c (agirlik merkezi), n (SVD normali), u, v."""
    c = P.mean(axis=0)
    _, _, Vt = np.linalg.svd(P - c)
    n = Vt[2]
    u = Vt[0]
    v = np.cross(n, u)
    return c, n, u, v


def duzlem_mesafe(X, c, n):
    """Her vokselin duzleme ISARETLI uzakligi (+ = normal yonunde)."""
    return (X - c) @ n


def yelpaze_mesafe(X, P, c, n, u, v):
    """Her vokselin, kendi acisal sektorune karsilik gelen UCGENE isaretli uzakligi."""
    d = X - c
    t = np.arctan2(d @ v, d @ u)                       # voksel acilari
    dp = P - c
    tp = np.arctan2(dp @ v, dp @ u)                    # rim nokta acilari
    sira = np.argsort(tp)
    Ps, tps = P[sira], tp[sira]
    m = len(Ps)
    # her voksel hangi sektorde: tps[i] <= t < tps[i+1]  (dairesel)
    i = np.searchsorted(tps, t, side='right') - 1      # -1 ... m-1
    i = np.mod(i, m)
    j = np.mod(i + 1, m)
    A, B = Ps[i], Ps[j]                                 # sektorun iki rim noktasi
    nn = np.cross(A - c, B - c)                         # ucgen (c, A, B) normali
    boy = np.linalg.norm(nn, axis=1, keepdims=True)
    boy[boy == 0] = 1.0
    nn = nn / boy
    isaret = np.sign(nn @ n)                            # hepsini global normalle ayni yone cevir
    isaret[isaret == 0] = 1.0
    nn = nn * isaret[:, None]
    return np.einsum('ij,ij->i', X - c, nn)


def main():
    rapor = {}
    for ad, (mp, sahne, dc, ks, kl) in OLG.items():
        if not os.path.isdir(dc):
            print('%s ATLA (DICOM yok)' % ad); continue
        F = np.load(mp)
        _, egri = params.load_scene(sahne)
        h, b = onisle.dicom_hacim(dc)
        ct_sekil = np.transpose(h, (2, 1, 0)).shape
        org = np.array(b['origin'], float)
        rows = np.diag([b['PixelSpacing'][0], b['PixelSpacing'][1], b['kesit_araligi']])
        vox = abs(float(np.linalg.det(rows)))
        print('=' * 76)
        print('%s — arastirmaci ONAYLI maske, arastirmaci duzeltilmis rim egrisi' % ad)
        rapor[ad] = {}
        for et, tar, k in ((1, 'sag', ks), (2, 'sol', kl)):
            M = (F == et)
            P = np.asarray(egri[k], float)
            c, n, u, v = cerceve(P)
            # maskenin voksel merkezleri -> RAS
            # DIKKAT (bu betikte BIR KEZ HATA YAPILDI, atlas §G): onisle'nin dondurdugu
            # `org` LPS'tir, params.load_scene'in egrisi RAS'tir. Cevrilmezse maske ile
            # egri x ve y'de AYNALI olur (x[-70,-32] ile x[+34,+71]) ve hicbir voksel
            # kirpilmaz — sessiz bir "fark yok" sonucu verir.
            idx = np.array(np.nonzero(M)).T
            X = (idx @ rows + org) * np.array([-1., -1., 1.])     # LPS -> RAS
            assert np.linalg.norm(X.mean(axis=0) - P.mean(axis=0)) < 60.0, \
                'maske ile egri ayni uzayda degil — koordinat konvansiyonunu denetle'
            # normalin yonu: kavitenin TERSINE bakmali (apeks arkada)
            if duzlem_mesafe(X, c, n).mean() > 0:
                n = -n; v = -v
            dd = duzlem_mesafe(X, c, n)
            dy = yelpaze_mesafe(X, P, c, n, u, v)
            ham = M.sum() * vox / 1000.
            sat = {'ham': round(ham, 3), 'duzlemsizlik_mm': round(float(np.abs(
                duzlem_mesafe(P, c, n)).max()), 2)}
            print('  %s — ham %.3f cm3 · rim noktalarinin duzlemden en buyuk sapmasi %.2f mm'
                  % (tar, ham, sat['duzlemsizlik_mm']))
            for kay in (0.0, 1.0):
                kd = (dd <= kay).sum() * vox / 1000.       # DUZLEM ile kirpilmis
                ky = (dy <= kay).sum() * vox / 1000.       # YELPAZE ile kirpilmis
                sat['duzlem_%+.0f' % kay] = round(kd, 3)
                sat['yelpaze_%+.0f' % kay] = round(ky, 3)
                sat['fark_%+.0f' % kay] = round(ky - kd, 3)
                print('      kaydirma %+0.0f mm:  DUZLEM %7.3f  ·  YELPAZE %7.3f  ·  fark %+6.3f cm3 (%+.2f%%)'
                      % (kay, kd, ky, ky - kd, 100 * (ky - kd) / kd if kd else 0))
            rapor[ad][tar] = sat
    json.dump(rapor, open('/home/claude/an/out/on_sinir.json', 'w'), ensure_ascii=False, indent=1)
    print('\nyazildi: out/on_sinir.json')


if __name__ == '__main__':
    main()
