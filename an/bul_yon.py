# -*- coding: utf-8 -*-
"""ORBITA BULUCU — YÖN ÖLÇÜTÜ BAŞIN DURUŞUNDAN BAĞIMSIZ HALE GETİRİLDİ.

SORUN (`0BE` ön kaydı, denek211'de ölçüldü): `bul.orbita_bul` bir adayı orbita
saymak için apertür normalinin ÖNE bakan bileşeninin 0,45'ten büyük olmasını
istiyor:

    if nrm[1] <= 0.45:        # A bileseni; one bakmayanlari at

`nrm[1]` TARAYICI eksenine göre ölçülür. Hastanın başı yatıksa (çene aşağı/
yukarı) orbital apertür normali kısmen yukarı/aşağı bakar, A bileşeni eşiğin
altına düşer ve ORBITA ELENİR. Orbita görüntüde vardır; reddedilen şey yönüdür.

DÜZELTME: "öne bakıyor mu" yerine "KAFANIN DIŞINA bakıyor mu". Orbitalar her
zaman beyinden dışarı açılır; bu ölçüt başın duruşundan bağımsızdır ve
tarayıcı eksenine hiç bakmaz.

    disa = nrm · birim(p - kafa_merkezi)   >= DISA_ESIK

NE DEĞİŞMEZ: bu ölçüt yalnız HANGİ ADAYIN orbita olduğuna karar verir.
Landmarkların nereye konduğuna karışmaz (`landmark._duzlem_cerceve` ayrı ve
DOKUNULMADI). Dolayısıyla, düzeltilmiş bulucu zaten ölçülmüş olgularda AYNI
orbitayı seçiyorsa, hiçbir ölçüm değeri oynamaz — ve bu SINANABİLİR.

DISA_ESIK nasıl seçildi: 0,45 — özgün koddaki sayının AYNISI. Yeni bir eşik
uydurulmadı; yalnız hangi eksende ölçüldüğü değişti.
"""
import sys
import numpy as np
from scipy import ndimage as ndi

sys.path.insert(0, '/home/claude/an')
import bul                                                    # noqa: E402

DISA_ESIK = 0.45          # ozgun koddaki sayinin AYNISI


def kafa_merkezi(ct, rows, org):
    """Kafanin agirlik merkezi (RAS). Yumusak doku + kemik."""
    kafa = ct > -500
    lab, n = ndi.label(ndi.binary_closing(kafa, ndi.generate_binary_structure(3, 1),
                                          iterations=2))
    if n > 1:
        boy = ndi.sum(np.ones_like(lab), lab, range(1, n + 1))
        kafa = (lab == (1 + int(np.argmax(boy))))
    idx = np.array(ndi.center_of_mass(kafa), float)
    return ((rows.T @ idx.reshape(3, 1)).T[0] + org) * np.array([-1., -1., 1.])


def yon_olcutu(p, nrm, merkez):
    """Apertur normali kafanin DISINA mi bakiyor? Donmeye duyarsiz."""
    d = np.asarray(p, float) - np.asarray(merkez, float)
    nd = np.linalg.norm(d)
    if nd < 1e-9:
        return -1.0
    return float(np.dot(np.asarray(nrm, float), d / nd))


def karsilastir(ct, rows, org, ayrinti=True):
    """Iki olcutu YAN YANA kosar; hicbir sey degistirmez, yalniz raporlar."""
    sp = np.array([abs(rows[0, 0]), abs(rows[1, 1]), abs(rows[2, 2])], float)
    merkez = kafa_merkezi(ct, rows, org)
    # bul.py'nin aday uretimini aynen tekrarla
    bone = ct >= bul.KEMIK
    kafa = ct > -500
    lab, n = ndi.label(ndi.binary_closing(kafa, ndi.generate_binary_structure(3, 1),
                                          iterations=2))
    if n > 1:
        boy = ndi.sum(np.ones_like(lab), lab, range(1, n + 1))
        kafa = (lab == (1 + int(np.argmax(boy))))
    kafa = ndi.binary_fill_holes(kafa)
    from scipy.ndimage import distance_transform_edt as edt
    yum = kafa & (~bone) & (ct > -200)
    D = edt(yum, sampling=sp)
    aday = (D > 9.0) & (D < 20.0)
    mx = ndi.maximum_filter(D, size=(9, 9, 5))
    tepe = aday & (D >= mx - 1e-6)
    idx = np.argwhere(tepe); dv = D[tepe]
    srt = np.argsort(dv)[::-1][:600]
    idx, dv = idx[srt], dv[srt]
    ras = ((rows.T @ idx.astype(float).T).T + org) * np.array([-1., -1., 1.])
    tut = []
    for p, d in zip(ras, dv):
        if all(np.linalg.norm(p - q[0]) > 14.0 for q in tut):
            tut.append((p, float(d)))
        if len(tut) >= 60:
            break
    eski, yeni = [], []
    for p, d in tut:
        oran, nrm, _ = bul.aciklik(ct, rows, org, p)
        if nrm is None or not (0.02 <= oran <= 0.45):
            continue
        a_eski = float(nrm[1])
        a_yeni = yon_olcutu(p, nrm, merkez)
        if a_eski > 0.45:
            eski.append((p, d, a_eski, a_yeni))
        if a_yeni >= DISA_ESIK:
            yeni.append((p, d, a_eski, a_yeni))
    if ayrinti:
        print('   kafa merkezi RAS %s' % np.round(merkez, 1).tolist())
        print('   aday tepe %d · ESKI olcutu gecen %d · YENI olcutu gecen %d'
              % (len(tut), len(eski), len(yeni)))
        for et, lst in (('ESKI', eski), ('YENI', yeni)):
            for p, d, ae, ay in sorted(lst, key=lambda t: -t[1])[:6]:
                print('     %s  RAS %-22s D=%5.2f  one=%.2f  disa=%.2f'
                      % (et, np.round(p, 1).tolist(), d, ae, ay))
    return eski, yeni, merkez
