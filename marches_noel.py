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
    "aXY+XG48ZmlndXJlIHN0eWxlPVwibWFyZ2luOjE4cHggMFwiPjxpbWcgY2xhc3M9XCJtaGMtaW1nXCIgc3R5bGU9XCJkaXNwbGF5"
    "OmJsb2NrIWltcG9ydGFudDttYXJnaW46MTRweCBhdXRvIWltcG9ydGFudDt3aWR0aDoxMDAlIWltcG9ydGFudDttYXgtd2lkdGg6"
    "NTYwcHghaW1wb3J0YW50O2hlaWdodDphdXRvIWltcG9ydGFudDttYXgtaGVpZ2h0OjUyMHB4IWltcG9ydGFudDtvYmplY3QtZml0"
    "OmNvbnRhaW4haW1wb3J0YW50O2JvcmRlci1yYWRpdXM6MTJweDtib3gtc2hhZG93OjAgMnB4IDE0cHggcmdiYSgwLDAsMCwuMTgp"
    "XCIgc3JjPVwiaHR0cHM6Ly9teWhvdGVsY29tcGFyZS5jb20vaW1hZ2VzL21hcmNoZXMtbm9lbC1jYXJ0ZS5qcGdcIiBhbHQ9XCJD"
    "YXJ0ZSBkZSBGcmFuY2UgZGVzIHNpeCBtYXJjaMOpcyBkZSBOb8OrbCA6IFN0cmFzYm91cmcsIENvbG1hciwgS2F5c2Vyc2Jlcmcs"
    "IFJlaW1zLCBMeW9uIGV0IEFubmVjeVwiIGxvYWRpbmc9XCJsYXp5XCI+PGZpZ2NhcHRpb24gY2xhc3M9XCJtaGMtY2FwXCIgc3R5"
    "bGU9XCJ0ZXh0LWFsaWduOmNlbnRlclwiPkxlcyBzaXggdmlsbGVzIGRlIG5vdHJlIHPDqWxlY3Rpb24gKGNhcnRlIHNjaMOpbWF0"
    "aXF1ZSwgcG9zaXRpb25zIGFwcHJveGltYXRpdmVzKS48L2ZpZ2NhcHRpb24+PC9maWd1cmU+XG48ZGl2IGNsYXNzPVwibWhjLXRv"
    "Y1wiPjxzdHJvbmc+U29tbWFpcmU8L3N0cm9uZz48b2w+PGxpPjxhIGhyZWY9XCIjbWhjLXN0cmFzYm91cmdcIj5TdHJhc2JvdXJn"
    "PC9hPjwvbGk+PGxpPjxhIGhyZWY9XCIjbWhjLWNvbG1hclwiPkNvbG1hcjwvYT48L2xpPjxsaT48YSBocmVmPVwiI21oYy1rYXlz"
    "ZXJzYmVyZ1wiPktheXNlcnNiZXJnPC9hPjwvbGk+PGxpPjxhIGhyZWY9XCIjbWhjLXJlaW1zXCI+UmVpbXM8L2E+PC9saT48bGk+"
    "PGEgaHJlZj1cIiNtaGMtbHlvblwiPkx5b248L2E+PC9saT48bGk+PGEgaHJlZj1cIiNtaGMtYW5uZWN5XCI+QW5uZWN5PC9hPjwv"
    "bGk+PGxpPjxhIGhyZWY9XCIjbWhjLXRhYmxlYXVcIj5MZSBjYWxlbmRyaWVyIGVuIHVuIGNvdXAgZOKAmcWTaWw8L2E+PC9saT48"
    "bGk+PGEgaHJlZj1cIiNtaGMtY29uc2VpbHNcIj5Ob3MgY29uc2VpbHMgcG91ciBiaWVuIGxlcyB2aXNpdGVyPC9hPjwvbGk+PGxp"
    "PjxhIGhyZWY9XCIjbWhjLWZhcVwiPlF1ZXN0aW9ucyBmcsOpcXVlbnRlczwvYT48L2xpPjwvb2w+PC9kaXY+XG48aDIgaWQ9XCJt"
    "aGMtc3RyYXNib3VyZ1wiPjEuIFN0cmFzYm91cmcsIGxhIMKrIGNhcGl0YWxlIGRlIE5vw6tsIMK7PC9oMj48ZGl2IGNsYXNzPVwi"
    "bWhjLWZhY3RzXCIgc3R5bGU9XCJkaXNwbGF5OmZsZXghaW1wb3J0YW50O2ZsZXgtd3JhcDp3cmFwIWltcG9ydGFudDtnYXA6OHB4"
    "O21hcmdpbjoxMHB4IDAgMTRweFwiPjxzcGFuIHN0eWxlPVwiZGlzcGxheTppbmxpbmUtYmxvY2shaW1wb3J0YW50O2JvcmRlcjox"
    "cHggc29saWQgcmdiYSg0NSwyMTIsMTkxLC42KTtiYWNrZ3JvdW5kOnJnYmEoNDUsMjEyLDE5MSwuMTApO2JvcmRlci1yYWRpdXM6"
    "OTk5cHg7cGFkZGluZzo0cHggMTJweDtmb250LXNpemU6Ljk1cmVtXCI+Mjcgbm92ZW1icmUg4oCTIDI0IGTDqWNlbWJyZTwvc3Bh"
    "bj48c3BhbiBzdHlsZT1cImRpc3BsYXk6aW5saW5lLWJsb2NrIWltcG9ydGFudDtib3JkZXI6MXB4IHNvbGlkIHJnYmEoNDUsMjEy"
    "LDE5MSwuNik7YmFja2dyb3VuZDpyZ2JhKDQ1LDIxMiwxOTEsLjEwKTtib3JkZXItcmFkaXVzOjk5OXB4O3BhZGRpbmc6NHB4IDEy"
    "cHg7Zm9udC1zaXplOi45NXJlbVwiPjggbWFyY2jDqXM8L3NwYW4+PHNwYW4gc3R5bGU9XCJkaXNwbGF5OmlubGluZS1ibG9jayFp"
    "bXBvcnRhbnQ7Ym9yZGVyOjFweCBzb2xpZCByZ2JhKDQ1LDIxMiwxOTEsLjYpO2JhY2tncm91bmQ6cmdiYSg0NSwyMTIsMTkxLC4x"
    "MCk7Ym9yZGVyLXJhZGl1czo5OTlweDtwYWRkaW5nOjRweCAxMnB4O2ZvbnQtc2l6ZTouOTVyZW1cIj5kZXB1aXMgMTU3MDwvc3Bh"
    "bj48L2Rpdj48cD5MYSBWaWxsZSBkZSBTdHJhc2JvdXJnIGZhaXQgbmHDrnRyZSBzb24gbWFyY2jDqSwgbGUgQ2hyaXN0a2luZGVs"
    "c23DpHJpaywgZW4gMTU3MCBldCBsZSBwcsOpc2VudGUgY29tbWUgbOKAmXVuIGRlcyBwbHVzIGFuY2llbnMgZOKAmUV1cm9wZS4g"
    "RWxsZSBzZSBkaXQgwqsgQ2FwaXRhbGUgZGUgTm/Dq2wgwrsgZGVwdWlzIDE5OTIuIEVuIDIwMjYsIGzigJlvdXZlcnR1cmUgYSBs"
    "aWV1IGxlIDxzdHJvbmc+dmVuZHJlZGkgMjcgbm92ZW1icmU8L3N0cm9uZz4sIGF2ZWMgaHVpdCBtYXJjaMOpcyBkYW5zIGxlIGNl"
    "bnRyZSBoaXN0b3JpcXVlIGV0IGxlIGdyYW5kIHNhcGluIGRlIGxhIHBsYWNlIEtsw6liZXIuIExhIHZpbGxlIGFubm9uY2UgZW52"
    "aXJvbiB0cm9pcyBtaWxsaW9ucyBkZSB2aXNpdGV1cnMgcGFyIGFuLjwvcD48ZmlndXJlIHN0eWxlPVwibWFyZ2luOjE4cHggMFwi"
    "PjxpbWcgY2xhc3M9XCJtaGMtaW1nXCIgc3R5bGU9XCJkaXNwbGF5OmJsb2NrIWltcG9ydGFudDttYXJnaW46MTRweCBhdXRvIWlt"
    "cG9ydGFudDt3aWR0aDoxMDAlIWltcG9ydGFudDttYXgtd2lkdGg6NTIwcHghaW1wb3J0YW50O2hlaWdodDphdXRvIWltcG9ydGFu"
    "dDttYXgtaGVpZ2h0OjM0MHB4IWltcG9ydGFudDtvYmplY3QtZml0OmNvbnRhaW4haW1wb3J0YW50O2JvcmRlci1yYWRpdXM6MTJw"
    "eDtib3gtc2hhZG93OjAgMnB4IDE0cHggcmdiYSgwLDAsMCwuMTgpXCIgc3JjPVwiaHR0cHM6Ly9teWhvdGVsY29tcGFyZS5jb20v"
    "aW1hZ2VzL21hcmNoZS1ub2VsLXN0cmFzYm91cmcuanBnXCIgYWx0PVwiTWFyY2jDqSBkZSBOb8OrbCBkZSBTdHJhc2JvdXJnLCBn"
    "cmFuZCBzYXBpbiBpbGx1bWluw6lcIiBsb2FkaW5nPVwibGF6eVwiPjxmaWdjYXB0aW9uIGNsYXNzPVwibWhjLWNhcFwiIHN0eWxl"
    "PVwidGV4dC1hbGlnbjpjZW50ZXJcIj5MZSBncmFuZCBzYXBpbiBldCBsZXMgY2hhbGV0cyBkdSBtYXJjaMOpIGRlIE5vw6tsIGRl"
    "IFN0cmFzYm91cmcgKGltYWdlIGTigJlpbGx1c3RyYXRpb24pLjwvZmlnY2FwdGlvbj48L2ZpZ3VyZT48cD48c3Ryb25nPsOAIHNh"
    "dm9pciA6PC9zdHJvbmc+IGxlcyB2b2l0dXJlcyBzb250IGludGVyZGl0ZXMgZGFucyBsYSBHcmFuZGUgw45sZSBhdXggaGV1cmVz"
    "IGTigJlvdXZlcnR1cmUuIExlIHBhcmtpbmcgcmVsYWlzIChQK1IpIGRlIGxhIENUUyBjb8O7dGUgNCwyMCDigqwgbGEgam91cm7D"
    "qWUsIGJ1cyBldCB0cmFtIGNvbXByaXMsIGV0IGxhIGdhcmUgZXN0IMOgIDEwIG1pbnV0ZXMgw6AgcGllZCBkZXMgcHJlbWllcnMg"
    "Y2hhbGV0cy4gTGUgZ29iZWxldCBlc3QgY29uc2lnbsOpIDEg4oKsLjwvcD48IS0tSE9URUxTIFN0cmFzYm91cmcgfCBmcmFuY2Ug"
    "fCBzdHJhc2JvdXJnIHwgaWxsa2lyY2gsc2NoaWx0aWdoZWltLGJpc2NoaGVpbSxzb3VmZmVsd2V5ZXJzaGVpbSxvYmVybmFpLG1v"
    "bHNoZWltLGtlaGwsZ2Vpc3BvbHNoZWltLS0+XG48aDIgaWQ9XCJtaGMtY29sbWFyXCI+Mi4gQ29sbWFyLCBzaXggbWFyY2jDqXMg"
    "ZXQgbGEgUGV0aXRlIFZlbmlzZTwvaDI+PGRpdiBjbGFzcz1cIm1oYy1mYWN0c1wiIHN0eWxlPVwiZGlzcGxheTpmbGV4IWltcG9y"
    "dGFudDtmbGV4LXdyYXA6d3JhcCFpbXBvcnRhbnQ7Z2FwOjhweDttYXJnaW46MTBweCAwIDE0cHhcIj48c3BhbiBzdHlsZT1cImRp"
    "c3BsYXk6aW5saW5lLWJsb2NrIWltcG9ydGFudDtib3JkZXI6MXB4IHNvbGlkIHJnYmEoNDUsMjEyLDE5MSwuNik7YmFja2dyb3Vu"
    "ZDpyZ2JhKDQ1LDIxMiwxOTEsLjEwKTtib3JkZXItcmFkaXVzOjk5OXB4O3BhZGRpbmc6NHB4IDEycHg7Zm9udC1zaXplOi45NXJl"
    "bVwiPjIzIG5vdmVtYnJlIOKAkyAyOSBkw6ljZW1icmU8L3NwYW4+PHNwYW4gc3R5bGU9XCJkaXNwbGF5OmlubGluZS1ibG9jayFp"
    "bXBvcnRhbnQ7Ym9yZGVyOjFweCBzb2xpZCByZ2JhKDQ1LDIxMiwxOTEsLjYpO2JhY2tncm91bmQ6cmdiYSg0NSwyMTIsMTkxLC4x"
    "MCk7Ym9yZGVyLXJhZGl1czo5OTlweDtwYWRkaW5nOjRweCAxMnB4O2ZvbnQtc2l6ZTouOTVyZW1cIj42IG1hcmNow6lzPC9zcGFu"
    "PjxzcGFuIHN0eWxlPVwiZGlzcGxheTppbmxpbmUtYmxvY2shaW1wb3J0YW50O2JvcmRlcjoxcHggc29saWQgcmdiYSg0NSwyMTIs"
    "MTkxLC42KTtiYWNrZ3JvdW5kOnJnYmEoNDUsMjEyLDE5MSwuMTApO2JvcmRlci1yYWRpdXM6OTk5cHg7cGFkZGluZzo0cHggMTJw"
    "eDtmb250LXNpemU6Ljk1cmVtXCI+Y3LDqcOpIGVuIDE5ODg8L3NwYW4+PC9kaXY+PHA+Q29sbWFyIGNvbXB0ZSBzaXggbWFyY2jD"
    "qXMgOiBwbGFjZSBKZWFubmUtZOKAmUFyYywgcGxhY2UgZGUgbOKAmUFuY2llbm5lLURvdWFuZSwgbGUgS2/Dr2ZodXMgKG1hcmNo"
    "w6kgY291dmVydCksIHBsYWNlIGRlcyBEb21pbmljYWlucywgbGUgbWFyY2jDqSBkZXMgZW5mYW50cyBkZSBsYSBQZXRpdGUgVmVu"
    "aXNlIGV0IGxlIE1hcmNow6kgR291cm1hbmQgZGUgbGEgTW9udGFnbmUgVmVydGUuIExlcyBjaGFsZXRzIHNvbnQgb3V2ZXJ0cyBk"
    "ZSAxMSBoIMOgIDE5IGggZHUgbHVuZGkgYXUgamV1ZGkgZXQgZGUgMTAgaCDDoCAyMCBoIGR1IHZlbmRyZWRpIGF1IGRpbWFuY2hl"
    "LiBMZSAyNCBkw6ljZW1icmUsIGlscyBmZXJtZW50IMOgIDE3IGguIExlIE1hcmNow6kgR291cm1hbmQgcmVzdGUgb3V2ZXJ0IGp1"
    "c3F14oCZYXUgMyBqYW52aWVyIDIwMjcuPC9wPjxmaWd1cmUgc3R5bGU9XCJtYXJnaW46MThweCAwXCI+PGltZyBjbGFzcz1cIm1o"
    "Yy1pbWdcIiBzdHlsZT1cImRpc3BsYXk6YmxvY2shaW1wb3J0YW50O21hcmdpbjoxNHB4IGF1dG8haW1wb3J0YW50O3dpZHRoOjEw"
    "MCUhaW1wb3J0YW50O21heC13aWR0aDo1MjBweCFpbXBvcnRhbnQ7aGVpZ2h0OmF1dG8haW1wb3J0YW50O21heC1oZWlnaHQ6MzQw"
    "cHghaW1wb3J0YW50O29iamVjdC1maXQ6Y29udGFpbiFpbXBvcnRhbnQ7Ym9yZGVyLXJhZGl1czoxMnB4O2JveC1zaGFkb3c6MCAy"
    "cHggMTRweCByZ2JhKDAsMCwwLC4xOClcIiBzcmM9XCJodHRwczovL215aG90ZWxjb21wYXJlLmNvbS9pbWFnZXMvbWFyY2hlLW5v"
    "ZWwtY29sbWFyLmpwZ1wiIGFsdD1cIlBldGl0ZSBWZW5pc2UgZGUgQ29sbWFyIGlsbHVtaW7DqWUgcG91ciBOb8OrbFwiIGxvYWRp"
    "bmc9XCJsYXp5XCI+PGZpZ2NhcHRpb24gY2xhc3M9XCJtaGMtY2FwXCIgc3R5bGU9XCJ0ZXh0LWFsaWduOmNlbnRlclwiPkxhIFBl"
    "dGl0ZSBWZW5pc2UgZGUgQ29sbWFyIGV0IHNlcyBtYWlzb25zIMOgIGNvbG9tYmFnZXMgYXUgYm9yZCBkZSBs4oCZZWF1IChpbWFn"
    "ZSBk4oCZaWxsdXN0cmF0aW9uKS48L2ZpZ2NhcHRpb24+PC9maWd1cmU+PHA+TGUgbWFyY2jDqSBkYXRlIGRlIDE5ODggZXQgYXR0"
    "aXJlIHBsdXMgZGUgZGV1eCBtaWxsaW9ucyBkZSB2aXNpdGV1cnMsIHNlbG9uIGxlcyBzb3VyY2VzIHRvdXJpc3RpcXVlcy4gTGUg"
    "c29pciwgbGVzIGlsbHVtaW5hdGlvbnMgZGUgbGEgR3JhbmTigJlSdWUgZXQgZGVzIHF1YWlzIGR1IGNhbmFsIHZhbGVudCBsZSBk"
    "w6l0b3VyLjwvcD48cD48c3Ryb25nPsOAIHNhdm9pciA6PC9zdHJvbmc+IFN0cmFzYm91cmcgZXN0IMOgIGVudmlyb24gMzAgbWlu"
    "dXRlcyBlbiB0cmFpbiwgTXVsaG91c2Ugw6AgMjAgbWludXRlcyBldCBCw6JsZSDDoCA0NSBtaW51dGVzLiBMZXMgbmF2ZXR0ZXMg"
    "ZHUgcGFya2luZyByZWxhaXMgbmUgY2lyY3VsZW50IHF1ZSBsZXMgd2Vlay1lbmRzIGRlIGzigJlBdmVudC4gw4l2aXRleiBsZXMg"
    "d2Vlay1lbmRzIDogbGVzIHBhcmtpbmdzIGVuIHBsZWluIGFpciBzb250IHBsZWlucyBkw6hzIDExIGguPC9wPjwhLS1IT1RFTFMg"
    "Q29sbWFyIHwgZnJhbmNlIHwgY29sbWFyIHwgZWd1aXNoZWltLHJpcXVld2locixyaWJlYXV2aWxsZSx0dXJja2hlaW0sbXVuc3Rl"
    "cixiZXJnaGVpbSxzaWdvbHNoZWltLGtpZW50emhlaW0sd2V0dG9sc2hlaW0tLT5cbjxoMiBpZD1cIm1oYy1rYXlzZXJzYmVyZ1wi"
    "PjMuIEtheXNlcnNiZXJnLCBsZSB2aWxsYWdlIGR1IHdlZWstZW5kPC9oMj48ZGl2IGNsYXNzPVwibWhjLWZhY3RzXCIgc3R5bGU9"
    "XCJkaXNwbGF5OmZsZXghaW1wb3J0YW50O2ZsZXgtd3JhcDp3cmFwIWltcG9ydGFudDtnYXA6OHB4O21hcmdpbjoxMHB4IDAgMTRw"
    "eFwiPjxzcGFuIHN0eWxlPVwiZGlzcGxheTppbmxpbmUtYmxvY2shaW1wb3J0YW50O2JvcmRlcjoxcHggc29saWQgcmdiYSg0NSwy"
    "MTIsMTkxLC42KTtiYWNrZ3JvdW5kOnJnYmEoNDUsMjEyLDE5MSwuMTApO2JvcmRlci1yYWRpdXM6OTk5cHg7cGFkZGluZzo0cHgg"
    "MTJweDtmb250LXNpemU6Ljk1cmVtXCI+NCB3ZWVrLWVuZHM8L3NwYW4+PHNwYW4gc3R5bGU9XCJkaXNwbGF5OmlubGluZS1ibG9j"
    "ayFpbXBvcnRhbnQ7Ym9yZGVyOjFweCBzb2xpZCByZ2JhKDQ1LDIxMiwxOTEsLjYpO2JhY2tncm91bmQ6cmdiYSg0NSwyMTIsMTkx"
    "LC4xMCk7Ym9yZGVyLXJhZGl1czo5OTlweDtwYWRkaW5nOjRweCAxMnB4O2ZvbnQtc2l6ZTouOTVyZW1cIj52ZW5kcmVkaSDigJMg"
    "ZGltYW5jaGU8L3NwYW4+PHNwYW4gc3R5bGU9XCJkaXNwbGF5OmlubGluZS1ibG9jayFpbXBvcnRhbnQ7Ym9yZGVyOjFweCBzb2xp"
    "ZCByZ2JhKDQ1LDIxMiwxOTEsLjYpO2JhY2tncm91bmQ6cmdiYSg0NSwyMTIsMTkxLC4xMCk7Ym9yZGVyLXJhZGl1czo5OTlweDtw"
    "YWRkaW5nOjRweCAxMnB4O2ZvbnQtc2l6ZTouOTVyZW1cIj4xMCBoIOKAkyAyMCBoPC9zcGFuPjwvZGl2PjxwPktheXNlcnNiZXJn"
    "IG7igJlvdXZyZSBzb24gbWFyY2jDqSBxdWUgbGVzIDxzdHJvbmc+dmVuZHJlZGlzLCBzYW1lZGlzIGV0IGRpbWFuY2hlcyBkZSBs"
    "4oCZQXZlbnQ8L3N0cm9uZz4gOiAyNyBhdSAyOSBub3ZlbWJyZSwgNCBhdSA2LCAxMSBhdSAxMyBldCAxOCBhdSAyMCBkw6ljZW1i"
    "cmUgMjAyNiwgZGUgMTAgaCDDoCAyMCBoLiBMZXMgY2hhbGV0cyBz4oCZaW5zdGFsbGVudCBkYW5zIGxhIGNvdXIgZGUgbOKAmUFy"
    "c2VuYWwgZXQgZGVycmnDqHJlIGzigJnDqWdsaXNlIFNhaW50ZS1Dcm9peCwgYXZlYyBwYWluIGTigJnDqXBpY2VzLCB2aW4gY2hh"
    "dWQsIGJyZXR6ZWxzLCBwZXRpdHMgYmlzY3VpdHMgZGUgTm/Dq2wgKGxlcyBicmVkZWxlKSBldCBhcnRpc2FuYXQgKGpvdWV0cyBl"
    "biBib2lzLCB2ZXJyZSBzb3VmZmzDqSwgZMOpY29yYXRpb25zKS48L3A+PGZpZ3VyZSBzdHlsZT1cIm1hcmdpbjoxOHB4IDBcIj48"
    "aW1nIGNsYXNzPVwibWhjLWltZ1wiIHN0eWxlPVwiZGlzcGxheTpibG9jayFpbXBvcnRhbnQ7bWFyZ2luOjE0cHggYXV0byFpbXBv"
    "cnRhbnQ7d2lkdGg6MTAwJSFpbXBvcnRhbnQ7bWF4LXdpZHRoOjUyMHB4IWltcG9ydGFudDtoZWlnaHQ6YXV0byFpbXBvcnRhbnQ7"
    "bWF4LWhlaWdodDozNDBweCFpbXBvcnRhbnQ7b2JqZWN0LWZpdDpjb250YWluIWltcG9ydGFudDtib3JkZXItcmFkaXVzOjEycHg7"
    "Ym94LXNoYWRvdzowIDJweCAxNHB4IHJnYmEoMCwwLDAsLjE4KVwiIHNyYz1cImh0dHBzOi8vbXlob3RlbGNvbXBhcmUuY29tL2lt"
    "YWdlcy9tYXJjaGUtbm9lbC1rYXlzZXJzYmVyZy5qcGdcIiBhbHQ9XCJDaGFsZXRzIGTDqWNvcsOpcyBk4oCZdW4gbWFyY2jDqSBk"
    "ZSBOb8OrbCBhbHNhY2llblwiIGxvYWRpbmc9XCJsYXp5XCI+PGZpZ2NhcHRpb24gY2xhc3M9XCJtaGMtY2FwXCIgc3R5bGU9XCJ0"
    "ZXh0LWFsaWduOmNlbnRlclwiPkNoYWxldHMgZXQgZMOpY29yYXRpb25zIGTigJl1biBtYXJjaMOpIGRlIE5vw6tsIGFsc2FjaWVu"
    "IChpbWFnZSBk4oCZaWxsdXN0cmF0aW9uKS48L2ZpZ2NhcHRpb24+PC9maWd1cmU+PHA+TGUgdmlsbGFnZSBhIMOpdMOpIMOpbHUg"
    "wqsgVmlsbGFnZSBwcsOpZsOpcsOpIGRlcyBGcmFuw6dhaXMgwrsgZW4gMjAxNywgc3VyIEZyYW5jZSAyLCBldCB1bmUgcGxhcXVl"
    "IGxlIHJhcHBlbGxlIHN1ciBsZSBwb250IGZvcnRpZmnDqS48L3A+PCEtLUhPVEVMUyBLYXlzZXJzYmVyZyB8IGZyYW5jZSB8IGth"
    "eXNlcnNiZXJnLGFtbWVyc2Nod2locixraWVudHpoZWltIHwgcmlxdWV3aWhyLHJpYmVhdXZpbGxlLHR1cmNraGVpbSxlZ3Vpc2hl"
    "aW0sY29sbWFyLHNpZ29sc2hlaW0sbXVuc3RlcixvcmJleSxsYXBvdXRyb2llLS0+XG48aDIgaWQ9XCJtaGMtcmVpbXNcIj40LiBS"
    "ZWltcywgbGUgbWFyY2jDqSBkZSBDaGFtcGFnbmU8L2gyPjxkaXYgY2xhc3M9XCJtaGMtZmFjdHNcIiBzdHlsZT1cImRpc3BsYXk6"
    "ZmxleCFpbXBvcnRhbnQ7ZmxleC13cmFwOndyYXAhaW1wb3J0YW50O2dhcDo4cHg7bWFyZ2luOjEwcHggMCAxNHB4XCI+PHNwYW4g"
    "c3R5bGU9XCJkaXNwbGF5OmlubGluZS1ibG9jayFpbXBvcnRhbnQ7Ym9yZGVyOjFweCBzb2xpZCByZ2JhKDQ1LDIxMiwxOTEsLjYp"
    "O2JhY2tncm91bmQ6cmdiYSg0NSwyMTIsMTkxLC4xMCk7Ym9yZGVyLXJhZGl1czo5OTlweDtwYWRkaW5nOjRweCAxMnB4O2ZvbnQt"
    "c2l6ZTouOTVyZW1cIj4yNSBub3ZlbWJyZSDigJMgMjcgZMOpY2VtYnJlPC9zcGFuPjxzcGFuIHN0eWxlPVwiZGlzcGxheTppbmxp"
    "bmUtYmxvY2shaW1wb3J0YW50O2JvcmRlcjoxcHggc29saWQgcmdiYSg0NSwyMTIsMTkxLC42KTtiYWNrZ3JvdW5kOnJnYmEoNDUs"
    "MjEyLDE5MSwuMTApO2JvcmRlci1yYWRpdXM6OTk5cHg7cGFkZGluZzo0cHggMTJweDtmb250LXNpemU6Ljk1cmVtXCI+ZW52aXJv"
    "biAxNTAgY2hhbGV0czwvc3Bhbj48c3BhbiBzdHlsZT1cImRpc3BsYXk6aW5saW5lLWJsb2NrIWltcG9ydGFudDtib3JkZXI6MXB4"
    "IHNvbGlkIHJnYmEoNDUsMjEyLDE5MSwuNik7YmFja2dyb3VuZDpyZ2JhKDQ1LDIxMiwxOTEsLjEwKTtib3JkZXItcmFkaXVzOjk5"
    "OXB4O3BhZGRpbmc6NHB4IDEycHg7Zm9udC1zaXplOi45NXJlbVwiPmdyYW5kZSByb3VlIGRlIDU1IG08L3NwYW4+PC9kaXY+PHA+"
    "w4AgUmVpbXMsIGxlIG1hcmNow6kgc+KAmWluc3RhbGxlIHN1ciBsZXMgSGF1dGVzIFByb21lbmFkZXMgSmVhbi1Mb3Vpcy1TY2hu"
    "ZWl0ZXIgZXQgbOKAmWVzcGxhbmFkZSBkZSBsYSBwb3J0ZSBkZSBNYXJzLCBhdmVjIGVudmlyb24gMTUwIGNoYWxldHMuIFVuZSBn"
    "cmFuZGUgcm91ZSBkZSA1NSBtw6h0cmVzIHNlIGRyZXNzZSBwbGFjZSBk4oCZRXJsb24gKDgg4oKsIHBvdXIgbGVzIGFkdWx0ZXMs"
    "IDYg4oKsIHBvdXIgbGVzIGVuZmFudHMpLiBMZSBzcGVjdGFjbGUgZGUgbHVtacOocmUgwqsgUmVnYWxpYSDCuyBlc3QgcHJvamV0"
    "w6kgZ3JhdHVpdGVtZW50IHN1ciBsYSBmYcOnYWRlIGRlIGxhIGNhdGjDqWRyYWxlIGxlIHZlbmRyZWRpIGV0IGxlIHNhbWVkaSDD"
    "oCAyMCBoIGp1c3F14oCZYXUgMyBqYW52aWVyLCBzYXVmIGV4Y2VwdGlvbiA6IHbDqXJpZmlleiBsZXMgZGF0ZXMgYXZhbnQgZGUg"
    "cGFydGlyLjwvcD48ZmlndXJlIHN0eWxlPVwibWFyZ2luOjE4cHggMFwiPjxpbWcgY2xhc3M9XCJtaGMtaW1nXCIgc3R5bGU9XCJk"
    "aXNwbGF5OmJsb2NrIWltcG9ydGFudDttYXJnaW46MTRweCBhdXRvIWltcG9ydGFudDt3aWR0aDoxMDAlIWltcG9ydGFudDttYXgt"
    "d2lkdGg6NTIwcHghaW1wb3J0YW50O2hlaWdodDphdXRvIWltcG9ydGFudDttYXgtaGVpZ2h0OjM0MHB4IWltcG9ydGFudDtvYmpl"
    "Y3QtZml0OmNvbnRhaW4haW1wb3J0YW50O2JvcmRlci1yYWRpdXM6MTJweDtib3gtc2hhZG93OjAgMnB4IDE0cHggcmdiYSgwLDAs"
    "MCwuMTgpXCIgc3JjPVwiaHR0cHM6Ly9teWhvdGVsY29tcGFyZS5jb20vaW1hZ2VzL21hcmNoZS1ub2VsLXJlaW1zLmpwZ1wiIGFs"
    "dD1cIk1hcmNow6kgZGUgTm/Dq2wgZGUgUmVpbXMgYXZlYyBsYSBncmFuZGUgcm91ZSBldCBsYSBjYXRow6lkcmFsZVwiIGxvYWRp"
    "bmc9XCJsYXp5XCI+PGZpZ2NhcHRpb24gY2xhc3M9XCJtaGMtY2FwXCIgc3R5bGU9XCJ0ZXh0LWFsaWduOmNlbnRlclwiPkFsbMOp"
    "ZSBkZSBjaGFsZXRzIGR1IG1hcmNow6kgZGUgTm/Dq2wgZGUgUmVpbXMsIGF2ZWMgbGEgZ3JhbmRlIHJvdWUgZXQgbGEgY2F0aMOp"
    "ZHJhbGUgYXUgZm9uZCAoaW1hZ2UgZOKAmWlsbHVzdHJhdGlvbikuPC9maWdjYXB0aW9uPjwvZmlndXJlPjxwPjxzdHJvbmc+w4Ag"
    "c2F2b2lyIDo8L3N0cm9uZz4ganVzcXXigJlhdSAyMCBkw6ljZW1icmUsIGxlcyBjaGFsZXRzIHNvbnQgb3V2ZXJ0cyBkZSAxMSBo"
    "IDMwIMOgIDIxIGggZHUgbWFyZGkgYXUgamV1ZGksIGp1c3F14oCZw6AgMjIgaCBsZSB2ZW5kcmVkaSBldCBkZSAxMCBoIMOgIDIy"
    "IGggbGUgc2FtZWRpLiBJbHMgc29udCBmZXJtw6lzIGxlIDI1IGTDqWNlbWJyZSwgZXQgbGUgMjQgaWxzIGZlcm1lbnQgw6AgMTgg"
    "aC48L3A+PCEtLUhPVEVMUyBSZWltcyB8IGZyYW5jZSB8IHJlaW1zIHwgZXBlcm5heSx0aW5xdWV1eCxiZXphbm5lcyxjb3Jtb250"
    "cmV1aWwsYXksaGF1dHZpbGxlcnMsY2hhbXBpbGxvbixtdXRpZ255LS0+XG48aDIgaWQ9XCJtaGMtbHlvblwiPjUuIEx5b24sIGVu"
    "dHJlIG1hcmNow6kgZXQgZsOqdGUgZGVzIEx1bWnDqHJlczwvaDI+PGRpdiBjbGFzcz1cIm1oYy1mYWN0c1wiIHN0eWxlPVwiZGlz"
    "cGxheTpmbGV4IWltcG9ydGFudDtmbGV4LXdyYXA6d3JhcCFpbXBvcnRhbnQ7Z2FwOjhweDttYXJnaW46MTBweCAwIDE0cHhcIj48"
    "c3BhbiBzdHlsZT1cImRpc3BsYXk6aW5saW5lLWJsb2NrIWltcG9ydGFudDtib3JkZXI6MXB4IHNvbGlkIHJnYmEoNDUsMjEyLDE5"
    "MSwuNik7YmFja2dyb3VuZDpyZ2JhKDQ1LDIxMiwxOTEsLjEwKTtib3JkZXItcmFkaXVzOjk5OXB4O3BhZGRpbmc6NHB4IDEycHg7"
    "Zm9udC1zaXplOi45NXJlbVwiPjIwIG5vdmVtYnJlIOKAkyAyNCBkw6ljZW1icmU8L3NwYW4+PHNwYW4gc3R5bGU9XCJkaXNwbGF5"
    "OmlubGluZS1ibG9jayFpbXBvcnRhbnQ7Ym9yZGVyOjFweCBzb2xpZCByZ2JhKDQ1LDIxMiwxOTEsLjYpO2JhY2tncm91bmQ6cmdi"
    "YSg0NSwyMTIsMTkxLC4xMCk7Ym9yZGVyLXJhZGl1czo5OTlweDtwYWRkaW5nOjRweCAxMnB4O2ZvbnQtc2l6ZTouOTVyZW1cIj5w"
    "bHVzIGRlIDEwMCBjaGFsZXRzPC9zcGFuPjxzcGFuIHN0eWxlPVwiZGlzcGxheTppbmxpbmUtYmxvY2shaW1wb3J0YW50O2JvcmRl"
    "cjoxcHggc29saWQgcmdiYSg0NSwyMTIsMTkxLC42KTtiYWNrZ3JvdW5kOnJnYmEoNDUsMjEyLDE5MSwuMTApO2JvcmRlci1yYWRp"
    "dXM6OTk5cHg7cGFkZGluZzo0cHggMTJweDtmb250LXNpemU6Ljk1cmVtXCI+THVtacOocmVzIDogNSDigJMgOCBkw6ljZW1icmU8"
    "L3NwYW4+PC9kaXY+PHA+TGUgbWFyY2jDqSBkZSBOb8OrbCBkZSBMeW9uIHNlIHRpZW50IHBsYWNlIENhcm5vdCwgw6AgY8O0dMOp"
    "IGRlIGxhIGdhcmUgZGUgUGVycmFjaGUsIGR1IDxzdHJvbmc+MjAgbm92ZW1icmUgYXUgMjQgZMOpY2VtYnJlPC9zdHJvbmc+LCBh"
    "dmVjIHBsdXMgZGUgMTAwIGNoYWxldHMgZXQgZW52aXJvbiA1MDAgMDAwIHZpc2l0ZXVycyBwYXIgw6lkaXRpb24gZOKAmWFwcsOo"
    "cyBsYSBWaWxsZS4gSWwgZXN0IHByw6lzZW50w6kgY29tbWUgbGUgcGx1cyBncmFuZCBkZSBsYSByw6lnaW9uLjwvcD48ZmlndXJl"
    "IHN0eWxlPVwibWFyZ2luOjE4cHggMFwiPjxpbWcgY2xhc3M9XCJtaGMtaW1nXCIgc3R5bGU9XCJkaXNwbGF5OmJsb2NrIWltcG9y"
    "dGFudDttYXJnaW46MTRweCBhdXRvIWltcG9ydGFudDt3aWR0aDoxMDAlIWltcG9ydGFudDttYXgtd2lkdGg6NTIwcHghaW1wb3J0"
    "YW50O2hlaWdodDphdXRvIWltcG9ydGFudDttYXgtaGVpZ2h0OjM0MHB4IWltcG9ydGFudDtvYmplY3QtZml0OmNvbnRhaW4haW1w"
    "b3J0YW50O2JvcmRlci1yYWRpdXM6MTJweDtib3gtc2hhZG93OjAgMnB4IDE0cHggcmdiYSgwLDAsMCwuMTgpXCIgc3JjPVwiaHR0"
    "cHM6Ly9teWhvdGVsY29tcGFyZS5jb20vaW1hZ2VzL21hcmNoZS1ub2VsLWx5b24uanBnXCIgYWx0PVwiTWFyY2jDqSBkZSBOb8Or"
    "bCDDoCBMeW9uIGF2ZWMgZ3JhbmRlIHJvdWUsIHBhdGlub2lyZSBldCBiYXNpbGlxdWUgZGUgRm91cnZpw6hyZVwiIGxvYWRpbmc9"
    "XCJsYXp5XCI+PGZpZ2NhcHRpb24gY2xhc3M9XCJtaGMtY2FwXCIgc3R5bGU9XCJ0ZXh0LWFsaWduOmNlbnRlclwiPkFtYmlhbmNl"
    "IGRlIE5vw6tsIMOgIEx5b24sIGF2ZWMgbGEgZ3JhbmRlIHJvdWUsIGxhIHBhdGlub2lyZSBldCBsYSBiYXNpbGlxdWUgZGUgRm91"
    "cnZpw6hyZSBlbiBmb25kIChpbWFnZSBk4oCZaWxsdXN0cmF0aW9uKS48L2ZpZ2NhcHRpb24+PC9maWd1cmU+PHA+RHUgPHN0cm9u"
    "Zz41IGF1IDggZMOpY2VtYnJlPC9zdHJvbmc+LCBsYSBGw6p0ZSBkZXMgTHVtacOocmVzIGFuaW1lIHRvdXRlIGxhIHZpbGxlLCBl"
    "dCBsZSBtYXJjaMOpIHBldXQgZmVybWVyIHBsdXMgdMO0dCBjZXMgam91cnMtbMOgIDogbOKAmWhldXJlIG7igJllc3QgcGFzIGVu"
    "Y29yZSBwdWJsacOpZSBwb3VyIDIwMjYuIExlcyB2YWNhbmNlcyBkZSBOb8OrbCBjb21tZW5jZW50IGxlIDE5IGTDqWNlbWJyZSDD"
    "oCBMeW9uLCBldCBsZXMgZGVybmllcnMgam91cnMgc29udCBkb25jIGxlcyBwbHVzIGNoYXJnw6lzLjwvcD48IS0tSE9URUxTIEx5"
    "b24gfCBmcmFuY2UgfCBseW9uIHwgdmlsbGV1cmJhbm5lLGNhbHVpcmUsdmF1bHgsYnJvbixlY3VsbHksdGFzc2luLG91bGxpbnMs"
    "ZnJhbmNoZXZpbGxlLS0+XG48aDIgaWQ9XCJtaGMtYW5uZWN5XCI+Ni4gQW5uZWN5LCBsZSBOb8OrbCBkZXMgQWxwZXM8L2gyPjxk"
    "aXYgY2xhc3M9XCJtaGMtZmFjdHNcIiBzdHlsZT1cImRpc3BsYXk6ZmxleCFpbXBvcnRhbnQ7ZmxleC13cmFwOndyYXAhaW1wb3J0"
    "YW50O2dhcDo4cHg7bWFyZ2luOjEwcHggMCAxNHB4XCI+PHNwYW4gc3R5bGU9XCJkaXNwbGF5OmlubGluZS1ibG9jayFpbXBvcnRh"
    "bnQ7Ym9yZGVyOjFweCBzb2xpZCByZ2JhKDQ1LDIxMiwxOTEsLjYpO2JhY2tncm91bmQ6cmdiYSg0NSwyMTIsMTkxLC4xMCk7Ym9y"
    "ZGVyLXJhZGl1czo5OTlweDtwYWRkaW5nOjRweCAxMnB4O2ZvbnQtc2l6ZTouOTVyZW1cIj4yNiBub3ZlbWJyZSDigJMgMyBqYW52"
    "aWVyPC9zcGFuPjxzcGFuIHN0eWxlPVwiZGlzcGxheTppbmxpbmUtYmxvY2shaW1wb3J0YW50O2JvcmRlcjoxcHggc29saWQgcmdi"
    "YSg0NSwyMTIsMTkxLC42KTtiYWNrZ3JvdW5kOnJnYmEoNDUsMjEyLDE5MSwuMTApO2JvcmRlci1yYWRpdXM6OTk5cHg7cGFkZGlu"
    "Zzo0cHggMTJweDtmb250LXNpemU6Ljk1cmVtXCI+cHLDqHMgZGUgMjAwIGNoYWxldHM8L3NwYW4+PHNwYW4gc3R5bGU9XCJkaXNw"
    "bGF5OmlubGluZS1ibG9jayFpbXBvcnRhbnQ7Ym9yZGVyOjFweCBzb2xpZCByZ2JhKDQ1LDIxMiwxOTEsLjYpO2JhY2tncm91bmQ6"
    "cmdiYSg0NSwyMTIsMTkxLC4xMCk7Ym9yZGVyLXJhZGl1czo5OTlweDtwYWRkaW5nOjRweCAxMnB4O2ZvbnQtc2l6ZTouOTVyZW1c"
    "Ij5hdSBib3JkIGR1IGxhYzwvc3Bhbj48L2Rpdj48cD5MZSBOb8OrbCBkZXMgQWxwZXMgZOKAmUFubmVjeSBzZSB0aWVudCBkdSA8"
    "c3Ryb25nPjI2IG5vdmVtYnJlIDIwMjYgYXUgMyBqYW52aWVyIDIwMjc8L3N0cm9uZz4sIGF2ZWMgcHLDqHMgZGUgMjAwIGNoYWxl"
    "dHMgYW5ub25jw6lzIHBhciBs4oCZb3JnYW5pc2F0ZXVyLiBJbCBvY2N1cGUgbGUgY2VudHJlLXZpbGxlLCBsZXMgcXVhaXMgKFZp"
    "Y2VuemEgZXQgQmF5cmV1dGgpIGV0IGxlcyBKYXJkaW5zIGRlIGzigJlFdXJvcGUuIExlIHNwZWN0YWNsZSBk4oCZb3V2ZXJ0dXJl"
    "IGEgbGlldSBsZSB2ZW5kcmVkaSAyNyBub3ZlbWJyZSDDoCBwYXJ0aXIgZGUgMTcgaCAzMC48L3A+PGZpZ3VyZSBzdHlsZT1cIm1h"
    "cmdpbjoxOHB4IDBcIj48aW1nIGNsYXNzPVwibWhjLWltZ1wiIHN0eWxlPVwiZGlzcGxheTpibG9jayFpbXBvcnRhbnQ7bWFyZ2lu"
    "OjE0cHggYXV0byFpbXBvcnRhbnQ7d2lkdGg6MTAwJSFpbXBvcnRhbnQ7bWF4LXdpZHRoOjUyMHB4IWltcG9ydGFudDtoZWlnaHQ6"
    "YXV0byFpbXBvcnRhbnQ7bWF4LWhlaWdodDozNDBweCFpbXBvcnRhbnQ7b2JqZWN0LWZpdDpjb250YWluIWltcG9ydGFudDtib3Jk"
    "ZXItcmFkaXVzOjEycHg7Ym94LXNoYWRvdzowIDJweCAxNHB4IHJnYmEoMCwwLDAsLjE4KVwiIHNyYz1cImh0dHBzOi8vbXlob3Rl"
    "bGNvbXBhcmUuY29tL2ltYWdlcy9tYXJjaGUtbm9lbC1hbm5lY3kuanBnXCIgYWx0PVwiVHVubmVsIGRlIGx1bWnDqHJlcyBkZSBO"
    "b8OrbCBhdSBib3JkIGRlIGzigJllYXVcIiBsb2FkaW5nPVwibGF6eVwiPjxmaWdjYXB0aW9uIGNsYXNzPVwibWhjLWNhcFwiIHN0"
    "eWxlPVwidGV4dC1hbGlnbjpjZW50ZXJcIj5JbGx1bWluYXRpb25zIGRlIE5vw6tsIGF1IGJvcmQgZGUgbOKAmWVhdS48L2ZpZ2Nh"
    "cHRpb24+PC9maWd1cmU+PHA+PHN0cm9uZz7DgCBzYXZvaXIgOjwvc3Ryb25nPiBsZXMgMjQgZXQgMzEgZMOpY2VtYnJlLCBsZSBt"
    "YXJjaMOpIGZlcm1lIMOgIDE5IGggYXUgY2VudHJlLXZpbGxlIGV0IMOgIDIwIGggYXV4IEphcmRpbnMgZGUgbOKAmUV1cm9wZS4g"
    "TGUgMjUgZMOpY2VtYnJlIGV0IGxlIDFlciBqYW52aWVyLCBs4oCZaG9yYWlyZSBk4oCZb3V2ZXJ0dXJlIHZhcmllIHNlbG9uIGxl"
    "cyBzb3VyY2VzIDogYXJyaXZleiBhcHLDqHMgMTUgaC4gTGVzIHBhcmtpbmdzIGNvdXZlcnRzIGR1IGNlbnRyZSBzb250IGNvbnNl"
    "aWxsw6lzLCBtYWlzIGxhIHBsdXBhcnQgbGltaXRlbnQgbGEgaGF1dGV1ciDDoCAxLDkwIG0uPC9wPjwhLS1IT1RFTFMgQW5uZWN5"
    "IHwgZnJhbmNlIHwgYW5uZWN5IHwgdGFsbG9pcmVzLHNldnJpZXIsdmV5cmllcixtZW50aG9uLGRvdXNzYXJkLHNhaW50LWpvcmlv"
    "eixkdWluZ3QsbGEtYmFsbWUtLT5cbjxoMiBpZD1cIm1oYy10YWJsZWF1XCI+TGUgY2FsZW5kcmllciBlbiB1biBjb3VwIGTigJnF"
    "k2lsPC9oMj48ZGl2IGNsYXNzPVwibWhjLXdyYXBcIj48dGFibGUgY2xhc3M9XCJtaGMtdGFibGVcIj48dGhlYWQ+PHRyPjx0aD5W"
    "aWxsZTwvdGg+PHRoPkRhdGVzIDIwMjY8L3RoPjx0aD7DgCByZXRlbmlyPC90aD48L3RyPjwvdGhlYWQ+PHRib2R5Pjx0cj48dGQ+"
    "THlvbjwvdGQ+PHRkIGNsYXNzPVwiblwiPjIwIG5vdi4g4oCTIDI0IGTDqWMuPC90ZD48dGQ+RsOqdGUgZGVzIEx1bWnDqHJlcyA1"
    "IOKAkyA4IGTDqWMuPC90ZD48L3RyPjx0cj48dGQ+Q29sbWFyPC90ZD48dGQgY2xhc3M9XCJuXCI+MjMgbm92LiDigJMgMjkgZMOp"
    "Yy48L3RkPjx0ZD42IG1hcmNow6lzLCBQZXRpdGUgVmVuaXNlPC90ZD48L3RyPjx0cj48dGQ+UmVpbXM8L3RkPjx0ZCBjbGFzcz1c"
    "Im5cIj4yNSBub3YuIOKAkyAyNyBkw6ljLjwvdGQ+PHRkPkdyYW5kZSByb3VlIGRlIDU1IG08L3RkPjwvdHI+PHRyPjx0ZD5Bbm5l"
    "Y3k8L3RkPjx0ZCBjbGFzcz1cIm5cIj4yNiBub3YuIOKAkyAzIGphbnYuPC90ZD48dGQ+UHLDqHMgZGUgMjAwIGNoYWxldHM8L3Rk"
    "PjwvdHI+PHRyPjx0ZD5TdHJhc2JvdXJnPC90ZD48dGQgY2xhc3M9XCJuXCI+Mjcgbm92LiDigJMgMjQgZMOpYy48L3RkPjx0ZD44"
    "IG1hcmNow6lzLCBkZXB1aXMgMTU3MDwvdGQ+PC90cj48dHI+PHRkPktheXNlcnNiZXJnPC90ZD48dGQgY2xhc3M9XCJuXCI+Mjcg"
    "bm92LiDigJMgMjAgZMOpYy48L3RkPjx0ZD5WZW5kcmVkaSBhdSBkaW1hbmNoZSBzZXVsZW1lbnQ8L3RkPjwvdHI+PC90Ym9keT48"
    "L3RhYmxlPjwvZGl2PjxwIGNsYXNzPVwibWhjLWNhcFwiPlNvdXJjZXMgOiBzaXRlcyBkZXMgdmlsbGVzIGV0IHByZXNzZSwgYXUg"
    "MjIgbm92ZW1icmUgMjAyNi4gTGVzIGRhdGVzIGRlIGZlcm1ldHVyZSBldCBsZXMgaG9yYWlyZXMgcGV1dmVudCDDqXZvbHVlci48"
    "L3A+XG48aDIgaWQ9XCJtaGMtY29uc2VpbHNcIj5Ob3MgY29uc2VpbHMgcG91ciBiaWVuIGxlcyB2aXNpdGVyPC9oMj48dWw+PGxp"
    "PjxzdHJvbmc+w4l2aXRleiBsZXMgd2Vlay1lbmRzIGV0IGxlcyBzb2lyw6llcyBk4oCZYWZmbHVlbmNlLjwvc3Ryb25nPiDDgCBT"
    "dHJhc2JvdXJnLCBsZXMgbHVuZGlzLCBtYXJkaXMgZXQgamV1ZGlzIHNvbnQgY2FsbWVzLCBldCBsZSBzYW1lZGkgZXN0IHRyw6hz"
    "IGZyw6lxdWVudMOpIGTDqHMgMTMgaC4gw4AgQ29sbWFyLCBsZXMgcGFya2luZ3MgZW4gcGxlaW4gYWlyIHNvbnQgcGxlaW5zIGTD"
    "qHMgMTEgaCBsZSB3ZWVrLWVuZC48L2xpPjxsaT48c3Ryb25nPkNvbWJpbmV6IGxlcyB2aWxsZXMgZOKAmUFsc2FjZSBlbiB0cmFp"
    "bi48L3N0cm9uZz4gQ29sbWFyIGVzdCDDoCBlbnZpcm9uIDMwIG1pbnV0ZXMgZGUgU3RyYXNib3VyZyBldCBsZSB0cmFqZXQgw6l2"
    "aXRlIGRlIGNoZXJjaGVyIHVuZSBwbGFjZS4gw4AgU3RyYXNib3VyZywgbGUgZGVybmllciBURVIgdmVycyBTw6lsZXN0YXQsIENv"
    "bG1hciBldCBNdWxob3VzZSBwYXJ0IMOgIDIzIGggMjAgbGUgdmVuZHJlZGkgZXQgbGUgc2FtZWRpIChob3JhaXJlIHRow6lvcmlx"
    "dWUganVzcXXigJlhdSAxMyBkw6ljZW1icmUpLjwvbGk+PGxpPjxzdHJvbmc+UsOpc2VydmV6IHZvdHJlIGjDtHRlbCB0w7R0Ljwv"
    "c3Ryb25nPiBMZXMgY2hhbWJyZXMgYXUgY2VudHJlIGRlIGNlcyB2aWxsZXMgc2UgcmVtcGxpc3NlbnQgdml0ZSBlbiBkw6ljZW1i"
    "cmUgOiBjb21wYXJleiBsZXMgbm90ZXMgZXQgbGVzIHByaXggZGFucyA8YSBocmVmPVwiaHR0cHM6Ly9teWhvdGVsY29tcGFyZS5j"
    "b20vaG90ZWxzLmh0bWxcIj5ub3MgaMO0dGVsczwvYT4gZXQgbGlzZXogPGEgaHJlZj1cImh0dHBzOi8vbXlob3RlbGNvbXBhcmUu"
    "Y29tL2NvbW1lbnQtdHJvdXZlci11bi1ob3RlbC1tb2lucy1jaGVyLmh0bWxcIj5jb21tZW50IHRyb3V2ZXIgdW4gaMO0dGVsIG1v"
    "aW5zIGNoZXI8L2E+LjwvbGk+PGxpPjxzdHJvbmc+UGFydGV6IGVuIHZvaXR1cmUgc2FucyBhdXRvcm91dGUuPC9zdHJvbmc+IFBy"
    "w6lwYXJleiB2b3RyZSB0cmFqZXQgYXZlYyA8YSBocmVmPVwiaHR0cHM6Ly9teWhvdGVsY29tcGFyZS5jb20vaXRpbmVyYWlyZS1k"
    "ZWNvdXZlcnRlLmh0bWxcIj5ub3RyZSBwbGFuaWZpY2F0ZXVyIGTigJlpdGluw6lyYWlyZXM8L2E+LCBvdSBsaXNleiBub3RyZSB0"
    "cmFqZXQgPGEgaHJlZj1cImh0dHBzOi8vbXlob3RlbGNvbXBhcmUuY29tL3N0cmFzYm91cmctbWlsYW4tc2Fucy1hdXRvcm91dGUu"
    "aHRtbFwiPlN0cmFzYm91cmcg4oCTIE1pbGFuIHNhbnMgYXV0b3JvdXRlPC9hPiwgcXVpIHBhcnQgZGUgU3RyYXNib3VyZy48L2xp"
    "PjxsaT48c3Ryb25nPkNob2lzaXNzZXogbGEgYm9ubmUgZGF0ZS48L3N0cm9uZz4gUG91ciBjb21wYXJlciBsZXMgcMOpcmlvZGVz"
    "LCB2b3lleiA8YSBocmVmPVwiaHR0cHM6Ly9teWhvdGVsY29tcGFyZS5jb20vcXVhbmQtcGFydGlyLWV0LW91LWNhbGVuZHJpZXIt"
    "dm95YWdldXJzLmh0bWxcIj5ub3RyZSBjYWxlbmRyaWVyIHF1YW5kIHBhcnRpciBldCBvw7k8L2E+LjwvbGk+PC91bD5cbjxoMiBp"
    "ZD1cIm1oYy1mYXFcIj5RdWVzdGlvbnMgZnLDqXF1ZW50ZXM8L2gyPjxkZXRhaWxzIGNsYXNzPVwibWhjLWZhcVwiPjxzdW1tYXJ5"
    "PlF1ZWwgZXN0IGxlIHBsdXMgYW5jaWVuIG1hcmNow6kgZGUgTm/Dq2wgZGUgRnJhbmNlID88L3N1bW1hcnk+PHA+U3RyYXNib3Vy"
    "ZyBtZXQgZW4gYXZhbnQgbGUgc2llbiA6IGxhIFZpbGxlIGxlIGZhaXQgbmHDrnRyZSBlbiAxNTcwIGV0IGxlIHByw6lzZW50ZSBj"
    "b21tZSBs4oCZdW4gZGVzIHBsdXMgYW5jaWVucyBk4oCZRXVyb3BlLjwvcD48L2RldGFpbHM+PGRldGFpbHMgY2xhc3M9XCJtaGMt"
    "ZmFxXCI+PHN1bW1hcnk+UXVlbCBtYXJjaMOpIGVzdCBsZSBtb2lucyBmcsOpcXVlbnTDqSA/PC9zdW1tYXJ5PjxwPkxlcyBqb3Vy"
    "cyBkZSBzZW1haW5lLCBob3JzIHZhY2FuY2VzIHNjb2xhaXJlcywgc29udCBsZXMgcGx1cyBjYWxtZXMuIMOAIFN0cmFzYm91cmcs"
    "IGxlcyBsdW5kaXMsIG1hcmRpcyBldCBqZXVkaXMgc29udCBsZXMgam91cnMgbGVzIHBsdXMgdHJhbnF1aWxsZXMuPC9wPjwvZGV0"
    "YWlscz48ZGV0YWlscyBjbGFzcz1cIm1oYy1mYXFcIj48c3VtbWFyeT5RdWVsIG1hcmNow6kgZGUgTm/Dq2wgb3V2cmUgZW4gcHJl"
    "bWllciA/PC9zdW1tYXJ5PjxwPlBhcm1pIG5vcyBzaXggdmlsbGVzLCBMeW9uIG91dnJlIGxlIDIwIG5vdmVtYnJlIDIwMjYsIHB1"
    "aXMgQ29sbWFyIGxlIDIzIG5vdmVtYnJlLjwvcD48L2RldGFpbHM+PGRldGFpbHMgY2xhc3M9XCJtaGMtZmFxXCI+PHN1bW1hcnk+"
    "S2F5c2Vyc2JlcmcgZXN0LWlsIG91dmVydCB0b3V0ZSBsYSBzZW1haW5lID88L3N1bW1hcnk+PHA+Tm9uLCBzZXVsZW1lbnQgZHUg"
    "dmVuZHJlZGkgYXUgZGltYW5jaGUsIHBlbmRhbnQgbGVzIHF1YXRyZSB3ZWVrLWVuZHMgZGUgbOKAmUF2ZW50IDogMjcgYXUgMjkg"
    "bm92ZW1icmUsIHB1aXMgNCBhdSA2LCAxMSBhdSAxMyBldCAxOCBhdSAyMCBkw6ljZW1icmUgMjAyNi48L3A+PC9kZXRhaWxzPjxk"
    "ZXRhaWxzIGNsYXNzPVwibWhjLWZhcVwiPjxzdW1tYXJ5PkZhdXQtaWwgdmVuaXIgZW4gdm9pdHVyZSA/PC9zdW1tYXJ5PjxwPlBh"
    "cyBmb3Jjw6ltZW50LiDDgCBTdHJhc2JvdXJnLCBsZXMgdm9pdHVyZXMgc29udCBpbnRlcmRpdGVzIGRhbnMgbGEgR3JhbmRlIMOO"
    "bGUgYXV4IGhldXJlcyBk4oCZb3V2ZXJ0dXJlLCBldCDDoCBDb2xtYXIgbGUgdHJhaW4gZGVwdWlzIFN0cmFzYm91cmcgZHVyZSBl"
    "bnZpcm9uIDMwIG1pbnV0ZXMuIExlIHBhcmtpbmcgcmVsYWlzIGVzdCB1bmUgYm9ubmUgc29sdXRpb24uPC9wPjwvZGV0YWlscz5c"
    "bjxkaXYgY2xhc3M9XCJnbGFzcy1ib3hcIiBzdHlsZT1cIm1hcmdpbjoyMnB4IDA7IGJvcmRlci1sZWZ0OjVweCBzb2xpZCB2YXIo"
    "LS1wcmltYXJ5KTsgdGV4dC1hbGlnbjpjZW50ZXI7XCI+PGgzIHN0eWxlPVwibWFyZ2luLXRvcDowO1wiPvCfjoQgUsOpc2VydmV6"
    "IHZvdHJlIHPDqWpvdXI8L2gzPjxwIHN0eWxlPVwibWFyZ2luLWJvdHRvbToxNnB4O1wiPkNvbXBhcmV6IGxlcyBow7R0ZWxzIGRl"
    "IHZvdHJlIHZpbGxlIGRlIG1hcmNow6kgZGUgTm/Dq2wsIGF2ZWMgbGVzIG5vdGVzLCBsZXMgcHJpeCBldCBsZXMgYXZpcyBkZXMg"
    "dm95YWdldXJzLjwvcD48YSBjbGFzcz1cImJ0blwiIGhyZWY9XCJodHRwczovL215aG90ZWxjb21wYXJlLmNvbS9ob3RlbHMuaHRt"
    "bFwiPkNvbXBhcmVyIGxlcyBow7R0ZWxzPC9hPjwvZGl2PlxuPGgyPlNvdXJjZXMgZXQgbcOpdGhvZGU8L2gyPjxwPkxlcyBkYXRl"
    "cyBldCBsZXMgY2hpZmZyZXMgdmllbm5lbnQgZGVzIHNpdGVzIGRlcyB2aWxsZXMsIGRlcyBvZmZpY2VzIGRlIHRvdXJpc21lIGV0"
    "IGRlIGxhIHByZXNzZSwgY29uc3VsdMOpcyBsZSAyMiBub3ZlbWJyZSAyMDI2IDogVGhlIENvbm5leGlvbiAoZGF0ZXMgMjAyNiBk"
    "ZXMgbWFyY2jDqXMgZGUgRnJhbmNlKSwgT25pdmFwcCAoU3RyYXNib3VyZywgQW5uZWN5LCBSZWltcywgTHlvbiksIFJ5byAoQ29s"
    "bWFyKSBldCBOb8OrbCDDoCBDb2xtYXIgKEtheXNlcnNiZXJnKS4gTGVzIGNoaWZmcmVzIGRlIGZyw6lxdWVudGF0aW9uIHNvbnQg"
    "Y2V1eCBhbm5vbmPDqXMgcGFyIGxlcyB2aWxsZXMgZXQgbGVzIHNvdXJjZXMgdG91cmlzdGlxdWVzLiBMZXMgaG9yYWlyZXMgMjAy"
    "NiBkZSBTdHJhc2JvdXJnIG5lIHNvbnQgcGFzIHRvdXMgcHVibGnDqXMgOiB2w6lyaWZpZXotbGVzIGF2YW50IGRlIHBhcnRpci4g"
    "TGUgY2hvaXggZGUgY2VzIHNpeCB2aWxsZXMgZXN0IHVuZSBzw6lsZWN0aW9uIGRlIE15SG90ZWxDb21wYXJlLCBwYXMgdW4gcGFs"
    "bWFyw6hzIG9mZmljaWVsLiBMZXMgaW1hZ2VzIHNpZ25hbMOpZXMgY29tbWUgaWxsdXN0cmF0aW9ucyBuZSBzb250IHBhcyBkZXMg"
    "cGhvdG9zIGTigJlhcmNoaXZlcyBkZXMgbWFyY2jDqXMuPC9wPlxuPC9kaXY+In0="
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
