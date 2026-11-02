"""Publie l'article « Décembre au soleil » dans blog_data.json avec les liens vers vos hôtels.
Usage (dossier comparateur-ia) :  python decembre_soleil.py
Sauvegarde automatique : blog_data.json.bak2"""
import base64, json, re, shutil, sys, unicodedata
from pathlib import Path

SITE = "https://myhotelcompare.com"
MAX = 6
ARTICLE_B64 = (
    "eyJpZCI6ICJkZWNlbWJyZS1hdS1zb2xlaWwtNy1kZXN0aW5hdGlvbnMiLCAidGl0cmUiOiAiUGFydGlyIGF1IHNvbGVpbCBlbiBk"
    "w6ljZW1icmUgOiA3IGRlc3RpbmF0aW9ucyBwb3VyIGZ1aXIgbGUgZnJvaWQiLCAic2x1ZyI6ICJkZWNlbWJyZS1hdS1zb2xlaWwt"
    "Ny1kZXN0aW5hdGlvbnMiLCAiaW1hZ2UiOiAiaW1hZ2VzL2RlY2VtYnJlLWF1LXNvbGVpbC5qcGciLCAicmVzdW1lIjogIk1hcm9j"
    "LCBUdW5pc2llLCDDiWd5cHRlLCBDYW5hcmllcyA6IDcgZGVzdGluYXRpb25zIG/DuSBpbCBmYWl0IGRvdXggZW4gZMOpY2VtYnJl"
    "LCBhdmVjIHRlbXDDqXJhdHVyZXMsIGR1csOpZXMgZGUgdm9sLCDDqXRhdCBkZSBsYSBtZXIgZXQgdW5lIHPDqWxlY3Rpb24gZGUg"
    "bm9zIGjDtHRlbHMuIiwgImRldGFpbHMiOiAiPHN0eWxlPlxuLm1oYy1ub3Rle2JvcmRlci1sZWZ0OjVweCBzb2xpZCAjMmRkNGJm"
    "O2JhY2tncm91bmQ6cmdiYSg0NSwyMTIsMTkxLC4xMik7cGFkZGluZzoxNHB4IDE4cHg7Ym9yZGVyLXJhZGl1czowIDhweCA4cHgg"
    "MDttYXJnaW46MjBweCAwfVxuLm1oYy10ZWFzZXJ7YmFja2dyb3VuZDpyZ2JhKDIzMiw5Niw3NiwuMTIpO3BhZGRpbmc6MTJweCAx"
    "NnB4O2JvcmRlci1yYWRpdXM6OHB4O21hcmdpbjoyNHB4IDB9XG4ubWhjLXRlYXNlciBie2NvbG9yOiNlODYwNGN9XG4ubWhjLXRv"
    "Y3tib3JkZXI6MXB4IHNvbGlkIHJnYmEoMTI4LDEyOCwxMjgsLjM1KTtib3JkZXItcmFkaXVzOjEwcHg7cGFkZGluZzoxNHB4IDE4"
    "cHg7bWFyZ2luOjIwcHggMH1cbi5taGMtdG9jIG9se21hcmdpbjo2cHggMCAwO3BhZGRpbmctbGVmdDoyMHB4fVxuLm1oYy13cmFw"
    "e292ZXJmbG93LXg6YXV0bzttYXJnaW46MjBweCAwfVxuLm1oYy10YWJsZXt3aWR0aDoxMDAlO21pbi13aWR0aDo0ODBweDtib3Jk"
    "ZXItY29sbGFwc2U6Y29sbGFwc2U7Ym94LXNoYWRvdzowIDJweCAxMHB4IHJnYmEoMCwwLDAsLjA4KTtib3JkZXItcmFkaXVzOjhw"
    "eDtvdmVyZmxvdzpoaWRkZW59XG4ubWhjLXRhYmxlIHRoe2JhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDkwZGVnLCNmZjdmNmIs"
    "IzJkZDRiZik7Y29sb3I6I2ZmZjt0ZXh0LWFsaWduOmxlZnQ7cGFkZGluZzoxMnB4IDE2cHg7Zm9udC1zaXplOjE0cHh9XG4ubWhj"
    "LXRhYmxlIHRke3BhZGRpbmc6MTJweCAxNnB4O2JvcmRlci1ib3R0b206MXB4IHNvbGlkIHJnYmEoMTI4LDEyOCwxMjgsLjI1KX1c"
    "bi5taGMtdGFibGUgLm57dGV4dC1hbGlnbjpyaWdodDt3aGl0ZS1zcGFjZTpub3dyYXB9XG4ubWhjLWNhcHtmb250LXNpemU6Ljg1"
    "cmVtO29wYWNpdHk6Ljc1O21hcmdpbi10b3A6NnB4fVxuLm1oYy1iaWd7Zm9udC1zaXplOjIuNnJlbTtmb250LXdlaWdodDo4MDA7"
    "Y29sb3I6I2U4NjA0YztsaW5lLWhlaWdodDoxLjE7bWFyZ2luOjI0cHggMCA0cHh9XG4ubWhjLWZhY3Rze2Rpc3BsYXk6ZmxleDtm"
    "bGV4LXdyYXA6d3JhcDtnYXA6OHB4O21hcmdpbjoxMHB4IDAgMTRweH1cbi5taGMtZmFjdHMgc3Bhbntib3JkZXI6MXB4IHNvbGlk"
    "IHJnYmEoNDUsMjEyLDE5MSwuNik7YmFja2dyb3VuZDpyZ2JhKDQ1LDIxMiwxOTEsLjEwKTtib3JkZXItcmFkaXVzOjk5OXB4O3Bh"
    "ZGRpbmc6NHB4IDEycHg7Zm9udC1zaXplOi45NXJlbX1cbi5taGMtaW1ne2Rpc3BsYXk6YmxvY2s7bWFyZ2luOjE0cHggYXV0bztt"
    "YXgtd2lkdGg6MTAwJTttYXgtaGVpZ2h0OjQ2MHB4O3dpZHRoOmF1dG87aGVpZ2h0OmF1dG87Ym9yZGVyLXJhZGl1czoxMnB4O2Jv"
    "eC1zaGFkb3c6MCAycHggMTRweCByZ2JhKDAsMCwwLC4xOCl9XG4ubWhjLWhvdGVsc3tib3JkZXI6MXB4IHNvbGlkIHJnYmEoMTI4"
    "LDEyOCwxMjgsLjM1KTtib3JkZXItcmFkaXVzOjEwcHg7cGFkZGluZzoxMnB4IDE4cHg7bWFyZ2luOjE0cHggMH1cbi5taGMtaG90"
    "ZWxzIHVse21hcmdpbjo2cHggMCAwO3BhZGRpbmctbGVmdDoyMHB4fVxuLm1oYy1mYXF7Ym9yZGVyLWJvdHRvbToxcHggc29saWQg"
    "cmdiYSgxMjgsMTI4LDEyOCwuMyk7cGFkZGluZzoxMHB4IDB9XG4ubWhjLWZhcSBzdW1tYXJ5e2N1cnNvcjpwb2ludGVyO2ZvbnQt"
    "d2VpZ2h0OjcwMH1cbi5taGMtYXJ0e2ZvbnQtc2l6ZToxLjE1cmVtIWltcG9ydGFudDtsaW5lLWhlaWdodDoxLjchaW1wb3J0YW50"
    "fVxuLm1oYy1hcnQgcCwubWhjLWFydCBsaXtmb250LXNpemU6MS4xNXJlbSFpbXBvcnRhbnQ7bGluZS1oZWlnaHQ6MS43IWltcG9y"
    "dGFudDttYXJnaW46MCAwIDE0cHghaW1wb3J0YW50fVxuLm1oYy1hcnQgaDJ7Zm9udC1zaXplOjEuN3JlbSFpbXBvcnRhbnQ7bGlu"
    "ZS1oZWlnaHQ6MS4yNSFpbXBvcnRhbnQ7bWFyZ2luOjMycHggMCAxMnB4IWltcG9ydGFudH1cbi5taGMtYXJ0IGgze2ZvbnQtc2l6"
    "ZToxLjNyZW0haW1wb3J0YW50O21hcmdpbjoyMnB4IDAgOHB4IWltcG9ydGFudH1cbi5taGMtYXJ0IGJye2Rpc3BsYXk6bm9uZSFp"
    "bXBvcnRhbnR9XG4ubWhjLWFydCAubWhjLXdyYXAsLm1oYy1hcnQgLm1oYy1ub3RlLC5taGMtYXJ0IC5taGMtdGVhc2VyLC5taGMt"
    "YXJ0IC5taGMtdG9je21hcmdpbjoxNnB4IDAhaW1wb3J0YW50fVxuLm1oYy1hcnQgdGFibGV7Zm9udC1zaXplOjEuMDVyZW0haW1w"
    "b3J0YW50O21hcmdpbjowIWltcG9ydGFudH1cbi5taGMtYXJ0IC5taGMtdGFibGUgdGQsLm1oYy1hcnQgLm1oYy10YWJsZSB0aHtw"
    "YWRkaW5nOjEwcHggMTRweCFpbXBvcnRhbnR9XG4ubWhjLWFydCAubWhjLWNhcHtmb250LXNpemU6LjlyZW0haW1wb3J0YW50O21h"
    "cmdpbjo2cHggMCAxNnB4IWltcG9ydGFudH1cbi5taGMtYXJ0IC5taGMtZmFjdHMgc3Bhbntmb250LXNpemU6Ljk1cmVtIWltcG9y"
    "dGFudH1cbi5taGMtYXJ0IC5taGMtaG90ZWxzIGxpe21hcmdpbjowIDAgNnB4IWltcG9ydGFudDtmb250LXNpemU6MS4wNXJlbSFp"
    "bXBvcnRhbnR9XG48L3N0eWxlPlxuXG48ZGl2IGNsYXNzPVwibWhjLWFydFwiPlxuPHA+PHN0cm9uZz5Ew6ljZW1icmUgYXJyaXZl"
    "LCBsZSBmcm9pZCBhdXNzaS48L3N0cm9uZz4gQm9ubmUgbm91dmVsbGUgOiDDoCBkZXV4IG91IGNpbnEgaGV1cmVzIGTigJlhdmlv"
    "biBkZSBQYXJpcywgcGx1c2lldXJzIGRlc3RpbmF0aW9ucyBvZmZyZW50IGVuY29yZSBkZXMgam91cm7DqWVzIGVudHJlIDE4IGV0"
    "IDI0IMKwQywgcGFyZm9pcyB1bmUgbWVyIMOgIHBsdXMgZGUgMjAgwrBDLiBNYWlzIHRvdXRlcyBuZSBzZSB2YWxlbnQgcGFzLCBl"
    "dCBsZSDCqyBpbCBmYWl0IGJlYXUgZW4gaGl2ZXIgwrsgbWFzcXVlIGRlIHZyYWllcyBkaWZmw6lyZW5jZXMuPC9wPlxuPHA+TGEg"
    "ZGlmZsOpcmVuY2UgbmUgdGllbnQgcGFzIHNldWxlbWVudCDDoCBsYSB0ZW1ww6lyYXR1cmUuIEVsbGUgdGllbnQgYXVzc2kgw6Ag"
    "bGEgPGVtPm1lcjwvZW0+IChwZXV0LW9uIHZyYWltZW50IHPigJl5IGJhaWduZXIgPyksIMOgIGxhIGR1csOpZSBkdSB2b2wgZXQg"
    "YXUgYnVkZ2V0LiBOb3VzIGF2b25zIHLDqXVuaSBzZXB0IGRlc3RpbmF0aW9ucywgYXZlYyBsZXMgbW95ZW5uZXMgZGUgZMOpY2Vt"
    "YnJlLCBsYSBkdXLDqWUgZGVzIHZvbHMgZGlyZWN0cyBkZXB1aXMgUGFyaXMgZXQgdW5lIHPDqWxlY3Rpb24gZGUgbm9zIGjDtHRl"
    "bHMuPC9wPlxuPGRpdiBjbGFzcz1cIm1oYy1ub3RlXCI+PHN0cm9uZz5DZSBxdWUgdm91cyBhbGxleiB0cm91dmVyIGljaSA6PC9z"
    "dHJvbmc+IHVuIHRhYmxlYXUgY29tcGFyYXRpZiBkZXMgc2VwdCBkZXN0aW5hdGlvbnMsIHVuZSBwcsOpc2VudGF0aW9uIGR1IE1h"
    "cm9jLCBkZSBsYSBUdW5pc2llLCBkZSBs4oCZw4lneXB0ZSBldCBkZXMgQ2FuYXJpZXMgYXZlYyBsZXMgY2hpZmZyZXMgZGUgZMOp"
    "Y2VtYnJlLCB1biBndWlkZSBwb3VyIHNhdm9pciBxdWFuZCByw6lzZXJ2ZXIsIGV0IHVuZSBGQVEuIExlcyBkZXN0aW5hdGlvbnMg"
    "b8O5IGxhIG1lciByZXN0ZSBmcmHDrmNoZSBzb250IHNpZ25hbMOpZXMgOiBtaWV1eCB2YXV0IGxlIHNhdm9pciBhdmFudCBkZSBy"
    "w6lzZXJ2ZXIuPC9kaXY+XG48ZGl2IGNsYXNzPVwibWhjLXRvY1wiPjxzdHJvbmc+U29tbWFpcmU8L3N0cm9uZz48b2w+PGxpPjxh"
    "IGhyZWY9XCIjbWhjLXRhYmxlYXVcIj5MZXMgc2VwdCBkZXN0aW5hdGlvbnMgZW4gdW4gY291cCBk4oCZxZNpbDwvYT48L2xpPjxs"
    "aT48YSBocmVmPVwiI21oYy1tYXJvY1wiPk1hcm9jIDogTWFycmFrZWNoIGV0IEFnYWRpcjwvYT48L2xpPjxsaT48YSBocmVmPVwi"
    "I21oYy10dW5pc2llXCI+VHVuaXNpZSA6IERqZXJiYSwgSGFtbWFtZXQgZXQgU291c3NlPC9hPjwvbGk+PGxpPjxhIGhyZWY9XCIj"
    "bWhjLWVneXB0ZVwiPsOJZ3lwdGUgOiBIdXJnaGFkYSwgTWFyc2EgQWxhbSBldCBTaGFybSBlbC1TaGVpa2g8L2E+PC9saT48bGk+"
    "PGEgaHJlZj1cIiNtaGMtY2FuYXJpZXNcIj5MZXMgQ2FuYXJpZXM8L2E+PC9saT48bGk+PGEgaHJlZj1cIiNtaGMtcmVzZXJ2ZXJc"
    "Ij5RdWFuZCByw6lzZXJ2ZXIgPzwvYT48L2xpPjxsaT48YSBocmVmPVwiI21oYy1mYXFcIj5RdWVzdGlvbnMgZnLDqXF1ZW50ZXM8"
    "L2E+PC9saT48L29sPjwvZGl2PlxuPGgyIGlkPVwibWhjLXRhYmxlYXVcIj4xLiBMZXMgc2VwdCBkZXN0aW5hdGlvbnMgZW4gdW4g"
    "Y291cCBk4oCZxZNpbDwvaDI+XG48ZGl2IGNsYXNzPVwibWhjLXdyYXBcIj48dGFibGUgY2xhc3M9XCJtaGMtdGFibGVcIj48dGhl"
    "YWQ+PHRyPjx0aD5EZXN0aW5hdGlvbjwvdGg+PHRoIGNsYXNzPVwiblwiPlZvbCBkZXB1aXMgUGFyaXM8L3RoPjx0aCBjbGFzcz1c"
    "Im5cIj5Kb3VybsOpZSBlbiBkw6ljZW1icmU8L3RoPjx0aCBjbGFzcz1cIm5cIj5NZXI8L3RoPjwvdHI+PC90aGVhZD48dGJvZHk+"
    "PHRyPjx0ZD5NYXJyYWtlY2g8L3RkPjx0ZCBjbGFzcz1cIm5cIj4zIGggMTU8L3RkPjx0ZCBjbGFzcz1cIm5cIj4yMSDCsEM8L3Rk"
    "Pjx0ZCBjbGFzcz1cIm5cIj7igJQ8L3RkPjwvdHI+PHRyPjx0ZD5BZ2FkaXI8L3RkPjx0ZCBjbGFzcz1cIm5cIj4zIGggMzA8L3Rk"
    "Pjx0ZCBjbGFzcz1cIm5cIj4yMyDCsEM8L3RkPjx0ZCBjbGFzcz1cIm5cIj4xOCDCsEM8L3RkPjwvdHI+PHRyPjx0ZD5EamVyYmE8"
    "L3RkPjx0ZCBjbGFzcz1cIm5cIj4yIGggMzU8L3RkPjx0ZCBjbGFzcz1cIm5cIj4xOCDCsEM8L3RkPjx0ZCBjbGFzcz1cIm5cIj4x"
    "OCw1IMKwQzwvdGQ+PC90cj48dHI+PHRkPkhhbW1hbWV0IC8gU291c3NlPC90ZD48dGQgY2xhc3M9XCJuXCI+MiBoIDIwKjwvdGQ+"
    "PHRkIGNsYXNzPVwiblwiPmRvdXg8L3RkPjx0ZCBjbGFzcz1cIm5cIj7igJQ8L3RkPjwvdHI+PHRyPjx0ZD5IdXJnaGFkYTwvdGQ+"
    "PHRkIGNsYXNzPVwiblwiPjQgaCAzNSDigJMgNSBoPC90ZD48dGQgY2xhc3M9XCJuXCI+MjQgwrBDPC90ZD48dGQgY2xhc3M9XCJu"
    "XCI+MjMgwrBDPC90ZD48L3RyPjx0cj48dGQ+U2hhcm0gZWwtU2hlaWtoPC90ZD48dGQgY2xhc3M9XCJuXCI+ZW52LiA1IGg8L3Rk"
    "Pjx0ZCBjbGFzcz1cIm5cIj5wcm9jaGUgZGUgSHVyZ2hhZGE8L3RkPjx0ZCBjbGFzcz1cIm5cIj5wcm9jaGUgZGUgSHVyZ2hhZGE8"
    "L3RkPjwvdHI+PHRyPjx0ZD5Uw6luw6lyaWZlIChzdWQpPC90ZD48dGQgY2xhc3M9XCJuXCI+NCBoIDE1PC90ZD48dGQgY2xhc3M9"
    "XCJuXCI+MjMgwrBDPC90ZD48dGQgY2xhc3M9XCJuXCI+MjEgwrBDPC90ZD48L3RyPjwvdGJvZHk+PC90YWJsZT48L2Rpdj48cCBj"
    "bGFzcz1cIm1oYy1jYXBcIj5Nb3llbm5lcyBkZSBkw6ljZW1icmUgOyBkdXLDqWVzIGRlIHZvbCBkaXJlY3RlcyBkZXB1aXMgUGFy"
    "aXMsIGluZGljYXRpdmVzIHNlbG9uIGzigJlhw6lyb3BvcnQgZXQgbGEgY29tcGFnbmllLiAqVm9scyB2ZXJzIE1vbmFzdGlyLiBT"
    "b3VyY2VzIGVuIGJhcyBkZSBwYWdlLjwvcD5cbjxwPkxpc2V6IGxhIGNvbG9ubmUgwqsgTWVyIMK7IDogbGEgYmFpZ25hZGUgbuKA"
    "mWVzdCB2cmFpbWVudCBjb25mb3J0YWJsZSBxdeKAmWVuIG1lciBSb3VnZSAoMjMgwrBDIMOgIEh1cmdoYWRhKSBldCBhdXggQ2Fu"
    "YXJpZXMgKDIxIMKwQyDDoCBUw6luw6lyaWZlKS4gQXUgTWFyb2MgZXQgZW4gVHVuaXNpZSwgbGEgbWVyIHJlc3RlIGF1dG91ciBk"
    "ZSAxOCDCsEMgOiBj4oCZZXN0IGxlIHNvbGVpbCBldCBsYSBkb3VjZXVyIHF1ZSBs4oCZb24gdmllbnQgY2hlcmNoZXIsIHBhcyBs"
    "YSBwbGFnZS4gUG91ciByw6lkdWlyZSBsYSBmYWN0dXJlLCBub3RyZSBndWlkZSA8YSBocmVmPVwiaHR0cHM6Ly9teWhvdGVsY29t"
    "cGFyZS5jb20vY29tbWVudC10cm91dmVyLXVuLWhvdGVsLW1vaW5zLWNoZXIuaHRtbFwiPmNvbW1lbnQgdHJvdXZlciB1biBow7R0"
    "ZWwgbW9pbnMgY2hlcjwvYT4gZG9ubmUgZGVzIHBpc3RlcyBjb25jcsOodGVzLjwvcD5cbjxkaXYgY2xhc3M9XCJtaGMtdGVhc2Vy"
    "XCI+PGI+w4Agc3VpdnJlIDo8L2I+IGxlcyBkZXN0aW5hdGlvbnMgbGVzIHBsdXMgcHJvY2hlcywgZW4gVHVuaXNpZSAoMiBoIDIw"
    "IMOgIDIgaCAzNSBkZSB2b2wpLCBzb250IGF1c3NpIGNlbGxlcyBvw7kgbOKAmWVhdSBlc3QgbGEgcGx1cyBmcmHDrmNoZS4gTGUg"
    "ZMOpdGFpbCBlc3QgZGFucyBsYSB0cm9pc2nDqG1lIHBhcnRpZS48L2Rpdj5cbjxoMiBpZD1cIm1oYy1tYXJvY1wiPjIuIE1hcm9j"
    "IDogTWFycmFrZWNoIGV0IEFnYWRpcjwvaDI+XG48aDM+TWFycmFrZWNoPC9oMz48aW1nIGNsYXNzPVwibWhjLWltZ1wiIHNyYz1c"
    "Imh0dHBzOi8vbXlob3RlbGNvbXBhcmUuY29tL2ltYWdlcy9kZWNlbWJyZS1tYXJyYWtlY2guanBnXCIgYWx0PVwiTWFycmFrZWNo"
    "LCBsYSB2aWxsZSByb3VnZSA6IG1pbmFyZXQgZGUgbGEgS291dG91YmlhLCBqYXJkaW5zIGV0IHNvdWtzXCIgbG9hZGluZz1cImxh"
    "enlcIj48ZGl2IGNsYXNzPVwibWhjLWZhY3RzXCI+PHNwYW4+4pyI77iPIDMgaCAxNSDigJMgMyBoIDI1PC9zcGFuPjxzcGFuPvCf"
    "jKHvuI8gMjEgwrBDIGxlIGpvdXIsIDEyIMKwQyBsYSBudWl0PC9zcGFuPjxzcGFuPuKYgO+4jyAxMCBoIGRlIHNvbGVpbCBwYXIg"
    "am91cjwvc3Bhbj48L2Rpdj48cD5Nw6lkaW5hLCBzb3VrcywgamFyZGlucyBldCBwYWxhaXMgc2UgdmlzaXRlbnQgdHLDqHMgYmll"
    "biBlbiBkw6ljZW1icmUsIHNhbnMgbGEgY2hhbGV1ciBkZSBs4oCZw6l0w6kuIExlcyBzb2lyw6llcyBzb250IGZyYcOuY2hlcyA6"
    "IHByw6l2b3lleiB1bmUgdmVzdGUuIElsIG7igJl5IGEgcGFzIGRlIG1lciwgbWFpcyBiZWF1Y291cCBk4oCZaMO0dGVscyBldCBk"
    "ZSByaWFkcyBvbnQgdW5lIHBpc2NpbmUgOyB2w6lyaWZpZXogc2kgZWxsZSBlc3QgY2hhdWZmw6llLjwvcD48IS0tSE9URUxTIE1h"
    "cnJha2VjaCAoTWFyb2MpIHwgbWFyb2MgfCBtYXJyYWtlY2gtLT5cbjxoMz5BZ2FkaXI8L2gzPjxkaXYgY2xhc3M9XCJtaGMtZmFj"
    "dHNcIj48c3Bhbj7inIjvuI8gMyBoIDMwIOKAkyAzIGggNDA8L3NwYW4+PHNwYW4+8J+Moe+4jyAyMyDCsEMgbGUgam91ciwgMTQg"
    "wrBDIGxhIG51aXQ8L3NwYW4+PHNwYW4+8J+MiiBtZXIgw6AgMTggwrBDPC9zcGFuPjwvZGl2PjxwPkxhIGdyYW5kZSBzdGF0aW9u"
    "IGJhbG7DqWFpcmUgbWFyb2NhaW5lLCB0csOocyBlbnNvbGVpbGzDqWUgZW4gaGl2ZXIgKGVudmlyb24gMTAgaCBkZSBzb2xlaWwg"
    "cGFyIGpvdXIpLiBM4oCZb2PDqWFuIGVzdCBmcmFpcywgdmVycyAxOCDCsEMgOiBsYSBiYWlnbmFkZSBzZSBmYWl0IHN1cnRvdXQg"
    "ZW4gcGlzY2luZSwgbWFpcyBsZXMgam91cm7DqWVzIGVuIHRlcnJhc3NlIG91IMOgIGxhIHBsYWdlIHNvbnQgYWdyw6lhYmxlcy4g"
    "VW4gYm9uIGNob2l4IHBvdXIgZGVzIHZhY2FuY2VzIGRlIE5vw6tsIGVuIGZhbWlsbGUuPC9wPjwhLS1IT1RFTFMgQWdhZGlyIChN"
    "YXJvYykgfCBtYXJvYyB8IGFnYWRpciwgdGFnaGF6b3V0LS0+XG48aDIgaWQ9XCJtaGMtdHVuaXNpZVwiPjMuIFR1bmlzaWUgOiBE"
    "amVyYmEsIEhhbW1hbWV0IGV0IFNvdXNzZTwvaDI+XG48aDM+RGplcmJhPC9oMz48aW1nIGNsYXNzPVwibWhjLWltZ1wiIHNyYz1c"
    "Imh0dHBzOi8vbXlob3RlbGNvbXBhcmUuY29tL2ltYWdlcy9kZWNlbWJyZS1kamVyYmEuanBnXCIgYWx0PVwiRGplcmJhIDogbWFp"
    "c29ucyBibGFuY2hlcywgYm91Z2FpbnZpbGzDqWVzIGV0IG9saXZpZXJzIGZhY2Ugw6AgbGEgbWVyXCIgbG9hZGluZz1cImxhenlc"
    "Ij48ZGl2IGNsYXNzPVwibWhjLWZhY3RzXCI+PHNwYW4+4pyI77iPIGVudmlyb24gMiBoIDM1PC9zcGFuPjxzcGFuPvCfjKHvuI8g"
    "MTggwrBDIGxlIGpvdXI8L3NwYW4+PHNwYW4+8J+MiiBtZXIgw6AgMTgsNSDCsEM8L3NwYW4+PC9kaXY+PHA+VW4gcGV1IHBsdXMg"
    "ZGUgMiBoIDMwIGRlIHZvbCBzdWZmaXNlbnQuIElsIHkgZmFpdCBkb3V4IG1haXMgcGFzIGNoYXVkIGVuIGTDqWNlbWJyZSA6IGPi"
    "gJllc3QgdW5lIGRlc3RpbmF0aW9uIGRlIHJlcG9zLCBkZSB0aGFsYXNzbyBldCBkZSBiYWxhZGVzIHBsdXTDtHQgcXVlIGRlIGJh"
    "aWduYWRlLiBCZWF1Y291cCBk4oCZaMO0dGVscyBvbnQgdW4gc3BhIG91IHVuZSBwaXNjaW5lIGNoYXVmZsOpZS48L3A+PCEtLUhP"
    "VEVMUyBEamVyYmEgKFR1bmlzaWUpIHwgdHVuaXNpZSB8IGRqZXJiYSwgbWlkb3VuLCBob3VtdC1zb3VrLS0+XG48aDM+SGFtbWFt"
    "ZXQgZXQgU291c3NlPC9oMz48ZGl2IGNsYXNzPVwibWhjLWZhY3RzXCI+PHNwYW4+4pyI77iPIGVudmlyb24gMiBoIDIwICh2b2xz"
    "IHZlcnMgTW9uYXN0aXIpPC9zcGFuPjxzcGFuPvCfjKHvuI8gZG91eCwgaGl2ZXJuYWw8L3NwYW4+PC9kaXY+PHA+TGEgY8O0dGUg"
    "dHVuaXNpZW5uZSBlc3Qgc3VydG91dCBjaG9pc2llIGVuIGhpdmVyIHBvdXIgc2VzIGjDtHRlbHMgYXZlYyBzcGEgZXQgdGhhbGFz"
    "c290aMOpcmFwaWUsIHBsdXMgcXVlIHBvdXIgbGEgcGxhZ2UuIEPigJllc3QgbOKAmXVuZSBkZXMgc29sdXRpb25zIGxlcyBwbHVz"
    "IGNvdXJ0ZXMgZW4gYXZpb24sIGV0IGxlcyBwcml4IGJhaXNzZW50IG5ldHRlbWVudCBob3JzIHZhY2FuY2VzIHNjb2xhaXJlcy48"
    "L3A+PCEtLUhPVEVMUyBIYW1tYW1ldCBldCBTb3Vzc2UgKFR1bmlzaWUpIHwgdHVuaXNpZSB8IGhhbW1hbWV0LCBzb3Vzc2UsIHBv"
    "cnQtZWwta2FudGFvdWksIG1vbmFzdGlyLS0+XG48aDIgaWQ9XCJtaGMtZWd5cHRlXCI+NC4gw4lneXB0ZSA6IEh1cmdoYWRhLCBN"
    "YXJzYSBBbGFtIGV0IFNoYXJtIGVsLVNoZWlraDwvaDI+XG48aDM+SHVyZ2hhZGEgZXQgTWFyc2EgQWxhbTwvaDM+PGltZyBjbGFz"
    "cz1cIm1oYy1pbWdcIiBzcmM9XCJodHRwczovL215aG90ZWxjb21wYXJlLmNvbS9pbWFnZXMvZGVjZW1icmUtaHVyZ2hhZGEuanBn"
    "XCIgYWx0PVwiSHVyZ2hhZGEgOiBwbGFnZSwgZMOpc2VydCBldCByw6ljaWZzIGRlIGxhIG1lciBSb3VnZVwiIGxvYWRpbmc9XCJs"
    "YXp5XCI+PGRpdiBjbGFzcz1cIm1oYy1mYWN0c1wiPjxzcGFuPuKciO+4jyA0IGggMzUg4oCTIDUgaCAwNSAoSHVyZ2hhZGEpPC9z"
    "cGFuPjxzcGFuPvCfjKHvuI8gMjQgwrBDIGxlIGpvdXIsIDEzIMKwQyBsYSBudWl0PC9zcGFuPjxzcGFuPvCfjIogbWVyIMOgIDIz"
    "IMKwQzwvc3Bhbj48c3Bhbj7imIDvuI8gOCBoIGRlIHNvbGVpbCBwYXIgam91cjwvc3Bhbj48L2Rpdj48cD5MYSBtZXIgUm91Z2Ug"
    "ZXN0IGxhIHZhbGV1ciBzw7tyZSBwb3VyIHNlIGJhaWduZXIgZW4gZMOpY2VtYnJlIDogbOKAmWVhdSByZXN0ZSBhdXRvdXIgZGUg"
    "MjMgwrBDLiBD4oCZZXN0IGF1c3NpIGxlIHBhcmFkaXMgZGVzIHLDqWNpZnMsIHBvdXIgbGEgcGxvbmfDqWUgZXQgbGUgc25vcmtl"
    "bGluZy4gTWFyc2EgQWxhbSBlc3QgcGx1cyBjYWxtZSBxdWUgSHVyZ2hhZGEuPC9wPjwhLS1IT1RFTFMgSHVyZ2hhZGEgZXQgTWFy"
    "c2EgQWxhbSAow4lneXB0ZSkgfCBlZ3lwdGUgfCBodXJnaGFkYSwgZWwtZ291bmEsIG1ha2FkaSwgc29tYS1iYXksIG1hcnNhLWFs"
    "YW0tLT5cbjxoMz5TaGFybSBlbC1TaGVpa2g8L2gzPjxpbWcgY2xhc3M9XCJtaGMtaW1nXCIgc3JjPVwiaHR0cHM6Ly9teWhvdGVs"
    "Y29tcGFyZS5jb20vaW1hZ2VzL2RlY2VtYnJlLXNoYXJtLmpwZ1wiIGFsdD1cIlNoYXJtIGVsLVNoZWlraCA6IHBsYWdlcyBldCBy"
    "w6ljaWZzIGRlIGxhIG1lciBSb3VnZVwiIGxvYWRpbmc9XCJsYXp5XCI+PGRpdiBjbGFzcz1cIm1oYy1mYWN0c1wiPjxzcGFuPuKc"
    "iO+4jyBlbnZpcm9uIDUgaDwvc3Bhbj48c3Bhbj7wn4yh77iPIGNsaW1hdCBwcm9jaGUgZGUgSHVyZ2hhZGE8L3NwYW4+PC9kaXY+"
    "PHA+TcOqbWUgbWVyIFJvdWdlLCBtw6ptZXMgcsOpY2lmcywgYXZlYyBkZXMgaMO0dGVscyBkZSBib3JkIGRlIHBsYWdlIHRyw6hz"
    "IG5vbWJyZXV4LiBBdmFudCBkZSByw6lzZXJ2ZXIsIGNvbnN1bHRleiBsZXMgY29uc2VpbHMgYXV4IHZveWFnZXVycyBkdSBtaW5p"
    "c3TDqHJlIGRlIGzigJlFdXJvcGUgZXQgZGVzIEFmZmFpcmVzIMOpdHJhbmfDqHJlcyAoRnJhbmNlIERpcGxvbWF0aWUpIDogaWxz"
    "IMOpdm9sdWVudCwgZXQgY+KAmWVzdCBs4oCZaW5mb3JtYXRpb24gZGUgcsOpZsOpcmVuY2UuPC9wPjwhLS1IT1RFTFMgU2hhcm0g"
    "ZWwtU2hlaWtoICjDiWd5cHRlKSB8IGVneXB0ZSB8IGNoYXJtLWVsLWNoZWlraCwgc2hhcm0tZWwtc2hlaWtoLCBzaGFybSwgbmFh"
    "bWEtYmF5LS0+XG48aDIgaWQ9XCJtaGMtY2FuYXJpZXNcIj41LiBMZXMgQ2FuYXJpZXM8L2gyPjxpbWcgY2xhc3M9XCJtaGMtaW1n"
    "XCIgc3JjPVwiaHR0cHM6Ly9teWhvdGVsY29tcGFyZS5jb20vaW1hZ2VzL2RlY2VtYnJlLXRlbmVyaWZlLmpwZ1wiIGFsdD1cIlTD"
    "qW7DqXJpZmUgOiB2b2xjYW4gVGVpZGUsIGZvcsOqdHMgZXQgY8O0dGUgYXRsYW50aXF1ZVwiIGxvYWRpbmc9XCJsYXp5XCI+PGRp"
    "diBjbGFzcz1cIm1oYy1mYWN0c1wiPjxzcGFuPuKciO+4jyBlbnZpcm9uIDQgaCAxNSAoVMOpbsOpcmlmZSk8L3NwYW4+PHNwYW4+"
    "8J+Moe+4jyAyMyDCsEMgbGUgam91ciBzdXIgbGEgY8O0dGUgc3VkPC9zcGFuPjxzcGFuPvCfjIogbWVyIMOgIDIxIMKwQzwvc3Bh"
    "bj48L2Rpdj48cD5M4oCZYXZhbnRhZ2UgZMOpY2lzaWYgOiBj4oCZZXN0IGzigJlFdXJvcGUsIGRvbmMgYXVjdW5lIGZvcm1hbGl0"
    "w6kgaG9ycyBVbmlvbi4gTGUgc3VkIGRlIFTDqW7DqXJpZmUgZXN0IGzigJllbmRyb2l0IGxlIHBsdXMgZG91eCBkZSBs4oCZw65s"
    "ZSwgYWxvcnMgcXVlIGxlIG5vcmQgZXQgbGEgbW9udGFnbmUgc29udCBiaWVuIHBsdXMgZnJhaXMgZXQgcGx1dmlldXguIEdyYW4g"
    "Q2FuYXJpYSwgTGFuemFyb3RlIGV0IEZ1ZXJ0ZXZlbnR1cmEgb2ZmcmVudCB1biBjbGltYXQgdm9pc2luLCBhdmVjIGNoYWN1bmUg"
    "c2EgcGVyc29ubmFsaXTDqS48L3A+XG48ZGl2IGNsYXNzPVwibWhjLW5vdGVcIj48c3Ryb25nPsOAIHJldGVuaXIgOjwvc3Ryb25n"
    "PiBwb3VyIHNlIGJhaWduZXIsIHZpc2V6IGxhIG1lciBSb3VnZSBvdSBsZXMgQ2FuYXJpZXMgOyBwb3VyIHVuIGNvdXJ0IHPDqWpv"
    "dXIgZGUgcmVwb3MsIERqZXJiYSwgSGFtbWFtZXQgb3UgTWFycmFrZWNoIDsgcG91ciBkZXMgdmFjYW5jZXMgZW4gZmFtaWxsZSBh"
    "dmVjIGdyYW5kZSBwbGFnZSBldCBwaXNjaW5lLCBBZ2FkaXIuPC9kaXY+XG48aDIgaWQ9XCJtaGMtcmVzZXJ2ZXJcIj42LiBRdWFu"
    "ZCByw6lzZXJ2ZXIgPzwvaDI+PHA+UG91ciBsZXMgZsOqdGVzIGRlIGZpbiBk4oCZYW5uw6llLCByw6lzZXJ2ZXogbGUgcGx1cyB0"
    "w7R0IHBvc3NpYmxlIDogaMO0dGVscyBldCB2b2xzIHNvbnQgY29tcGxldHMgcGx1c2lldXJzIHNlbWFpbmVzIMOgIGzigJlhdmFu"
    "Y2UuIExlcyB2YWNhbmNlcyBkZSBOb8OrbCBjb21tZW5jZW50IGxlIDE5IGTDqWNlbWJyZSAyMDI2IGV0IHNlIHRlcm1pbmVudCBs"
    "ZSAzIGphbnZpZXIgMjAyNy4gSG9ycyB2YWNhbmNlcyBzY29sYWlyZXMsIGRlIGJvbm5lcyBhZmZhaXJlcyBhcHBhcmFpc3NlbnQg"
    "w6AgbGEgZGVybmnDqHJlIG1pbnV0ZS4gQ29tcGFyZXogbGVzIHNhaXNvbnMgYXZlYyBub3RyZSA8YSBocmVmPVwiaHR0cHM6Ly9t"
    "eWhvdGVsY29tcGFyZS5jb20vcXVhbmQtcGFydGlyLWV0LW91LWNhbGVuZHJpZXItdm95YWdldXJzLmh0bWxcIj5jYWxlbmRyaWVy"
    "IGRlcyBtZWlsbGV1cmVzIHDDqXJpb2RlcyBwb3VyIHBhcnRpcjwvYT4uPC9wPlxuPGgyIGlkPVwibWhjLWZhcVwiPjcuIFF1ZXN0"
    "aW9ucyBmcsOpcXVlbnRlczwvaDI+PGRldGFpbHMgY2xhc3M9XCJtaGMtZmFxXCI+PHN1bW1hcnk+T8O5IGZhaXQtaWwgbGUgcGx1"
    "cyBjaGF1ZCBlbiBkw6ljZW1icmUgPzwvc3VtbWFyeT48cD5QYXJtaSBsZXMgZGVzdGluYXRpb25zIGRvbnQgbm91cyBhdm9ucyB2"
    "w6lyaWZpw6kgbGVzIGNoaWZmcmVzLCBIdXJnaGFkYSBhcnJpdmUgZW4gdMOqdGUgYXZlYyBlbnZpcm9uIDI0IMKwQyBkZSBtb3ll"
    "bm5lIGxlIGpvdXIsIGRldmFudCBBZ2FkaXIgZXQgbGUgc3VkIGRlIFTDqW7DqXJpZmUgKGVudmlyb24gMjMgwrBDKS48L3A+PC9k"
    "ZXRhaWxzPjxkZXRhaWxzIGNsYXNzPVwibWhjLWZhcVwiPjxzdW1tYXJ5PlBldXQtb24gc2UgYmFpZ25lciBlbiBkw6ljZW1icmUg"
    "Pzwvc3VtbWFyeT48cD5PdWkgZW4gbWVyIFJvdWdlIChlbnZpcm9uIDIzIMKwQyDDoCBIdXJnaGFkYSkgZXQgc3VyIGxhIGPDtHRl"
    "IHN1ZCBkZSBUw6luw6lyaWZlIChlbnZpcm9uIDIxIMKwQykuIMOAIEFnYWRpciAoZW52aXJvbiAxOCDCsEMpIGV0IMOgIERqZXJi"
    "YSAoZW52aXJvbiAxOCw1IMKwQyksIGzigJllYXUgZXN0IGZyYcOuY2hlIDogbGEgcGlzY2luZSBjaGF1ZmbDqWUgZXN0IHBsdXMg"
    "Y29uZm9ydGFibGUuPC9wPjwvZGV0YWlscz48ZGV0YWlscyBjbGFzcz1cIm1oYy1mYXFcIj48c3VtbWFyeT5RdWVsbGUgZXN0IGxh"
    "IGRlc3RpbmF0aW9uIGxhIHBsdXMgcHJvY2hlID88L3N1bW1hcnk+PHA+TGVzIHZvbHMgdmVycyBsYSBUdW5pc2llIHNvbnQgbGVz"
    "IHBsdXMgY291cnRzIDogZW52aXJvbiAyIGggMjAgdmVycyBNb25hc3RpciBldCAyIGggMzUgdmVycyBEamVyYmEuPC9wPjwvZGV0"
    "YWlscz48ZGV0YWlscyBjbGFzcz1cIm1oYy1mYXFcIj48c3VtbWFyeT5GYXV0LWlsIHLDqXNlcnZlciBsb25ndGVtcHMgw6AgbOKA"
    "mWF2YW5jZSA/PC9zdW1tYXJ5PjxwPlBvdXIgbGVzIHZhY2FuY2VzIGRlIE5vw6tsLCBvdWkgOiBwbHVzaWV1cnMgc2VtYWluZXMu"
    "IEhvcnMgdmFjYW5jZXMgc2NvbGFpcmVzLCBsZXMgcHJpeCBiYWlzc2VudCBldCBsYSBkZXJuacOocmUgbWludXRlIGRldmllbnQg"
    "aW50w6lyZXNzYW50ZS48L3A+PC9kZXRhaWxzPlxuPGRpdiBjbGFzcz1cImdsYXNzLWJveFwiIHN0eWxlPVwibWFyZ2luOjIycHgg"
    "MDsgYm9yZGVyLWxlZnQ6NXB4IHNvbGlkIHZhcigtLXByaW1hcnkpOyB0ZXh0LWFsaWduOmNlbnRlcjtcIj48aDMgc3R5bGU9XCJt"
    "YXJnaW4tdG9wOjA7XCI+4piA77iPIMOAIHZvdXMgZGUgY2hvaXNpcjwvaDM+PHAgc3R5bGU9XCJtYXJnaW4tYm90dG9tOjE2cHg7"
    "XCI+Vm91cyBhdmV6IGxlcyBjaGlmZnJlcyA6IGNvbXBhcmV6IG1haW50ZW5hbnQgbGVzIGjDtHRlbHMgZGUgdm90cmUgZGVzdGlu"
    "YXRpb24sIGF2ZWMgbGVzIG5vdGVzLCBsZXMgw6lxdWlwZW1lbnRzIGV0IGxlcyBvZmZyZXMgZGUgbm9zIHBhcnRlbmFpcmVzLjwv"
    "cD48YSBocmVmPVwiaHR0cHM6Ly9teWhvdGVsY29tcGFyZS5jb20vaG90ZWxzLmh0bWxcIiBjbGFzcz1cImJ0blwiPkNvbXBhcmVy"
    "IGxlcyBow7R0ZWxzPC9hPjxwIHN0eWxlPVwibWFyZ2luOjE2cHggMCAwO1wiPlB1aXMgOiA8YSBocmVmPVwiaHR0cHM6Ly9teWhv"
    "dGVsY29tcGFyZS5jb20vY29tbWVudC10cm91dmVyLXVuLWhvdGVsLW1vaW5zLWNoZXIuaHRtbFwiPm5vcyBhc3R1Y2VzIHBvdXIg"
    "dW4gaMO0dGVsIG1vaW5zIGNoZXI8L2E+IMK3IDxhIGhyZWY9XCJodHRwczovL215aG90ZWxjb21wYXJlLmNvbS9xdWFuZC1wYXJ0"
    "aXItZXQtb3UtY2FsZW5kcmllci12b3lhZ2V1cnMuaHRtbFwiPmxlIGNhbGVuZHJpZXIgZGVzIHZveWFnZXVyczwvYT48L3A+PC9k"
    "aXY+XG48aDI+U291cmNlcyBldCBtw6l0aG9kZTwvaDI+PHA+TGVzIHRlbXDDqXJhdHVyZXMgc29udCBkZXMgbW95ZW5uZXMgbWVu"
    "c3VlbGxlcyBkZSBkw6ljZW1icmUsIGxlcyBkdXLDqWVzIGRlIHZvbCBzb250IGNlbGxlcyBkZXMgdm9scyBkaXJlY3RzIGRlcHVp"
    "cyBQYXJpcyBldCBwZXV2ZW50IHZhcmllciBzZWxvbiBs4oCZYcOpcm9wb3J0IGV0IGxhIGNvbXBhZ25pZS4gTm91cyBu4oCZYXZv"
    "bnMgcGFzIGRlIG1veWVubmUgZmlhYmxlIHBvdXIgU2hhcm0gZWwtU2hlaWtoLCBIYW1tYW1ldCBldCBTb3Vzc2UgOiBub3VzIG5l"
    "IGxlcyBjaGlmZnJvbnMgZG9uYyBwYXMuIFbDqXJpZmlleiBsZXMgZm9ybWFsaXTDqXMgZOKAmWVudHLDqWUgZXQgbGVzIGNvbnNl"
    "aWxzIGF1eCB2b3lhZ2V1cnMgZGUgY2hhcXVlIHBheXMgYXZhbnQgZGUgcGFydGlyLjwvcD48dWw+PGxpPkNsaW1hdCBNYXJvYyBl"
    "dCBEamVyYmEgZW4gZMOpY2VtYnJlIDogb3UtZXQtcXVhbmQubmV0PC9saT48bGk+Q2xpbWF0IEh1cmdoYWRhIGV0IFTDqW7DqXJp"
    "ZmUgZW4gZMOpY2VtYnJlIDogY2xpbWF0c2V0dm95YWdlcy5jb208L2xpPjxsaT5EdXLDqWVzIGRlIHZvbCBQYXJpc+KAk01hcnJh"
    "a2VjaCwgQWdhZGlyLCBIdXJnaGFkYSwgVMOpbsOpcmlmZSA6IHBhcnRpci5jb208L2xpPjxsaT5EdXLDqWVzIGRlIHZvbCBQYXJp"
    "c+KAk1R1bmlzaWUgOiBvdS1ldC1xdWFuZC5uZXQ8L2xpPjwvdWw+XG48L2Rpdj4ifQ=="
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

def main():
    art = json.loads(base64.b64decode("".join(ARTICLE_B64)).decode("utf-8"))
    fiches = charger("data", "") + charger("data_logements", "atypique-")
    print(len(fiches), "fiche(s) lue(s).")

    def rempl(m):
        titre, pays, villes = m.group(1).strip(), slug(m.group(2)), [slug(v) for v in m.group(3).split(",") if v.strip()]
        ok = [f for f in fiches if f["pays"] == pays and any(v in f["ville"] for v in villes)]
        ok = sorted(ok, key=lambda f: (-f["et"], f["nom"]))[:MAX]
        print(f"  {titre} : {len(ok)} hotel(s)")
        if not ok:
            return ""
        lis = "".join('<li><a href="' + f["url"] + '">' + f["nom"] + '</a> (' + f["ville_aff"] + (f', {f["et"]} étoiles' if f["et"] else "") + ')</li>' for f in ok)
        return '<div class="mhc-hotels"><strong>Nos hôtels : ' + titre + '</strong><ul>' + lis + '</ul></div>'

    art["details"] = re.sub(r"<!--HOTELS\s+(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*-->", rempl, art["details"])
    p = Path("blog_data.json")
    if not p.exists():
        sys.exit("blog_data.json introuvable : lancez le script dans le dossier comparateur-ia.")
    data = json.loads(p.read_text(encoding="utf-8"))
    shutil.copy(p, "blog_data.json.bak2")
    liste = data["articles"] if isinstance(data, dict) and isinstance(data.get("articles"), list) else data
    if not isinstance(liste, list):
        sys.exit("Structure inattendue de blog_data.json.")
    liste[:] = [a for a in liste if not (isinstance(a, dict) and a.get("slug") == art["slug"])]
    liste.insert(0, art)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK : {len(liste)} articles au total.")

if __name__ == "__main__":
    main()
