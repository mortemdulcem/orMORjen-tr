# -*- coding: utf-8 -*-
"""APEKS KESTIRIMI — 7 sablonlu NICP (`0M` SS3 KOL B).

`0M` SS3: "`d` ve `mf` icin ZATEN CALISAN makine apekse cevrilir -- `an/medial.py`:
Procrustes on hizalama + NICP + cok sablon medyani, 7 sablon. Tek fark hedef ve
hizalama kumeleri:
  HEDEF    = `apex-r`, `apex-l`
  HIZALAMA = kalan 12 nokta (`d`, `mf`, `mso`, `fmo`, `ek`, `o`) -- APEKS YOK"

Apeksin hizalamadan cikarilmasi SART: hedefi hizalamada kullanmak cevabi cevapla
bulmaktir (`0M` SS3). `medial.py`'nin kendisi ayni gerekceyle `d`/`mf`'yi disarida
birakir.

`medial.py` DEGISTIRILMEDI, yalniz hedef/hizalama kumeleri SECIMLIK parametre
yapildi; varsayilan cagrilar (d/mf yolu) aynen onceki davranisi verir.
"""
import sys

sys.path.insert(0, '/home/claude/an')
import medial as M

HEDEF_NOKTA = ('apex-r', 'apex-l')
HIZA_NOKTA = ('d-r', 'd-l', 'mf-r', 'mf-l', 'mso-r', 'mso-l',
              'fmo-r', 'fmo-l', 'ek-r', 'ek-l', 'o-r', 'o-l')   # 12, apeks YOK


def kestir(hedef_v, hedef_lm_hiza, kutuphane, **kw):
    """Apeksi kestirir. Donus `medial.kestir` ile ayni bicimdedir."""
    return M.kestir(hedef_v, hedef_lm_hiza, kutuphane,
                    hedef_nokta=HEDEF_NOKTA, hiza_nokta=HIZA_NOKTA, **kw)


def kestir_tek(sablon, hedef_v, hedef_lm_hiza, **kw):
    return M.kestir_tek(sablon, hedef_v, hedef_lm_hiza,
                        hedef_nokta=HEDEF_NOKTA, hiza_nokta=HIZA_NOKTA, **kw)
