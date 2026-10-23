"""appliquer_patch_nomad.py

Branche reponses_site.json sur la page « Vos désirs sont des ordres » (générée par generateur.py).
À lancer UNE fois, à la racine du projet :   python appliquer_patch_nomad.py
- sauvegarde generateur.py en generateur.py.bak
- n'écrit rien si un repère n'est pas trouvé exactement une fois
"""
import shutil
import sys
from pathlib import Path

CIBLE = Path("generateur.py")

# ---------- 1. Génération de reponses-site.js (Python) ----------
PY_NOUVEAU = '''def generer_reponses_manuelles():
    """Écrit reponses-site.js à partir de reponses_site.json : réponses écrites à la main,
    prioritaires sur la page « Vos désirs sont des ordres »."""
    chemin = BASE_DIR / "reponses_site.json"
    try:
        reponses = json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else []
    except Exception as e:
        print(f"reponses_site.json ignoré : {e}")
        reponses = []
    reponses = [r for r in reponses if isinstance(r, dict) and r.get("questions") and r.get("reponse")]
    write_html(OUTPUT_DIR / "reponses-site.js",
               "window.NOMAD_REPONSES=" + json.dumps(reponses, ensure_ascii=False, separators=(",", ":")) + ";")
    print(f"Réponses manuelles : {len(reponses)}")


generer_base_connaissances(loueurs_data, croisieres_data)
generer_reponses_manuelles()'''

# ---------- 2. Fonctions JavaScript (accolades doublées : on est dans un f-string) ----------
JS_FONCTIONS = '''const REPONSES_MANUELLES = window.NOMAD_REPONSES || [];
function racineMot(m) {{ return m.replace(/[sx]$/, '').replace(/e+$/, ''); }}
function motsCles(texte) {{
    return normalize(texte).replace(/[^a-z0-9 ]/g, ' ').split(/\\\\s+/)
        .filter(m => m.length > 2 && !stopWords.has(m)).map(racineMot);
}}
function reponseManuelle(query) {{
    const q = new Set(motsCles(query));
    if (!q.size) return null;
    let meilleure = null, meilleurScore = 0;
    for (const r of REPONSES_MANUELLES) {{
        if (r.assistant_seulement) continue;
        for (const question of r.questions) {{
            const t = [...new Set(motsCles(question))];
            if (!t.length) continue;
            const communs = t.filter(m => q.has(m)).length;
            if (communs < Math.min(2, t.length)) continue;
            const score = 2 * communs / (t.length + q.size);
            if (score > meilleurScore) {{ meilleure = r; meilleurScore = score; }}
        }}
    }}
    if (!meilleure || meilleurScore < 0.5) return null;
    const lien = meilleure.lien ? `<p style="margin:12px 0 0;"><a class="btn" href="${{escapeText(meilleure.lien)}}">${{escapeText(meilleure.lien_texte || 'Voir la page')}}</a></p>` : '';
    return {{
        html: `<div class="glass-box" style="margin-bottom:16px; border-left:5px solid var(--success);"><h3 style="margin-top:0;">💡 Réponse de Nomad</h3><p style="margin:0; line-height:1.7;">${{escapeText(meilleure.reponse)}}</p>${{lien}}</div>`
    }};
}}
'''

# ---------- 3. Utilisation dans le formulaire ----------
JS_UTILISATION = '''const manuelle = reponseManuelle(query);
    if (manuelle) {{
        document.getElementById('smart-answers').innerHTML = extrasHtml + manuelle.html;
        container.innerHTML = '';
        return;
    }}
    '''

ANCRE_SCRIPT = '<script src="recherche-nomad.js"></script>'
ANCRE_SUBMIT = "document.getElementById('smart-search').addEventListener('submit', event => {{"
ANCRE_ANSWER = "const answerPromise = window.nomadAnswer"
ANCRE_PY = "generer_base_connaissances(loueurs_data, croisieres_data)"

REMPLACEMENTS = [
    (ANCRE_PY, PY_NOUVEAU, "appel de génération (Python)"),
    (ANCRE_SCRIPT, '<script src="reponses-site.js"></script>\n' + ANCRE_SCRIPT, "chargement de reponses-site.js"),
    (ANCRE_SUBMIT, JS_FONCTIONS + ANCRE_SUBMIT, "fonctions JavaScript"),
    (ANCRE_ANSWER, JS_UTILISATION + ANCRE_ANSWER, "utilisation dans le formulaire"),
]


def main():
    if not CIBLE.exists():
        sys.exit("generateur.py introuvable : lancez ce script depuis la racine du projet.")
    brut = CIBLE.read_bytes().decode("utf-8")
    crlf = "\r\n" in brut
    txt = brut.replace("\r\n", "\n")
    if "NOMAD_REPONSES" in txt:
        sys.exit("Le patch semble déjà appliqué (NOMAD_REPONSES trouvé). Rien à faire.")
    for ancre, nouveau, nom in REMPLACEMENTS:
        n = txt.count(ancre)
        if n != 1:
            sys.exit(f"Repère introuvable ou en double ({n} fois) pour : {nom}. Rien n'a été modifié.")
        txt = txt.replace(ancre, nouveau)
    try:
        compile(txt, "generateur.py", "exec")
    except SyntaxError as e:
        sys.exit(f"Le résultat contiendrait une erreur de syntaxe ({e}). Rien n'a été modifié.")
    shutil.copy(CIBLE, CIBLE.with_suffix(".py.bak"))
    CIBLE.write_bytes((txt.replace("\n", "\r\n") if crlf else txt).encode("utf-8"))
    print("Patch appliqué. Sauvegarde : generateur.py.bak")
    print("Relancez ensuite :  python generateur.py --reset")


if __name__ == "__main__":
    main()