# -*- coding: utf-8 -*-
"""TAM OTOMATIK OLCUM — girdi YALNIZ ham DICOM klasorudur.

    python3 -I orbita_hat/otomasyon2.py <dicom_klasoru> <kimlik> [--disla hastaN]

Hicbir landmark, maske ya da egri verilmez. Zincir:
 1. ALIM      DICOM -> HU hacmi; gecerlilik ve geometri kapilari
 2. KIMLIK    BT parmak izi (boyut + spacing + origin + ORTA KESIT HU OZETI)
 3. ATLAS     sekil / rim / apeks atlasi yuklenir; --disla verilirse o olgu CIKARILIR (LOO)
 4. LANDMARK  orbita bulma + 14 nokta (an/landmark.tespit)
 5. RIM       apertur kenar egrisi (otomatik)
 6. MASKE     isin yontemiyle kavite (otomatik egri on sinir olarak)
 7. OLCUM     43 parametre (olcum_zinciri, n=12 altigen katsayilari)
 8. DENETIM   00 §6 kapilari + Slicer .mrk.json ciktisi + rapor

4b. ADIM (medial iyilestirme) 2026-10-20'de VARSAYILAN ACIK yapildi. LOO karnesi:
`d`/`mf` hatasi 3,44 -> **2,37 mm** (en kotu 6,71 -> 4,64) · IOD hatasi %12,87 -> **%3,97**
(en kotu %30,24 -> %12,41) · OW %5,41 -> **%3,99** · OH, apertur alani ve hacim DEGISMEDI.
Kapatmak icin: --medial yok. Ayrinti 07 §7e.

Eski `otomasyon.py` 3. adimda DURUYORDU ("landmark yerlestirme otomatiklestirilmedi,
atlas aktarimi reddedildi: OH hatasi -22 mm"). O gerekce 2026-10-14'te gecersiz kaldi:
atlas tabanli hat gozlemcinin kendi tekrar isaretleme bandinda (3,23-3,67 mm).
"""
from __future__ import annotations
import os, sys, json, glob, hashlib, argparse, datetime
import numpy as np

sys.path.insert(0, "/home/claude/an")
sys.path.insert(0, "/home/claude/orbita_hat")
import params, rayseg, rimcurve, landmark as L, mrk        # noqa: E402
import olcum_zinciri as oz                                 # noqa: E402
import kalinlik_bolgesel as kb                             # noqa: E402
import onisle                                              # noqa: E402

KOK = "/home/claude/orbita_hat"
AN = "/home/claude/an"
# Sablonlar arasi yayilim esigi (UYARI).
# DIKKAT — BU BIR BELIRSIZLIK OLCUSU DEGILDIR. LOO'da yayilim ile gercek hata
# arasindaki korelasyon NEGATIF cikti (varyant A r=-0,365 · varyant B r=-0,126),
# yani yayilim hatayi ONGORMUYOR. Esik de kalibre degildir (§0.12) ve LOO'da
# hic ateslenmedi (gozlenen en buyuk yayilim 2,78 mm). Burada yalnizca KABA bir
# felaket sigortasi olarak duruyor: sablonlar birbirini hic tutmazsa haber verir.
# Guven araligi gibi YORUMLANMAZ (07 §7e).
MEDIAL_YAYILIM_UYARI = 3.0
ORD, AD = L.ORD, L.AD
# atlas havuzu: sekil modeli bu olgulardan kurulur
ATLAS_OLGU = [("hasta7", "/home/claude/h7/ham/ölçüm1"),
              ("hasta8", "/home/claude/h8m/ham/ölçüm2"),
              ("hasta9", "/home/claude/h9m/ham/ölçüm5"),
              ("hasta10", "/home/claude/h10m/ham/ölçüm4"),
              ("hasta11", "/home/claude/h11m3/ham/ölçüm3")]
# bilinen BT parmak izleri (§6.1) — kimlik denetimi icin
PARMAK = os.path.join(KOK, "bt_parmak_izi.json")


def _log(adim, m):
    print("[%s] %s" % (adim, m), flush=True)


def parmak_izi(ct, org, rows, bilgi):
    """§6.1: boyut + spacing + origin + ORTA KESITIN HU matrisinin ozeti."""
    z = ct.shape[2] // 2
    orta = np.ascontiguousarray(ct[:, :, z].astype(np.int16))
    return {
        "boyut": list(ct.shape),
        "spacing": [round(float(x), 6) for x in np.diag(rows)],
        "origin": [round(float(x), 3) for x in org],
        "orta_kesit_ozeti": hashlib.sha256(orta.tobytes()).hexdigest()[:16],
        "orta_kesit_ort": round(float(orta.mean()), 2),
        "StudyUID_ozet": bilgi.get("StudyUID_ozet"),
        "SeriesUID_ozet": bilgi.get("SeriesUID_ozet"),
    }


def kimlik_denetimi(pi, kimlik):
    """Parmak izini bilinenlerle karsilastirir; yeni ise dosyaya ekler."""
    db = json.load(open(PARMAK, encoding="utf-8")) if os.path.exists(PARMAK) else {}
    for ad, e in db.items():
        if ad == kimlik:
            continue
        if e.get("orta_kesit_ozeti") == pi["orta_kesit_ozeti"]:
            return {"mukerrer": ad, "olcut": "orta kesit HU ozeti BIREBIR AYNI",
                    "uyari": "AYNI TARAMA daha once '%s' kimligiyle islenmis." % ad}
        if (e.get("boyut") == pi["boyut"] and e.get("spacing") == pi["spacing"]
                and e.get("origin") == pi["origin"]):
            return {"mukerrer": ad, "olcut": "boyut+spacing+origin ayni, HU ozeti farkli",
                    "uyari": "Ayni geometri '%s' ile ortusuyor ama goruntu farkli — "
                             "ayni hastanin baska serisi olabilir." % ad}
    benzer = [ad for ad, e in db.items()
              if ad != kimlik and e.get("boyut") == pi["boyut"]]
    db[kimlik] = pi
    json.dump(db, open(PARMAK, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return {"mukerrer": None, "ayni_boyut": benzer}


def atlas_yukle(disla=None):
    RA = json.load(open(os.path.join(AN, "out/rimatlas.json"), encoding="utf-8"))
    AA = json.load(open(os.path.join(AN, "out/apeks_atlas.json"), encoding="utf-8"))
    sek, kullanilan = [], []
    for ad, F in ATLAS_OLGU:
        if disla and ad == disla:
            continue
        la, _ = params.load_scene(F)
        for a, b in (("fso-r", "mso-r"), ("fso-l", "mso-l")):
            if a in la and b not in la:
                la[b] = la[a]
        sek.append(np.array([np.asarray(la[k], float) for k in AD]))
        kullanilan.append(ad)
    ra = {}
    for b in ORD:
        aa, rr = [], []
        for k, v in RA["olgu"].items():
            if (disla and k.startswith(disla + "_")) or b not in v:
                continue
            aa.append(v[b][0]); rr.append(v[b][1])
        aa = np.array(aa, float)
        if aa.max() - aa.min() > 180:
            aa = np.where(aa < 0, aa + 360, aa)
        m = float(aa.mean())
        ra[b] = dict(aci=(m - 360 if m > 180 else m), r=float(np.mean(rr)))
    av = [x for k, x in AA.items() if not (disla and k.startswith(disla + "_"))]
    apa = {k: float(np.mean([x[k] for x in av])) for k in ("t", "dik", "yan")}
    return L.gpa(sek), ra, apa, kullanilan


def _yuzeye_izdusur(ct, rows, org, p, kemik=150.0, kup_mm=12.0):
    """Noktayi 150 HU kemik yuzeyine izdusur ve BIR VOKSEL DISARI cek.

    Doner: (yeni_nokta, onceki_isaretli_uzaklik, yeni_isaretli_uzaklik).
    Isaretli uzaklik: + = kemigin ICINDE, - = disinda (atlas §BL ile ayni tanim).
    Nokta zaten disaridaysa (<= 0) DOKUNULMAZ — yalniz kemige gomulmus noktalar
    duzeltilir.

    KOORDINAT: `org` LPS'tir, `p` RAS'tir. Cevirmeden indekslemek bu oturumda
    UC KEZ hata verdi (atlas §G) — bu yuzden donusum burada acikca yapilir.
    """
    from scipy import ndimage as ndi
    LPS = np.array([-1., -1., 1.])
    sp = np.array([rows[0, 0], rows[1, 1], rows[2, 2]], float)
    i0 = np.linalg.solve(rows.T, (p * LPS - org))
    ic = np.rint(i0).astype(int)
    r = np.ceil(kup_mm / sp).astype(int)
    sl = tuple(slice(max(0, ic[k] - r[k]), min(ct.shape[k], ic[k] + r[k] + 1)) for k in range(3))
    blok = ct[sl] >= kemik
    if blok.all() or not blok.any():
        return None, float('nan'), float('nan')
    din = ndi.distance_transform_edt(blok, sampling=sp)
    dout = ndi.distance_transform_edt(~blok, sampling=sp)
    j = tuple(int(round(i0[k])) - sl[k].start for k in range(3))
    if not all(0 <= j[k] < blok.shape[k] for k in range(3)):
        return None, float('nan'), float('nan')
    d0 = float(din[j] - dout[j])
    if d0 <= 0.0:
        return None, d0, d0          # zaten disarida — dokunma
    # kemigin icinde: en yakin DISARI vokseli bul, bir voksel disari cek
    hedef = ~blok
    ind = ndi.distance_transform_edt(blok, sampling=sp, return_distances=False,
                                     return_indices=True)
    # EN YAKIN DIS VOKSEL. Fazladan itme YOK: bu voksel zaten kemigin bir voksel
    # disindadir, yani arastirmacinin elle `mf` bandinin (-0,88 ... -0,49 mm,
    # SS 0,11) tam karsiligi. Bir ilk surumde fazladan bir adim itiliyordu ve
    # hasta16 sagda -1,36 mm'ye tasiyordu (2,6 voksel) — kaldirildi.
    q = np.array([ind[k][j] for k in range(3)], float)
    yeni_i = q + np.array([sl[k].start for k in range(3)], float)
    yeni = (rows.T @ yeni_i + org) * LPS
    # yeni uzakligi dogrula
    i1 = np.linalg.solve(rows.T, (yeni * LPS - org))
    j1 = tuple(int(round(i1[k])) - sl[k].start for k in range(3))
    d1 = (float(din[j1] - dout[j1])
          if all(0 <= j1[k] < blok.shape[k] for k in range(3)) else float('nan'))
    return yeni, d0, d1


def medial_iyilestir(ct, rows, org, lm, disla=None, ds=4, ayrinti=False):
    """ISTEGE BAGLI 4b. ADIM — `d` ve `mf`'yi sablon hizalamasiyla (NICP) duzelt.

    YALNIZ bu dort noktaya dokunur: d-r, d-l, mf-r, mf-l. Diger 10 nokta ve
    butun ara degerler aynen kalir, boylece dogrulanmis sonuclar degismez.
    On hizalama hedefin `d`/`mf`'sini KULLANMAZ — yalniz hattin kestirdigi 12
    medial-olmayan noktayi kullanir (an/medial.py).

    Donus: (yeni_lm, bilgi). Basarisiz olursa lm'yi DEGISTIRMEDEN dondurur.
    ETKI: IOD_d ve IOD_mf bu noktalardan hesaplanir; kalinlik ekseni de altigen
    ortalamasini kullandigi icin cok az oynar. Apertur alani/cevresi EGRIDEN
    geldigi icin DEGISMEZ.
    """
    sys.path.insert(0, AN)
    import sablon as SB, medial as MD, yuzey as YZ
    try:
        kut = SB.kutuphane(ds=ds, disla=disla, ayrinti=False)
        v, _f = YZ.hazirla(ct, rows, org, lm, AD, ds=ds)
        hiza = {k: np.asarray(lm[k], float) for k in MD.HIZA_NOKTA if k in lm}
        yeni, b = MD.kestir(v, hiza, kut, ayrinti=ayrinti)
    except Exception as e:
        return lm, {'sonuc': 'HATA', 'mesaj': str(e)[:200]}
    out = dict(lm)
    oynama = {}
    for k in MD.HEDEF_NOKTA:
        if yeni.get(k) is None:
            continue
        oynama[k] = round(float(np.linalg.norm(np.asarray(lm[k], float) - yeni[k])), 2)
        out[k] = yeni[k]
    # --- 4c) YUZEYE IZDUSUM (2026-10-23) ------------------------------------
    # OLCULMUS KUSUR: NICP'nin `mf` ciktisi kemigin ICINDE kaliyor. hasta16'da
    # +1,25 / +0,53 mm derinde, HU 1041 / 454 — arastirmacinin elle bandi 25-163 HU.
    # ANATOMIK OLCUT (arastirmacinin 10 elle `mf` noktasindan, SS 0,11 mm):
    #   `mf` kemik yuzeyinin TAM BIR VOKSEL DISINDADIR (-0,88 ... -0,49 mm).
    #   Degerler olgunun voksel boyutuna birebir esit — atlas §BL.
    # Bu bir test kumesine uydurma DEGILDIR: olcut anatomiktir (`mf` orbita
    # kenarinda, frontomaksiller sutur uzerinde bir YUZEY noktasidir; kemik
    # govdesinin icinde olamaz).
    # `d` icin UYGULANMAZ: ayni olcut `d`de ayirt etmiyor (elle `d` noktalari
    # sinirin iki yanina dagiliyor, -2,0 ... +1,4 voksel; atlas §BL).
    izdusum = {}
    for k in ('mf-r', 'mf-l'):
        if k not in out:
            continue
        try:
            p2, d0, d1 = _yuzeye_izdusur(ct, rows, org, np.asarray(out[k], float))
        except Exception:
            continue
        if p2 is None:
            continue
        izdusum[k] = {'once_mm': round(d0, 2), 'sonra_mm': round(d1, 2),
                      'kayma_mm': round(float(np.linalg.norm(p2 - out[k])), 2)}
        out[k] = p2
    if izdusum:
        b['yuzey_izdusum'] = izdusum
    return out, {'sonuc': 'TAMAM', 'sablon_sayisi': b['sablon_sayisi'],
                 'yuzey_izdusum': izdusum,
                 'yayilim_mm': b['yayilim'], 'oynama_mm': oynama,
                 'hedef_nokta': list(MD.HEDEF_NOKTA), 'ds': ds,
                 'onceki': {k: [round(float(x), 3) for x in np.asarray(lm[k], float)]
                            for k in MD.HEDEF_NOKTA}}


def calistir(kaynak, kimlik, disla=None, kok=KOK, cikti_mrk=True, medial="nicp"):
    t0 = datetime.datetime.now()
    rapor = {"kimlik": kimlik, "kaynak": kaynak, "disla": disla,
             "baslangic": t0.isoformat(timespec="seconds"), "adimlar": []}

    # --- 1) ALIM
    _log("1/8 ALIM", "DICOM okunuyor: %s" % kaynak)
    hacim, bilgi = onisle.dicom_hacim(kaynak)
    ct = np.transpose(hacim, (2, 1, 0))
    org = np.array(bilgi["origin"], float)
    rows = np.diag([bilgi["PixelSpacing"][0], bilgi["PixelSpacing"][1],
                    bilgi["kesit_araligi"]])
    vox = abs(float(np.linalg.det(rows)))
    hu_ok = bool(ct.min() <= -900 and ct.max() >= 1000)
    rapor["bt"] = bilgi
    rapor["bt"]["HU_aralik"] = [int(ct.min()), int(ct.max())]
    rapor["bt"]["voksel_mm3"] = round(vox, 5)
    _log("1/8 ALIM", "%d kesit %s · voksel %.5f mm3 · anizotropi %s · HU %d..%d %s"
         % (bilgi["kesit"], ct.shape, vox, bilgi["anizotropi"], ct.min(), ct.max(),
            "GECERLI" if hu_ok else "KAPI RED"))
    rapor["adimlar"].append({"adim": "alim", "sonuc": "TAMAM" if hu_ok else "RED",
                             "HU_gecerli": hu_ok})
    if not hu_ok:
        raise SystemExit("DURDU: HU gecerlilik kapisi")

    # --- 2) KIMLIK
    pi = parmak_izi(ct, org, rows, bilgi)
    kd = kimlik_denetimi(pi, kimlik)
    rapor["parmak_izi"] = pi
    rapor["kimlik_denetimi"] = kd
    if kd.get("mukerrer"):
        _log("2/8 KIMLIK", "UYARI: %s (%s)" % (kd["uyari"], kd["olcut"]))
    else:
        _log("2/8 KIMLIK", "parmak izi YENI · ayni boyutta olgu: %s"
             % (kd.get("ayni_boyut") or "yok"))

    # --- 3) ATLAS
    ort, ra, apa, kull = atlas_yukle(disla)
    _log("3/8 ATLAS", "sekil modeli %d olgudan: %s%s"
         % (len(kull), ", ".join(kull), "  (%s DISLANDI)" % disla if disla else ""))
    rapor["atlas"] = {"olgular": kull, "disla": disla, "apeks": {k: round(v, 3)
                                                                 for k, v in apa.items()}}

    # --- 4) LANDMARK (orbita bulma dahil)
    _log("4/8 LANDMARK", "orbita bulma + 14 nokta")
    lm, bil = L.tespit(ct, rows, org, ort, ra, apeks_atlas=apa)
    if lm is None:
        rapor["adimlar"].append({"adim": "landmark", "sonuc": "RED", "hata": bil})
        json.dump(rapor, open(os.path.join(kok, "raporlar", "%s_OTO.json" % kimlik), "w",
                              encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
        raise SystemExit("DURDU: landmark tespiti basarisiz: %s" % bil)
    cm, nv = oz._msp(lm)
    sap = [abs(float(((lm[b + "-r"] + lm[b + "-l"]) / 2 - cm) @ nv)) for b in ORD]
    msoo = {}
    for s, S in (("r", "sag"), ("l", "sol")):
        v = np.asarray(lm["o-" + s], float) - np.asarray(lm["mso-" + s], float)
        msoo[S] = round(float(np.linalg.norm(v) - abs(v[2])), 2)
    _log("4/8 LANDMARK", "14 nokta · MSP ort %.2f maks %.2f mm · mso-o %s / %s mm"
         % (np.mean(sap), max(sap), msoo["sag"], msoo["sol"]))
    rapor["landmark"] = {"msp_ort": round(float(np.mean(sap)), 2),
                         "msp_maks": round(float(max(sap)), 2), "mso_o": msoo,
                         "olcut_msp": bool(np.mean(sap) <= 1.0),
                         "olcut_mso_o": bool(all(v <= 2.0 for v in msoo.values())),
                         "nokta": {k: [round(float(x), 3) for x in np.asarray(lm[k], float)]
                                   for k in AD}}
    rapor["adimlar"].append({"adim": "landmark", "sonuc": "TAMAM"})

    # --- 4b) ISTEGE BAGLI: medial iyilestirme (d, mf) — VARSAYILAN KAPALI
    if medial == "nicp":
        _log("4b MEDIAL", "d ve mf sablon hizalamasiyla (NICP) duzeltiliyor")
        lm, mb = medial_iyilestir(ct, rows, org, lm, disla=disla)
        rapor["medial"] = mb
        if mb["sonuc"] != "TAMAM":
            _log("4b MEDIAL", "BASARISIZ, landmarklar DEGISMEDI: %s" % mb.get("mesaj"))
        else:
            _log("4b MEDIAL", "%d sablon · oynama %s mm · yayilim %s mm"
                 % (mb["sablon_sayisi"], mb["oynama_mm"], mb["yayilim_mm"]))
            # yayilim = belirsizlik; hasta13'teki SESSIZ medial hatanin uyarisi
            ky = [v for v in mb["yayilim_mm"].values() if v is not None]
            if ky and max(ky) > MEDIAL_YAYILIM_UYARI:
                rapor.setdefault("ek_uyari", []).append(
                    {"kapi": "medial_yayilim", "deger": max(ky),
                     "olcut": MEDIAL_YAYILIM_UYARI, "sonuc": "UYARI",
                     "aciklama": "Sablonlar d/mf icin dagilik kestirim veriyor. "
                                 "NOT: yayilim hatayi ONGORMUYOR (r<0, 07 §7e); "
                                 "bu kapi kaba bir felaket sigortasidir."})
                _log("   kapi", "UYARI  medial_yayilim %.2f mm" % max(ky))
        # RAPORDAKI NOKTA BLOGU 4. ADIMDA yazildi; 4b landmarklari degistirdiyse
        # blok GUNCELLENMELI. 2026-10-20'de bu atlanmisti: hasta13'un raporu
        # iyilestirme ONCESI koordinatlari tutuyordu, olcumler ise SONRASINI
        # kullaniyordu (teslim edilen .mrk.json dosyalari dogruydu). Kayitli
        # koordinat, sayiyi ureten koordinat olmalidir.
        rapor["landmark"]["nokta"] = {k: [round(float(x), 3)
                                          for x in np.asarray(lm[k], float)]
                                      for k in AD}
        rapor["landmark"]["medial_iyilestirildi"] = (mb["sonuc"] == "TAMAM")
        rapor["adimlar"].append({"adim": "medial", "sonuc": mb["sonuc"]})
    elif medial in (None, "yok", "kapali", ""):
        rapor["medial"] = {"sonuc": "KAPALI"}
    else:
        raise SystemExit("bilinmeyen --medial degeri: %s (gecerli: nicp | yok)" % medial)

    # --- 5) RIM
    E = {}
    for S in ("sag", "sol"):
        e = bil.get("egri", {}).get(S)
        E[S] = np.asarray(e, float) if isinstance(e, (list, np.ndarray)) else None
    for s, S in (("r", "sag"), ("l", "sol")):
        if E[S] is None:
            a, _ = rimcurve.auto_rim(ct, rows, org, lm, s, win=0.75, n_out=20)
            E[S] = np.asarray(a, float) if a is not None else None
    if E["sag"] is None or E["sol"] is None:
        raise SystemExit("DURDU: rim egrisi uretilemedi")
    _log("5/8 RIM", "otomatik egri · alan %.1f / %.1f mm2 · duzlemsizlik %.3f / %.3f"
         % (params.newell_area(E["sag"]), params.newell_area(E["sol"]),
            params.plane(E["sag"])[2], params.plane(E["sol"])[2]))
    rapor["adimlar"].append({"adim": "rim", "sonuc": "TAMAM", "kaynak": "otomatik"})

    # --- 6) MASKE
    M = {}
    for s, S in (("r", "sag"), ("l", "sol")):
        o = rayseg.ray_volume(ct, rows, org, lm, s, rim_curve=E[S], plane_shift=0.0,
                              return_mask=True, acma_mm=1.5)
        M[s] = o["maske"]
    _log("6/8 MASKE", "isin maskesi · %.3f / %.3f cm3"
         % (M["r"].sum() * vox / 1000., M["l"].sum() * vox / 1000.))
    rapor["adimlar"].append({"adim": "maske", "sonuc": "TAMAM",
                             "kaynak": "rayseg (isin) + otomatik egri on siniri"})

    # --- 7) OLCUM
    _log("7/8 OLCUM", "43 parametre (altigen katsayilari n=12)")
    R = oz.olc(ct, rows, org, lm, M["r"], M["l"], rim_r=E["sag"], rim_l=E["sol"],
               kaynak="TAM OTOMATIK (girdi yalniz ham DICOM)", kimlik=kimlik + "_OTO",
               on_sinir_duzlemde=True,      # plane_shift=0 — bkz. denetle()
               apeks_atlastan=True)         # apeks atlas kestirimi -> DERINLIK OLCULMEZ
    for s, S in (("r", "sag"), ("l", "sol")):
        eks = np.asarray(lm["apex-" + s], float) - np.mean([lm[b + "-" + s] for b in ORD], axis=0)
        t = kb.measure_side(ct, rows, org, M[s], eks, s)
        for bol in ("superior", "inferior", "medial", "lateral"):
            if t[bol]["durum"] == "TAMAM":
                R["kal_%s_%s" % (bol[:3], S)] = round(t[bol]["medyan"], 2)
                R["kal_%s_%s_ince" % (bol[:3], S)] = round(t[bol]["p2"], 2)
                R["kal_%s_%s_kalin" % (bol[:3], S)] = round(t[bol]["p98"], 2)
    rapor["olcum"] = {k: v for k, v in R.items() if k != "denetim"}

    # --- 8) DENETIM + CIKTI
    den = R["denetim"]
    red = [u for u in den["uyari"] if u["sonuc"] == "RED"]
    uya = [u for u in den["uyari"] if u["sonuc"] != "RED"]
    _log("8/8 DENETIM", "RED %d · UYARI %d · hacim yazilabilir: %s"
         % (len(red), len(uya), den["hacim_veri_setine_yazilabilir"]))
    for u in den["uyari"]:
        _log("   kapi", "%-6s %-18s %-4s %s" % (u["sonuc"], u["kapi"], u.get("taraf", ""),
                                                str(u.get("deger", ""))[:20]))
    # ek kapilar: medial en ince mi, hacim bandi, OI
    ek = {}
    for S in ("sag", "sol"):
        kal = {b: R.get("kal_%s_%s" % (b, S)) for b in ("sup", "inf", "med", "lat")}
        if all(v is not None for v in kal.values()):
            ek["medial_en_ince_" + S] = bool(kal["med"] == min(kal.values()))
    for S in ("sag", "sol"):
        h = R.get("hacimK_" + S)
        ek["hacim_bandi_" + S] = bool(h is not None and 19.9 <= h <= 33.4)
        ek["OI_100_" + S] = bool(R.get("OI_" + S, 0) < 100)
    rapor["ek_kapilar"] = ek
    rapor["denetim"] = den
    _log("   kapi", "ek: %s" % ek)

    if cikti_mrk:
        kl = os.path.join("/home/claude/veri_disk/otomatik_landmark", kimlik + "_TAMOTO")
        os.makedirs(kl, exist_ok=True)
        mrk.yaz({k: np.asarray(lm[k], float) for k in AD}, kl, on_ek="OTO_")
        for S in ("sag", "sol"):
            mrk.egri_yaz(E[S], "rim_" + S, kl, on_ek="OTO_")
        rapor["mrk_klasoru"] = kl
        _log("8/8 KAYIT", kl)

    rapor["sure_sn"] = round((datetime.datetime.now() - t0).total_seconds(), 1)
    os.makedirs(os.path.join(kok, "raporlar"), exist_ok=True)
    ry = os.path.join(kok, "raporlar", "%s_OTO.json" % kimlik)
    json.dump(rapor, open(ry, "w", encoding="utf-8"), ensure_ascii=False, indent=1,
              default=float)
    _log("8/8 KAYIT", ry)
    return rapor


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("kaynak"); ap.add_argument("kimlik")
    ap.add_argument("--disla", default=None)
    ap.add_argument("--medial", default="nicp",
                    help="nicp (VARSAYILAN) -> d ve mf'yi sablon hizalamasiyla "
                         "duzelt · yok -> kapat. LOO karnesi 07 §7e")
    a = ap.parse_args()
    r = calistir(a.kaynak, a.kimlik, a.disla, medial=a.medial)
    print("\n--- OZET (%s, %.1f sn) ---" % (a.kimlik, r["sure_sn"]))
    o = r["olcum"]
    for k in ("OW_sag", "OW_sol", "OH_sag", "OH_sol", "OI_sag", "OI_sol",
              "IOD_d", "IOD_mf", "BOW_ek", "BOW_fmo", "centroid",
              "APalan_sag", "APalan_sol", "APcevre_sag", "APcevre_sol",
              "derinlik_sag", "derinlik_sol", "hacim_sag", "hacim_sol",
              "hacimK_sag", "hacimK_sol", "kal_sup_sag", "kal_sup_sol",
              "kal_inf_sag", "kal_inf_sol", "kal_med_sag", "kal_med_sol",
              "kal_lat_sag", "kal_lat_sol"):
        print("  %-14s %s" % (k, o.get(k)))
