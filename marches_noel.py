"""Publie l'article « Marchés de Noël 2026 » dans blog_data.json avec les liens vers vos hôtels ET vos logements atypiques.
Usage (dossier comparateur-ia) :  python marches_noel.py
Sauvegarde automatique : blog_data.json.bak3"""
import base64, json, re, shutil, sys, unicodedata
from pathlib import Path

SITE = "https://myhotelcompare.com"
MAX_HOTELS = 6
MAX_ATYP = 4
ARTICLE_B64 = (
    "eyJpZCI6ICJtYXJjaGVzLWRlLW5vZWwtMjAyNi1vdS1kb3JtaXIiLCAidGl0cmUiOiAiTWFyY2jDqXMgZGUgTm/Dq2wgMjAyNiA6"
    "IGxlcyA2IHZpbGxlcyBsZXMgcGx1cyBmw6llcmlxdWVzIGV0IG/DuSB5IGRvcm1pciIsICJzbHVnIjogIm1hcmNoZXMtZGUtbm9l"
    "bC0yMDI2LW91LWRvcm1pciIsICJpbWFnZSI6ICJpbWFnZXMvbWFyY2hlcy1kZS1ub2VsLmpwZyIsICJyZXN1bWUiOiAiU3RyYXNi"
    "b3VyZywgQ29sbWFyLCBLYXlzZXJzYmVyZywgUmVpbXMsIEx5b24gZXQgQW5uZWN5IDogZGF0ZXMgMjAyNiwgY2hpZmZyZXMgdsOp"
    "cmlmacOpcywgY29uc2VpbHMgcG91ciDDqXZpdGVyIGxhIGZvdWxlIGV0IG5vcyBow7R0ZWxzIGRhbnMgY2hhcXVlIHZpbGxlLiIs"
    "ICJkZXRhaWxzIjogIjxzdHlsZT5cbi5taGMtbm90ZXtib3JkZXItbGVmdDo1cHggc29saWQgIzJkZDRiZjtiYWNrZ3JvdW5kOnJn"
    "YmEoNDUsMjEyLDE5MSwuMTIpO3BhZGRpbmc6MTRweCAxOHB4O2JvcmRlci1yYWRpdXM6MCA4cHggOHB4IDA7bWFyZ2luOjIwcHgg"
    "MH1cbi5taGMtdGVhc2Vye2JhY2tncm91bmQ6cmdiYSgyMzIsOTYsNzYsLjEyKTtwYWRkaW5nOjEycHggMTZweDtib3JkZXItcmFk"
    "aXVzOjhweDttYXJnaW46MjRweCAwfVxuLm1oYy10ZWFzZXIgYntjb2xvcjojZTg2MDRjfVxuLm1oYy10b2N7Ym9yZGVyOjFweCBz"
    "b2xpZCByZ2JhKDEyOCwxMjgsMTI4LC4zNSk7Ym9yZGVyLXJhZGl1czoxMHB4O3BhZGRpbmc6MTRweCAxOHB4O21hcmdpbjoyMHB4"
    "IDB9XG4ubWhjLXRvYyBvbHttYXJnaW46NnB4IDAgMDtwYWRkaW5nLWxlZnQ6MjBweH1cbi5taGMtd3JhcHtvdmVyZmxvdy14OmF1"
    "dG87bWFyZ2luOjIwcHggMH1cbi5taGMtdGFibGV7d2lkdGg6MTAwJTttaW4td2lkdGg6NDgwcHg7Ym9yZGVyLWNvbGxhcHNlOmNv"
    "bGxhcHNlO2JveC1zaGFkb3c6MCAycHggMTBweCByZ2JhKDAsMCwwLC4wOCk7Ym9yZGVyLXJhZGl1czo4cHg7b3ZlcmZsb3c6aGlk"
    "ZGVufVxuLm1oYy10YWJsZSB0aHtiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCg5MGRlZywjZmY3ZjZiLCMyZGQ0YmYpO2NvbG9y"
    "OiNmZmY7dGV4dC1hbGlnbjpsZWZ0O3BhZGRpbmc6MTJweCAxNnB4O2ZvbnQtc2l6ZToxNHB4fVxuLm1oYy10YWJsZSB0ZHtwYWRk"
    "aW5nOjEycHggMTZweDtib3JkZXItYm90dG9tOjFweCBzb2xpZCByZ2JhKDEyOCwxMjgsMTI4LC4yNSl9XG4ubWhjLXRhYmxlIC5u"
    "e3RleHQtYWxpZ246cmlnaHQ7d2hpdGUtc3BhY2U6bm93cmFwfVxuLm1oYy1jYXB7Zm9udC1zaXplOi44NXJlbTtvcGFjaXR5Oi43"
    "NTttYXJnaW4tdG9wOjZweH1cbi5taGMtYmlne2ZvbnQtc2l6ZToyLjZyZW07Zm9udC13ZWlnaHQ6ODAwO2NvbG9yOiNlODYwNGM7"
    "bGluZS1oZWlnaHQ6MS4xO21hcmdpbjoyNHB4IDAgNHB4fVxuLm1oYy1mYWN0c3tkaXNwbGF5OmZsZXg7ZmxleC13cmFwOndyYXA7"
    "Z2FwOjhweDttYXJnaW46MTBweCAwIDE0cHh9XG4ubWhjLWZhY3RzIHNwYW57Ym9yZGVyOjFweCBzb2xpZCByZ2JhKDQ1LDIxMiwx"
    "OTEsLjYpO2JhY2tncm91bmQ6cmdiYSg0NSwyMTIsMTkxLC4xMCk7Ym9yZGVyLXJhZGl1czo5OTlweDtwYWRkaW5nOjRweCAxMnB4"
    "O2ZvbnQtc2l6ZTouOTVyZW19XG4ubWhjLWltZ3tkaXNwbGF5OmJsb2NrO21hcmdpbjoxNHB4IGF1dG87d2lkdGg6MTAwJSFpbXBv"
    "cnRhbnQ7bWF4LXdpZHRoOjUyMHB4IWltcG9ydGFudDtoZWlnaHQ6YXV0byFpbXBvcnRhbnQ7bWF4LWhlaWdodDozNDBweCFpbXBv"
    "cnRhbnQ7b2JqZWN0LWZpdDpjb250YWluO2JvcmRlci1yYWRpdXM6MTJweDtib3gtc2hhZG93OjAgMnB4IDE0cHggcmdiYSgwLDAs"
    "MCwuMTgpfVxuLm1oYy1ob3RlbHN7Ym9yZGVyOjFweCBzb2xpZCByZ2JhKDEyOCwxMjgsMTI4LC4zNSk7Ym9yZGVyLXJhZGl1czox"
    "MHB4O3BhZGRpbmc6MTJweCAxOHB4O21hcmdpbjoxNHB4IDB9XG4ubWhjLWhvdGVscyB1bHttYXJnaW46NnB4IDAgMDtwYWRkaW5n"
    "LWxlZnQ6MjBweH1cbi5taGMtZmFxe2JvcmRlci1ib3R0b206MXB4IHNvbGlkIHJnYmEoMTI4LDEyOCwxMjgsLjMpO3BhZGRpbmc6"
    "MTBweCAwfVxuLm1oYy1mYXEgc3VtbWFyeXtjdXJzb3I6cG9pbnRlcjtmb250LXdlaWdodDo3MDB9XG4ubWhjLWFydHtmb250LXNp"
    "emU6MS4xNXJlbSFpbXBvcnRhbnQ7bGluZS1oZWlnaHQ6MS43IWltcG9ydGFudH1cbi5taGMtYXJ0IHAsLm1oYy1hcnQgbGl7Zm9u"
    "dC1zaXplOjEuMTVyZW0haW1wb3J0YW50O2xpbmUtaGVpZ2h0OjEuNyFpbXBvcnRhbnQ7bWFyZ2luOjAgMCAxNHB4IWltcG9ydGFu"
    "dH1cbi5taGMtYXJ0IGgye2ZvbnQtc2l6ZToxLjdyZW0haW1wb3J0YW50O2xpbmUtaGVpZ2h0OjEuMjUhaW1wb3J0YW50O21hcmdp"
    "bjozMnB4IDAgMTJweCFpbXBvcnRhbnR9XG4ubWhjLWFydCBoM3tmb250LXNpemU6MS4zcmVtIWltcG9ydGFudDttYXJnaW46MjJw"
    "eCAwIDhweCFpbXBvcnRhbnR9XG4ubWhjLWFydCBicntkaXNwbGF5Om5vbmUhaW1wb3J0YW50fVxuLm1oYy1hcnQgLm1oYy13cmFw"
    "LC5taGMtYXJ0IC5taGMtbm90ZSwubWhjLWFydCAubWhjLXRlYXNlciwubWhjLWFydCAubWhjLXRvY3ttYXJnaW46MTZweCAwIWlt"
    "cG9ydGFudH1cbi5taGMtYXJ0IHRhYmxle2ZvbnQtc2l6ZToxLjA1cmVtIWltcG9ydGFudDttYXJnaW46MCFpbXBvcnRhbnR9XG4u"
    "bWhjLWFydCAubWhjLXRhYmxlIHRkLC5taGMtYXJ0IC5taGMtdGFibGUgdGh7cGFkZGluZzoxMHB4IDE0cHghaW1wb3J0YW50fVxu"
    "Lm1oYy1hcnQgLm1oYy1jYXB7Zm9udC1zaXplOi45cmVtIWltcG9ydGFudDttYXJnaW46NnB4IDAgMTZweCFpbXBvcnRhbnR9XG4u"
    "bWhjLWFydCAubWhjLWZhY3RzIHNwYW57Zm9udC1zaXplOi45NXJlbSFpbXBvcnRhbnR9XG4ubWhjLWFydCAubWhjLWhvdGVscyBs"
    "aXttYXJnaW46MCAwIDZweCFpbXBvcnRhbnQ7Zm9udC1zaXplOjEuMDVyZW0haW1wb3J0YW50fVxuPC9zdHlsZT5cblxuPGRpdiBj"
    "bGFzcz1cIm1oYy1hcnRcIj5cbjxwPjxzdHJvbmc+TGVzIG1hcmNow6lzIGRlIE5vw6tsIG91dnJlbnQgY2V0dGUgc2VtYWluZS48"
    "L3N0cm9uZz4gRW50cmUgbGUgMjAgbm92ZW1icmUgZXQgbGUgMyBqYW52aWVyLCBzaXggdmlsbGVzIGRlIEZyYW5jZSBwcm9wb3Nl"
    "bnQgZGVzIG1hcmNow6lzIHRyw6hzIGRpZmbDqXJlbnRzIDogdW4gbWFyY2jDqSB2aWV1eCBkZSBwbHVzaWV1cnMgc2nDqGNsZXMs"
    "IGRlcyBtYWlzb25zIMOgIGNvbG9tYmFnZXMsIHVuIHZpbGxhZ2UgYWxzYWNpZW4gb3V2ZXJ0IHNldWxlbWVudCBsZSB3ZWVrLWVu"
    "ZCwgbGEgQ2hhbXBhZ25lLCBsYSBmw6p0ZSBkZXMgTHVtacOocmVzIG91IHVuIGxhYyBkZXMgQWxwZXMuPC9wPlxuPGRpdiBjbGFz"
    "cz1cIm1oYy1ub3RlXCI+PHN0cm9uZz5EYXRlcyAyMDI2IHbDqXJpZmnDqWVzPC9zdHJvbmc+IGF1cHLDqHMgZGVzIHNpdGVzIGRl"
    "cyB2aWxsZXMgZXQgZGUgbGEgcHJlc3NlIGF1IDIyIG5vdmVtYnJlIDIwMjYuIExlcyBob3JhaXJlcyBwZXV2ZW50IGVuY29yZSBj"
    "aGFuZ2VyIDogdsOpcmlmaWV6LWxlcyBzdXIgbGUgc2l0ZSBvZmZpY2llbCBkZSBsYSB2aWxsZSBhdmFudCBkZSBwYXJ0aXIuPC9k"
    "aXY+XG48ZmlndXJlIHN0eWxlPVwibWFyZ2luOjE4cHggMFwiPjxpbWcgY2xhc3M9XCJtaGMtaW1nXCIgc3JjPVwiaHR0cHM6Ly9t"
    "eWhvdGVsY29tcGFyZS5jb20vaW1hZ2VzL21hcmNoZXMtbm9lbC1jYXJ0ZS5qcGdcIiBhbHQ9XCJDYXJ0ZSBkZSBGcmFuY2UgZGVz"
    "IHNpeCBtYXJjaMOpcyBkZSBOb8OrbCA6IFN0cmFzYm91cmcsIENvbG1hciwgS2F5c2Vyc2JlcmcsIFJlaW1zLCBMeW9uIGV0IEFu"
    "bmVjeVwiIGxvYWRpbmc9XCJsYXp5XCI+PGZpZ2NhcHRpb24gY2xhc3M9XCJtaGMtY2FwXCIgc3R5bGU9XCJ0ZXh0LWFsaWduOmNl"
    "bnRlclwiPkxlcyBzaXggdmlsbGVzIGRlIG5vdHJlIHPDqWxlY3Rpb24gKGNhcnRlIHNjaMOpbWF0aXF1ZSwgcG9zaXRpb25zIGFw"
    "cHJveGltYXRpdmVzKS48L2ZpZ2NhcHRpb24+PC9maWd1cmU+XG48ZGl2IGNsYXNzPVwibWhjLXRvY1wiPjxzdHJvbmc+U29tbWFp"
    "cmU8L3N0cm9uZz48b2w+PGxpPjxhIGhyZWY9XCIjbWhjLXN0cmFzYm91cmdcIj5TdHJhc2JvdXJnPC9hPjwvbGk+PGxpPjxhIGhy"
    "ZWY9XCIjbWhjLWNvbG1hclwiPkNvbG1hcjwvYT48L2xpPjxsaT48YSBocmVmPVwiI21oYy1rYXlzZXJzYmVyZ1wiPktheXNlcnNi"
    "ZXJnPC9hPjwvbGk+PGxpPjxhIGhyZWY9XCIjbWhjLXJlaW1zXCI+UmVpbXM8L2E+PC9saT48bGk+PGEgaHJlZj1cIiNtaGMtbHlv"
    "blwiPkx5b248L2E+PC9saT48bGk+PGEgaHJlZj1cIiNtaGMtYW5uZWN5XCI+QW5uZWN5PC9hPjwvbGk+PGxpPjxhIGhyZWY9XCIj"
    "bWhjLXRhYmxlYXVcIj5MZSBjYWxlbmRyaWVyIGVuIHVuIGNvdXAgZOKAmcWTaWw8L2E+PC9saT48bGk+PGEgaHJlZj1cIiNtaGMt"
    "Y29uc2VpbHNcIj5Ob3MgY29uc2VpbHMgcG91ciBiaWVuIGxlcyB2aXNpdGVyPC9hPjwvbGk+PGxpPjxhIGhyZWY9XCIjbWhjLWZh"
    "cVwiPlF1ZXN0aW9ucyBmcsOpcXVlbnRlczwvYT48L2xpPjwvb2w+PC9kaXY+XG48aDIgaWQ9XCJtaGMtc3RyYXNib3VyZ1wiPjEu"
    "IFN0cmFzYm91cmcsIGxhIMKrIGNhcGl0YWxlIGRlIE5vw6tsIMK7PC9oMj48ZGl2IGNsYXNzPVwibWhjLWZhY3RzXCI+PHNwYW4+"
    "Mjcgbm92ZW1icmUg4oCTIDI0IGTDqWNlbWJyZTwvc3Bhbj48c3Bhbj44IG1hcmNow6lzPC9zcGFuPjxzcGFuPmRlcHVpcyAxNTcw"
    "PC9zcGFuPjwvZGl2PjxwPkxhIFZpbGxlIGRlIFN0cmFzYm91cmcgZmFpdCBuYcOudHJlIHNvbiBtYXJjaMOpLCBsZSBDaHJpc3Rr"
    "aW5kZWxzbcOkcmlrLCBlbiAxNTcwIGV0IGxlIHByw6lzZW50ZSBjb21tZSBs4oCZdW4gZGVzIHBsdXMgYW5jaWVucyBk4oCZRXVy"
    "b3BlLiBFbGxlIHNlIGRpdCDCqyBDYXBpdGFsZSBkZSBOb8OrbCDCuyBkZXB1aXMgMTk5Mi4gRW4gMjAyNiwgbOKAmW91dmVydHVy"
    "ZSBhIGxpZXUgbGUgPHN0cm9uZz52ZW5kcmVkaSAyNyBub3ZlbWJyZTwvc3Ryb25nPiwgYXZlYyBodWl0IG1hcmNow6lzIGRhbnMg"
    "bGUgY2VudHJlIGhpc3RvcmlxdWUgZXQgbGUgZ3JhbmQgc2FwaW4gZGUgbGEgcGxhY2UgS2zDqWJlci4gTGEgdmlsbGUgYW5ub25j"
    "ZSBlbnZpcm9uIHRyb2lzIG1pbGxpb25zIGRlIHZpc2l0ZXVycyBwYXIgYW4uPC9wPjxmaWd1cmUgc3R5bGU9XCJtYXJnaW46MThw"
    "eCAwXCI+PGltZyBjbGFzcz1cIm1oYy1pbWdcIiBzcmM9XCJodHRwczovL215aG90ZWxjb21wYXJlLmNvbS9pbWFnZXMvbWFyY2hl"
    "LW5vZWwtc3RyYXNib3VyZy5qcGdcIiBhbHQ9XCJNYXJjaMOpIGRlIE5vw6tsIGRlIFN0cmFzYm91cmcsIGdyYW5kIHNhcGluIGls"
    "bHVtaW7DqVwiIGxvYWRpbmc9XCJsYXp5XCI+PGZpZ2NhcHRpb24gY2xhc3M9XCJtaGMtY2FwXCIgc3R5bGU9XCJ0ZXh0LWFsaWdu"
    "OmNlbnRlclwiPkxlIGdyYW5kIHNhcGluIGV0IGxlcyBjaGFsZXRzIGR1IG1hcmNow6kgZGUgTm/Dq2wgZGUgU3RyYXNib3VyZyAo"
    "aW1hZ2UgZOKAmWlsbHVzdHJhdGlvbikuPC9maWdjYXB0aW9uPjwvZmlndXJlPjxwPjxzdHJvbmc+w4Agc2F2b2lyIDo8L3N0cm9u"
    "Zz4gbGVzIHZvaXR1cmVzIHNvbnQgaW50ZXJkaXRlcyBkYW5zIGxhIEdyYW5kZSDDjmxlIGF1eCBoZXVyZXMgZOKAmW91dmVydHVy"
    "ZS4gTGUgcGFya2luZyByZWxhaXMgKFArUikgZGUgbGEgQ1RTIGNvw7t0ZSA0LDIwIOKCrCBsYSBqb3VybsOpZSwgYnVzIGV0IHRy"
    "YW0gY29tcHJpcywgZXQgbGEgZ2FyZSBlc3Qgw6AgMTAgbWludXRlcyDDoCBwaWVkIGRlcyBwcmVtaWVycyBjaGFsZXRzLiBMZSBn"
    "b2JlbGV0IGVzdCBjb25zaWduw6kgMSDigqwuPC9wPjwhLS1IT1RFTFMgU3RyYXNib3VyZyB8IGZyYW5jZSB8IHN0cmFzYm91cmcg"
    "fCBpbGxraXJjaCxzY2hpbHRpZ2hlaW0sYmlzY2hoZWltLHNvdWZmZWx3ZXllcnNoZWltLG9iZXJuYWksbW9sc2hlaW0sa2VobCxn"
    "ZWlzcG9sc2hlaW0tLT5cbjxoMiBpZD1cIm1oYy1jb2xtYXJcIj4yLiBDb2xtYXIsIHNpeCBtYXJjaMOpcyBldCBsYSBQZXRpdGUg"
    "VmVuaXNlPC9oMj48ZGl2IGNsYXNzPVwibWhjLWZhY3RzXCI+PHNwYW4+MjMgbm92ZW1icmUg4oCTIDI5IGTDqWNlbWJyZTwvc3Bh"
    "bj48c3Bhbj42IG1hcmNow6lzPC9zcGFuPjxzcGFuPmNyw6nDqSBlbiAxOTg4PC9zcGFuPjwvZGl2PjxwPkNvbG1hciBjb21wdGUg"
    "c2l4IG1hcmNow6lzIDogcGxhY2UgSmVhbm5lLWTigJlBcmMsIHBsYWNlIGRlIGzigJlBbmNpZW5uZS1Eb3VhbmUsIGxlIEtvw69m"
    "aHVzIChtYXJjaMOpIGNvdXZlcnQpLCBwbGFjZSBkZXMgRG9taW5pY2FpbnMsIGxlIG1hcmNow6kgZGVzIGVuZmFudHMgZGUgbGEg"
    "UGV0aXRlIFZlbmlzZSBldCBsZSBNYXJjaMOpIEdvdXJtYW5kIGRlIGxhIE1vbnRhZ25lIFZlcnRlLiBMZXMgY2hhbGV0cyBzb250"
    "IG91dmVydHMgZGUgMTEgaCDDoCAxOSBoIGR1IGx1bmRpIGF1IGpldWRpIGV0IGRlIDEwIGggw6AgMjAgaCBkdSB2ZW5kcmVkaSBh"
    "dSBkaW1hbmNoZS4gTGUgMjQgZMOpY2VtYnJlLCBpbHMgZmVybWVudCDDoCAxNyBoLiBMZSBNYXJjaMOpIEdvdXJtYW5kIHJlc3Rl"
    "IG91dmVydCBqdXNxdeKAmWF1IDMgamFudmllciAyMDI3LjwvcD48ZmlndXJlIHN0eWxlPVwibWFyZ2luOjE4cHggMFwiPjxpbWcg"
    "Y2xhc3M9XCJtaGMtaW1nXCIgc3JjPVwiaHR0cHM6Ly9teWhvdGVsY29tcGFyZS5jb20vaW1hZ2VzL21hcmNoZS1ub2VsLWNvbG1h"
    "ci5qcGdcIiBhbHQ9XCJQZXRpdGUgVmVuaXNlIGRlIENvbG1hciBpbGx1bWluw6llIHBvdXIgTm/Dq2xcIiBsb2FkaW5nPVwibGF6"
    "eVwiPjxmaWdjYXB0aW9uIGNsYXNzPVwibWhjLWNhcFwiIHN0eWxlPVwidGV4dC1hbGlnbjpjZW50ZXJcIj5MYSBQZXRpdGUgVmVu"
    "aXNlIGRlIENvbG1hciBldCBzZXMgbWFpc29ucyDDoCBjb2xvbWJhZ2VzIGF1IGJvcmQgZGUgbOKAmWVhdSAoaW1hZ2UgZOKAmWls"
    "bHVzdHJhdGlvbikuPC9maWdjYXB0aW9uPjwvZmlndXJlPjxwPkxlIG1hcmNow6kgZGF0ZSBkZSAxOTg4IGV0IGF0dGlyZSBwbHVz"
    "IGRlIGRldXggbWlsbGlvbnMgZGUgdmlzaXRldXJzLCBzZWxvbiBsZXMgc291cmNlcyB0b3VyaXN0aXF1ZXMuIExlIHNvaXIsIGxl"
    "cyBpbGx1bWluYXRpb25zIGRlIGxhIEdyYW5k4oCZUnVlIGV0IGRlcyBxdWFpcyBkdSBjYW5hbCB2YWxlbnQgbGUgZMOpdG91ci48"
    "L3A+PHA+PHN0cm9uZz7DgCBzYXZvaXIgOjwvc3Ryb25nPiBTdHJhc2JvdXJnIGVzdCDDoCBlbnZpcm9uIDMwIG1pbnV0ZXMgZW4g"
    "dHJhaW4sIE11bGhvdXNlIMOgIDIwIG1pbnV0ZXMgZXQgQsOibGUgw6AgNDUgbWludXRlcy4gTGVzIG5hdmV0dGVzIGR1IHBhcmtp"
    "bmcgcmVsYWlzIG5lIGNpcmN1bGVudCBxdWUgbGVzIHdlZWstZW5kcyBkZSBs4oCZQXZlbnQuIMOJdml0ZXogbGVzIHdlZWstZW5k"
    "cyA6IGxlcyBwYXJraW5ncyBlbiBwbGVpbiBhaXIgc29udCBwbGVpbnMgZMOocyAxMSBoLjwvcD48IS0tSE9URUxTIENvbG1hciB8"
    "IGZyYW5jZSB8IGNvbG1hciB8IGVndWlzaGVpbSxyaXF1ZXdpaHIscmliZWF1dmlsbGUsdHVyY2toZWltLG11bnN0ZXIsYmVyZ2hl"
    "aW0sc2lnb2xzaGVpbSxraWVudHpoZWltLHdldHRvbHNoZWltLS0+XG48aDIgaWQ9XCJtaGMta2F5c2Vyc2JlcmdcIj4zLiBLYXlz"
    "ZXJzYmVyZywgbGUgdmlsbGFnZSBkdSB3ZWVrLWVuZDwvaDI+PGRpdiBjbGFzcz1cIm1oYy1mYWN0c1wiPjxzcGFuPjQgd2Vlay1l"
    "bmRzPC9zcGFuPjxzcGFuPnZlbmRyZWRpIOKAkyBkaW1hbmNoZTwvc3Bhbj48c3Bhbj4xMCBoIOKAkyAyMCBoPC9zcGFuPjwvZGl2"
    "PjxwPktheXNlcnNiZXJnIG7igJlvdXZyZSBzb24gbWFyY2jDqSBxdWUgbGVzIDxzdHJvbmc+dmVuZHJlZGlzLCBzYW1lZGlzIGV0"
    "IGRpbWFuY2hlcyBkZSBs4oCZQXZlbnQ8L3N0cm9uZz4gOiAyNyBhdSAyOSBub3ZlbWJyZSwgNCBhdSA2LCAxMSBhdSAxMyBldCAx"
    "OCBhdSAyMCBkw6ljZW1icmUgMjAyNiwgZGUgMTAgaCDDoCAyMCBoLiBMZXMgY2hhbGV0cyBz4oCZaW5zdGFsbGVudCBkYW5zIGxh"
    "IGNvdXIgZGUgbOKAmUFyc2VuYWwgZXQgZGVycmnDqHJlIGzigJnDqWdsaXNlIFNhaW50ZS1Dcm9peCwgYXZlYyBwYWluIGTigJnD"
    "qXBpY2VzLCB2aW4gY2hhdWQsIGJyZXR6ZWxzLCBwZXRpdHMgYmlzY3VpdHMgZGUgTm/Dq2wgKGxlcyBicmVkZWxlKSBldCBhcnRp"
    "c2FuYXQgKGpvdWV0cyBlbiBib2lzLCB2ZXJyZSBzb3VmZmzDqSwgZMOpY29yYXRpb25zKS48L3A+PGZpZ3VyZSBzdHlsZT1cIm1h"
    "cmdpbjoxOHB4IDBcIj48aW1nIGNsYXNzPVwibWhjLWltZ1wiIHNyYz1cImh0dHBzOi8vbXlob3RlbGNvbXBhcmUuY29tL2ltYWdl"
    "cy9tYXJjaGUtbm9lbC1rYXlzZXJzYmVyZy5qcGdcIiBhbHQ9XCJDaGFsZXRzIGTDqWNvcsOpcyBk4oCZdW4gbWFyY2jDqSBkZSBO"
    "b8OrbCBhbHNhY2llblwiIGxvYWRpbmc9XCJsYXp5XCI+PGZpZ2NhcHRpb24gY2xhc3M9XCJtaGMtY2FwXCIgc3R5bGU9XCJ0ZXh0"
    "LWFsaWduOmNlbnRlclwiPkNoYWxldHMgZXQgZMOpY29yYXRpb25zIGTigJl1biBtYXJjaMOpIGRlIE5vw6tsIGFsc2FjaWVuIChp"
    "bWFnZSBk4oCZaWxsdXN0cmF0aW9uKS48L2ZpZ2NhcHRpb24+PC9maWd1cmU+PHA+TGUgdmlsbGFnZSBhIMOpdMOpIMOpbHUgwqsg"
    "VmlsbGFnZSBwcsOpZsOpcsOpIGRlcyBGcmFuw6dhaXMgwrsgZW4gMjAxNywgc3VyIEZyYW5jZSAyLCBldCB1bmUgcGxhcXVlIGxl"
    "IHJhcHBlbGxlIHN1ciBsZSBwb250IGZvcnRpZmnDqS48L3A+PCEtLUhPVEVMUyBLYXlzZXJzYmVyZyB8IGZyYW5jZSB8IGtheXNl"
    "cnNiZXJnLGFtbWVyc2Nod2locixraWVudHpoZWltIHwgcmlxdWV3aWhyLHJpYmVhdXZpbGxlLHR1cmNraGVpbSxlZ3Vpc2hlaW0s"
    "Y29sbWFyLHNpZ29sc2hlaW0sbXVuc3RlcixvcmJleSxsYXBvdXRyb2llLS0+XG48aDIgaWQ9XCJtaGMtcmVpbXNcIj40LiBSZWlt"
    "cywgbGUgbWFyY2jDqSBkZSBDaGFtcGFnbmU8L2gyPjxkaXYgY2xhc3M9XCJtaGMtZmFjdHNcIj48c3Bhbj4yNSBub3ZlbWJyZSDi"
    "gJMgMjcgZMOpY2VtYnJlPC9zcGFuPjxzcGFuPmVudmlyb24gMTUwIGNoYWxldHM8L3NwYW4+PHNwYW4+Z3JhbmRlIHJvdWUgZGUg"
    "NTUgbTwvc3Bhbj48L2Rpdj48cD7DgCBSZWltcywgbGUgbWFyY2jDqSBz4oCZaW5zdGFsbGUgc3VyIGxlcyBIYXV0ZXMgUHJvbWVu"
    "YWRlcyBKZWFuLUxvdWlzLVNjaG5laXRlciBldCBs4oCZZXNwbGFuYWRlIGRlIGxhIHBvcnRlIGRlIE1hcnMsIGF2ZWMgZW52aXJv"
    "biAxNTAgY2hhbGV0cy4gVW5lIGdyYW5kZSByb3VlIGRlIDU1IG3DqHRyZXMgc2UgZHJlc3NlIHBsYWNlIGTigJlFcmxvbiAoOCDi"
    "gqwgcG91ciBsZXMgYWR1bHRlcywgNiDigqwgcG91ciBsZXMgZW5mYW50cykuIExlIHNwZWN0YWNsZSBkZSBsdW1pw6hyZSDCqyBS"
    "ZWdhbGlhIMK7IGVzdCBwcm9qZXTDqSBncmF0dWl0ZW1lbnQgc3VyIGxhIGZhw6dhZGUgZGUgbGEgY2F0aMOpZHJhbGUgbGUgdmVu"
    "ZHJlZGkgZXQgbGUgc2FtZWRpIMOgIDIwIGgganVzcXXigJlhdSAzIGphbnZpZXIsIHNhdWYgZXhjZXB0aW9uIDogdsOpcmlmaWV6"
    "IGxlcyBkYXRlcyBhdmFudCBkZSBwYXJ0aXIuPC9wPjxmaWd1cmUgc3R5bGU9XCJtYXJnaW46MThweCAwXCI+PGltZyBjbGFzcz1c"
    "Im1oYy1pbWdcIiBzcmM9XCJodHRwczovL215aG90ZWxjb21wYXJlLmNvbS9pbWFnZXMvbWFyY2hlLW5vZWwtcmVpbXMuanBnXCIg"
    "YWx0PVwiTWFyY2jDqSBkZSBOb8OrbCBkZSBSZWltcyBhdmVjIGxhIGdyYW5kZSByb3VlIGV0IGxhIGNhdGjDqWRyYWxlXCIgbG9h"
    "ZGluZz1cImxhenlcIj48ZmlnY2FwdGlvbiBjbGFzcz1cIm1oYy1jYXBcIiBzdHlsZT1cInRleHQtYWxpZ246Y2VudGVyXCI+QWxs"
    "w6llIGRlIGNoYWxldHMgZHUgbWFyY2jDqSBkZSBOb8OrbCBkZSBSZWltcywgYXZlYyBsYSBncmFuZGUgcm91ZSBldCBsYSBjYXRo"
    "w6lkcmFsZSBhdSBmb25kIChpbWFnZSBk4oCZaWxsdXN0cmF0aW9uKS48L2ZpZ2NhcHRpb24+PC9maWd1cmU+PHA+PHN0cm9uZz7D"
    "gCBzYXZvaXIgOjwvc3Ryb25nPiBqdXNxdeKAmWF1IDIwIGTDqWNlbWJyZSwgbGVzIGNoYWxldHMgc29udCBvdXZlcnRzIGRlIDEx"
    "IGggMzAgw6AgMjEgaCBkdSBtYXJkaSBhdSBqZXVkaSwganVzcXXigJnDoCAyMiBoIGxlIHZlbmRyZWRpIGV0IGRlIDEwIGggw6Ag"
    "MjIgaCBsZSBzYW1lZGkuIElscyBzb250IGZlcm3DqXMgbGUgMjUgZMOpY2VtYnJlLCBldCBsZSAyNCBpbHMgZmVybWVudCDDoCAx"
    "OCBoLjwvcD48IS0tSE9URUxTIFJlaW1zIHwgZnJhbmNlIHwgcmVpbXMgfCBlcGVybmF5LHRpbnF1ZXV4LGJlemFubmVzLGNvcm1v"
    "bnRyZXVpbCxheSxoYXV0dmlsbGVycyxjaGFtcGlsbG9uLG11dGlnbnktLT5cbjxoMiBpZD1cIm1oYy1seW9uXCI+NS4gTHlvbiwg"
    "ZW50cmUgbWFyY2jDqSBldCBmw6p0ZSBkZXMgTHVtacOocmVzPC9oMj48ZGl2IGNsYXNzPVwibWhjLWZhY3RzXCI+PHNwYW4+MjAg"
    "bm92ZW1icmUg4oCTIDI0IGTDqWNlbWJyZTwvc3Bhbj48c3Bhbj5wbHVzIGRlIDEwMCBjaGFsZXRzPC9zcGFuPjxzcGFuPkx1bWnD"
    "qHJlcyA6IDUg4oCTIDggZMOpY2VtYnJlPC9zcGFuPjwvZGl2PjxwPkxlIG1hcmNow6kgZGUgTm/Dq2wgZGUgTHlvbiBzZSB0aWVu"
    "dCBwbGFjZSBDYXJub3QsIMOgIGPDtHTDqSBkZSBsYSBnYXJlIGRlIFBlcnJhY2hlLCBkdSA8c3Ryb25nPjIwIG5vdmVtYnJlIGF1"
    "IDI0IGTDqWNlbWJyZTwvc3Ryb25nPiwgYXZlYyBwbHVzIGRlIDEwMCBjaGFsZXRzIGV0IGVudmlyb24gNTAwIDAwMCB2aXNpdGV1"
    "cnMgcGFyIMOpZGl0aW9uIGTigJlhcHLDqHMgbGEgVmlsbGUuIElsIGVzdCBwcsOpc2VudMOpIGNvbW1lIGxlIHBsdXMgZ3JhbmQg"
    "ZGUgbGEgcsOpZ2lvbi48L3A+PGZpZ3VyZSBzdHlsZT1cIm1hcmdpbjoxOHB4IDBcIj48aW1nIGNsYXNzPVwibWhjLWltZ1wiIHNy"
    "Yz1cImh0dHBzOi8vbXlob3RlbGNvbXBhcmUuY29tL2ltYWdlcy9tYXJjaGUtbm9lbC1seW9uLmpwZ1wiIGFsdD1cIk1hcmNow6kg"
    "ZGUgTm/Dq2wgw6AgTHlvbiBhdmVjIGdyYW5kZSByb3VlLCBwYXRpbm9pcmUgZXQgYmFzaWxpcXVlIGRlIEZvdXJ2acOocmVcIiBs"
    "b2FkaW5nPVwibGF6eVwiPjxmaWdjYXB0aW9uIGNsYXNzPVwibWhjLWNhcFwiIHN0eWxlPVwidGV4dC1hbGlnbjpjZW50ZXJcIj5B"
    "bWJpYW5jZSBkZSBOb8OrbCDDoCBMeW9uLCBhdmVjIGxhIGdyYW5kZSByb3VlLCBsYSBwYXRpbm9pcmUgZXQgbGEgYmFzaWxpcXVl"
    "IGRlIEZvdXJ2acOocmUgZW4gZm9uZCAoaW1hZ2UgZOKAmWlsbHVzdHJhdGlvbikuPC9maWdjYXB0aW9uPjwvZmlndXJlPjxwPkR1"
    "IDxzdHJvbmc+NSBhdSA4IGTDqWNlbWJyZTwvc3Ryb25nPiwgbGEgRsOqdGUgZGVzIEx1bWnDqHJlcyBhbmltZSB0b3V0ZSBsYSB2"
    "aWxsZSwgZXQgbGUgbWFyY2jDqSBwZXV0IGZlcm1lciBwbHVzIHTDtHQgY2VzIGpvdXJzLWzDoCA6IGzigJloZXVyZSBu4oCZZXN0"
    "IHBhcyBlbmNvcmUgcHVibGnDqWUgcG91ciAyMDI2LiBMZXMgdmFjYW5jZXMgZGUgTm/Dq2wgY29tbWVuY2VudCBsZSAxOSBkw6lj"
    "ZW1icmUgw6AgTHlvbiwgZXQgbGVzIGRlcm5pZXJzIGpvdXJzIHNvbnQgZG9uYyBsZXMgcGx1cyBjaGFyZ8Opcy48L3A+PCEtLUhP"
    "VEVMUyBMeW9uIHwgZnJhbmNlIHwgbHlvbiB8IHZpbGxldXJiYW5uZSxjYWx1aXJlLHZhdWx4LGJyb24sZWN1bGx5LHRhc3Npbixv"
    "dWxsaW5zLGZyYW5jaGV2aWxsZS0tPlxuPGgyIGlkPVwibWhjLWFubmVjeVwiPjYuIEFubmVjeSwgbGUgTm/Dq2wgZGVzIEFscGVz"
    "PC9oMj48ZGl2IGNsYXNzPVwibWhjLWZhY3RzXCI+PHNwYW4+MjYgbm92ZW1icmUg4oCTIDMgamFudmllcjwvc3Bhbj48c3Bhbj5w"
    "csOocyBkZSAyMDAgY2hhbGV0czwvc3Bhbj48c3Bhbj5hdSBib3JkIGR1IGxhYzwvc3Bhbj48L2Rpdj48cD5MZSBOb8OrbCBkZXMg"
    "QWxwZXMgZOKAmUFubmVjeSBzZSB0aWVudCBkdSA8c3Ryb25nPjI2IG5vdmVtYnJlIDIwMjYgYXUgMyBqYW52aWVyIDIwMjc8L3N0"
    "cm9uZz4sIGF2ZWMgcHLDqHMgZGUgMjAwIGNoYWxldHMgYW5ub25jw6lzIHBhciBs4oCZb3JnYW5pc2F0ZXVyLiBJbCBvY2N1cGUg"
    "bGUgY2VudHJlLXZpbGxlLCBsZXMgcXVhaXMgKFZpY2VuemEgZXQgQmF5cmV1dGgpIGV0IGxlcyBKYXJkaW5zIGRlIGzigJlFdXJv"
    "cGUuIExlIHNwZWN0YWNsZSBk4oCZb3V2ZXJ0dXJlIGEgbGlldSBsZSB2ZW5kcmVkaSAyNyBub3ZlbWJyZSDDoCBwYXJ0aXIgZGUg"
    "MTcgaCAzMC48L3A+PGZpZ3VyZSBzdHlsZT1cIm1hcmdpbjoxOHB4IDBcIj48aW1nIGNsYXNzPVwibWhjLWltZ1wiIHNyYz1cImh0"
    "dHBzOi8vbXlob3RlbGNvbXBhcmUuY29tL2ltYWdlcy9tYXJjaGUtbm9lbC1hbm5lY3kuanBnXCIgYWx0PVwiVHVubmVsIGRlIGx1"
    "bWnDqHJlcyBkZSBOb8OrbCBhdSBib3JkIGRlIGzigJllYXVcIiBsb2FkaW5nPVwibGF6eVwiPjxmaWdjYXB0aW9uIGNsYXNzPVwi"
    "bWhjLWNhcFwiIHN0eWxlPVwidGV4dC1hbGlnbjpjZW50ZXJcIj5JbGx1bWluYXRpb25zIGRlIE5vw6tsIGF1IGJvcmQgZGUgbOKA"
    "mWVhdS48L2ZpZ2NhcHRpb24+PC9maWd1cmU+PHA+PHN0cm9uZz7DgCBzYXZvaXIgOjwvc3Ryb25nPiBsZXMgMjQgZXQgMzEgZMOp"
    "Y2VtYnJlLCBsZSBtYXJjaMOpIGZlcm1lIMOgIDE5IGggYXUgY2VudHJlLXZpbGxlIGV0IMOgIDIwIGggYXV4IEphcmRpbnMgZGUg"
    "bOKAmUV1cm9wZS4gTGUgMjUgZMOpY2VtYnJlIGV0IGxlIDFlciBqYW52aWVyLCBs4oCZaG9yYWlyZSBk4oCZb3V2ZXJ0dXJlIHZh"
    "cmllIHNlbG9uIGxlcyBzb3VyY2VzIDogYXJyaXZleiBhcHLDqHMgMTUgaC4gTGVzIHBhcmtpbmdzIGNvdXZlcnRzIGR1IGNlbnRy"
    "ZSBzb250IGNvbnNlaWxsw6lzLCBtYWlzIGxhIHBsdXBhcnQgbGltaXRlbnQgbGEgaGF1dGV1ciDDoCAxLDkwIG0uPC9wPjwhLS1I"
    "T1RFTFMgQW5uZWN5IHwgZnJhbmNlIHwgYW5uZWN5IHwgdGFsbG9pcmVzLHNldnJpZXIsdmV5cmllcixtZW50aG9uLGRvdXNzYXJk"
    "LHNhaW50LWpvcmlveixkdWluZ3QsbGEtYmFsbWUtLT5cbjxoMiBpZD1cIm1oYy10YWJsZWF1XCI+TGUgY2FsZW5kcmllciBlbiB1"
    "biBjb3VwIGTigJnFk2lsPC9oMj48ZGl2IGNsYXNzPVwibWhjLXdyYXBcIj48dGFibGUgY2xhc3M9XCJtaGMtdGFibGVcIj48dGhl"
    "YWQ+PHRyPjx0aD5WaWxsZTwvdGg+PHRoPkRhdGVzIDIwMjY8L3RoPjx0aD7DgCByZXRlbmlyPC90aD48L3RyPjwvdGhlYWQ+PHRi"
    "b2R5Pjx0cj48dGQ+THlvbjwvdGQ+PHRkIGNsYXNzPVwiblwiPjIwIG5vdi4g4oCTIDI0IGTDqWMuPC90ZD48dGQ+RsOqdGUgZGVz"
    "IEx1bWnDqHJlcyA1IOKAkyA4IGTDqWMuPC90ZD48L3RyPjx0cj48dGQ+Q29sbWFyPC90ZD48dGQgY2xhc3M9XCJuXCI+MjMgbm92"
    "LiDigJMgMjkgZMOpYy48L3RkPjx0ZD42IG1hcmNow6lzLCBQZXRpdGUgVmVuaXNlPC90ZD48L3RyPjx0cj48dGQ+UmVpbXM8L3Rk"
    "Pjx0ZCBjbGFzcz1cIm5cIj4yNSBub3YuIOKAkyAyNyBkw6ljLjwvdGQ+PHRkPkdyYW5kZSByb3VlIGRlIDU1IG08L3RkPjwvdHI+"
    "PHRyPjx0ZD5Bbm5lY3k8L3RkPjx0ZCBjbGFzcz1cIm5cIj4yNiBub3YuIOKAkyAzIGphbnYuPC90ZD48dGQ+UHLDqHMgZGUgMjAw"
    "IGNoYWxldHM8L3RkPjwvdHI+PHRyPjx0ZD5TdHJhc2JvdXJnPC90ZD48dGQgY2xhc3M9XCJuXCI+Mjcgbm92LiDigJMgMjQgZMOp"
    "Yy48L3RkPjx0ZD44IG1hcmNow6lzLCBkZXB1aXMgMTU3MDwvdGQ+PC90cj48dHI+PHRkPktheXNlcnNiZXJnPC90ZD48dGQgY2xh"
    "c3M9XCJuXCI+Mjcgbm92LiDigJMgMjAgZMOpYy48L3RkPjx0ZD5WZW5kcmVkaSBhdSBkaW1hbmNoZSBzZXVsZW1lbnQ8L3RkPjwv"
    "dHI+PC90Ym9keT48L3RhYmxlPjwvZGl2PjxwIGNsYXNzPVwibWhjLWNhcFwiPlNvdXJjZXMgOiBzaXRlcyBkZXMgdmlsbGVzIGV0"
    "IHByZXNzZSwgYXUgMjIgbm92ZW1icmUgMjAyNi4gTGVzIGRhdGVzIGRlIGZlcm1ldHVyZSBldCBsZXMgaG9yYWlyZXMgcGV1dmVu"
    "dCDDqXZvbHVlci48L3A+XG48aDIgaWQ9XCJtaGMtY29uc2VpbHNcIj5Ob3MgY29uc2VpbHMgcG91ciBiaWVuIGxlcyB2aXNpdGVy"
    "PC9oMj48dWw+PGxpPjxzdHJvbmc+w4l2aXRleiBsZXMgd2Vlay1lbmRzIGV0IGxlcyBzb2lyw6llcyBk4oCZYWZmbHVlbmNlLjwv"
    "c3Ryb25nPiDDgCBTdHJhc2JvdXJnLCBsZXMgbHVuZGlzLCBtYXJkaXMgZXQgamV1ZGlzIHNvbnQgY2FsbWVzLCBldCBsZSBzYW1l"
    "ZGkgZXN0IHRyw6hzIGZyw6lxdWVudMOpIGTDqHMgMTMgaC4gw4AgQ29sbWFyLCBsZXMgcGFya2luZ3MgZW4gcGxlaW4gYWlyIHNv"
    "bnQgcGxlaW5zIGTDqHMgMTEgaCBsZSB3ZWVrLWVuZC48L2xpPjxsaT48c3Ryb25nPkNvbWJpbmV6IGxlcyB2aWxsZXMgZOKAmUFs"
    "c2FjZSBlbiB0cmFpbi48L3N0cm9uZz4gQ29sbWFyIGVzdCDDoCBlbnZpcm9uIDMwIG1pbnV0ZXMgZGUgU3RyYXNib3VyZyBldCBs"
    "ZSB0cmFqZXQgw6l2aXRlIGRlIGNoZXJjaGVyIHVuZSBwbGFjZS4gw4AgU3RyYXNib3VyZywgbGUgZGVybmllciBURVIgdmVycyBT"
    "w6lsZXN0YXQsIENvbG1hciBldCBNdWxob3VzZSBwYXJ0IMOgIDIzIGggMjAgbGUgdmVuZHJlZGkgZXQgbGUgc2FtZWRpIChob3Jh"
    "aXJlIHRow6lvcmlxdWUganVzcXXigJlhdSAxMyBkw6ljZW1icmUpLjwvbGk+PGxpPjxzdHJvbmc+UsOpc2VydmV6IHZvdHJlIGjD"
    "tHRlbCB0w7R0Ljwvc3Ryb25nPiBMZXMgY2hhbWJyZXMgYXUgY2VudHJlIGRlIGNlcyB2aWxsZXMgc2UgcmVtcGxpc3NlbnQgdml0"
    "ZSBlbiBkw6ljZW1icmUgOiBjb21wYXJleiBsZXMgbm90ZXMgZXQgbGVzIHByaXggZGFucyA8YSBocmVmPVwiaHR0cHM6Ly9teWhv"
    "dGVsY29tcGFyZS5jb20vaG90ZWxzLmh0bWxcIj5ub3MgaMO0dGVsczwvYT4gZXQgbGlzZXogPGEgaHJlZj1cImh0dHBzOi8vbXlo"
    "b3RlbGNvbXBhcmUuY29tL2NvbW1lbnQtdHJvdXZlci11bi1ob3RlbC1tb2lucy1jaGVyLmh0bWxcIj5jb21tZW50IHRyb3V2ZXIg"
    "dW4gaMO0dGVsIG1vaW5zIGNoZXI8L2E+LjwvbGk+PGxpPjxzdHJvbmc+UGFydGV6IGVuIHZvaXR1cmUgc2FucyBhdXRvcm91dGUu"
    "PC9zdHJvbmc+IFByw6lwYXJleiB2b3RyZSB0cmFqZXQgYXZlYyA8YSBocmVmPVwiaHR0cHM6Ly9teWhvdGVsY29tcGFyZS5jb20v"
    "aXRpbmVyYWlyZS1kZWNvdXZlcnRlLmh0bWxcIj5ub3RyZSBwbGFuaWZpY2F0ZXVyIGTigJlpdGluw6lyYWlyZXM8L2E+LCBvdSBs"
    "aXNleiBub3RyZSB0cmFqZXQgPGEgaHJlZj1cImh0dHBzOi8vbXlob3RlbGNvbXBhcmUuY29tL3N0cmFzYm91cmctbWlsYW4tc2Fu"
    "cy1hdXRvcm91dGUuaHRtbFwiPlN0cmFzYm91cmcg4oCTIE1pbGFuIHNhbnMgYXV0b3JvdXRlPC9hPiwgcXVpIHBhcnQgZGUgU3Ry"
    "YXNib3VyZy48L2xpPjxsaT48c3Ryb25nPkNob2lzaXNzZXogbGEgYm9ubmUgZGF0ZS48L3N0cm9uZz4gUG91ciBjb21wYXJlciBs"
    "ZXMgcMOpcmlvZGVzLCB2b3lleiA8YSBocmVmPVwiaHR0cHM6Ly9teWhvdGVsY29tcGFyZS5jb20vcXVhbmQtcGFydGlyLWV0LW91"
    "LWNhbGVuZHJpZXItdm95YWdldXJzLmh0bWxcIj5ub3RyZSBjYWxlbmRyaWVyIHF1YW5kIHBhcnRpciBldCBvw7k8L2E+LjwvbGk+"
    "PC91bD5cbjxoMiBpZD1cIm1oYy1mYXFcIj5RdWVzdGlvbnMgZnLDqXF1ZW50ZXM8L2gyPjxkZXRhaWxzIGNsYXNzPVwibWhjLWZh"
    "cVwiPjxzdW1tYXJ5PlF1ZWwgZXN0IGxlIHBsdXMgYW5jaWVuIG1hcmNow6kgZGUgTm/Dq2wgZGUgRnJhbmNlID88L3N1bW1hcnk+"
    "PHA+U3RyYXNib3VyZyBtZXQgZW4gYXZhbnQgbGUgc2llbiA6IGxhIFZpbGxlIGxlIGZhaXQgbmHDrnRyZSBlbiAxNTcwIGV0IGxl"
    "IHByw6lzZW50ZSBjb21tZSBs4oCZdW4gZGVzIHBsdXMgYW5jaWVucyBk4oCZRXVyb3BlLjwvcD48L2RldGFpbHM+PGRldGFpbHMg"
    "Y2xhc3M9XCJtaGMtZmFxXCI+PHN1bW1hcnk+UXVlbCBtYXJjaMOpIGVzdCBsZSBtb2lucyBmcsOpcXVlbnTDqSA/PC9zdW1tYXJ5"
    "PjxwPkxlcyBqb3VycyBkZSBzZW1haW5lLCBob3JzIHZhY2FuY2VzIHNjb2xhaXJlcywgc29udCBsZXMgcGx1cyBjYWxtZXMuIMOA"
    "IFN0cmFzYm91cmcsIGxlcyBsdW5kaXMsIG1hcmRpcyBldCBqZXVkaXMgc29udCBsZXMgam91cnMgbGVzIHBsdXMgdHJhbnF1aWxs"
    "ZXMuPC9wPjwvZGV0YWlscz48ZGV0YWlscyBjbGFzcz1cIm1oYy1mYXFcIj48c3VtbWFyeT5RdWVsIG1hcmNow6kgZGUgTm/Dq2wg"
    "b3V2cmUgZW4gcHJlbWllciA/PC9zdW1tYXJ5PjxwPlBhcm1pIG5vcyBzaXggdmlsbGVzLCBMeW9uIG91dnJlIGxlIDIwIG5vdmVt"
    "YnJlIDIwMjYsIHB1aXMgQ29sbWFyIGxlIDIzIG5vdmVtYnJlLjwvcD48L2RldGFpbHM+PGRldGFpbHMgY2xhc3M9XCJtaGMtZmFx"
    "XCI+PHN1bW1hcnk+S2F5c2Vyc2JlcmcgZXN0LWlsIG91dmVydCB0b3V0ZSBsYSBzZW1haW5lID88L3N1bW1hcnk+PHA+Tm9uLCBz"
    "ZXVsZW1lbnQgZHUgdmVuZHJlZGkgYXUgZGltYW5jaGUsIHBlbmRhbnQgbGVzIHF1YXRyZSB3ZWVrLWVuZHMgZGUgbOKAmUF2ZW50"
    "IDogMjcgYXUgMjkgbm92ZW1icmUsIHB1aXMgNCBhdSA2LCAxMSBhdSAxMyBldCAxOCBhdSAyMCBkw6ljZW1icmUgMjAyNi48L3A+"
    "PC9kZXRhaWxzPjxkZXRhaWxzIGNsYXNzPVwibWhjLWZhcVwiPjxzdW1tYXJ5PkZhdXQtaWwgdmVuaXIgZW4gdm9pdHVyZSA/PC9z"
    "dW1tYXJ5PjxwPlBhcyBmb3Jjw6ltZW50LiDDgCBTdHJhc2JvdXJnLCBsZXMgdm9pdHVyZXMgc29udCBpbnRlcmRpdGVzIGRhbnMg"
    "bGEgR3JhbmRlIMOObGUgYXV4IGhldXJlcyBk4oCZb3V2ZXJ0dXJlLCBldCDDoCBDb2xtYXIgbGUgdHJhaW4gZGVwdWlzIFN0cmFz"
    "Ym91cmcgZHVyZSBlbnZpcm9uIDMwIG1pbnV0ZXMuIExlIHBhcmtpbmcgcmVsYWlzIGVzdCB1bmUgYm9ubmUgc29sdXRpb24uPC9w"
    "PjwvZGV0YWlscz5cbjxkaXYgY2xhc3M9XCJnbGFzcy1ib3hcIiBzdHlsZT1cIm1hcmdpbjoyMnB4IDA7IGJvcmRlci1sZWZ0OjVw"
    "eCBzb2xpZCB2YXIoLS1wcmltYXJ5KTsgdGV4dC1hbGlnbjpjZW50ZXI7XCI+PGgzIHN0eWxlPVwibWFyZ2luLXRvcDowO1wiPvCf"
    "joQgUsOpc2VydmV6IHZvdHJlIHPDqWpvdXI8L2gzPjxwIHN0eWxlPVwibWFyZ2luLWJvdHRvbToxNnB4O1wiPkNvbXBhcmV6IGxl"
    "cyBow7R0ZWxzIGRlIHZvdHJlIHZpbGxlIGRlIG1hcmNow6kgZGUgTm/Dq2wsIGF2ZWMgbGVzIG5vdGVzLCBsZXMgcHJpeCBldCBs"
    "ZXMgYXZpcyBkZXMgdm95YWdldXJzLjwvcD48YSBjbGFzcz1cImJ0blwiIGhyZWY9XCJodHRwczovL215aG90ZWxjb21wYXJlLmNv"
    "bS9ob3RlbHMuaHRtbFwiPkNvbXBhcmVyIGxlcyBow7R0ZWxzPC9hPjwvZGl2PlxuPGgyPlNvdXJjZXMgZXQgbcOpdGhvZGU8L2gy"
    "PjxwPkxlcyBkYXRlcyBldCBsZXMgY2hpZmZyZXMgdmllbm5lbnQgZGVzIHNpdGVzIGRlcyB2aWxsZXMsIGRlcyBvZmZpY2VzIGRl"
    "IHRvdXJpc21lIGV0IGRlIGxhIHByZXNzZSwgY29uc3VsdMOpcyBsZSAyMiBub3ZlbWJyZSAyMDI2IDogVGhlIENvbm5leGlvbiAo"
    "ZGF0ZXMgMjAyNiBkZXMgbWFyY2jDqXMgZGUgRnJhbmNlKSwgT25pdmFwcCAoU3RyYXNib3VyZywgQW5uZWN5LCBSZWltcywgTHlv"
    "biksIFJ5byAoQ29sbWFyKSBldCBOb8OrbCDDoCBDb2xtYXIgKEtheXNlcnNiZXJnKS4gTGVzIGNoaWZmcmVzIGRlIGZyw6lxdWVu"
    "dGF0aW9uIHNvbnQgY2V1eCBhbm5vbmPDqXMgcGFyIGxlcyB2aWxsZXMgZXQgbGVzIHNvdXJjZXMgdG91cmlzdGlxdWVzLiBMZXMg"
    "aG9yYWlyZXMgMjAyNiBkZSBTdHJhc2JvdXJnIG5lIHNvbnQgcGFzIHRvdXMgcHVibGnDqXMgOiB2w6lyaWZpZXotbGVzIGF2YW50"
    "IGRlIHBhcnRpci4gTGUgY2hvaXggZGUgY2VzIHNpeCB2aWxsZXMgZXN0IHVuZSBzw6lsZWN0aW9uIGRlIE15SG90ZWxDb21wYXJl"
    "LCBwYXMgdW4gcGFsbWFyw6hzIG9mZmljaWVsLiBMZXMgaW1hZ2VzIHNpZ25hbMOpZXMgY29tbWUgaWxsdXN0cmF0aW9ucyBuZSBz"
    "b250IHBhcyBkZXMgcGhvdG9zIGTigJlhcmNoaXZlcyBkZXMgbWFyY2jDqXMuPC9wPlxuPC9kaXY+In0="
)

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
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        for nom, v in data.items():
            if isinstance(v, dict) and slug(nom):
                try:
                    et = int(re.search(r"\d", str(v.get("etoiles", ""))).group())
                except Exception:
                    et = 0
                res.append({"nom": nom, "ville": slug(v.get("ville", "")), "ville_aff": v.get("ville", ""),
                            "pays": slug(v.get("pays", "")), "et": et,
                            "url": f"{SITE}/{prefixe}{slug(nom)}.html"})
    return res

def liste(items, etoiles=True):
    return "".join('<li><a href="' + f["url"] + '">' + f["nom"] + '</a> (' + f["ville_aff"] +
                   (f', {f["et"]} étoiles' if etoiles and f["et"] else "") + ')</li>' for f in items)

def main():
    art = json.loads(base64.b64decode("".join(ARTICLE_B64)).decode("utf-8"))
    hotels = charger("data", "")
    atyp = charger("data_logements", "atypique-")
    print(len(hotels), "hotel(s) et", len(atyp), "logement(s) atypique(s) lus.")

    def trouve(src, pays, villes, n, cle):
        ok = [f for f in src if f["pays"] == pays and any(v in f["ville"] for v in villes)]
        return sorted(ok, key=cle)[:n]

    def rempl(m):
        titre, pays = m.group(1).strip(), slug(m.group(2))
        villes = [slug(v) for v in m.group(3).split(",") if v.strip()]
        alent = [slug(v) for v in (m.group(4) or "").split(",") if v.strip()]
        h = trouve(hotels, pays, villes, MAX_HOTELS, lambda f: (-f["et"], f["nom"]))
        a = trouve(atyp, pays, villes, MAX_ATYP, lambda f: f["nom"])
        vus = {f["url"] for f in h + a}
        h2 = [f for f in trouve(hotels, pays, alent, 60, lambda f: (-f["et"], f["nom"])) if f["url"] not in vus][:MAX_HOTELS]
        a2 = [f for f in trouve(atyp, pays, alent, 60, lambda f: f["nom"]) if f["url"] not in vus][:MAX_ATYP]
        print(f"  {titre} : {len(h)} hotel(s) + {len(a)} atypique(s) en ville ; {len(h2)} hotel(s) + {len(a2)} atypique(s) a proximite")
        out = ""
        if h:
            out += '<div class="mhc-hotels"><strong>Nos hôtels : ' + titre + '</strong><ul>' + liste(h) + '</ul></div>'
        if a:
            out += '<div class="mhc-hotels"><strong>Logements atypiques : ' + titre + '</strong><ul>' + liste(a, False) + '</ul></div>'
        if h2:
            out += '<div class="mhc-hotels"><strong>Hôtels à proximité : ' + titre + '</strong><ul>' + liste(h2) + '</ul></div>'
        if a2:
            out += '<div class="mhc-hotels"><strong>Logements atypiques à proximité : ' + titre + '</strong><ul>' + liste(a2, False) + '</ul></div>'
        return out

    art["details"] = re.sub(r"<!--HOTELS\s+(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)(?:\s*\|\s*(.+?))?\s*-->", rempl, art["details"])
    p = Path("blog_data.json")
    if not p.exists():
        sys.exit("blog_data.json introuvable : lancez le script dans le dossier comparateur-ia.")
    data = json.loads(p.read_text(encoding="utf-8"))
    shutil.copy(p, "blog_data.json.bak3")
    liste_art = data["articles"] if isinstance(data, dict) and isinstance(data.get("articles"), list) else data
    if not isinstance(liste_art, list):
        sys.exit("Structure inattendue de blog_data.json.")
    liste_art[:] = [a for a in liste_art if not (isinstance(a, dict) and a.get("slug") == art["slug"])]
    liste_art.insert(0, art)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK : {len(liste_art)} articles au total.")

if __name__ == "__main__":
    main()
