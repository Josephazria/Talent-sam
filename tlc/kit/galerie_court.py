#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Galerie d'un kit court TLC : construit art/ (hd/, apercus/, reels/, sources/) et index.html."""
import os, glob, json, shutil, sys, html
from PIL import Image

KIT, REELS, SRC, OUT = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
MARQUE = "Lancaster"; QUAND = "Mercredi 7 octobre 2026, 18h"; REMISE = 80; COULEUR = "#F5A11A"
for d in ("hd", "apercus", "reels", "sources"): os.makedirs(os.path.join(OUT, d), exist_ok=True)

def jpg(src, dst, w, q):
    im = Image.open(src).convert("RGB")
    if im.width > w: im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    im.save(dst, quality=q, optimize=True)

files = sorted(glob.glob(os.path.join(KIT, "*.png")))
for f in files:
    n = os.path.splitext(os.path.basename(f))[0]
    jpg(f, os.path.join(OUT, "hd", n + ".jpg"), 1080, 88); jpg(f, os.path.join(OUT, "apercus", n + ".jpg"), 480, 82)
for f in sorted(glob.glob(os.path.join(REELS, "*.mp4"))): shutil.copy(f, os.path.join(OUT, "reels", os.path.basename(f)))
for f in sorted(glob.glob(os.path.join(SRC, "*"))):
    n, e = os.path.splitext(os.path.basename(f))
    if e.lower() in (".jpg", ".jpeg", ".webp"): jpg(f, os.path.join(OUT, "sources", n + ".jpg"), 1200, 86)
    else: shutil.copy(f, os.path.join(OUT, "sources", os.path.basename(f)))

# --- contenu ---
FAM = [
    ("Manchette packshot", "Le nom en manchette géante, le sac détouré passe devant les lettres, sur l'orange de la vente. Le post d'annonce (nouveauté du 30/09, toujours à valider).",
     [("manchette_noir_couleur_post", "Sac noir · post", "reco"), ("manchette_noir_couleur_story", "Sac noir · story", "reco"),
      ("manchette_camel_couleur_post", "Sac camel · post", "warn:camel sur orange, peu de contraste"), ("manchette_camel_couleur_story", "Sac camel · story", "warn:camel sur orange, peu de contraste")]),
    ("Couverture", "La mannequin devant le nom, photo de campagne AH26 en 1280×1600 (la meilleure définition disponible sur lancaster.com). Le post sponsorisé.",
     [("couverture_bordeaux_mur_post", "Mur de bois, sac bordeaux · post", "reco"), ("couverture_bordeaux_mur_story", "Mur de bois, sac bordeaux · story", "reco"),
      ("couverture_bordeaux_chaise_post", "Chaise, sac bordeaux · post", ""), ("couverture_bordeaux_chaise_story", "Chaise, sac bordeaux · story", "")]),
    ("Sponso", "Photo assombrie, logo B en bas. La créa B de la pub Meta, à comparer avec la couverture après 48 h.",
     [("sponso_bordeaux_mur_post", "Sac bordeaux · post", ""), ("sponso_bordeaux_mur_story", "Sac bordeaux · story", "")]),
    ("Packshots", "Les deux sacs du site détourés, le bloc typo au-dessus. À remplacer par les vrais modèles du live si Romain en donne d'autres.",
     [("packshot_noir_papier_post", "Sac noir · post", ""), ("packshot_noir_papier_story", "Sac noir · story", ""),
      ("packshot_camel_papier_post", "Sac camel · post", ""), ("packshot_camel_papier_story", "Sac camel · story", ""), ("duo", "Duo", "reco")]),
    ("Cartes typo", "Sans photo. La story papier sert de miniature Whatnot, le carré de vignette du show.",
     [("typo_papier_post", "papier · post", ""), ("typo_papier_story", "papier · story", "reco"), ("typo_papier_carre", "papier · carré Whatnot", "reco"),
      ("typo_couleur_post", "orange · post", ""), ("typo_couleur_story", "orange · story", "")]),
    ("Bandeau site", "Bloc typo à gauche, photo à droite, pour la carte de thelivecorner.com.",
     [("hero_bordeaux_mur_1920x1080", "1920×1080", ""), ("hero_bordeaux_mur_1080x1080", "Mobile 1080×1080", "")]),
]
REELS_TXT = [("lancaster_reel-R1-defile_story_slogan", "R1 « Le défilé » · story 9:16 · 15 s"), ("lancaster_reel-R1-defile_post_slogan", "R1 « Le défilé » · post 4:5"),
             ("lancaster_reel-R2A-battements_story_slogan", "R2 « Battements » · story 9:16 · 12 s"), ("lancaster_reel-R2A-battements_post_slogan", "R2 « Battements » · post 4:5")]
LEGENDES = [
    ("Annonce", f"Vente privée Lancaster, en live sur Whatnot. Jusqu’à −{REMISE} %. Mercredi 7 octobre, 18h. Le lien est dans la bio."),
    ("Pub abonnées", f"Vente privée Lancaster, en live sur Whatnot mercredi à 18h. Jusqu’à −{REMISE} %. Abonnez-vous pour ne rater aucune vente."),
    ("Story jour J", f"C’est maintenant. Lancaster, en live sur Whatnot. Jusqu’à −{REMISE} %. Le lien est dans la bio."),
    ("Réels", "Lancaster, en live sur Whatnot. Mercredi 7 octobre, 18h. Le lien est dans la bio."),
]

def card(key, label, flag):
    cls = "card"; badge = ""
    if flag == "reco": badge = '<span class="badge reco">recommandé</span>'
    elif flag.startswith("warn:"): cls += " warn"; badge = f'<span class="badge warn">déconseillé · {html.escape(flag[5:])}</span>'
    return f'''<figure class="{cls}"><a href="hd/{key}.jpg" target="_blank" rel="noopener"><img src="apercus/{key}.jpg" alt="{html.escape(label)}" loading="lazy"></a>
<figcaption>{html.escape(label)} {badge}<a class="open" href="hd/{key}.jpg" target="_blank" rel="noopener">Ouvrir en grand</a></figcaption></figure>'''

fams = ""
for titre, desc, items in FAM:
    cards = "".join(card(*it) for it in items if os.path.exists(os.path.join(OUT, "hd", it[0] + ".jpg")))
    fams += f'<section><h2>{html.escape(titre)}</h2><p class="lead">{html.escape(desc)}</p><div class="grid">{cards}</div></section>'
reels = "".join(f'<figure class="card"><video src="reels/{k}.mp4" controls playsinline preload="metadata"></video><figcaption>{html.escape(t)}</figcaption></figure>'
                for k, t in REELS_TXT if os.path.exists(os.path.join(OUT, "reels", k + ".mp4")))
legs = "".join(f'<div class="leg"><div><strong>{html.escape(t)}</strong><p>{html.escape(x)}</p></div><button type="button" class="copy" data-t="{html.escape(x)}">Copier</button></div>' for t, x in LEGENDES)
srcs = "".join(f'<a href="sources/{html.escape(n)}" target="_blank" rel="noopener">{html.escape(n)}</a>' for n in sorted(os.listdir(os.path.join(OUT, "sources"))))

page = f'''<title>Kit Lancaster 3</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500&family=Archivo:wght@400;500;600&display=swap">
<style>
/* Charte The Live Corner : papier / encre, Fraunces pour les titres, Archivo pour le texte ; une colonne de lecture, grilles de vignettes. */
:root {{ --bg:#F3EEE3; --fg:#1F1B17; --mute:#6E675C; --line:#D9D2C4; --card:#FBF8F1; --accent:{COULEUR}; --ok:#2E6B3A; --warnc:#8A3B1F; --warnbg:#F6E3DA;
        --display:'Fraunces', Georgia, serif; --body:'Archivo', 'Helvetica Neue', Arial, sans-serif; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#1A1714; --fg:#F3EEE3; --mute:#B4AC9E; --line:#3A342D; --card:#232019; --warnbg:#3A2419; --ok:#8CCB97; --warnc:#F0A98A; color-scheme: dark }} }}
:root[data-theme="dark"] {{ --bg:#1A1714; --fg:#F3EEE3; --mute:#B4AC9E; --line:#3A342D; --card:#232019; --warnbg:#3A2419; --ok:#8CCB97; --warnc:#F0A98A; color-scheme: dark }}
body {{ background:var(--bg); color:var(--fg); font-family:var(--body); font-size:15px; line-height:1.5; margin:0; padding-block:32px 64px; padding-inline:16px; }}
main {{ max-width:1180px; margin:0 auto; }}
h1 {{ font-family:var(--display); font-weight:500; font-size:clamp(40px,7vw,76px); line-height:1; margin:0 0 8px; text-wrap:balance; }}
h2 {{ font-family:var(--display); font-weight:500; font-size:30px; margin:0 0 6px; text-wrap:balance; }}
.eyebrow {{ font-size:12px; letter-spacing:.14em; text-transform:uppercase; color:var(--mute); font-weight:600; }}
.when {{ font-size:22px; font-weight:500; margin:4px 0 0; }}
.sub {{ color:var(--mute); margin:4px 0 20px; }}
.lead {{ color:var(--mute); max-width:70ch; margin:0 0 14px; }}
.etat {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:12px 28px; padding:18px 0; border-top:1px solid var(--line); border-bottom:1px solid var(--line); margin-bottom:28px; }}
.etat ul {{ margin:6px 0 0; padding-left:18px; }} .etat li {{ margin:3px 0; }}
.etat h3 {{ font-size:13px; letter-spacing:.12em; text-transform:uppercase; margin:0; color:var(--mute); }}
section {{ margin:34px 0; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); gap:16px; }}
.card {{ margin:0; min-width:0; }} .card img, .card video {{ width:100%; height:auto; display:block; background:var(--card); border:1px solid var(--line); }}
.card.warn img {{ opacity:.78; }}
figcaption {{ font-size:13px; margin-top:6px; display:flex; flex-wrap:wrap; gap:4px 8px; align-items:center; }}
.badge {{ font-size:11px; letter-spacing:.06em; text-transform:uppercase; font-weight:600; padding:2px 7px; border-radius:3px; }}
.badge.reco {{ background:var(--accent); color:#1F1B17; }} .badge.warn {{ background:var(--warnbg); color:var(--warnc); text-transform:none; letter-spacing:0; }}
.open {{ color:var(--mute); font-size:12px; margin-left:auto; }}
.leg {{ display:flex; gap:14px; align-items:flex-start; justify-content:space-between; padding:12px 0; border-top:1px solid var(--line); }}
.leg p {{ margin:4px 0 0; max-width:70ch; }}
.copy {{ font:600 13px var(--body); background:var(--fg); color:var(--bg); border:0; padding:8px 14px; border-radius:3px; cursor:pointer; flex:none; }}
.copy:focus-visible, a:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; }}
.srcs {{ display:flex; flex-wrap:wrap; gap:8px 16px; font-size:13px; }}
footer {{ margin-top:48px; color:var(--mute); font-size:12px; border-top:1px solid var(--line); padding-top:12px; }}
a {{ color:inherit; }}
</style>
<main>
<div class="eyebrow">The Live Corner · kit visuel de vente · kit court</div>
<h1>Lancaster</h1>
<p class="when">{QUAND} · Déborah</p>
<p class="sub">Vente privée en live sur Whatnot · jusqu’à −{REMISE} % · orange {COULEUR} · 22 visuels + 4 réels, produits le 05/10/2026</p>
<div class="etat">
<div><h3>État</h3><ul>
<li>Planning Notion : ligne « Vente privée — Lancaster (3) », Confirmé, Déborah.</li>
<li>Site thelivecorner : vente publiée, photo de campagne ; Lancaster (2) et By June passées en terminé.</li>
<li>Photos : lancaster.com, 6 photos de campagne AH26 en 1280×1600 (accord acquis) ; 2 packshots PNG du kit 2.</li>
<li>« sur Whatnot » écrit sur tous les visuels et dans les réels.</li>
</ul></div>
<div><h3>À trancher</h3><ul>
<li>Le lien Whatnot du show (site + légendes + lien de la bio).</li>
<li>Les modèles réellement dans le live : les sacs montrés (noir, camel) viennent du site.</li>
<li>La « manchette packshot » comme post d'annonce : toujours à valider.</li>
<li>Prix TLC / boutique pour des tuiles prix.</li>
</ul></div>
<div><h3>Limites</h3><ul>
<li>Pas de tuile prix (prix non fixés), pas de vestiaire (2 packshots).</li>
<li>Camel sur orange : peu de contraste, gardé pour mémoire.</li>
<li>Photos en 1280 px : bien pour Instagram, juste pour une pub ; demander les originaux à Lancaster.</li>
</ul></div>
</div>
<section><h2>Ce que je publierais</h2><p class="lead">Annonce : la manchette noire en post, la story de même. Pub Meta : couverture (créa A) contre sponso (créa B), même audience, on garde la moins chère au résultat après 48 h. Whatnot : la carte typo papier en miniature. Stories des jours d'avant : packshots et typo orange. Réels : R1 en annonce, R2 la veille.</p></section>
{fams}
<section><h2>Réels</h2><p class="lead">Sans son (musique dans Instagram). Carton final avec le slogan « Le live qui vous va bien. ».</p><div class="grid">{reels}</div></section>
<section><h2>Légendes</h2><p class="lead">Prêtes à coller. Toujours « en live », jamais « en direct ».</p>{legs}</section>
<section><h2>Sources</h2><p class="lead">Récupérées sur lancaster.com le 05/10/2026, telles quelles (gs = galerie campagne, pk = packshots, fp/lb = kit 2).</p><div class="srcs">{srcs}</div></section>
<footer>The Live Corner · papier #F3EEE3 · encre #1F1B17 · Fraunces &amp; Archivo · le rouge #D8261C seulement dans le point du logo</footer>
</main>
<script>
document.querySelectorAll('.copy').forEach(b => b.addEventListener('click', () => {{
  const t = b.dataset.t; const done = () => {{ b.textContent = 'Copié'; setTimeout(() => b.textContent = 'Copier', 1500); }};
  if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(done).catch(() => fallback(b, t, done)); else fallback(b, t, done);
}}));
function fallback(b, t, done) {{ const p = b.parentElement.querySelector('p'); const r = document.createRange(); r.selectNodeContents(p); const s = getSelection(); s.removeAllRanges(); s.addRange(r); done(); }}
</script>
'''
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(page)
print("index.html", len(page), "octets ;", len(os.listdir(os.path.join(OUT, "hd"))), "hd ;", len(os.listdir(os.path.join(OUT, "reels"))), "réels ;", len(os.listdir(os.path.join(OUT, "sources"))), "sources")
