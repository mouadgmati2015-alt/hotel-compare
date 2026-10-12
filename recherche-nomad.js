/* Nomad : réponses de la page « Vos désirs sont des ordres ».
 * Répond aux questions sur les visas, les aéroports et toutes les infos du site
 * (FAQ des hôtels, accès, compagnies aériennes, loueurs, croisières, blog...).
 * Données chargées à la demande : base-connaissances.js, visas-data.js, villes-aeroports.js
 * (générés / copiés par le script de génération du site).
 */
(function () {
  'use strict';

  /* ---------- Outils ---------- */
  function norm(s) {
    return String(s == null ? '' : s).toLowerCase().normalize('NFD')
      .replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function loose(s) {
    return norm(s).replace(/sh/g, 'ch').replace(/kh/g, 'k').replace(/ch/g, 'c').replace(/ei/g, 'i')
      .replace(/ey/g, 'i').replace(/ph/g, 'f').replace(/y/g, 'i').replace(/([a-z])\1+/g, '$1');
  }
  function hasWord(padded, w) { return padded.indexOf(' ' + w + ' ') >= 0; }
  function hasStem(padded, stem) { return padded.indexOf(' ' + stem) >= 0; }
  function anyStem(padded, list) { return list.some(function (s) { return hasStem(padded, s); }); }

  var loaded = {};
  function load(src) {
    if (!loaded[src]) {
      loaded[src] = new Promise(function (resolve) {
        var s = document.createElement('script');
        s.src = src;
        s.onload = function () { resolve(true); };
        s.onerror = function () { resolve(false); };
        document.head.appendChild(s);
      });
    }
    return loaded[src];
  }

  /* ---------- Intentions ---------- */
  var VISA_STEMS = ['visa', 'passeport', 'formalite', 'nationalite', 'ressortissant', 'autorisation de voyage', 'carte d identite', 'document de voyage', 'documents de voyage'];
  var VISA_WORDS = ['esta', 'eta', 'entrer', 'entree', 'frontiere'];
  var AIRPORT_STEMS = ['aeroport', 'airport', 'atterri', 'navette', 'transfert', 'aerodrome'];
  var INFO_STEMS = ['bagage', 'compagnie', 'alliance', 'flotte', 'croisiere', 'itineraire', 'loueur', 'location de voiture', 'location de vehicule', 'blog', 'conseil', 'partenaire', 'contact', 'affilie', 'faq', 'animaux', 'annulation', 'enfant', 'acces', 'comment', 'pourquoi', 'quand', 'combien'];
  var QUESTION_RE = /^(comment|quel|quelle|quels|quelles|combien|ou|quand|pourquoi|est ce|y a t il|peut on|faut il|puis je|dois je|a t on|existe t il|est il|est elle)\b/;
  var HOTEL_SEARCH_RE = /\b(hotel|hotels|sejour|budget|euro|euros|piscine|plage|spa|tout compris|parc aquatique|resort|chambre|reserver|pas cher)\b/;

  var STOP = new Set(('je tu il elle on nous vous ils elles le la les un une des de du au aux a en et ou mais donc or ni car que qui quoi dont ' +
    'ce cet cette ces mon ma mes ton ta tes son sa ses notre nos votre vos leur leurs ' +
    'pour par sur sous dans avec sans chez vers entre est sont etre ete avoir ai as avons avez ont suis sommes ' +
    'quel quelle quels quelles comment combien quand pourquoi ou y ya il faut peut puis dois veux voudrais cherche recherche ' +
    'se sa ne pas plus moins tres trop bien aussi si cela ca ici la alors avez aller faire fait info infos information informations renseignement renseignements savoir sujet compagnie compagnies aerienne aeriennes aerien desservent dessert desservi desservie vol vols avion avions propose proposer hotel hotels hebergement hebergements logement logements etablissement etablissements sejour sejours lieu lieux endroit endroits trouver eau').split(' '));

  var ALIAS_PAYS = {
    'usa': 'etats unis', 'etats unis': 'etats unis', 'amerique': 'etats unis', 'uk': 'royaume uni', 'angleterre': 'royaume uni',
    'grande bretagne': 'royaume uni', 'emirats': 'emirats arabes unis', 'dubai': 'emirats arabes unis', 'tcheque': 'republique tcheque',
    'tchequie': 'republique tcheque', 'hollande': 'pays bas', 'birmanie': 'myanmar'
  };
  var ALIAS_NAT = {
    'belge': 'belgique', 'ivoirien': 'cote d ivoire', 'americain': 'etats unis', 'britannique': 'royaume uni', 'anglais': 'royaume uni',
    'emirati': 'emirats arabes unis', 'congolais': 'congo', 'tcheque': 'tchequie', 'coreen': 'coree', 'neerlandais': 'pays bas',
    'hollandais': 'pays bas', 'suisse': 'suisse', 'canadien': 'canada', 'turc': 'turquie', 'grec': 'grece', 'polonais': 'pologne',
    'japonais': 'japon', 'chinois': 'chine', 'indien': 'inde', 'russe': 'russie', 'libanais': 'liban', 'egyptien': 'egypte',
    'senegalais': 'senegal', 'camerounais': 'cameroun', 'malien': 'mali', 'nigerian': 'nigeria', 'bresilien': 'bresil',
    'mexicain': 'mexique', 'australien': 'australie', 'autrichien': 'autriche', 'hongrois': 'hongrie', 'roumain': 'roumanie',
    'bulgare': 'bulgarie', 'serbe': 'serbie', 'croate': 'croatie', 'saoudien': 'arabie saoudite', 'thailandais': 'thailande',
    'vietnamien': 'viet nam', 'philippin': 'philippines', 'pakistanais': 'pakistan', 'tunisien': 'tunisie', 'marocain': 'maroc',
    'algerien': 'algerie', 'francais': 'france', 'francaise': 'france', 'allemand': 'allemagne', 'espagnol': 'espagne',
    'italien': 'italie', 'portugais': 'portugal'
  };
  var NAT_STOP = new Set(['visa', 'visas', 'voyage', 'voyager', 'pour', 'avec', 'besoin', 'passeport', 'nationalite', 'suis', 'sommes',
    'faut', 'peut', 'dois', 'puis', 'entrer', 'aller', 'partir', 'sejour', 'vacances', 'obligatoire', 'necessaire', 'quel', 'quelle',
    'documents', 'document', 'formalites', 'formalite', 'hotel', 'ville', 'pays', 'dans', 'comme', 'etre', 'avoir']);

  /* ---------- Données ---------- */
  var idx = null;
  function buildIndex() {
    if (idx) { return idx; }
    var KB = window.NOMAD_KB || { docs: [], etabs: [], villes: [] };
    var V = window.NOMAD_VISAS || null;
    idx = { KB: KB, V: V, countries: {}, cities: [], hotels: [], destKeyByNorm: {} };
    function addCountry(name) {
      if (name) { idx.countries[norm(name)] = name; }
    }
    KB.villes.forEach(function (c) {
      addCountry(c.p);
      if (c.v) { idx.cities.push({ n: norm(c.v), l: loose(c.v), v: c.v, p: c.p }); }
    });
    if (V) {
      Object.keys(V.dest).forEach(function (k) {
        addCountry(V.dest[k].n);
        idx.destKeyByNorm[norm(V.dest[k].n)] = k;
      });
    }
    idx.cities.sort(function (a, b) { return b.n.length - a.n.length; });
    KB.etabs.forEach(function (e) {
      var n = norm(e.n);
      if (n.length >= 5) { idx.hotels.push({ n: n, e: e }); }
    });
    idx.hotels.sort(function (a, b) { return b.n.length - a.n.length; });
    return idx;
  }

  /* Trouve l'établissement, la ville ou le pays demandé. Retourne aussi le texte retiré de la question. */
  function findDest(padded) {
    var I = buildIndex();
    var res = { hotel: null, ville: null, pays: null, remaining: padded };
    var i, h, c;
    for (i = 0; i < I.hotels.length; i++) {
      h = I.hotels[i];
      if (hasWord(padded, h.n)) {
        res.hotel = h.e; res.ville = h.e.v; res.pays = h.e.p;
        res.remaining = padded.replace(' ' + h.n + ' ', '  ');
        return res;
      }
    }
    for (i = 0; i < I.cities.length; i++) {
      c = I.cities[i];
      if (c.n && hasWord(padded, c.n)) {
        res.ville = c.v; res.pays = c.p;
        res.remaining = padded.replace(' ' + c.n + ' ', '  ');
        break;
      }
    }
    if (!res.ville) {
      var pl = ' ' + loose(padded.trim()) + ' ';
      for (i = 0; i < I.cities.length; i++) {
        c = I.cities[i];
        if (c.l && c.l.length >= 4 && hasWord(pl, c.l)) {
          res.ville = c.v; res.pays = c.p;
          var drop = {};
          c.l.split(' ').forEach(function (t) { drop[t] = true; });
          res.remaining = ' ' + padded.trim().split(/\s+/).filter(function (t) { return !drop[loose(t)]; }).join(' ') + ' ';
          break;
        }
      }
    }
    if (!res.pays) {
      var best = '';
      Object.keys(I.countries).forEach(function (n) {
        if (n.length > best.length && hasWord(padded, n)) { best = n; }
      });
      if (!best) {
        Object.keys(ALIAS_PAYS).forEach(function (a) {
          var target = ALIAS_PAYS[a];
          if (a.length > best.length && hasWord(padded, a) && I.countries[target]) { best = a; }
        });
        if (best) {
          res.pays = I.countries[ALIAS_PAYS[best]];
          res.remaining = padded.replace(' ' + best + ' ', '  ');
        }
      } else {
        res.pays = I.countries[best];
        res.remaining = padded.replace(' ' + best + ' ', '  ');
      }
    }
    return res;
  }

  /* ---------- Visas ---------- */
  function commonPrefix(a, b) {
    var n = Math.min(a.length, b.length), i = 0;
    while (i < n && a.charAt(i) === b.charAt(i)) { i++; }
    return i;
  }
  function findNationality(cleanPadded) {
    var V = window.NOMAD_VISAS;
    if (!V) { return null; }
    var words = cleanPadded.trim().split(/\s+/).filter(function (w) { return w.length >= 4 && !NAT_STOP.has(w) && !STOP.has(w); });
    var best = null, bestScore = 0;
    Object.keys(V.nats).forEach(function (code) {
      var name = norm(V.nats[code]);
      if (name.indexOf(' ') > 0 && hasWord(cleanPadded, name)) {
        if (name.length + 10 > bestScore) { bestScore = name.length + 10; best = code; }
        return;
      }
      words.forEach(function (w0) {
        var w = ALIAS_NAT[w0] || w0;
        var p = commonPrefix(w, name);
        var shortest = Math.min(w.length, name.length);
        if (p >= 4 && p >= 0.6 * shortest && p >= 0.5 * Math.max(w.length, name.length) && p > bestScore) {
          bestScore = p; best = code;
        }
      });
    });
    return best;
  }

  function visaResultHtml(destKey, code) {
    var V = window.NOMAD_VISAS, dest = V.dest[destKey];
    if (!dest || !V.nats[code]) { return ''; }
    var rule = V.regles[dest.r[code]];
    // Les règles viennent de ton propre fichier nationalites.json : elles sont insérées telles quelles (comme dans les fiches).
    return '<p style="margin:0 0 8px;">✈️ Pour un voyage vers <strong>' + esc(dest.n) + '</strong> avec un passeport <strong>' + esc(V.nats[code]) + '</strong> :</p>' +
      '<p style="margin:0 0 8px; font-weight:600;">' + rule + '</p>' +
      '<small style="color:var(--muted); display:block;">💡 <em>Conseil Nomad :</em> confirmez toujours vos formalités sur l\'outil officiel ' +
      '<a href="https://www.iatatravelcentre.com" target="_blank" rel="noopener">IATA Travel Centre</a>.</small>';
  }

  window.nomadVisaCheck = function () {
    var d = document.getElementById('nomad-visa-dest'), n = document.getElementById('nomad-visa-nat'), out = document.getElementById('nomad-visa-result');
    if (!d || !n || !out) { return; }
    out.innerHTML = (d.value && n.value) ? visaResultHtml(d.value, n.value) : '<span style="color:var(--muted);">Choisissez un pays et un passeport pour voir les formalités.</span>';
  };

  function visaSection(query, padded) {
    var V = window.NOMAD_VISAS;
    if (!V) { return { html: '', answered: false }; }
    var I = buildIndex();
    var dest = findDest(padded);
    var destKey = dest.pays ? I.destKeyByNorm[norm(dest.pays)] : '';
    var code = findNationality(dest.remaining);
    var selectStyle = 'width:100%; max-width:360px; padding:10px; border-radius:10px; border:1px solid var(--line); margin-bottom:10px;';

    var destOptions = '<option value="">-- Pays de destination --</option>' + Object.keys(V.dest)
      .sort(function (a, b) { return V.dest[a].n.localeCompare(V.dest[b].n, 'fr'); })
      .map(function (k) { return '<option value="' + esc(k) + '"' + (k === destKey ? ' selected' : '') + '>' + esc(V.dest[k].n) + '</option>'; }).join('');
    var natOptions = '<option value="">-- Votre passeport --</option>' + Object.keys(V.nats)
      .sort(function (a, b) { return String(V.nats[a]).localeCompare(String(V.nats[b]), 'fr'); })
      .map(function (c) { return '<option value="' + esc(c) + '"' + (c === code ? ' selected' : '') + '>' + esc(V.nats[c]) + '</option>'; }).join('');

    var defaulted = false;
    if (destKey && !code && V.nats['FR']) { code = 'FR'; defaulted = true; }
    var intro, answered = !!(destKey && code);
    if (answered) {
      intro = defaulted ? '<p style="margin:0 0 10px; color:var(--muted); font-size:.92rem;">Passeport français sélectionné par défaut. Changez-le ci-dessous si besoin.</p>' : '';
    } else if (destKey) {
      intro = '<p style="margin:0 0 10px;">Pour vous répondre pour <strong>' + esc(V.dest[destKey].n) + '</strong>, j\'ai besoin de votre nationalité (passeport) :</p>';
    } else if (code) {
      intro = '<p style="margin:0 0 10px;">Vers quel pays voyagez-vous ?</p>';
    } else {
      intro = '<p style="margin:0 0 10px;">Indiquez votre destination et votre passeport pour connaître les formalités :</p>';
    }

    var note = '';
    if (destKey) {
      var noms = {};
      I.KB.etabs.forEach(function (e) { if (norm(e.p) === norm(V.dest[destKey].n)) { noms[e.n] = true; } });
      var vu = {};
      I.KB.docs.forEach(function (d) {
        if (d.k === 'visa' && !vu[d.x] && noms[d.t.split(' : ')[0]] && Object.keys(vu).length < 1) {
          vu[d.x] = true;
          note = '<p style="margin:10px 0 0; padding:10px; border-left:4px solid var(--warning); background:#fff8e8; border-radius:8px;">⚠️ ' + esc(d.x) + '</p>';
        }
      });
    }

    var html = '<div class="glass-box" style="margin-bottom:14px; border-left:5px solid var(--secondary);">' +
      '<h3 style="margin-top:0;">🛂 Visa et formalités</h3>' + intro +
      '<select id="nomad-visa-dest" onchange="nomadVisaCheck()" style="' + selectStyle + '">' + destOptions + '</select><br>' +
      '<select id="nomad-visa-nat" onchange="nomadVisaCheck()" style="' + selectStyle + '">' + natOptions + '</select>' +
      '<div id="nomad-visa-result" style="padding:12px; background:var(--panel); border-radius:8px; line-height:1.5;">' +
      (answered ? visaResultHtml(destKey, code) : '<span style="color:var(--muted);">Choisissez un pays et un passeport pour voir les formalités.</span>') +
      '</div>' + note + '</div>';
    return { html: html, answered: answered };
  }

  /* ---------- Aéroports ---------- */
  function iataOf(text) {
    var m = /\(([A-Z]{3})\)/.exec(text || '');
    return m ? m[1] : '';
  }

  function airportSection(query, padded) {
    var I = buildIndex();
    var dest = findDest(padded);
    var html = '', answered = false;

    if (dest.hotel) {
      var e = dest.hotel;
      html += '<div class="glass-box" style="margin-bottom:14px; border-left:5px solid var(--primary);">' +
        '<h3 style="margin-top:0;">✈️ Aéroport pour ' + esc(e.n) + '</h3>' +
        (e.a ? '<p style="margin:0 0 8px; font-weight:600;">' + esc(e.a) + '</p>' : '<p style="margin:0 0 8px; color:var(--muted);">Aéroport non renseigné pour cet établissement.</p>') +
        (e.ac && e.ac.length ? '<ul style="margin:0 0 8px;">' + e.ac.map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('') + '</ul>' : '') +
        '<a class="btn" href="' + esc(e.u) + '">Voir la fiche</a></div>';
      answered = true;
    } else if (dest.ville || dest.pays) {
      var list = I.KB.etabs.filter(function (e) {
        return dest.ville ? norm(e.v) === norm(dest.ville) : norm(e.p) === norm(dest.pays);
      });
      var groups = {}, order = [];
      list.forEach(function (e) {
        if (!e.a) { return; }
        var key = iataOf(e.a) || norm(e.a);
        if (!groups[key]) { groups[key] = { label: e.a, lieux: {}, hotels: [] }; order.push(key); }
        groups[key].lieux[e.v] = true;
        groups[key].hotels.push(e);
      });
      if (order.length) {
        var titre = dest.ville ? esc(dest.ville) + (dest.pays ? ', ' + esc(dest.pays) : '') : esc(dest.pays);
        html += '<div class="glass-box" style="margin-bottom:14px; border-left:5px solid var(--primary);"><h3 style="margin-top:0;">✈️ Aéroports pour ' + titre + '</h3>' +
          order.slice(0, 8).map(function (k) {
            var g = groups[k], villes = Object.keys(g.lieux).filter(Boolean);
            var exemples = g.hotels.slice(0, 3).map(function (e) { return '<a href="' + esc(e.u) + '">' + esc(e.n) + '</a>'; }).join(', ');
            return '<p style="margin:0 0 10px;"><strong>' + esc(g.label) + '</strong><br><span style="color:var(--muted); font-size:.9rem;">' +
              (dest.ville ? '' : 'Dessert : ' + esc(villes.slice(0, 5).join(', ')) + ' · ') +
              g.hotels.length + ' hébergement(s) : ' + exemples + (g.hotels.length > 3 ? '…' : '') + '</span></p>';
          }).join('') + '</div>';
        answered = true;
      }
    }

    // Aéroports des villes de départ (ex : « quel aéroport à Strasbourg ? »)
    if (typeof VILLES_AEROPORTS !== 'undefined' && Array.isArray(VILLES_AEROPORTS)) {
      var trouves = VILLES_AEROPORTS.filter(function (v) { var nv = v.ville ? norm(String(v.ville).split(',')[0]) : ''; return nv.length > 2 && hasWord(padded, nv); });
      if (trouves.length) {
        html += '<div class="glass-box" style="margin-bottom:14px; border-left:5px solid var(--primary);"><h3 style="margin-top:0;">🛫 Aéroports de départ</h3>' +
          trouves.slice(0, 6).map(function (v) { return '<p style="margin:0 0 6px;"><strong>' + esc(String(v.ville).split(',')[0]) + '</strong> : code aéroport <strong>' + esc(v.code) + '</strong></p>'; }).join('') + '</div>';
        answered = true;
      }
    }

    if (!answered) {
      html = '<div class="glass-box" style="margin-bottom:14px; border-left:5px solid var(--primary);"><h3 style="margin-top:0;">✈️ Aéroports</h3>' +
        '<p style="margin:0;">Précisez une ville, un pays ou un hôtel (par exemple « aéroport le plus proche de Djerba ») et je vous indique l\'aéroport et l\'accès.</p></div>';
    }
    return { html: html, answered: answered };
  }

  /* ---------- Recherche générale dans toutes les infos du site ---------- */
  var KIND_LABEL = { faq: 'Question fréquente', acces: 'Accès', hotel: 'Fiche hôtel', logement: 'Logement atypique', compagnie: 'Compagnie aérienne',
    loueur: 'Location de véhicules', croisiere: 'Croisière', blog: 'Blog', visa: 'Formalités', info: 'Infos du site' };

  function stripTags(t) { return String(t == null ? '' : t).replace(/<[^>]*(>|$)/g, ' ').replace(/\s+/g, ' ').trim(); }
  function stem(w) { return (w.length > 4 && /[sx]$/.test(w)) ? w.slice(0, -1) : w; }

  function bestSnippet(doc, tokens) {
    var txt = stripTags(doc.x);
    if (doc.k === 'faq') { return txt.length > 420 ? txt.slice(0, 417) + '…' : txt; }
    var sentences = txt.split(/(?<=[.!?])\s+/), best = 0, bestScore = -1;
    sentences.forEach(function (s, i) {
      var n = norm(s), sc = 0;
      tokens.forEach(function (t) { if (n.indexOf(t) >= 0) { sc++; } });
      if (sc > bestScore) { bestScore = sc; best = i; }
    });
    var out = sentences[best] + (sentences[best + 1] && sentences[best].length < 160 ? ' ' + sentences[best + 1] : '');
    return out.length > 340 ? out.slice(0, 337) + '…' : out;
  }

  var CONCEPTS = [
    { re: / sur l eau | sur leau | sur les eaux | pilotis | pieds dans l eau | flottant | flottante | flottantes /,
      add: ['pilotis', 'peniche', 'houseboat', 'overwater', 'cabane flottante', 'cabanes flottantes', 'maison flottante', 'logement flottant', 'sur l eau'] },
    { re: / dans les arbres | dans un arbre | perchee | perchees | treehouse | cabane dans | cabanes dans /,
      add: ['cabane dans les arbres', 'cabanes dans les arbres', 'dans les arbres', 'perchee', 'treehouse', 'cabane perchee'] },
    { re: / troglodyte | troglodytes | troglodytique | troglodytiques | troglo | grotte | grottes | rupestre | souterrain /,
      add: ['troglodyte', 'troglodytes', 'troglodytique', 'grotte', 'grottes', 'rupestre'] },
    { re: / vue sur la mer | vue mer | vue sur mer | face a la mer | vue sur l ocean | front de mer | vue sur le lagon | vue sur la plage /,
      add: ['vue sur la mer', 'vue mer', 'face a la mer', 'vue sur l ocean', 'front de mer', 'vue panoramique sur la mer', 'vue sur le lagon'] }
  ];
  function conceptFor(padded) {
    for (var i = 0; i < CONCEPTS.length; i++) { if (CONCEPTS[i].re.test(padded)) { return CONCEPTS[i]; } }
    return null;
  }

  function has(txt, t) { return t.length > 4 ? txt.indexOf(t) >= 0 : (' ' + txt + ' ').indexOf(' ' + t + ' ') >= 0; }
  function genericSection(query, padded) {
    var I = buildIndex();
    var tokens = padded.trim().split(/\s+/).filter(function (w) { return w.length > 2 && !STOP.has(w); }).map(stem);
    tokens = tokens.filter(function (t, i) { return tokens.indexOf(t) === i; });
    var conceptHit = false, cc = conceptFor(padded);
    if (cc) { tokens = cc.add.slice(); conceptHit = true; }
    if (!tokens.length) { return { html: '', answered: false }; }
    var docs = I.KB.docs;
    var KIND_WORDS = { croisiere: ' croisiere', compagnie: ' compagnie aerienne', loueur: ' location voiture vehicule loueur' };
    docs.forEach(function (d) {
      if (d._n !== undefined) { return; }
      var titre = d.k === 'faq' && d.t.indexOf(' : ') > 0 ? d.t.slice(d.t.indexOf(' : ') + 3) : d.t;
      d._n = norm(titre);
      d._x = norm(stripTags(d.x)) + (KIND_WORDS[d.k] || '');
    });
    var N = docs.length, df = {};
    tokens.forEach(function (t) {
      df[t] = 0;
      docs.forEach(function (d) { if (has(d._n, t) || has(d._x, t)) { df[t]++; } });
    });
    var needed = conceptHit ? 1 : Math.max(1, Math.round(tokens.length * 0.6));
    var scored = [];
    docs.forEach(function (d) {
      var score = 0, matched = 0;
      tokens.forEach(function (t) {
        if (!df[t]) { return; }
        var idf = Math.log(1 + N / df[t]);
        var inTitle = has(d._n, t), inText = has(d._x, t);
        if (inTitle || inText) {
          matched++;
          score += idf * ((inTitle ? 3 : 0) + (inText ? 1 : 0));
        }
      });
      if (matched >= needed) { scored.push({ d: d, s: score * (matched / tokens.length) }); }
    });
    scored.sort(function (a, b) { return b.s - a.s; });
    var seuil = scored.length ? scored[0].s * 0.3 : 0, parPage = {}, top = [];
    scored.forEach(function (r) {
      if (top.length >= 4 || r.s < seuil) { return; }
      parPage[r.d.u] = (parPage[r.d.u] || 0) + 1;
      if (parPage[r.d.u] <= 2) { top.push(r); }
    });
    if (!top.length) { return { html: '', answered: false }; }
    var html = '<div class="glass-box" style="margin-bottom:14px; border-left:5px solid var(--success);"><h3 style="margin-top:0;">📚 Dans nos pages</h3>' +
      top.map(function (r) {
        var d = r.d;
        return '<div style="margin-bottom:14px;"><p style="margin:0 0 4px; font-weight:700;">' + esc(d.t) +
          ' <span style="font-weight:400; font-size:.78rem; color:var(--muted);">· ' + esc(KIND_LABEL[d.k] || 'Infos') + '</span></p>' +
          '<p style="margin:0 0 6px; color:var(--text); line-height:1.5;">' + esc(bestSnippet(d, tokens)) + '</p>' +
          '<a href="' + esc(d.u) + '">Voir la page →</a></div>';
      }).join('') + '</div>';
    return { html: html, answered: true };
  }

  /* ---------- Compagnies aériennes qui desservent la destination ---------- */
  function airportTerms(I, dest) {
    var terms = [];
    if (dest.ville) { terms.push(loose(dest.ville)); }
    I.KB.etabs.forEach(function (e) {
      if (!e.a) { return; }
      var same = dest.ville ? norm(e.v) === norm(dest.ville) : (dest.pays && norm(e.p) === norm(dest.pays));
      if (!same) { return; }
      var code = iataOf(e.a);
      if (code && terms.indexOf(norm(code)) < 0) { terms.push(norm(code)); }
      var nm = loose(String(e.a).replace(/\([A-Z]{3}\)/, '').replace(/^\s*a[eé]roport( international)?( de| d'| du)?\s*/i, ''));
      if (nm.length >= 5 && terms.indexOf(nm) < 0) { terms.push(nm); }
    });
    return terms;
  }

  function airlineSection(query, padded) {
    var I = buildIndex();
    var dest = findDest(padded);
    if (!dest.ville && !dest.pays) { return { html: '', answered: false }; }
    var airlines = I.KB.docs.filter(function (d) { return d.k === 'compagnie' && /\(compagnie a[ée]rienne\)$/.test(d.t); });
    airlines.forEach(function (d) { if (d._l === undefined) { d._l = ' ' + loose(d.x) + ' '; } });
    var terms = airportTerms(I, dest), level = 'ville';
    var matches = airlines.filter(function (d) { return terms.some(function (t) { return hasWord(d._l, t); }); });
    var termsUsed = terms;
    if (!matches.length && dest.pays) {
      termsUsed = [loose(dest.pays)];
      matches = airlines.filter(function (d) { return hasWord(d._l, termsUsed[0]); });
      level = 'pays';
    }
    var lieu = dest.ville && level === 'ville' ? dest.ville : dest.pays;
    var html = '<div class="glass-box" style="margin-bottom:14px; border-left:5px solid var(--primary);"><h3 style="margin-top:0;">✈️ Compagnies aériennes vers ' + esc(lieu) + '</h3>';
    if (!matches.length) {
      html += '<p style="margin:0;">Aucune compagnie de notre sélection ne cite ' + esc(lieu) + ' dans ses liaisons. Utilisez le comparateur de vols sur la fiche d\'un hôtel de la destination pour voir les vols au départ de votre ville.</p></div>';
      return { html: html, answered: false };
    }
    if (level === 'pays') {
      html += '<p style="margin:0 0 10px; color:var(--muted); font-size:.92rem;">Aucune compagnie ne cite précisément cette ville dans nos fiches ; voici celles qui desservent le pays :</p>';
    }
    html += matches.slice(0, 8).map(function (d) {
      var pieces = d.x.split(/\s*[;,]\s*|(?<=[.!?])\s+/).filter(function (t) {
        var l = ' ' + loose(t) + ' ';
        return termsUsed.some(function (term) { return hasWord(l, term); });
      }).slice(0, 3).join(' · ');
      var nom = d.t.replace(/\s*\(compagnie a[ée]rienne\)$/, '');
      return '<p style="margin:0 0 10px;"><strong>' + esc(nom) + '</strong>' + (pieces ? '<br><span style="color:var(--muted); font-size:.92rem;">' + esc(pieces.length > 220 ? pieces.slice(0, 217) + '…' : pieces) + '</span>' : '') +
        '<br><a href="' + esc(d.u) + '">Voir la compagnie →</a></p>';
    }).join('');
    html += '<small style="color:var(--muted);">Liaisons indicatives : vérifiez les horaires et les escales au moment de réserver.</small></div>';
    return { html: html, answered: true };
  }

  /* ---------- Hôtels de la destination (ville ou pays détecté) ---------- */
  function hotelsSection(query, padded) {
    if (typeof hotels === 'undefined' || typeof renderHotel !== 'function' || !Array.isArray(hotels)) { return { html: '', answered: false }; }
    var dest = findDest(padded);
    if (!dest.ville && !dest.pays) { return { html: '', answered: false }; }
    var list, lieu;
    if (dest.ville) {
      var key = loose(dest.ville);
      list = hotels.filter(function (h) { var l = loose(h.ville || ''); return l === key || (key.length >= 5 && hasWord(' ' + l + ' ', key)); });
      lieu = dest.ville;
    }
    if (!list || !list.length) {
      if (!dest.pays) { return { html: '', answered: false }; }
      list = hotels.filter(function (h) { return norm(h.pays) === norm(dest.pays); });
      lieu = dest.pays;
    }
    if (!list.length) {
      return {
        html: '<div class="glass-box" style="margin:6px 0 14px; border-left:5px solid var(--warning);"><h3 style="margin:0 0 6px;">🏨 Hôtels : ' + esc(dest.pays) + '</h3>' +
          '<p style="margin:0;">Nous n\'avons pas encore d\'hôtels en ' + esc(dest.pays) + ' dans notre sélection. <a href="hotels.html">Voir toutes les destinations disponibles →</a></p></div>',
        answered: true
      };
    }
    function stars(h) { var m = /(\d)/.exec(String(h.etoiles)); return m ? parseInt(m[1], 10) : 0; }
    var sorted = list.slice().sort(function (a, b) { return stars(b) - stars(a); });
    var shown = sorted.slice(0, 12);
    var html = '<div class="glass-box" style="margin:6px 0 14px;"><h3 style="margin:0;">🏨 Hôtels à ' + esc(lieu) + ' (' + list.length + ')</h3>' +
      (list.length > shown.length ? '<p style="margin:6px 0 0; color:var(--muted); font-size:.92rem;">Les ' + shown.length + ' mieux classés. Précisez un budget ou un équipement pour affiner.</p>' : '') + '</div>' +
      shown.map(function (h) { return renderHotel(h); }).join('');
    return { html: html, answered: true };
  }

  /* ---------- Point d'entrée ---------- */
  var AIRLINE_STEMS = ['compagnie', 'aerien', 'desser', 'airline', 'avion', 'volr', 'voler', 'vols'];

  window.nomadAnswer = function (query, hotelCount) {
    var padded = ' ' + norm(query) + ' ';
    var wantVisa = anyStem(padded, VISA_STEMS) || VISA_WORDS.some(function (w) { return hasWord(padded, w); });
    var wantAirport = anyStem(padded, AIRPORT_STEMS);
    var wantAirline = anyStem(padded, AIRLINE_STEMS) || hasWord(padded, 'vol');
    var wantHotels = /\b(hotel|hotels|hebergement|hebergements|logement|logements|resort)\b/.test(norm(query));
    var questionLike = QUESTION_RE.test(norm(query)) || /\?/.test(query);
    var concept = conceptFor(padded);
    var wantInfo = questionLike || anyStem(padded, INFO_STEMS) || hotelCount === 0 || !!concept;
    if (!wantVisa && !wantAirport && !wantAirline && !wantInfo) { return Promise.resolve(null); }

    var loads = [load('base-connaissances.js')];
    if (wantVisa) { loads.push(load('visas-data.js')); }
    if (wantAirport && typeof VILLES_AEROPORTS === 'undefined') { loads.push(load('villes-aeroports.js')); }

    return Promise.all(loads).then(function () {
      if (!window.NOMAD_KB) { return null; }
      idx = null; // reconstruit l'index avec les données chargées
      var sections = [], answered = false, airlineShown = false, hotelsShown = false, hotelsHtml = '';

      if (wantVisa) {
        var v = visaSection(query, padded);
        if (v.html) { sections.push(v.html); }
        answered = answered || v.answered;
      }
      if (wantAirport) {
        var a = airportSection(query, padded);
        if (a.html) { sections.push(a.html); }
        answered = answered || a.answered;
      }
      if (wantAirline) {
        var al = airlineSection(query, padded);
        if (al.html) { sections.push(al.html); }
        airlineShown = al.answered;
        answered = answered || al.answered;
      }
      if (wantHotels && (wantVisa || wantAirport || wantAirline || wantInfo)) {
        var hs = hotelsSection(query, padded);
        hotelsHtml = hs.html;
        hotelsShown = hs.answered;
        answered = answered || hs.answered;
      }
      // Recherche libre dans toutes les pages seulement si rien d'autre n'a répondu
      if (!sections.length && wantInfo) {
        var g = genericSection(query, padded);
        if (g.html) { sections.push(g.html); }
        answered = answered || g.answered;
      }
      if (!sections.length && !hotelsHtml) { return null; }

      var hotelSearch = HOTEL_SEARCH_RE.test(norm(query));
      var hideHotels = hotelsShown || ((wantVisa || wantAirport || airlineShown || (answered && hotelCount === 0) || (concept && answered)) && !hotelSearch);
      return {
        html: (sections.length ? '<div class="card" style="margin-top:22px;"><h2 style="margin-top:0;">💡 Réponses de Nomad</h2>' + sections.join('') + '</div>' : '') + hotelsHtml,
        hideHotels: hideHotels
      };
    });
  };
})();