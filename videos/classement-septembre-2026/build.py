#!/usr/bin/env python3
"""Lit le classement de septembre dans l'Excel, cale le découpage sur la musique
et injecte tout dans index.html (à partir de src/template.html).

Usage : python3 build.py <classement.xlsx>

Arbitrages validés avec la demandeuse (14/10/2026) :
- BARAN Karolina : on retient la colonne « Retraitement » (4 ventes) ;
- « Patricia LESIMPLE » est affichée « LESIMPLE Patricia » ;
- uniquement l'onglet « Classement Septembre » (98 vendeurs).

Musique : Cosmonkey – Old Sneakers (droits fournis par Médicis), 188 BPM.
Le morceau avance par cycles de 8 temps (U ≈ 2,553 s) ; toutes les scènes
démarrent sur un début de cycle ou de demi-cycle. Montage musical :
  m 2,751 → 97,219 s (intro, partie A, pont calme, début de la partie B)
  puis m 107,432 → 117,644 s (fin de la partie B et queue du morceau).
"""
import json
import re
import sys
import warnings
from collections import Counter
from pathlib import Path

import openpyxl

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent

NAME_FIXES = {"Patricia LESIMPLE": "LESIMPLE Patricia"}

# ---------- grille musicale ----------
BEAT = 0.3191489410201198
PHASE = 0.1974033241369979
U = 8 * BEAT


def m_unit(k):
    return PHASE + k * U


# segments du montage musical : (début dans le morceau, fin dans le morceau)
MUSIC_EDIT = [(m_unit(1), m_unit(38)), (m_unit(42), m_unit(46))]


def m_to_v(m):
    v0 = 0.0
    for a, b in MUSIC_EDIT:
        if a - 1e-6 <= m < b - 1e-6:
            return v0 + (m - a)
        v0 += b - a
    return None


def r(x):
    return round(x, 4)


# Découpage temporel (secondes vidéo), en cycles U depuis le début de la vidéo.
T = {
    "intro": 0.0,
    "figures": r(2 * U),  # arrivée de la partie A
    "top": r(4.5 * U),
    "t6": r(8.5 * U),
    "t5": r(10.5 * U),
    "t4": r(12.5 * U),
    "t3": r(15 * U),
    "t3page2": r(17 * U),
    "crawlA": r(19 * U),  # pont calme du morceau
    "crawlB": r(26 * U),  # retour de la partie B (drop)
    "outro": r(37 * U),
    "tail": r(39 * U),  # queue du morceau
    "end": r(41 * U),
    "beat": BEAT,
    "U": U,
}


def read_ranking(xlsx):
    wb = openpyxl.load_workbook(xlsx, data_only=True)
    ws = wb["Classement Septembre"]
    people = []
    for row in ws.iter_rows(min_row=5, max_col=4, values_only=True):
        _, label, pts, retraitement = row
        if not label:
            continue
        agence, nom_complet = (s.strip() for s in label.split(":", 1))
        nom_complet = NAME_FIXES.get(nom_complet, nom_complet)
        ventes = int(retraitement if retraitement is not None else pts)
        tokens = nom_complet.split(" ")
        i = 0
        while i < len(tokens) - 1 and tokens[i] == tokens[i].upper():
            i += 1
        people.append(
            {
                "nom": " ".join(tokens[:i]),
                "prenom": " ".join(tokens[i:]),
                "agence": agence,
                "ventes": ventes,
            }
        )
    return people


def video_beats():
    beats = json.loads((HERE / "beats/assets/music/old-sneakers.mp3.json").read_text())["beats"]
    out = []
    for b in beats:
        k = round((b["time"] - PHASE) / BEAT)
        v = m_to_v(PHASE + k * BEAT)
        if v is None or v > T["end"] - 1.2:
            continue
        out.append([r(v), round(b["strength"], 3), 1 if k % 8 == 0 else 0])
    return out


def logo_svg(cls):
    """Logo Médicis en SVG inline, chaque élément classé pour l'animation."""
    src = (HERE / "assets/logo/medicis-blanc-orange.svg").read_text()
    groups = re.findall(r"<g>(.*?)</g>", src, re.S)
    small = re.findall(r'd="([^"]+)"', groups[0])
    big = re.findall(r'd="([^"]+)"', groups[1])
    dots = re.findall(r"<rect[^>]*/>", src)
    swoosh = re.search(r'<path class="st0" d="([^"]+)"', src).group(1)
    parts = [f'<svg class="logo {cls}" viewBox="0 0 452.23 166.12" aria-label="Médicis Immobilier Neuf">']
    parts += [f'<path class="lg-l" fill="#fff" d="{d}"/>' for d in big]
    parts += [re.sub(r'class="st1"', 'class="lg-dot" fill="#fff"', d) for d in dots]
    parts.append(f'<path class="lg-sw" fill="#ea653d" d="{swoosh}"/>')
    parts += [f'<path class="lg-s" fill="#fff" d="{d}"/>' for d in small]
    parts.append("</svg>")
    return "".join(parts)


def main():
    people = read_ranking(sys.argv[1])
    keys = [(p["nom"], p["prenom"]) for p in people]
    assert len(keys) == len(set(keys)), "doublon détecté"

    tiers = {}
    for p in people:
        tiers.setdefault(p["ventes"], []).append(p)
    for v in tiers.values():  # ex æquo : ordre alphabétique, aucun départage
        v.sort(key=lambda p: (p["nom"], p["prenom"]))

    counts = Counter(p["ventes"] for p in people)
    stats = {
        "count": len(people),
        "total": sum(p["ventes"] for p in people),
        "max": max(counts),
    }
    data = {
        "T": T,
        "stats": stats,
        "music": [[r(a), r(b)] for a, b in MUSIC_EDIT],
        "tiers": [
            {"n": n, "people": [{k: p[k] for k in ("nom", "prenom", "agence")} for p in tiers[n]]}
            for n in sorted(tiers, reverse=True)
        ],
    }
    assert len(data["tiers"]) == 7, "la mise en scène attend 7 paliers (top, 4 écrans, 2 défilés)"
    (HERE / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))
    data["beats"] = video_beats()

    mids = [d["n"] for d in data["tiers"][1:5]]
    bounds = [T["t6"], T["t5"], T["t4"], T["t3"], T["crawlA"]]
    sections = "\n".join(
        f'        <section id="s-tier-{n}" class="clip scene" data-start="{bounds[i]}" '
        f'data-duration="{r(bounds[i + 1] - bounds[i] + 0.4)}" data-track-index="1"></section>'
        for i, n in enumerate(mids)
    )
    html = (HERE / "src" / "template.html").read_text()
    repl = {
        "__DATA__": json.dumps(data, ensure_ascii=False),
        "__TIER_SECTIONS__": sections.strip(),
        "__LOGO_INTRO__": logo_svg("logo-intro"),
        "__LOGO_OUTRO__": logo_svg("logo-outro"),
    }
    for k, v in T.items():
        repl[f"__T_{k.upper()}__"] = str(v)
    repl["__D_INTRO__"] = str(r(T["figures"] + 0.7))
    repl["__D_FIGURES__"] = str(r(T["top"] - T["figures"]))
    repl["__D_TOP__"] = str(r(T["t6"] - T["top"] + 0.1))
    repl["__D_TH__"] = str(r(T["outro"] + 0.3 - T["t6"]))
    repl["__D_CRAWL__"] = str(r(T["outro"] + 0.3 - T["crawlA"]))
    repl["__D_OUTRO__"] = str(r(T["end"] - T["outro"]))
    for k, v in sorted(repl.items(), key=lambda kv: -len(kv[0])):
        html = html.replace(k, v)
    assert "__" not in re.sub(r"__timelines|__hyperframes|__hfForceTimelineRebind", "", html), "placeholder oublié"
    (HERE / "index.html").write_text(html)

    print("Décompte de contrôle")
    for n in sorted(tiers, reverse=True):
        print(f"  {n} vente{'s' if n > 1 else ''} : {len(tiers[n])}")
    print(f"  total vendeurs : {stats['count']} | total ventes : {stats['total']} | max : {stats['max']}")
    print(f"  durée vidéo : {T['end']} s")


if __name__ == "__main__":
    main()
