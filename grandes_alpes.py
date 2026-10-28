"""Publie l'article Route des Grandes Alpes dans blog_data.json, avec vos hôtels.

Usage (dans le dossier comparateur-ia) :  python grandes_alpes.py
L'article est inclus dans ce fichier. Une sauvegarde blog_data.json.bak est créée avant toute modification.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

SITE = "https://myhotelcompare.com"
MAX_PAR_ETAPE = 6


def slug(t):
    t = unicodedata.normalize("NFKD", str(t).lower().strip()).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def charger(dossier, prefixe):
    res = []
    d = Path(dossier)
    if not d.exists():
        return res
    for f in sorted(d.glob("*.json")):
        if f.name.startswith("_") or f.name == "promo_semaine.json":
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print("  (ignoré)", f.name, e)
            continue
        if not isinstance(data, dict):
            continue
        for nom, v in data.items():
            if not isinstance(v, dict) or not slug(nom):
                continue
            res.append({"nom": nom, "ville": slug(v.get("ville", "")), "ville_aff": v.get("ville", ""),
                        "pays": slug(v.get("pays", "")), "etoiles": v.get("etoiles"),
                        "url": f"{SITE}/{prefixe}{slug(nom)}.html"})
    return res


import base64, shutil

ARTICLE_B64 = (
    "ewogICJpZCI6ICJyb3V0ZS1kZXMtZ3JhbmRlcy1hbHBlcy10aG9ub24tbWVudG9uIiwKICAidGl0cmUiOiAiTGEgUm91dGUgZGVz"
    "IEdyYW5kZXMgQWxwZXMgOiBkZSBUaG9ub24tbGVzLUJhaW5zIMOgIE1lbnRvbiwgMTggY29scyBldCB6w6lybyBhdXRvcm91dGUi"
    "LAogICJzbHVnIjogInJvdXRlLWRlcy1ncmFuZGVzLWFscGVzLXRob25vbi1tZW50b24iLAogICJpbWFnZSI6ICJpbWFnZXMvcm91"
    "dGUtZGVzLWdyYW5kZXMtYWxwZXMuanBnIiwKICAicmVzdW1lIjogIkVudmlyb24gNzAwIGttLCAxOCBjb2xzLCBkZSBsJ0lzZXJh"
    "biBhdSBHYWxpYmllciA6IGwnaGlzdG9pcmUgZGUgbGEgUm91dGUgZGVzIEdyYW5kZXMgQWxwZXMsIGRlIGxhIGNvbnF1w6p0ZSBk"
    "ZSBsYSBtb250YWduZSDDoCBub3Mgam91cnMsIGF2ZWMgdW4gaXRpbsOpcmFpcmUgZW4gNiDDqXRhcGVzIGRlIFRob25vbi1sZXMt"
    "QmFpbnMgw6AgTWVudG9uLiIsCiAgImRldGFpbHMiOiAiPHA+RWxsZSBhIMOpdMOpIHBlbnPDqWUgcG91ciBsZXMgcHJlbWllcnMg"
    "YXV0b21vYmlsaXN0ZXMsIGF2YW50IG3Dqm1lIHF1ZSBsYSByb3V0ZSBzb2l0IHZyYWltZW50IGZhaXRlIHBvdXIgZXV4LiBBdWpv"
    "dXJkJ2h1aSwgbGEgPHN0cm9uZz5Sb3V0ZSBkZXMgR3JhbmRlcyBBbHBlczwvc3Ryb25nPiByZWxpZSBsZSBsYWMgTMOpbWFuIMOg"
    "IGxhIE3DqWRpdGVycmFuw6llLCBkZSA8c3Ryb25nPlRob25vbi1sZXMtQmFpbnMgw6AgTWVudG9uPC9zdHJvbmc+LCBlbiB0cmF2"
    "ZXJzYW50IGxlcyBBbHBlcyBwYXIgdW5lIHN1Y2Nlc3Npb24gZGUgY29scyBteXRoaXF1ZXMgOiBJc2VyYW4sIEdhbGliaWVyLCBJ"
    "em9hcmQsIENheW9sbGUsIFR1cmluaeKApiBFbnZpcm9uIDcwMCBrbSwgMTggY29scyBldCBwYXMgdW4gbcOodHJlIGQnYXV0b3Jv"
    "dXRlIDogYydlc3QgbGUgcm9hZCB0cmlwIHNhbnMgYXV0b3JvdXRlIHBhciBleGNlbGxlbmNlLiBWb2ljaSBzb24gaGlzdG9pcmUs"
    "IHNvbiBpdGluw6lyYWlyZSBlbiA2IMOpdGFwZXMgZXQgbm9zIGNvbnNlaWxzIHBvdXIgbGEgcGFyY291cmlyLiBQb3VyIGNvbnN0"
    "cnVpcmUgdm90cmUgcHJvcHJlIHRyYWpldCwgZXNzYXlleiBhdXNzaSBub3RyZSA8YSBocmVmPVwiaHR0cHM6Ly9teWhvdGVsY29t"
    "cGFyZS5jb20vaXRpbmVyYWlyZS1kZWNvdXZlcnRlLmh0bWxcIj5wbGFuaWZpY2F0ZXVyIGQnaXRpbsOpcmFpcmUgc2FucyBhdXRv"
    "cm91dGU8L2E+LjwvcD48YnI+PGgyPjEuIFVuZSByb3V0ZSBuw6llIGRlIGxhIGNvbnF1w6p0ZSBkZSBsYSBtb250YWduZTwvaDI+"
    "PGJyPjxwPsOAIGxhIGZpbiBkdSBYSVhlIHNpw6hjbGUsIGxhIGJpY3ljbGV0dGUgcHVpcyBsJ2F1dG9tb2JpbGUgZG9ubmVudCBh"
    "dXggdm95YWdldXJzIGwnZW52aWUgZGUgZnJhbmNoaXIgbGVzIEFscGVzLiBMZSA8c3Ryb25nPlRvdXJpbmcgQ2x1YiBkZSBGcmFu"
    "Y2U8L3N0cm9uZz4sIGQnYWJvcmQgdG91cm7DqSB2ZXJzIGxlIGN5Y2xvdG91cmlzbWUgcHVpcyB2ZXJzIGxlIHRvdXJpc21lIGF1"
    "dG9tb2JpbGUsIGFtw6lsaW9yZSBsZXMgcm91dGVzLCBpbnN0YWxsZSBsYSBzaWduYWxpc2F0aW9uIGV0IHRyYWNlIHBsdXNpZXVy"
    "cyBncmFuZHMgaXRpbsOpcmFpcmVzIHRvdXJpc3RpcXVlcy4gSWwgY29tbWVuY2Ugw6AgdHJhdmFpbGxlciBzdXIgY2VsdWkgZGVz"
    "IEFscGVzIGVuIDxzdHJvbmc+MTkwOTwvc3Ryb25nPiA7IGwnaXRpbsOpcmFpcmUgZXN0IGRlc3NpbsOpIGVuIDxzdHJvbmc+MTkx"
    "MTwvc3Ryb25nPi48L3A+PHA+RW4gPHN0cm9uZz4xOTEzPC9zdHJvbmc+LCBsYSBDb21wYWduaWUgUGFyaXMtTHlvbi1Nw6lkaXRl"
    "cnJhbsOpZSAoUExNKSBvdXZyZSBsYSB0cmF2ZXJzw6llIGNvbXBsw6h0ZSwgZMOpY291cMOpZSBlbiA8c3Ryb25nPjUgw6l0YXBl"
    "czwvc3Ryb25nPiwgYXZlYyBzZXMgYXV0b2NhcnMgcXVpIGZvbnQgZnJhbmNoaXIgbGVzIGNvbHMgYXV4IHZveWFnZXVycy4gTGEg"
    "Z3VlcnJlIGRlIDE5MTQtMTkxOCBpbnRlcnJvbXB0IGxlcyB0cmF2YXV4LiBJbHMgcmVwcmVubmVudCBlbnN1aXRlLCBldCBsYSBy"
    "b3V0ZSBzZSBjb21wbMOodGUgZW4gPHN0cm9uZz4xOTM3PC9zdHJvbmc+IGF2ZWMgbCdpbmF1Z3VyYXRpb24gcGFyIGxlIHByw6lz"
    "aWRlbnQgQWxiZXJ0IExlYnJ1biBkZSBsYSByb3V0ZSBkdSA8c3Ryb25nPmNvbCBkZSBsJ0lzZXJhbjwvc3Ryb25nPiwgYWxvcnMg"
    "cHLDqXNlbnTDqWUgY29tbWUgbGEgcGx1cyBoYXV0ZSByb3V0ZSBkZSBmcmFuY2hpc3NlbWVudCBkJ0V1cm9wZS48L3A+PHA+RCdh"
    "Ym9yZCByw6lzZXJ2w6llIMOgIHVuZSDDqWxpdGUsIGwnYXV0b21vYmlsZSB0b3VjaGUgdW4gcHVibGljIHBsdXMgbGFyZ2UgYXBy"
    "w6hzIGxlcyBhbm7DqWVzIDE5MzAsIGF2ZWMgZGVzIHZvaXR1cmVzIHBsdXMgcGV0aXRlcyBldCBtb2lucyBjaMOocmVzLCBwdWlz"
    "IHZpdCBzb24gw6JnZSBkJ29yIGF2ZWMgbGVzIFRyZW50ZSBHbG9yaWV1c2VzIDogNENWLCAyQ1YsIERhdXBoaW5lLCBDb2NjaW5l"
    "bGxl4oCmIExhIHJvdXRlIGR1IDxzdHJvbmc+Q29ybWV0IGRlIFJvc2VsZW5kPC9zdHJvbmc+IGVzdCBvdXZlcnRlIGVuIDE5NzAs"
    "IGxhIGxpYWlzb24gZGUgVGhvbm9uIMOgIE1lbnRvbiBlc3QgY29tcGzDqXTDqWUgZW4gMTk5NSwgZXQgZGVwdWlzIDIwMTIgbCdh"
    "cnJpdsOpZSBvZmZpY2llbGxlIGRlcyBjeWNsaXN0ZXMgc2UgZmFpdCDDoCA8c3Ryb25nPk5pY2U8L3N0cm9uZz4gKGxlcyBhdXRv"
    "bW9iaWxpc3RlcyBjb250aW51ZW50IHRyYWRpdGlvbm5lbGxlbWVudCBqdXNxdSfDoCBNZW50b24pLiBQb3VyIGVuIHNhdm9pciBw"
    "bHVzIHN1ciBjZXR0ZSDDqXBvcXVlIGRlcyByb3V0ZXMgZGUgdmFjYW5jZXMsIGxpc2V6IG5vdHJlIGFydGljbGUgc3VyIGxhIDxh"
    "IGhyZWY9XCJodHRwczovL215aG90ZWxjb21wYXJlLmNvbS9wYXJpcy1tZW50b24tc2Fucy1hdXRvcm91dGUuaHRtbFwiPk5hdGlv"
    "bmFsZSA3LCBsYSByb3V0ZSBkZXMgdmFjYW5jZXM8L2E+LCBvdSBzdXIgbCdoaXN0b2lyZSBkZXMgPGEgaHJlZj1cImh0dHBzOi8v"
    "bXlob3RlbGNvbXBhcmUuY29tL2hpc3RvaXJlLWNvbmdlcy1wYXllcy1mcmFuY2UtbW9uZGUtb3Utc2Utc2l0dWVudC1zYWxhcmll"
    "cy5odG1sXCI+Y29uZ8OpcyBwYXnDqXM8L2E+IHF1aSBvbnQgbGFuY8OpIGxlcyBGcmFuw6dhaXMgc3VyIGxlcyByb3V0ZXMuPC9w"
    "Pjxicj48aDI+Mi4gTGVzIGNvbHMgZGUgbGEgcm91dGUsIGR1IGxhYyBMw6ltYW4gw6AgbGEgUml2aWVyYTwvaDI+PGJyPjxwPlZv"
    "aWNpIGxlcyBwcmluY2lwYXV4IGNvbHMgZHUgcGFyY291cnMsIGRhbnMgbCdvcmRyZSwgYXZlYyBsZXVyIGFsdGl0dWRlIGFwcHJv"
    "eGltYXRpdmUgKGVsbGUgdmFyaWUgZGUgcXVlbHF1ZXMgbcOodHJlcyBzZWxvbiBsZXMgc291cmNlcykgOjwvcD48dWw+PGxpPjxz"
    "dHJvbmc+Q29sIGRlcyBHZXRzPC9zdHJvbmc+ICgxIDE2MyBtKSA6IHBvcnRlIGQnZW50csOpZSBkYW5zIGxlcyBBbHBlcywgYXUt"
    "ZGVzc3VzIGRlIE1vcnppbmUuPC9saT48bGk+PHN0cm9uZz5Db2wgZGUgbGEgQ29sb21iacOocmU8L3N0cm9uZz4gKDEgNjEzIG0p"
    "IGV0IDxzdHJvbmc+Y29sIGRlcyBBcmF2aXM8L3N0cm9uZz4gKDEgNDg3IG0pIDogbGVzIHByZW1pZXJzIHZyYWlzIHDDonR1cmFn"
    "ZXMgZCdhbHRpdHVkZS48L2xpPjxsaT48c3Ryb25nPkNvbCBkZXMgU2Fpc2llczwvc3Ryb25nPiAoZW52aXJvbiAxIDY1MCBtKSBl"
    "dCA8c3Ryb25nPkNvcm1ldCBkZSBSb3NlbGVuZDwvc3Ryb25nPiAoMSA5NjcgbSkgOiBsZXMgcGF5c2FnZXMgZHUgQmVhdWZvcnRh"
    "aW4sIGF1dG91ciBkdSBsYWMgZGUgUm9zZWxlbmQuPC9saT48bGk+PHN0cm9uZz5Db2wgZGUgbCdJc2VyYW48L3N0cm9uZz4gKDIg"
    "NzY0IG0pIDogbGUgcGx1cyBoYXV0IGNvbCByb3V0aWVyIGRlIGxhIHJvdXRlLCBldCBsJ3VuIGRlcyBwbHVzIGhhdXRzIGRlcyBB"
    "bHBlcy48L2xpPjxsaT48c3Ryb25nPkNvbCBkdSBUw6lsw6lncmFwaGU8L3N0cm9uZz4gKDEgNTY2IG0pLCA8c3Ryb25nPmNvbCBk"
    "dSBHYWxpYmllcjwvc3Ryb25nPiAoZW52aXJvbiAyIDY0MCBtKSBldCA8c3Ryb25nPmNvbCBkdSBMYXV0YXJldDwvc3Ryb25nPiAo"
    "MiAwNTggbSkgOiBsZSB0cmlvIG15dGhpcXVlIGRlIGxhIE1hdXJpZW5uZSBldCBkZSBsJ09pc2FucywgYmllbiBjb25udSBkZXMg"
    "YW1hdGV1cnMgZHUgVG91ciBkZSBGcmFuY2UuPC9saT48bGk+PHN0cm9uZz5Db2wgZCdJem9hcmQ8L3N0cm9uZz4gKDIgMzYwIG0p"
    "IDogbGEgbW9udMOpZSB2ZXJzIGxhIENhc3NlIETDqXNlcnRlLCB1biBwYXlzYWdlIGRlIHJvY2hlcyBwcmVzcXVlIGx1bmFpcmUu"
    "PC9saT48bGk+PHN0cm9uZz5Db2wgZGUgVmFyczwvc3Ryb25nPiAoMiAxMDkgbSkgZXQgPHN0cm9uZz5jb2wgZGUgbGEgQ2F5b2xs"
    "ZTwvc3Ryb25nPiAoMiAzMjYgbSkgOiBsZSBwYXNzYWdlIHZlcnMgbCdVYmF5ZSBldCBsZXMgQWxwZXMtTWFyaXRpbWVzLjwvbGk+"
    "PGxpPjxzdHJvbmc+Q29sIGRlIFZhbGJlcmc8L3N0cm9uZz4gKDEgNjczIG0pLCA8c3Ryb25nPmNvbCBkZSBsYSBDb3VpbGxvbGU8"
    "L3N0cm9uZz4gKDEgNjc4IG0pIGV0IDxzdHJvbmc+Y29sIFNhaW50LU1hcnRpbjwvc3Ryb25nPiAoMSA1MDAgbSkgOiBsZXMgcm91"
    "dGVzIGRlIGwnYXJyacOocmUtcGF5cyBuacOnb2lzLjwvbGk+PGxpPjxzdHJvbmc+Q29sIGRlIFR1cmluaTwvc3Ryb25nPiAoMSA2"
    "MDcgbSkgOiBjw6lsw6hicmUgcG91ciBsZSBSYWxseWUgTW9udGUtQ2FybG8uPC9saT48bGk+PHN0cm9uZz5Db2wgZGUgQ2FzdGls"
    "bG9uPC9zdHJvbmc+ICg3MjggbSkgZXQgPHN0cm9uZz5jb2wgZCfDiHplPC9zdHJvbmc+ICg1MDcgbSkgOiBsYSBkZXNjZW50ZSBm"
    "aW5hbGUgdmVycyBsYSBNw6lkaXRlcnJhbsOpZS48L2xpPjwvdWw+PHA+Q2VydGFpbnMgaXRpbsOpcmFpcmVzIHByb3Bvc2VudCBh"
    "dXNzaSwgZW4gdmFyaWFudGUsIGxhIHJvdXRlIGR1IDxzdHJvbmc+Y29sIGRlIGxhIEJvbmV0dGU8L3N0cm9uZz4gKGVudmlyb24g"
    "MiA4MDAgbSkuPC9wPjxicj48aDI+My4gTCdpdGluw6lyYWlyZSBlbiA2IMOpdGFwZXM8L2gyPjxicj48cD5MYSByb3V0ZSBwZXV0"
    "IHNlIGZhaXJlIGVuIDUgw6AgMTAgam91cnMsIHNlbG9uIHZvdHJlIHbDqWhpY3VsZSBldCB2b3RyZSBlbnZpZSBkZSB2b3VzIGFy"
    "csOqdGVyLiBWb2ljaSB1bmUgcHJvcG9zaXRpb24gZW4gNiDDqXRhcGVzLCBxdWUgdm91cyBwb3V2ZXogYWRhcHRlci4gTGVzIGRp"
    "c3RhbmNlcyB2YXJpZW50IHNlbG9uIGxlcyB2YXJpYW50ZXMgY2hvaXNpZXMgOiB2w6lyaWZpZXotbGVzIHN1ciB2b3RyZSBHUFMu"
    "PC9wPjxicj48aDM+w4l0YXBlIDEgOiBUaG9ub24tbGVzLUJhaW5zIC0gTWVnw6h2ZTwvaDM+PHA+RMOpcGFydCBhdSBib3JkIGR1"
    "IGxhYyBMw6ltYW4sIMOgIDxzdHJvbmc+VGhvbm9uLWxlcy1CYWluczwvc3Ryb25nPiA6IHZvdXMgcG91dmV6IGRlc2NlbmRyZSB2"
    "ZXJzIGxlcyBxdWFpcyBkZSBSaXZlcyBhdmFudCBkZSBwYXJ0aXIuIERpcmVjdGlvbiA8c3Ryb25nPkxlcyBHZXRzPC9zdHJvbmc+"
    "IGV0IHNvbiBjb2wsIHB1aXMgPHN0cm9uZz5DbHVzZXM8L3N0cm9uZz4gZGFucyBsYSB2YWxsw6llIGRlIGwnQXJ2ZSwgbGUgY29s"
    "IGRlIGxhIENvbG9tYmnDqHJlLCBsZSBjb2wgZGVzIEFyYXZpcyBldCBlbmZpbiA8c3Ryb25nPk1lZ8OodmU8L3N0cm9uZz4gKMOp"
    "dGFwZSBkZSBudWl0IHBvc3NpYmxlIGF1c3NpIMOgIDxzdHJvbmc+U2FpbnQtR2VydmFpczwvc3Ryb25nPikuPC9wPjwhLS1IT1RF"
    "TFMgVGhvbm9uLWxlcy1CYWlucywgTWVnw6h2ZSBldCBTYWludC1HZXJ2YWlzIDogdGhvbm9uLWxlcy1iYWlucywgZXZpYW4tbGVz"
    "LWJhaW5zLCBsZXMtZ2V0cywgbW9yemluZSwgY2x1c2VzLCBzYWludC1nZXJ2YWlzLCBzYWludC1nZXJ2YWlzLWxlcy1iYWlucywg"
    "bWVnZXZlLCBjb21ibG91eCwgbGUtZ3JhbmQtYm9ybmFuZCwgbGEtY2x1c2F6LS0+PGJyPjxoMz7DiXRhcGUgMiA6IE1lZ8OodmUg"
    "LSBWYWwtZCdJc8OocmU8L2gzPjxwPkxlIDxzdHJvbmc+Y29sIGRlcyBTYWlzaWVzPC9zdHJvbmc+LCA8c3Ryb25nPkJlYXVmb3J0"
    "PC9zdHJvbmc+IChsYSB2aWxsZSBkdSBmcm9tYWdlIGR1IG3Dqm1lIG5vbSksIGxlIDxzdHJvbmc+Q29ybWV0IGRlIFJvc2VsZW5k"
    "PC9zdHJvbmc+IGV0IDxzdHJvbmc+Qm91cmctU2FpbnQtTWF1cmljZTwvc3Ryb25nPiwgYXZhbnQgZGUgbW9udGVyIHZlcnMgPHN0"
    "cm9uZz5WYWwtZCdJc8OocmU8L3N0cm9uZz4gZXQgbGUgPHN0cm9uZz5jb2wgZGUgbCdJc2VyYW48L3N0cm9uZz4uIFNpIHZvdXMg"
    "c291aGFpdGV6IGRvcm1pciBlbiBiYXMsIEJvdXJnLVNhaW50LU1hdXJpY2UgZXN0IHVuZSDDqXRhcGUgcGx1cyBzaW1wbGUuPC9w"
    "PjwhLS1IT1RFTFMgQmVhdWZvcnQsIEJvdXJnLVNhaW50LU1hdXJpY2UgZXQgVmFsLWQnSXPDqHJlIDogYmVhdWZvcnQsIGxlcy1z"
    "YWlzaWVzLCBib3VyZy1zYWludC1tYXVyaWNlLCBsZXMtYXJjcywgdmFsLWQtaXNlcmUsIHRpZ25lcywgc2FpbnRlLWZveS10YXJl"
    "bnRhaXNlLS0+PGJyPjxoMz7DiXRhcGUgMyA6IFZhbC1kJ0lzw6hyZSAtIEJyaWFuw6dvbjwvaDM+PHA+QXByw6hzIGwnSXNlcmFu"
    "LCBkZXNjZW50ZSB2ZXJzIGxhIE1hdXJpZW5uZSAoPHN0cm9uZz5Nb2RhbmU8L3N0cm9uZz4pLCBwdWlzIGxlIDxzdHJvbmc+Y29s"
    "IGR1IFTDqWzDqWdyYXBoZTwvc3Ryb25nPiwgbGUgPHN0cm9uZz5jb2wgZHUgR2FsaWJpZXI8L3N0cm9uZz4gZXQgbGUgPHN0cm9u"
    "Zz5jb2wgZHUgTGF1dGFyZXQ8L3N0cm9uZz4uIDxzdHJvbmc+TGEgR3JhdmU8L3N0cm9uZz4gZXQgc2VzIHZ1ZXMgc3VyIGxhIE1l"
    "aWplIHZvdXMgYXR0ZW5kZW50IGF2YW50IGQnYXJyaXZlciDDoCA8c3Ryb25nPkJyaWFuw6dvbjwvc3Ryb25nPiwgZG9udCBsZXMg"
    "Zm9ydGlmaWNhdGlvbnMgZGUgVmF1YmFuIHNvbnQgY2xhc3PDqWVzIMOgIGwnVU5FU0NPLjwvcD48IS0tSE9URUxTIE1vZGFuZSwg"
    "VmFsbG9pcmUsIExhIEdyYXZlIGV0IEJyaWFuw6dvbiA6IG1vZGFuZSwgc2FpbnQtbWljaGVsLWRlLW1hdXJpZW5uZSwgdmFsbG9p"
    "cmUsIHZhbG1laW5pZXIsIGxhLWdyYXZlLCBsZS1tb25ldGllci1sZXMtYmFpbnMsIHNlcnJlLWNoZXZhbGllciwgYnJpYW5jb24t"
    "LT48YnI+PGgzPsOJdGFwZSA0IDogQnJpYW7Dp29uIC0gQmFyY2Vsb25uZXR0ZTwvaDM+PHA+TGUgPHN0cm9uZz5jb2wgZCdJem9h"
    "cmQ8L3N0cm9uZz4gZXQgbGEgQ2Fzc2UgRMOpc2VydGUsIHB1aXMgPHN0cm9uZz5FbWJydW48L3N0cm9uZz4gYXUgYm9yZCBkdSBs"
    "YWMgZGUgU2VycmUtUG9uw6dvbiwgbGUgPHN0cm9uZz5jb2wgZGUgVmFyczwvc3Ryb25nPiBldCA8c3Ryb25nPkJhcmNlbG9ubmV0"
    "dGU8L3N0cm9uZz4sIGRhbnMgbGEgdmFsbMOpZSBkZSBsJ1ViYXllLCBjb25udWUgcG91ciBzZXMgdmlsbGFzIGNvbG9yw6llcyBj"
    "b25zdHJ1aXRlcyBwYXIgbGVzIMKrIEJhcmNlbG9ubmV0dGVzIMK7LCBkZXMgaGFiaXRhbnRzIHBhcnRpcyBmYWlyZSBmb3J0dW5l"
    "IGF1IE1leGlxdWUgcHVpcyByZXZlbnVzIGF1IHBheXMuPC9wPjwhLS1IT1RFTFMgRW1icnVuLCBKYXVzaWVycyBldCBCYXJjZWxv"
    "bm5ldHRlIDogZW1icnVuLCBndWlsbGVzdHJlLCB2YXJzLCBqYXVzaWVycywgYmFyY2Vsb25uZXR0ZSwgbGUtbGF1emV0LXViYXll"
    "LS0+PGJyPjxoMz7DiXRhcGUgNSA6IEJhcmNlbG9ubmV0dGUgLSBTYWludC1NYXJ0aW4tVsOpc3ViaWU8L2gzPjxwPkxlIDxzdHJv"
    "bmc+Y29sIGRlIGxhIENheW9sbGU8L3N0cm9uZz4sIHB1aXMgbGEgZGVzY2VudGUgdmVycyBsZXMgZ29yZ2VzIGRlIERhbHVpcywg"
    "PHN0cm9uZz5WYWxiZXJnPC9zdHJvbmc+LCBsZSA8c3Ryb25nPmNvbCBkZSBsYSBDb3VpbGxvbGU8L3N0cm9uZz4gZXQgbGUgPHN0"
    "cm9uZz5jb2wgU2FpbnQtTWFydGluPC9zdHJvbmc+IGp1c3F1J8OgIDxzdHJvbmc+U2FpbnQtTWFydGluLVbDqXN1YmllPC9zdHJv"
    "bmc+LCB1biB2aWxsYWdlIGR1IE1lcmNhbnRvdXIgdHLDqHMgY2FsbWUuPC9wPjwhLS1IT1RFTFMgVmFsYmVyZyBldCBTYWludC1N"
    "YXJ0aW4tVsOpc3ViaWUgOiBndWlsbGF1bWVzLCB2YWxiZXJnLCBiZXVpbCwgc2FpbnQtbWFydGluLXZlc3ViaWUsIGlzb2xhLCBz"
    "YWludC1ldGllbm5lLWRlLXRpbmVlLS0+PGJyPjxoMz7DiXRhcGUgNiA6IFNhaW50LU1hcnRpbi1Ww6lzdWJpZSAtIE1lbnRvbjwv"
    "aDM+PHA+RGVybmnDqHJlIGpvdXJuw6llIDogbGUgPHN0cm9uZz5jb2wgZGUgVHVyaW5pPC9zdHJvbmc+IGV0IHNlcyB2aXJhZ2Vz"
    "IGPDqWzDqGJyZXMsIHB1aXMgbGUgPHN0cm9uZz5jb2wgZGUgQ2FzdGlsbG9uPC9zdHJvbmc+LCBsZSA8c3Ryb25nPmNvbCBkJ8OI"
    "emU8L3N0cm9uZz4gc3VyIGxhIGNvcm5pY2hlLCBldCBsYSBSaXZpZXJhLiBBcnJpdsOpZSDDoCA8c3Ryb25nPk1lbnRvbjwvc3Ry"
    "b25nPiA6IGphcmRpbnMsIHZpZWlsbGUgdmlsbGUgY29sb3LDqWUsIGV0IGbDqnRlIGR1IENpdHJvbiBlbiBmw6l2cmllci4gVm91"
    "cyBwb3V2ZXogYXVzc2kgcHJvbG9uZ2VyIGp1c3F1J8OgIDxzdHJvbmc+TmljZTwvc3Ryb25nPiwgZMOpc29ybWFpcyBsJ2Fycml2"
    "w6llIG9mZmljaWVsbGUgZGVzIGN5Y2xpc3Rlcy48L3A+PCEtLUhPVEVMUyBOaWNlIGV0IE1lbnRvbiA6IG1lbnRvbiwgcm9xdWVi"
    "cnVuZS1jYXAtbWFydGluLCBuaWNlLCBlemUsIHZpbGxlZnJhbmNoZS1zdXItbWVyLCBiZWF1bGlldS1zdXItbWVyLCBjYXAtZC1h"
    "aWwsIG1vbmFjby0tPjxicj48aDI+NC4gTm9zIGNvbnNlaWxzIHByYXRpcXVlczwvaDI+PGJyPjxvbD48bGk+PHN0cm9uZz5QYXJ0"
    "ZXogYXUgYm9uIG1vbWVudCA6PC9zdHJvbmc+IGxlcyBncmFuZHMgY29scyBzb250IGZlcm3DqXMgZW4gaGl2ZXIuIElscyBvdXZy"
    "ZW50IGVuIGfDqW7DqXJhbCBlbnRyZSBqdWluIGV0IG9jdG9icmUgc2Vsb24gbCdlbm5laWdlbWVudCA6IHbDqXJpZmlleiBsJ291"
    "dmVydHVyZSBhdmFudCBkZSBwYXJ0aXIuIE5vdHJlIDxhIGhyZWY9XCJodHRwczovL215aG90ZWxjb21wYXJlLmNvbS9xdWFuZC1w"
    "YXJ0aXItZXQtb3UtY2FsZW5kcmllci12b3lhZ2V1cnMuaHRtbFwiPmNhbGVuZHJpZXIgZGVzIHZveWFnZXVycyBtYWxpbnM8L2E+"
    "IHZvdXMgYWlkZSDDoCBjaG9pc2lyIGxhIGJvbm5lIHDDqXJpb2RlLjwvbGk+PGxpPjxzdHJvbmc+UHLDqXZveWV6IHBsdXMgZGUg"
    "dGVtcHMgcXVlIGQnaGFiaXR1ZGUgOjwvc3Ryb25nPiBsZXMgcm91dGVzIHNvbnQgc2ludWV1c2VzIGV0IGxlcyBwYXlzYWdlcyBp"
    "bnZpdGVudCDDoCBzJ2FycsOqdGVyLiBDb21wdGV6IDUgw6AgNyBqb3VycyBtaW5pbXVtLCBldCBnYXJkZXogdW5lIG1hcmdlIHBv"
    "dXIgbGEgbcOpdMOpby48L2xpPjxsaT48c3Ryb25nPkZhaXRlcyBsZSBwbGVpbiBhdmFudCBsZXMgZ3JhbmRzIGNvbHMsPC9zdHJv"
    "bmc+IGV0IGdhcmRleiBkZSBxdW9pIHZvdXMgY291dnJpciA6IMOgIDIgNTAwIG0sIG3Dqm1lIGVuIMOpdMOpLCBpbCBwZXV0IGZh"
    "aXJlIHRyw6hzIGZyYWlzLCBldCB1biBvcmFnZSBhcnJpdmUgdml0ZS48L2xpPjxsaT48c3Ryb25nPk3DqW5hZ2V6IHZvdHJlIHZv"
    "aXR1cmUgOjwvc3Ryb25nPiB1dGlsaXNleiBsZSBmcmVpbiBtb3RldXIgZGFucyBsZXMgZGVzY2VudGVzIHBvdXIgbmUgcGFzIGZh"
    "aXJlIGNoYXVmZmVyIGxlcyBmcmVpbnMuPC9saT48bGk+PHN0cm9uZz5Sw6lzZXJ2ZXogw6AgbCdhdmFuY2UgOjwvc3Ryb25nPiBs"
    "ZXMgw6l0YXBlcyBlbiBoYXV0ZSBzYWlzb24gKGp1aWxsZXQtYW/Du3QpIHNlIHJlbXBsaXNzZW50IHZpdGUuIENvbXBhcmV6IGxl"
    "cyBwcml4IHN1ciBub3RyZSBwYWdlIDxhIGhyZWY9XCJodHRwczovL215aG90ZWxjb21wYXJlLmNvbS9ob3RlbHMuaHRtbFwiPkjD"
    "tHRlbHM8L2E+IGV0IHN1aXZleiBub3MgY29uc2VpbHMgcG91ciA8YSBocmVmPVwiaHR0cHM6Ly9teWhvdGVsY29tcGFyZS5jb20v"
    "Y29tbWVudC10cm91dmVyLXVuLWhvdGVsLW1vaW5zLWNoZXIuaHRtbFwiPnRyb3V2ZXIgdW4gaMO0dGVsIG1vaW5zIGNoZXI8L2E+"
    "LjwvbGk+PGxpPjxzdHJvbmc+UGFzIGRlIHbDqWhpY3VsZSBhZGFwdMOpID88L3N0cm9uZz4gQ29tcGFyZXogbGVzIG9mZnJlcyBz"
    "dXIgbm90cmUgcGFnZSA8YSBocmVmPVwiaHR0cHM6Ly9teWhvdGVsY29tcGFyZS5jb20vbG91ZXVycy12ZWhpY3VsZXMuaHRtbFwi"
    "PkxvY2F0aW9uIGRlIHbDqWhpY3VsZXM8L2E+IGF2YW50IGRlIHBhcnRpci48L2xpPjxsaT48c3Ryb25nPlN1cnZlaWxsZXogdm90"
    "cmUgYnVkZ2V0IDo8L3N0cm9uZz4gY2FyYnVyYW50LCB0YXhlcyBldCBwcml4IGRlcyB0cmFuc3BvcnRzIHDDqHNlbnQgc3VyIGxl"
    "cyB2YWNhbmNlcy4gTm90cmUgYXJ0aWNsZSBzdXIgbGUgPGEgaHJlZj1cImh0dHBzOi8vbXlob3RlbGNvbXBhcmUuY29tL2J1ZGdl"
    "dC1ldGF0LXZhY2FuY2VzLXRheGUta2Vyb3NlbmUtc3VjcmUuaHRtbFwiPmJ1ZGdldCBkZSBsJ8OJdGF0IGV0IHNvbiBpbXBhY3Qg"
    "c3VyIHZvcyB2YWNhbmNlczwvYT4gZMOpdGFpbGxlIGxlcyBhc3R1Y2VzIHBvdXIgcGFydGlyIG1hbGluLjwvbGk+PC9vbD48YnI+"
    "PHA+VsOpcmlmaWV6IGhvcmFpcmVzLCB0YXJpZnMsIG91dmVydHVyZXMgZGUgY29scyBldCBjb25kaXRpb25zIGRlIGNpcmN1bGF0"
    "aW9uIGF2YW50IGRlIHBhcnRpciA6IGlscyDDqXZvbHVlbnQgZCd1bmUgc2Fpc29uIMOgIGwnYXV0cmUuPC9wPjxicj48ZGl2IGNs"
    "YXNzPVwiZ2xhc3MtYm94XCIgc3R5bGU9XCJtYXJnaW46MjJweCAwOyBib3JkZXItbGVmdDo1cHggc29saWQgdmFyKC0tcHJpbWFy"
    "eSk7IHRleHQtYWxpZ246Y2VudGVyO1wiPjxoMyBzdHlsZT1cIm1hcmdpbi10b3A6MDtcIj7wn6etIFBsYW5pZmlleiB2b3RyZSBw"
    "cm9wcmUgcm91dGU8L2gzPjxwIHN0eWxlPVwibWFyZ2luLWJvdHRvbToxNnB4O1wiPkVudHJleiB2b3RyZSBkw6lwYXJ0IGV0IHZv"
    "dHJlIGFycml2w6llIDogTXlIb3RlbENvbXBhcmUgZMOpY291cGUgdm90cmUgdHJhamV0IHNhbnMgYXV0b3JvdXRlIGVuIMOpdGFw"
    "ZXMsIGF2ZWMgbGlldXggw6AgdmlzaXRlciwgcmVzdGF1cmFudHMsIHZpbGxlLcOpdGFwZSBldCBjb21wYXJhaXNvbiBkZSBjb8O7"
    "dCBhdmVjIGwnYXV0b3JvdXRlLjwvcD48YSBocmVmPVwiaHR0cHM6Ly9teWhvdGVsY29tcGFyZS5jb20vaXRpbmVyYWlyZS1kZWNv"
    "dXZlcnRlLmh0bWxcIiBjbGFzcz1cImJ0blwiPkNhbGN1bGVyIG1vbiBpdGluw6lyYWlyZTwvYT48cCBzdHlsZT1cIm1hcmdpbjox"
    "NnB4IDAgMDtcIj7DgCBsaXJlIGF1c3NpIDogPGEgaHJlZj1cImh0dHBzOi8vbXlob3RlbGNvbXBhcmUuY29tL2Jsb2cuaHRtbFwi"
    "PnRvdXMgbGVzIGFydGljbGVzIGR1IGJsb2c8L2E+PC9wPjwvZGl2PiIKfQ=="
)


def main():
    art = json.loads(base64.b64decode("".join(ARTICLE_B64)).decode("utf-8"))
    fiches = charger("data", "") + charger("data_logements", "atypique-")
    print(f"{len(fiches)} fiche(s) lue(s).")

    def remplacer(m):
        titre, villes = m.group(1).strip(), [slug(v) for v in m.group(2).split(",") if v.strip()]
        trouves = [f for f in fiches if f["ville"] in villes and f["pays"] in ("france", "")]
        trouves = sorted(trouves, key=lambda f: villes.index(f["ville"]))[:MAX_PAR_ETAPE]
        print(f"  {titre} : {len(trouves)} établissement(s)")
        if not trouves:
            return ""
        lis = "".join(
            f'<li><a href="{f["url"]}">{f["nom"]}</a> ({f["ville_aff"]}'
            + (f', {f["etoiles"]} étoiles' if str(f.get("etoiles") or "").strip().isdigit() else "") + ")</li>"
            for f in trouves)
        return f'<h4>Nos hôtels à {titre}</h4><ul>{lis}</ul>'

    art["details"] = re.sub(r"<!--HOTELS\s+(.+?)\s*:\s*(.+?)\s*-->", remplacer, art["details"])

    p = Path("blog_data.json")
    if not p.exists():
        sys.exit("blog_data.json introuvable : lancez le script dans le dossier comparateur-ia.")
    data = json.loads(p.read_text(encoding="utf-8"))
    shutil.copy(p, "blog_data.json.bak")
    if isinstance(data, dict) and isinstance(data.get("articles"), list):
        liste = data["articles"]
    elif isinstance(data, list):
        liste = data
    else:
        sys.exit("Structure de blog_data.json inattendue (ni liste, ni {'articles': [...]}) - envoyez-moi le début du fichier.")
    liste[:] = [a for a in liste if not (isinstance(a, dict) and a.get("slug") == art["slug"])]
    liste.insert(0, art)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK : article ajouté ({len(liste)} articles au total). Sauvegarde : blog_data.json.bak")


if __name__ == "__main__":
    main()