#!/usr/bin/env python3
"""Lit le classement de septembre dans l'Excel, prépare les données de la vidéo
et injecte tout dans index.html (à partir de src/template.html).

Usage : python3 build.py <classement.xlsx>

Arbitrages validés avec la demandeuse (14/10/2026) :
- BARAN Karolina : on retient la colonne « Retraitement » (4 ventes) ;
- « Patricia LESIMPLE » est affichée « LESIMPLE Patricia » ;
- uniquement l'onglet « Classement Septembre » (98 vendeurs).
"""
import json
import sys
import warnings
from collections import Counter
from pathlib import Path

import openpyxl

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent

NAME_FIXES = {"Patricia LESIMPLE": "LESIMPLE Patricia"}

# Découpage temporel (secondes). Toutes les bornes tombent sur la grille 120 BPM (0,5 s).
T = {
    "intro": 0.0,
    "figures": 4.0,
    "top": 10.0,
    "t6": 17.0,
    "t5": 20.5,
    "t4": 24.5,
    "t3": 29.5,
    "t3page2": 34.0,
    "crawl": 38.5,
    "outro": 69.0,
    "end": 73.0,
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
                "source": label,
            }
        )
    return people


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
        "tiers": [
            {"n": n, "people": [{k: p[k] for k in ("nom", "prenom", "agence")} for p in tiers[n]]}
            for n in sorted(tiers, reverse=True)
        ],
    }
    (HERE / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))

    tpl = (HERE / "src" / "template.html").read_text()
    # paliers intermédiaires : les 4 paliers sous le top, un écran chacun
    mids = [d["n"] for d in data["tiers"][1:5]]
    bounds = [T["t6"], T["t5"], T["t4"], T["t3"], T["crawl"]]
    sections = "\n".join(
        f'      <section id="s-tier-{n}" class="clip scene" data-start="{bounds[i]}" '
        f'data-duration="{bounds[i + 1] - bounds[i]}" data-track-index="1"></section>'
        for i, n in enumerate(mids)
    )
    html = tpl
    for k, v in {
        "__DATA__": json.dumps(data, ensure_ascii=False),
        "__TIER_SECTIONS__": sections.strip(),
        "__CRAWL_START__": str(T["crawl"]),
        "__CRAWL_DUR__": str(T["outro"] - T["crawl"]),
        "__OUTRO_START__": str(T["outro"]),
        "__OUTRO_DUR__": str(T["end"] - T["outro"]),
        "__END__": str(T["end"]),
    }.items():
        html = html.replace(k, v)
    (HERE / "index.html").write_text(html)

    print("Décompte de contrôle")
    for n in sorted(tiers, reverse=True):
        print(f"  {n} vente{'s' if n > 1 else ''} : {len(tiers[n])}")
    print(f"  total vendeurs : {stats['count']} | total ventes : {stats['total']} | max : {stats['max']}")


if __name__ == "__main__":
    main()
