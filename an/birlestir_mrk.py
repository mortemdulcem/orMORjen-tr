# -*- coding: utf-8 -*-
"""ALI'nin grup basina yazdigi .mrk.json dosyalarini tek dosyada birlestirir.

Koordinat sistemi DEGISTIRILMEZ; hepsi ayni sistemde (LPS) gelir, dogrulanir.
Ayni etiket iki dosyada varsa hata verir (sessizce birini secmek yasak).
"""
import json
import sys

cikti, *girdiler = sys.argv[1:]
nokta, sistem = {}, None
for y in girdiler:
    d = json.load(open(y))
    for m in d['markups']:
        s = m.get('coordinateSystem')
        if sistem is None:
            sistem = s
        elif s != sistem:
            raise SystemExit('koordinat sistemi uyusmuyor: %s != %s (%s)' % (s, sistem, y))
        for c in m['controlPoints']:
            e = c['label']
            if e in nokta and nokta[e] != c['position']:
                raise SystemExit('ayni etiket iki dosyada farkli: %s' % e)
            nokta[e] = c['position']

gov = json.load(open(girdiler[0]))
gov['markups'] = [gov['markups'][0]]
gov['markups'][0]['coordinateSystem'] = sistem
gov['markups'][0]['controlPoints'] = [
    {'id': str(i + 1), 'label': e, 'position': p, 'visibility': True, 'selected': True}
    for i, (e, p) in enumerate(sorted(nokta.items()))
]
json.dump(gov, open(cikti, 'w'), indent=2)
print('birlestirildi: %d landmark -> %s' % (len(nokta), cikti))
