# -*- coding: utf-8 -*-
"""Otomatik landmarklari Slicer .mrk.json olarak yaz (arastirmaci duzeltsin diye)."""
import json, os
import numpy as np


def yaz(nokta_ras, klasor, on_ek=''):
    """nokta_ras: {'d-r': [r,a,s], ...}  -> her nokta icin bir .mrk.json (LPS)."""
    os.makedirs(klasor, exist_ok=True)
    yollar = []
    for ad, P in nokta_ras.items():
        P = np.asarray(P, float)
        lps = [-float(P[0]), -float(P[1]), float(P[2])]
        d = {
            "@schema": "https://raw.githubusercontent.com/slicer/slicer/master/Modules/Loadable/"
                       "Markups/Resources/Schema/markups-schema-v1.0.3.json#",
            "markups": [{
                "type": "Fiducial", "coordinateSystem": "LPS", "coordinateUnits": "mm",
                "locked": False, "fixedNumberOfControlPoints": False,
                "labelFormat": "%N-%d",
                "lastUsedControlPointNumber": 1,
                "controlPoints": [{
                    "id": "1", "label": ad, "description": "OTOMATIK — denetlenmeli",
                    "associatedNodeID": "", "position": lps,
                    "orientation": [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
                    "selected": True, "locked": False, "visibility": True,
                    "positionStatus": "defined"}],
                "measurements": [],
                "display": {
                    "visibility": True, "opacity": 1.0, "color": [1.0, 0.5, 0.0],
                    "selectedColor": [1.0, 0.5, 0.0], "activeColor": [0.4, 1.0, 0.0],
                    "propertiesLabelVisibility": False, "pointLabelsVisibility": True,
                    "textScale": 3.0, "glyphType": "Sphere3D", "glyphScale": 1.0,
                    "glyphSize": 5.0, "useGlyphScale": True, "sliceProjection": False,
                    "sliceProjectionUseFiducialColor": True, "sliceProjectionOutlinedBehindSlicePlane": False,
                    "sliceProjectionColor": [1.0, 1.0, 1.0], "sliceProjectionOpacity": 0.6}
            }]
        }
        y = os.path.join(klasor, '%s%s.mrk.json' % (on_ek, ad))
        json.dump(d, open(y, 'w'), indent=2)
        yollar.append(y)
    return yollar


def egri_yaz(E, ad, klasor, on_ek=''):
    """Kapali egriyi .mrk.json olarak yaz."""
    os.makedirs(klasor, exist_ok=True)
    cp = []
    for i, P in enumerate(np.asarray(E, float)):
        cp.append({"id": str(i + 1), "label": "%s-%d" % (ad, i + 1),
                   "description": "OTOMATIK — denetlenmeli", "associatedNodeID": "",
                   "position": [-float(P[0]), -float(P[1]), float(P[2])],
                   "orientation": [1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0],
                   "selected": True, "locked": False, "visibility": True,
                   "positionStatus": "defined"})
    d = {"@schema": "https://raw.githubusercontent.com/slicer/slicer/master/Modules/Loadable/"
                    "Markups/Resources/Schema/markups-schema-v1.0.3.json#",
         "markups": [{"type": "ClosedCurve", "coordinateSystem": "LPS", "coordinateUnits": "mm",
                      "locked": False, "fixedNumberOfControlPoints": False,
                      "labelFormat": "%N-%d", "lastUsedControlPointNumber": len(cp),
                      "controlPoints": cp, "measurements": [],
                      "display": {"visibility": True, "opacity": 1.0,
                                  "color": [1.0, 0.5, 0.0], "selectedColor": [1.0, 0.5, 0.0],
                                  "activeColor": [0.4, 1.0, 0.0], "pointLabelsVisibility": False,
                                  "textScale": 3.0, "glyphType": "Sphere3D",
                                  "glyphScale": 1.0, "glyphSize": 5.0, "useGlyphScale": True,
                                  "curveLineSizeMode": "UseLineThickness", "lineThickness": 0.2}}]}
    y = os.path.join(klasor, '%s%s.mrk.json' % (on_ek, ad))
    json.dump(d, open(y, 'w'), indent=2)
    return y
