# -*- coding: utf-8 -*-
"""OLCUM ZINCIRI — maske nereden gelirse gelsin, 43 parametreyi YEREL cozunurlukte uretir.

Katmanlar:
  1. SEGMENTASYON (kaba)   : sinir agi (160x160) VEYA rayseg isin yontemi VEYA arastirmaci
  2. OLCUM (yerel)         : params.py + rimcurve.py + kalinlik_bolgesel.py   <- bu dosya
  3. DENETIM               : §6 kalite kapilari; gecemezse sayi veri setine yazilmaz

COZUNURLUK KURALI — ihlal edilmez:
  Sinir agi duzlem-ici 160x160 calisir. 512 px / 0.6016 mm bir BT'de bu 1.925 mm/piksel
  demektir. Olculen duvar kalinligi medyanlari 1.04-2.24 mm oldugundan AGIN CIKTISINDAN
  KALINLIK OLCULEMEZ; hacim de yari piksellik sinir hatasiyla birkac cm3 oynar.
  Bu yuzden ag ciktisi YALNIZ kaba yer bulucudur (`kaynak="ag_kaba"` olarak isaretlenir);
  olcum daima yerel izgarada yapilir. Arastirmacinin kendi notu ayni sinira isaret eder:
  .agents/memory/thickness-resolution-censoring.md
"""
from __future__ import annotations
import os, sys, json, math
import numpy as np

sys.path.insert(0, "/home/claude/an")
import params, rayseg, rimcurve, kalinlik_bolgesel as kb

ORD = ("d", "mf", "mso", "fmo", "ek", "o")
# Altigen duzeltme katsayilari — n=8 orbita (2026-10-12; 00 §3 ve 01 ile ayni).
# 2026-10-13: hat n=6 degerlerinde kalmisti (1.4243 / 1.1006 / 1.523 / 1.3) ve belgelerle
# celisiyordu; egri olmayan yeni bir olguda eski katsayilarla deger uretirdi. Guncellendi.
# n=12 orbita / 6 hasta (2026-10-15, an/kats12.py). Onceki: n=8 1.4015/1.0974/1.539/1.39.
# Sacilma: alan SS %4,5 · cevre %1,4 · derinlik %21,8 · duzlem ofset araligi -1,03...-1,86 mm.
ALTIGEN = {"alan": 1.3832, "cevre": 1.0927, "derinlik": 1.532, "duzlem_kaydirma": 1.41}

# --- ON SINIR YUZEYI (2026-10-23 karari) -------------------------------------
# Tez metni (gerec-yontem) bastan beri Jansen ve ark. 2016'nin yontemini yaziyordu:
#   "orbita kenari landmarklari + AGIRLIK MERKEZI ile kurulan apertur duzlemi
#    (Jansen; gozlemciler arasi ICC 0,992)"
# Jansen'in tarifi (Int J CARS 2016;11:11-18, s.12) bir DUZLEM degil bir YUZEYDIR:
#   "a surface was reconstructed connecting all landmarks AS WELL AS THE CENTER OF
#    GRAVITY of these landmarks"
# Kod ise eğriye SVD ile DUZLEM uyduruyordu. Kenar duzlemsel degil (rim noktalarinin
# duzlemden sapmasi 3,01-4,67 mm), bu yuzden ikisi ayni sey degil.
# OLCULDU (an/on_sinir.py, iki onayli maske / dort orbita): yelpaze 8/8 olcumde
# duzlemden DAHA COK kirpiyor; +1 mm ayarinda fark 0,020-0,235 cm3 (%0,08-0,98).
# KARAR: yelpaze benimsendi — metin zaten onu iddia ediyor ve ona ICC atfediyor.
#
# ⚠ YALNIZ GERCEK EGRI VARKEN. Altigen yolunda elde 6 kose vardir; 6 ucgenlik bir
# yelpaze Jansen'in ~20 noktali yuzeyinin kaba bir taklidi olur ve duzlemden daha
# iyi oldugu GOSTERILMEMISTIR. O yolda DUZLEM kalir.
# Geri almak icin: ON_SINIR = "duzlem".
ON_SINIR = "yelpaze"


def _yelpaze_mesafe(P, egri, c, n):
    """Jansen 2016 on sinir YUZEYINE isaretli uzaklik (+ = yuzeyin onunde).

    Yuzey, rim noktalarini agirlik merkezine baglayan ucgen yelpazedir. Her nokta,
    kendi acisal sektorune karsilik gelen ucgenin duzlemine gore olculur — boylece
    kenarin gercek 3B kivrimi izlenir.

    P    : (N,3) RAS noktalari (voksel merkezleri)
    egri : (M,3) rim egrisi, RAS
    c, n : egriden SVD ile kurulan duzlemin noktasi ve ONE bakan normali
    """
    Q = np.asarray(egri, float)
    cg = Q.mean(axis=0)                       # AGIRLIK MERKEZI — yelpazenin tepesi
    u = Q[0] - cg
    u = u - (u @ n) * n
    nu = np.linalg.norm(u)
    u = u / nu if nu > 1e-9 else np.eye(3)[int(np.argmin(np.abs(n)))]
    v = np.cross(n, u)
    dq = Q - cg
    tq = np.arctan2(dq @ v, dq @ u)
    sira = np.argsort(tq)
    Qs, tqs = Q[sira], tq[sira]
    m = len(Qs)
    d = P - cg
    t = np.arctan2(d @ v, d @ u)
    i = np.mod(np.searchsorted(tqs, t, side="right") - 1, m)
    j = np.mod(i + 1, m)
    nn = np.cross(Qs[i] - cg, Qs[j] - cg)     # sektor ucgeninin normali
    boy = np.linalg.norm(nn, axis=1, keepdims=True)
    boy[boy == 0] = 1.0
    nn = nn / boy
    isaret = np.sign(nn @ n)                  # hepsini global normalle ayni yone cevir
    isaret[isaret == 0] = 1.0
    return np.einsum("ij,ij->i", P - cg, nn * isaret[:, None])

# HACIM BANDI — projedeki ARASTIRMACI ONAYLI 14 orbitadan turetildi (2026-10-12):
#   P01 31.231/31.572 · P04 26.671/27.828 · P05 25.999/25.742 · P06 24.014/24.290
#   P07 25.377/25.501 · P08 25.427/25.936 · P09 26.804/26.775
#   aralik 24.01-31.57 · ortalama 26.655 · SS 2.242 · ort+-3SS = 19.9-33.4
# DUZELTME: onceki band (21-28) YANLISTI — P01'in iki onayli orbitasini (31.2/31.6)
# disarida birakiyordu. Band yalniz P04-P09'dan turetilmisti; P01 atlanmisti.
HACIM_BANDI = (19.9, 33.4)
# Hava orani: maskedeki < -300 HU voksel yuzdesi. Kavite yag+kas+glob+sinirdir; hava
# varsa maske sinuse ya da etmoide tasmistir. 2026-10-14'te eklendi — olcut §6 kontrol
# listesinde yaziliydi ama KODDA YOKTU ve hasta6'nin %0,62 / %1,23'u sessizce gecmisti.
# Esik 10 onayli orbitadan: 0,000-0,13 (hasta7 0,037/0,007 · hasta8 0,000/0,000 ·
# hasta9 0,06/0,03 · hasta10 0,13/0,03 · hasta11 0,00/0,00). Kalibre sayilmaz (§0.12),
# bu yuzden RED degil UYARI.
HAVA_UYARI = 0.5
HACIM_BANDI_KAYNAK = "14 onayli orbita, ortalama 26.655 +- 3x2.242"
# Apeks kesiti olcutu (100 mm2) TEK OLGUDA uydurulmustu; §0.12 geregi esik olarak
# kullanilmaz, yalniz UYARI uretir. Kalibre edilince RED'e yukseltilebilir.
APEKS_KESIT_UYARI = 100.0
# IOD bandi: elle olculmus 8 olgunun 16 degeri 18.53-22.76 (ort 20.67); +-3 mm pay.
# KALIBRE DEGIL (n=8, §0.12) -> UYARI duzeyinde. 2026-10-19, hasta13 vesilesiyle.
IOD_BANDI = (15.5, 25.8)


def _msp(lm):
    pr = ["d", "mf", "fmo", "ek", "mso", "o"]
    n = np.mean([lm[b + "-r"] - lm[b + "-l"] for b in pr], axis=0)
    n /= np.linalg.norm(n)
    c = np.mean([(lm[b + "-r"] + lm[b + "-l"]) / 2 for b in pr], axis=0)
    return c, n


def maske_yerel_izgaraya(maske_kaba, hedef_sekil):
    """Agin 160x160 ciktisini yerel izgaraya tasir. KABA kalir; olcum icin degil."""
    from scipy import ndimage as ndi
    z = [hedef_sekil[i] / maske_kaba.shape[i] for i in range(3)]
    return ndi.zoom(maske_kaba.astype(np.uint8), z, order=0).astype(bool)


def olc(ct, rows, org, lm, maske_r, maske_l, rim_r=None, rim_l=None,
        kaynak="bilinmiyor", kimlik="?", on_sinir_duzlemde=False,
        apeks_atlastan=False):
    """on_sinir_duzlemde: maskenin on siniri apertur egrisinin KENDI duzlemi mi?
    (tam otomatik hatta plane_shift=0 ile boyledir.) Oyleyse `kesit_apertur_asimi`
    kapisi apertur'u apertur'le karsilastirir ve ayriklastirmadan ateslenir —
    2026-10-19'da 14 orbitada olculdu, RED yerine UYARI'ya indirildi (atlas §AW).

    apeks_atlastan: apeks ATLAS KESTIRIMIYSE True. O durumda DERINLIK OLCULMEZ ve
    None yazilir. Gerekce (atlas §AZ, 2026-10-19): atlas apeksi
    c - n*t + u*dik + v*yan olarak konur ve u,v ⊥ n oldugu icin
    derinlik = |(apeks-c)·n| ≡ t, yani ATLAS SABITI. Sekiz olguda saga/sola ayni
    sayi cikti (42,30-42,82). Sabitin elle olculmus derinliklere karsi hatasi %3,27'dir
    ama bu bir olcum basarisi DEGIL, orneklemin dagiliminin darligidir (elle derinlik
    ort 42,53 ± 1,55 = DV %3,6). Maskenin arka ucu da denendi: r = -0,015, yani
    bilgi tasimiyor. Derinlik bu yolda OLCULEMEZ; sabit yazmak uydurma sayi uretir."""
    vox = abs(float(np.linalg.det(rows)))
    for a, b in (("fso-r", "mso-r"), ("fso-l", "mso-l")):
        if a in lm and b not in lm:
            lm[b] = lm[a]
    R = {"kimlik": kimlik, "maske_kaynagi": kaynak, "voksel_mm3": round(vox, 5)}
    cm, nv = _msp(lm)
    D = lambda a, b: float(np.linalg.norm(a - b))

    # --- 1-6, 9-10, 15-16, 38: landmarklardan (maskeden bagimsiz) ---
    for s, S in (("r", "sag"), ("l", "sol")):
        R["OW_" + S] = round(D(lm["mf-" + s], lm["ek-" + s]), 2)
        R["OH_" + S] = round(D(lm["mso-" + s], lm["o-" + s]), 2)
        R["OI_" + S] = round(100 * R["OH_" + S] / R["OW_" + S], 1)
    R["IOD_d"] = round(D(lm["d-r"], lm["d-l"]), 2)
    R["IOD_mf"] = round(D(lm["mf-r"], lm["mf-l"]), 2)
    R["BOW_ek"] = round(D(lm["ek-r"], lm["ek-l"]), 2)
    R["BOW_fmo"] = round(D(lm["fmo-r"], lm["fmo-l"]), 2)
    cfg = [lm[b + "-" + s] for b in ("d", "mf", "fmo", "ek", "mso", "o") for s in ("r", "l")]
    R["centroid"] = round(params.csize(np.array(cfg)), 2)

    # --- 17-18, 5-6: apertur egrisi (yoksa otomatik uret, yoksa altigen+duzeltme) ---
    for s, S, egri, maske in (("r", "sag", rim_r, maske_r), ("l", "sol", rim_l, maske_l)):
        H = np.array([lm[b + "-" + s] for b in ORD])
        ch, nh, _, _ = params.plane(H)
        if np.dot(lm["apex-" + s] - ch, nh) > 0:
            nh = -nh                                   # nh ONE bakar
        if egri is None:
            try:
                egri, bilgi = rimcurve.auto_rim(ct, rows, org, lm, s, win=0.75, n_out=20)
                kaynak_ap = "egri (otomatik - taslak)" if egri is not None else None
            except Exception:
                egri, kaynak_ap = None, None
        else:
            kaynak_ap = "egri (arastirmaci)"
        if egri is not None:
            c, n, rr, dev = params.plane(egri)
            if np.dot(lm["apex-" + s] - c, n) > 0:
                n = -n
            R["APalan_" + S] = round(params.newell_area(egri), 1)
            R["APcevre_" + S] = round(params.perim(egri), 2)
            R["APduzlemsizlik_" + S] = round(rr, 3)
            R["APsapma_" + S] = round(dev, 2)
            # DERINLIK: apeks atlastan geldiyse olculmemis sayilir (bkz. apeks_atlastan)
            R["derinlik_" + S] = (None if apeks_atlastan
                                  else round(abs(float((lm["apex-" + s] - c) @ n)), 2))
            if apeks_atlastan:
                R["derinlik_%s_not" % S] = ("OLCULMEDI — apeks atlas kestirimi; "
                                            "derinlik atlas sabiti t'ye esit olur (§AZ)")
            R["AP_kaynak_" + S] = kaynak_ap
            duzlem = (c, n)
        else:
            R["APalan_" + S] = round(params.newell_area(H) * ALTIGEN["alan"], 1)
            R["APcevre_" + S] = round(params.perim(H) * ALTIGEN["cevre"], 2)
            R["derinlik_" + S] = (None if apeks_atlastan else
                                  round(abs(float((lm["apex-" + s] - ch) @ nh))
                                        + ALTIGEN["derinlik"], 2))
            if apeks_atlastan:
                R["derinlik_%s_not" % S] = ("OLCULMEDI — apeks atlas kestirimi "
                                            "(altigen yolu da ayni sebeple gecersiz)")
            R["AP_kaynak_" + S] = "altigen+duzeltme"
            duzlem = (ch + ALTIGEN["duzlem_kaydirma"] * nh, nh)

        # --- 7-8: hacim + kubbe kirpma (apertur duzlemi + 1 mm) ---
        if maske is not None and maske.any():
            R["hacim_" + S] = round(float(maske.sum()) * vox / 1000.0, 3)
            idx = np.array(np.nonzero(maske))
            P = (org + idx.T.astype(float) @ rows) * np.array([-1.0, -1.0, 1.0])
            c0, n0 = duzlem
            # ON SINIR: gercek rim egrisi varsa Jansen'in YELPAZE yuzeyi, yoksa duzlem
            if ON_SINIR == "yelpaze" and egri is not None and len(np.asarray(egri)) >= 8:
                t0 = _yelpaze_mesafe(P, egri, c0, n0)
                R["AP_on_sinir_" + S] = "yelpaze (Jansen 2016)"
            else:
                t0 = (P - c0) @ n0
                R["AP_on_sinir_" + S] = "duzlem (SVD)"
            # IKI AYRI BUYUKLUK — karistirilmamali:
            #   kubbe    = apertur DUZLEMININ onundeki hacim (anatomik gozlem)
            #   kirpilan = duzlem + 1 mm'nin otesi, yani gercekten atilan hacim
            # hacimK = hacim - kirpilan  (kubbe DEGIL). 2026-10-13 duzeltmesi:
            # onceki surum kirpilani "kubbe" diye yaziyordu; hasta10'da kayitli
            # kubbe 0.797/0.527 iken kirpilan 0.180/0.083'tur.
            R["kubbe_" + S] = round(float((t0 > 0).sum()) * vox / 1000.0, 3)
            R["kirpilan_" + S] = round(float((t0 > 1.0).sum()) * vox / 1000.0, 3)
            R["hacimK_" + S] = round(R["hacim_" + S] - R["kirpilan_" + S], 3)
            # hava orani: maskedeki < -300 HU voksel yuzdesi (kapi icin, 2026-10-14)
            hu = ct[tuple(idx)]
            R["hava_orani_" + S] = round(100.0 * float((hu < -300).sum()) / len(hu), 3)
            R["HU_ort_" + S] = round(float(hu.mean()), 1)
            # denetim: kesit alani apertur alanini asamaz / apekse yakin kesit < 100 mm2
            t = (P - lm["apex-" + s]) @ n0
            if t.max() > 0:
                dilim = (t > t.max() - 3)
                R["kesit_apertur_" + S] = round(float(dilim.sum()) * vox / 3.0, 0)
            yakin = t < 5.0
            R["kesit_apeks_" + S] = round(float(yakin.sum()) * vox / 5.0, 0)
        else:
            for k in ("hacim_", "kubbe_", "kirpilan_", "hacimK_"):
                R[k + S] = None

    # --- 11-14: duvar kalinligi (YEREL izgara, bolgesel medyan) ---
    for s, S, maske in (("r", "sag", maske_r), ("l", "sol", maske_l)):
        if maske is None or not maske.any():
            continue
        eksen = lm["apex-" + s] - np.mean([lm[b + "-" + s] for b in ORD], axis=0)
        try:
            t = kb.measure_side(ct, rows, org, maske, eksen, s)
            for bol, kisa in (("superior", "sup"), ("inferior", "inf"),
                              ("medial", "med"), ("lateral", "lat")):
                d = t.get(bol, {})
                tam = d.get("durum") == "TAMAM"
                # UC DEGER: ince (p2) · medyan · kalin (p98)
                R["kal_%s_%s_ince" % (kisa, S)] = d.get("p2") if tam else None
                R["kal_%s_%s" % (kisa, S)] = d.get("medyan") if tam else None
                R["kal_%s_%s_kalin" % (kisa, S)] = d.get("p98") if tam else None
                R["kal_%s_%s_n" % (kisa, S)] = d.get("n")
                R["kal_%s_%s_hammin" % (kisa, S)] = d.get("min") if tam else None
                R["kal_%s_%s_hammaks" % (kisa, S)] = d.get("maks") if tam else None
            R["kal_sinir"] = "dar"
        except Exception as e:
            R["kal_hata_" + S] = str(e)

    # --- 19-24: asimetri indeksleri ---
    AI = lambda a, b: (round(100 * abs(a - b) / ((a + b) / 2), 2)
                       if (a is not None and b is not None) else None)
    R["AI_OW"] = AI(R["OW_sag"], R["OW_sol"]); R["AI_OH"] = AI(R["OH_sag"], R["OH_sol"])
    R["AI_OI"] = AI(R["OI_sag"], R["OI_sol"])
    R["AI_hacim"] = AI(R.get("hacimK_sag"), R.get("hacimK_sol"))
    R["AI_APalan"] = AI(R["APalan_sag"], R["APalan_sol"])
    R["AI_APcevre"] = AI(R["APcevre_sag"], R["APcevre_sol"])
    R["AI_derinlik"] = AI(R["derinlik_sag"], R["derinlik_sol"])

    R["on_sinir_duzlemde"] = bool(on_sinir_duzlemde)
    R["denetim"] = denetle(R, kaynak, on_sinir_duzlemde)
    return R


def denetle(R, kaynak, on_sinir_duzlemde=False):
    """§6 kalite kapilari. Gecmeyen olgunun hacmi veri setine YAZILMAZ."""
    uyari = []
    if kaynak == "ag_kaba":
        uyari.append({"kapi": "cozunurluk", "sonuc": "RED",
                      "aciklama": "Sinir agi ciktisi 160x160 kaba izgaradir; hacim ve "
                                  "kalinlik olcumu icin kullanilamaz, yalniz yer bulucudur."})
    for S in ("sag", "sol"):
        v = R.get("hacimK_" + S) or R.get("hacim_" + S)
        if v is not None and not (HACIM_BANDI[0] <= v <= HACIM_BANDI[1]):
            uyari.append({"kapi": "hacim_bandi", "taraf": S, "deger": v,
                          "band": list(HACIM_BANDI), "kaynak": HACIM_BANDI_KAYNAK,
                          "sonuc": "RED"})
        ka, ap = R.get("kesit_apertur_" + S), R.get("APalan_" + S)
        if ka and ap and ka > ap:
            # On sinir egrinin KENDI duzlemiyse (plane_shift=0, tam otomatik hat) bu kapi
            # apertur'u apertur'le karsilastirir: en ondeki 3 mm'lik dilim acikligin
            # kendisidir, asim ayriklastirmadan gelir. 2026-10-19'da 14 orbitada olculdu:
            # asim %-5,2...+6,5 ve BUYUKLUGU bilinen kacagi (hasta11) en uste koymuyor
            # (hasta11 +%1,8/+%4,2 iken hasta6 +%5,6/+%6,5). Yerine konacak bir on-kesit
            # olcusu de bulunamadi (duzlemin 3-6 ve 6-9 mm arkasi da ayirmiyor; atlas §AW).
            # Bu yuzden bu yolda RED degil UYARI. Kacagi bu hatta yakalayan iki kapi:
            # hacim bandi ve apeks kesiti.
            uyari.append({"kapi": "kesit_apertur_asimi", "taraf": S,
                          "kesit": ka, "apertur": ap,
                          "sonuc": "UYARI" if on_sinir_duzlemde else "RED",
                          "aciklama": ("On sinir egri duzleminin kendisi; asim buyuk olcude "
                                       "ayriklastirmadir. Kacak kanitini hacim bandi ve "
                                       "apeks kesiti verir (atlas §AW)."
                                       if on_sinir_duzlemde else
                                       "Apertur hizasindaki kesit apertur alanini asiyor "
                                       "-> fissur/yanal kacak.")})
        hv = R.get("hava_orani_" + S)
        if hv is not None and hv > HAVA_UYARI:
            uyari.append({"kapi": "hava_orani", "taraf": S, "deger": hv,
                          "olcut": HAVA_UYARI, "sonuc": "UYARI",
                          "aciklama": "Maskede hava var -> sinus/etmoid tasmasi. "
                                      "Esik 10 orbitadan (0,000-0,13), kalibre DEGIL "
                                      "(§0.12): RED degil UYARI. Hacim taslak sayilir."})
        kap = R.get("kesit_apeks_" + S)
        if kap and kap > APEKS_KESIT_UYARI:
            uyari.append({"kapi": "apeks_kesiti", "taraf": S, "deger": kap,
                          "olcut": APEKS_KESIT_UYARI, "sonuc": "UYARI",
                          "aciklama": "Apeksin 5 mm yakinindaki kesit genis — otomatik "
                                      "maskenin 8/8 orbitada belgelenen apeks fazlasi. "
                                      "Esik tek olguda konuldu, kalibre DEGIL (§0.12): "
                                      "bu yuzden RED degil UYARI."})
        med = R.get("kal_med_" + S)
        digerleri = [R.get("kal_%s_%s" % (k, S)) for k in ("sup", "inf", "lat")]
        if med is not None and all(d is not None for d in digerleri) and med > min(digerleri):
            uyari.append({"kapi": "medial_en_ince", "taraf": S, "medial": med,
                          "sonuc": "UYARI",
                          "aciklama": "Medial duvar en ince olmali; degilse maskede kacak var."})
        oi = R.get("OI_" + S)
        if oi is not None and oi >= 100:
            uyari.append({"kapi": "orbital_indeks", "taraf": S, "deger": oi, "sonuc": "RED"})
    # --- IOD BANDI (2026-10-19, hasta13'te sessizce gecti — §8b) ---
    # Elle olculmus 8 olgunun 16 IOD degeri 18,53-22,76 mm araligindadir (ort 20,67).
    # Band = gozlenen aralik +-3 mm pay: 15,5-25,8. Bu bir KALIBRE esik DEGILDIR
    # (§0.12, n=8), o yuzden RED degil UYARI. IOD zaten tam otomatik yolda
    # kullanilamaz (%12,9 hata, 07 §7b); kapinin isi SESSIZ kalmasini onlemektir.
    for ad in ("IOD_d", "IOD_mf"):
        v = R.get(ad)
        if v is not None and not (IOD_BANDI[0] <= v <= IOD_BANDI[1]):
            uyari.append({"kapi": "iod_bandi", "olcu": ad, "deger": v,
                          "band": list(IOD_BANDI), "sonuc": "UYARI",
                          "aciklama": "IOD elle olculmus seri bandinin disinda -> medial "
                                      "landmarklar (d, mf) kacmis olabilir. Elle "
                                      "isaretlenmeden kullanilmaz."})
    return {"uyari": uyari,
            "hacim_veri_setine_yazilabilir":
                not any(u["sonuc"] == "RED" for u in uyari)}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ct", required=True); ap.add_argument("--sahne", required=True)
    ap.add_argument("--maske"); ap.add_argument("--kimlik", default="?")
    a = ap.parse_args()
    lm, egriler = params.load_scene(a.sahne)
    ct, rows, org = rayseg.load_ct(a.ct)
    mr = ml = None
    if a.maske:
        import nrrd
        d, h = nrrd.read(a.maske)
        mr, ml = (d == 1), (d == 2)
    R = olc(ct, rows, org, lm, mr, ml, kimlik=a.kimlik,
            kaynak="dosya" if a.maske else "maske_yok")
    print(json.dumps(R, ensure_ascii=False, indent=1, default=float))
