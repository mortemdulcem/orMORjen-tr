# -*- coding: utf-8 -*-
"""Arastirmacinin 'denekN slicer duzeltme' paketlerini isler (0BO / 0BQ).

  1. RAR'i ac (cok parcali da olur), sahne klasorunu bul
  2. ARASTIRMACI OLCUMU: elle_olc.py (segmentasyonu varsa hacim ondan)  -> AYRI tutulur
       kohort/elle_duzeltme/<denek>_ELLE_OLCUM.json
  3. KARSILASTIRMA: ayni olgunun OTOMATIK satiri (kohort_98.csv) ile parametre parametre fark
       kohort/elle_duzeltme/karsilastirma.csv   (her olgu bir satir; ustune yazilmaz, eklenir)
  4. EGITIM VERISI: landmark + egri + segmentasyon dosyalari  egitim/<denek>/  (yerel; GitHub'a GITMEZ)
  5. KUME: on kayitli kural (0BQ §3) -> iyilestirme / sinav
Kullanim: python3 duzeltme_isle.py <denek> <rar_parca1> [parca2 ...]
"""
import sys, os, json, csv, glob, shutil, subprocess, hashlib
denek, parcalar = sys.argv[1], sys.argv[2:]
SP = '/tmp/claude-0/-home-claude/9f46a888-8a38-562b-887d-ad413187b1aa/scratchpad/duz_' + denek
REPO = '/home/claude/ormorjen-tr/kohort'
EG = '/home/claude/egitim/' + denek
P = ['OW_sag', 'OW_sol', 'OH_sag', 'OH_sol', 'OI_sag', 'OI_sol', 'APalan_sag', 'APalan_sol',
     'APcevre_sag', 'APcevre_sol', 'hacim_sag', 'hacim_sol', 'IOD_d', 'IOD_mf', 'BOW_ek', 'BOW_fmo',
     'centroid', 'derinlik_sag', 'derinlik_sol', 'kal_sup_sag', 'kal_sup_sol', 'kal_inf_sag',
     'kal_inf_sol', 'kal_med_sag', 'kal_med_sol', 'kal_lat_sag', 'kal_lat_sol']


# AYNI KISI = AYNI KAT (ezber/sizinti olmasin): pilot ile denek ayni taramaysa kat kisiye gore atanir
AYNI_KISI = {'hasta5': 'denek255', 'hasta7': 'denek245', 'hasta10': 'denek24', 'hasta11': 'denek50'}


def kume(ad):
    """0BQ §3 (2026-11-16 09:54 guncel): 5 katli capraz dogrulama. Kat = SHA-256(ad) mod 5.
    Her olgu 4 katta EGITIME, kendi katinda SINAVA girer; ayni anda ikisine asla. Son model butun olgularla egitilir."""
    kisi = AYNI_KISI.get(ad, ad)
    return 'kat%d' % (int(hashlib.sha256(kisi.encode()).hexdigest(), 16) % 5)


shutil.rmtree(SP, ignore_errors=True); os.makedirs(SP + '/r'); os.makedirs(SP + '/x')
env = dict(os.environ, LANG='C.UTF-8', LC_ALL='C.UTF-8')
for i, p in enumerate(parcalar, 1):
    shutil.copy(p, SP + '/r/p.part%d.rar' % i if len(parcalar) > 1 else SP + '/r/p.rar')
ilk = SP + ('/r/p.part1.rar' if len(parcalar) > 1 else '/r/p.rar')
subprocess.run(['unrar', 'x', '-idq', ilk, SP + '/x/'], env=env, check=True)
mrml = glob.glob(SP + '/x/**/*.mrml', recursive=True)
assert mrml, 'sahne (.mrml) yok'
kl = os.path.dirname(mrml[0])
ctler = [f for f in glob.glob(kl + '/*.nrrd') if not f.endswith('.seg.nrrd')]
assert ctler, 'BT (.nrrd) yok'
ct = max(ctler, key=os.path.getsize)
r = subprocess.run(['python3', '/home/claude/an/elle_olc.py', denek, ct, kl], capture_output=True, text=True)
print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip().splitlines()[-1])
J = '/home/claude/an/out/elle/%s_ELLE_OLCUM.json' % denek
assert os.path.exists(J), 'elle olcum uretilemedi'
d = json.load(open(J)); d.pop('slicer_klasoru', None)
b = d['bt']; d['bt'] = {k: b.get(k) for k in ('kesit', 'voksel_mm', 'kesit_kalinligi', 'cekirdek', 'spacing')}
d['kume'] = kume(denek)
os.makedirs(REPO + '/elle_duzeltme', exist_ok=True)
json.dump(d, open(REPO + '/elle_duzeltme/%s_ELLE_OLCUM.json' % denek, 'w'), ensure_ascii=False, indent=1)
# egitim verisi (hasta verisi: yerel)
shutil.rmtree(EG, ignore_errors=True); os.makedirs(EG)
for f in glob.glob(kl + '/*.mrk.json') + glob.glob(kl + '/*.seg.nrrd') + glob.glob(kl + '/*.mrml'):
    shutil.copy(f, EG)
# karsilastirma
oto = {}
for row in csv.DictReader(open(REPO + '/kohort_98.csv', encoding='utf-8')):
    if row['denek'] == denek:
        oto = row
e = d['olcum']
satir = {'denek': denek, 'kume': d['kume'], 'maske_kaynak': d.get('maske_kaynak', ''),
         'oto_var': bool(oto), 'oto_red': oto.get('red_kapilari', '') if oto else ''}
for p in P:
    ev = e.get(p); ov = oto.get(p) if oto else None
    satir['elle_' + p] = ev
    try:
        satir['fark_' + p] = round(float(ov) - float(ev), 3)      # OTOMATIK - ARASTIRMACI
    except (TypeError, ValueError):
        satir['fark_' + p] = ''
kf = REPO + '/elle_duzeltme/karsilastirma.csv'
eski = list(csv.DictReader(open(kf, encoding='utf-8'))) if os.path.exists(kf) else []
eski = [x for x in eski if x['denek'] != denek] + [satir]
with open(kf, 'w', encoding='utf-8', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(satir.keys())); w.writeheader(); w.writerows(eski)
# capraz denetim: arastirmacinin Slicer Segment Statistics tablosu (Table.tsv, LM hacim) ile bizim okudugumuz hacim
tab = {}
for f in glob.glob(kl + '/Table*.tsv'):
    if f.endswith('schema.tsv'):
        continue
    for row in csv.DictReader(open(f, encoding='utf-8'), delimiter='\t'):
        if 'Volume cm3 (LM)' in row and row.get('Segment', '').lower()[:2] in ('sa', 'so'):
            tab['sag' if row['Segment'].lower().startswith('sa') else 'sol'] = float(row['Volume cm3 (LM)'])
tablo_fark = {S: round(e.get('hacim_' + S, float('nan')) - v, 3) for S, v in tab.items()}
red = [u['kapi'] for u in d['denetim']['uyari'] if u['sonuc'] == 'RED']
print('TAMAM', denek, 'Table.tsv farki', tablo_fark, d['kume'], d.get('maske_kaynak', '')[:30], 'RED', red,
      ' '.join('%s=%s' % (p, satir['fark_' + p]) for p in ('OW_sag', 'OW_sol', 'OH_sag', 'hacim_sag', 'hacim_sol', 'IOD_d')))
shutil.rmtree(SP, ignore_errors=True)
