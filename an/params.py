# -*- coding: utf-8 -*-
"""Bir Slicer sahne klasorunden orbita parametrelerini RAS'ta hesaplar.

KAYNAK: proje belgesi `claude/cozumleme-betikleri-kaynak-kod.md` -> "## params.py"
BIREBIR AKTARILMISTIR (2026-11-10 konteyner kurtarmasi, `0AT`).
"""
import json, os, glob, math, sys
import numpy as np
import nrrd

def read_tables(folder):
    """Slicer'in disa aktardigi Table_*.csv / .tsv dosyalarindan RAS noktalari."""
    import csv
    pts, curves = {}, {}
    for f in sorted(glob.glob(os.path.join(folder, 'Table*.csv')) +
                    glob.glob(os.path.join(folder, 'Table*.tsv'))):
        if 'schema' in os.path.basename(f).lower():
            continue
        dl = '\t' if f.endswith('.tsv') else ','
        try:
            rows = list(csv.DictReader(open(f, encoding='utf-8-sig'), delimiter=dl))
        except Exception:
            continue
        if not rows or 'r' not in rows[0]:
            continue
        labs = [(r.get('label') or '').strip() for r in rows]
        try:
            P = np.array([[float(r['r']), float(r['a']), float(r['s'])] for r in rows], float)
        except Exception:
            continue
        if len(rows) == 1:
            pts[labs[0].lower()] = P[0]
        elif len(rows) > 3:
            base = labs[0].split('-')[0].lower()
            nm = 'sag' if base.startswith('sag') or base.startswith('cc_') else (
                 'sol' if base.startswith('sol') or base.startswith('cc') else base)
            curves.setdefault(nm, P)
    return pts, curves


def load_scene(folder):
    pts, curves = {}, {}
    for f in sorted(glob.glob(os.path.join(folder, '*.mrk.json'))):
        try:
            j = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        for m in j.get('markups', []):
            cs = (m.get('coordinateSystem') or 'LPS').upper()
            flip = np.array([-1, -1, 1.0]) if cs == 'LPS' else np.ones(3)
            cps = m.get('controlPoints', [])
            if m.get('type') == 'Fiducial':
                for cp in cps:
                    lab = (cp.get('label') or '').strip().lower()
                    pts[lab] = np.array(cp['position'], float) * flip
            elif m.get('type') in ('ClosedCurve', 'Curve'):
                nm = os.path.basename(f).replace('.mrk.json', '').lower()
                curves[nm] = np.array([cp['position'] for cp in cps], float) * flip
    tp, tc = read_tables(folder)
    for k, v in tp.items():
        pts.setdefault(k, v)     # JSON bozuksa/eksikse tablodan tamamla
    for k, v in tc.items():
        curves.setdefault(k, v)
    return pts, curves

def newell_area(P):
    n = np.zeros(3); m = len(P)
    for i in range(m):
        n += np.cross(P[i], P[(i+1) % m])
    return float(np.linalg.norm(n) / 2.0)

def perim(P):
    m = len(P)
    return float(sum(np.linalg.norm(P[(i+1) % m] - P[i]) for i in range(m)))

def plane(P):
    c = P.mean(axis=0)
    u, s, vt = np.linalg.svd(P - c)
    return c, vt[2], s[2] / s[0], float(np.abs((P - c) @ vt[2]).max())

def csize(P):
    c = P.mean(axis=0)
    return float(math.sqrt(((P - c) ** 2).sum()))

def seg_vols(path):
    data, h = nrrd.read(path)
    sd = np.array(h['space directions'], float)
    rows = [r for r in sd if not np.isnan(r).any()]
    vox = abs(float(np.linalg.det(np.array(rows[:3]))))
    labels = {k.split('_')[0]: int(v) for k, v in h.items() if k.endswith('_LabelValue')}
    out = {}
    for k, lv in labels.items():
        nm = h.get(k + '_Name', k)
        if data.ndim == 4:
            lay = int(h.get(k + '_Layer', 0)); cnt = int((data[lay] == lv).sum())
        else:
            cnt = int((data == lv).sum())
        out[nm.strip().lower()] = (cnt, cnt * vox / 1000.0)
    return out

def D(a, b):
    return float(np.linalg.norm(a - b))

def analyse(folder, tag):
    pts, curves = load_scene(folder)
    R = {}
    R['etiket'] = tag
    cts = [f for f in glob.glob(os.path.join(folder, '*.nrrd'))
           if 'segmentation' not in os.path.basename(f).lower() and '_seg' not in os.path.basename(f).lower()]
    if cts:
        h = nrrd.read_header(cts[0])
        sd = np.array(h['space directions'], float)
        R['boyut'] = tuple(int(x) for x in h['sizes'])
        R['spacing'] = tuple(round(float(np.linalg.norm(sd[i])), 4) for i in range(3))
        R['origin'] = tuple(round(float(x), 2) for x in h['space origin'])
    # es anlamli / yazim hatasi olan etiketler
    ALIAS = {'fso-r': 'mso-r', 'fso-l': 'mso-l', 'mfo-r': 'fmo-r', 'mfo-l': 'fmo-l',
             'fom-r': 'fmo-r', 'fom-l': 'fmo-l'}
    for a, b in ALIAS.items():
        if a in pts and b not in pts:
            pts[b] = pts[a]
    if 'sa' in curves and 'sag' not in curves:
        curves['sag'] = curves.pop('sa')
    R['landmark'] = {k: v for k, v in pts.items()}
    need = ['d-r','d-l','mf-r','mf-l','fmo-r','fmo-l','ek-r','ek-l','mso-r','mso-l','o-r','o-l','apex-r','apex-l']
    R['eksik'] = [k for k in need if k not in pts]
    g = lambda k: pts.get(k)
    # taraf denetimi (RAS: sag = +x)
    mids = []
    for b in ('d','mf','fmo','ek','mso','o','apex'):
        if g(b+'-r') is not None and g(b+'-l') is not None:
            mids.append((b, g(b+'-r')[0], g(b+'-l')[0]))
    R['taraf_denetimi'] = mids
    R['orta_hat_x'] = round(float(np.mean([(a+b)/2 for _, a, b in mids])), 2) if mids else None
    R['taraf_hatasi'] = [b for b, ar, al in mids if ar <= al]
    # olculer
    for s, S in (('r','sag'), ('l','sol')):
        if g('mf-'+s) is not None and g('ek-'+s) is not None:
            R['OW_'+S] = round(D(g('mf-'+s), g('ek-'+s)), 2)
        if g('mso-'+s) is not None and g('o-'+s) is not None:
            R['OH_'+S] = round(D(g('mso-'+s), g('o-'+s)), 2)
    if 'OW_sag' in R and 'OH_sag' in R: R['OI_sag'] = round(100*R['OH_sag']/R['OW_sag'], 1)
    if 'OW_sol' in R and 'OH_sol' in R: R['OI_sol'] = round(100*R['OH_sol']/R['OW_sol'], 1)
    if g('mf-r') is not None and g('mf-l') is not None: R['IOD_mf'] = round(D(g('mf-r'), g('mf-l')), 2)
    if g('d-r') is not None and g('d-l') is not None: R['IOD_d'] = round(D(g('d-r'), g('d-l')), 2)
    if g('ek-r') is not None and g('ek-l') is not None: R['BOW_ek'] = round(D(g('ek-r'), g('ek-l')), 2)
    if g('fmo-r') is not None and g('fmo-l') is not None: R['BOW_fmo'] = round(D(g('fmo-r'), g('fmo-l')), 2)
    # apertur
    for nm, P in curves.items():
        S = 'sag' if nm.startswith('sag') else ('sol' if nm.startswith('sol') else nm)
        c, n, rr, dev = plane(P)
        R['APalan_'+S] = round(newell_area(P), 1)
        R['APcevre_'+S] = round(perim(P), 2)
        R['APduzlemsizlik_'+S] = (round(rr, 3), round(dev, 2))
        R['APnokta_'+S] = len(P)
        s = 'r' if S == 'sag' else 'l'
        ap = g('apex-'+s)
        if ap is not None:
            R['derinlik_duzlem_'+S] = round(abs(float((ap - c) @ n)), 2)
            R['derinlik_merkez_'+S] = round(D(ap, c), 2)
    segs = glob.glob(os.path.join(folder, '*Segmentation*.nrrd')) + glob.glob(os.path.join(folder, '*_seg.nrrd'))
    if segs:
        try:
            v = seg_vols(segs[0])
            for k, (cnt, vol) in v.items():
                R['hacim_'+k] = round(vol, 3)
                R['voksel_'+k] = cnt
        except Exception as e:
            R['hacim_hata'] = str(e)
    # centroid buyuklugu (12 landmark)
    cfg = [g(b+'-'+s) for b in ('d','mf','fmo','ek','mso','o') for s in ('r','l')]
    if all(x is not None for x in cfg):
        R['centroid_buyuklugu'] = round(csize(np.array(cfg)), 2)
    return R
