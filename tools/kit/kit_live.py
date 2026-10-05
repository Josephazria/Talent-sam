#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ohlalive — RUNNER du kit visuel de live.
Usage : python3 kit_live.py live.json [--sans-reels]
Produit dans /home/claude/carrousel/kit/<slug>/ :
  post-teasing/ story-teasing/ story-live/ cover-whatnot/ banniere-site/ (6 dérivés + PLANCHE chacun)
  reels/ (R1 + R2 en story et post, prompts Seedance R3-R4)
  apercus/ (JPEG 540 px pour la galerie), index.html (galerie), _files.json (liste à publier)

live.json minimal :
{
  "slug": "2026-09-22",
  "date_label": "MARDI 22 SEPTEMBRE  ·  12H",
  "title": "Sélection", "title_italic": "de luxe",
  "sub_upper": "SÉLECTION DE LUXE",
  "beats": ["Mardi 22", "12H", "Sélection", "de luxe", "en live", "sur Whatnot"],
  "whatnot_url": "https://www.whatnot.com/fr-FR/user/ohlaliveparis",
  "title_human": "Sélection de luxe", "date_human": "Mardi 22 septembre · 12H"
}
"""
import os, sys, json, glob, html
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ohlalive_kit import contact_sheet
import post_teasing, vertical_kit, banner_site, reels

ROOT = os.environ.get("KIT_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "kit"))

def build_all(live, with_reels=True):
    slug = live["slug"]
    out = f"{ROOT}/{slug}"
    os.makedirs(out, exist_ok=True)

    # 1. post teasing (portrait)
    d = f"{out}/post-teasing"; os.makedirs(d, exist_ok=True)
    paths, labels = [], []
    for compo, cname in (("A", "A-typo"), ("B", "B-embleme")):
        for scheme in ("framboise", "mimosa", "ivoire"):
            p = f"{d}/{slug}_post-teasing_{cname}_{scheme}.png"
            post_teasing.build(scheme, compo, live).save(p)
            paths.append(p); labels.append(f"{cname.upper()}  ·  {scheme.upper()}")
    contact_sheet(paths, labels, cols=3, thumb_w=520).save(f"{d}/{slug}_post-teasing_PLANCHE.png")

    # 2-4. verticales
    vertical_kit.build_family(slug, "story-teasing", {
        "eyebrow": live["date_label"], "head": live["title"], "italic": live["title_italic"],
        "footer": ["EN LIVE SUR WHATNOT", "@OHLALIVEPARIS"], "top_safe": 250, "bottom_safe": 330})
    vertical_kit.build_family(slug, "story-live", {
        "eyebrow": "C'EST MAINTENANT", "head": "On est", "italic": "en live",
        "sub": live["sub_upper"], "footer": ["SUR WHATNOT", "@OHLALIVEPARIS"], "top_safe": 250, "bottom_safe": 330})
    vertical_kit.build_family(slug, "cover-whatnot", {
        "head": live["title"], "italic": live["title_italic"],
        "sub": live.get("brands_line"), "footer": ["@OHLALIVEPARIS"],
        "logo_w": 960, "top_safe": 140, "bottom_safe": 160})

    # 5. bannière site
    d = f"{out}/banniere-site"; os.makedirs(d, exist_ok=True)
    spec = {"eyebrow": f"PROCHAIN LIVE  ·  {live['date_label']}", "head": live["title"],
            "italic": live["title_italic"], "footer": "EN LIVE SUR WHATNOT"}
    paths, labels = [], []
    for compo, cname in (("A", "A-typo"), ("B", "B-embleme")):
        for scheme in ("framboise", "mimosa", "ivoire"):
            p = f"{d}/{slug}_banniere-site_{cname}_{scheme}.png"
            banner_site.render(scheme, compo, spec).save(p)
            paths.append(p); labels.append(f"{cname.upper()}  ·  {scheme.upper()}")
    contact_sheet(paths, labels, cols=2, thumb_w=700).save(f"{d}/{slug}_banniere-site_PLANCHE.png")

    # 6. réels
    d = f"{out}/reels"; os.makedirs(d, exist_ok=True)
    if with_reels:
        for fmt, size in {"story": (1080, 1920), "post": (1080, 1350)}.items():
            p = f"{d}/{slug}_reel-R1-montee_framboise_{fmt}.mp4"
            reels.encode(reels.reel_montee("framboise", size, live, p), size, p)
            p = f"{d}/{slug}_reel-R2-battements_{fmt}.mp4"
            reels.encode(reels.reel_battements(size, live, p), size, p)
    write_seedance_prompts(live, f"{d}/SEEDANCE_prompts_R3-R4.md")

    # 7. galerie
    build_gallery(live, out)
    return out

def write_seedance_prompts(live, path):
    txt = f"""# Réels teasing R3 & R4 — prompts Seedance 2.5 (BytePlus Playground)

Live : {live['title_human']} — {live['date_human']}, Whatnot.
Durée cible : 5–6 s de plan Seedance + 2 s de carton de fin (story-teasing A framboise du kit).
Format : 9:16 (1080×1920). Pour le post, recadrer en 4:5 sur la zone centrale. Sans son (musique ajoutée dans Instagram).
Règles maison : aucune marchandise identifiable, pas d'écran de téléphone, visages de trois-quarts / profil / dos, pas de lit ni de tenue légère.

## R3 — « L'avalanche »
Intérieur haussmannien lumineux, parquet point de Hongrie, moulures, grande fenêtre en lumière naturelle douce. Une femme élégante de 40-45 ans, vue de trois-quarts dos, ouvre les deux portes d'un immense placard encastré qui déborde : robes, manteaux, boîtes et pochettes en tissu s'effondrent sur elle en avalanche. Elle recule, lève les bras, puis se laisse tomber assise dans la pile, épuisée et amusée, visage de profil. Caméra fixe à hauteur d'épaule, léger zoom avant lent. Palette chaude, textures nobles, pas de logo ni de marque visible, pas de téléphone. Ton : humour chic, exaspération tendre. Cinématographique, 24 fps, grain fin.
Négatif : visage de face centré, écran, téléphone, logo, texte à l'image, lit, tenue légère.
Montage : 5 s → cut sec → carton de fin 2 s (fond framboise).

## R4 — « La sélection »
Gros plans lents, lumière du matin rasante sur une console en marbre blanc veiné dans un salon haussmannien. Des mains de femme soignées, manches en soie ivoire, disposent avec précision des objets précieux abstraits : un foulard de soie plié, une boîte gainée de cuir fermée, un écrin fermé, un ruban framboise. Aucun logo, aucune marque lisible. Travelling latéral très lent, faible profondeur de champ, reflets doux, poussière dans la lumière. Cinématographique, 24 fps, grain fin.
Négatif : visage, écran, téléphone, logo, texte, sac ou bijou identifiable, mouvement rapide.
Montage : 4–5 s → fondu 0,3 s → carton de fin 2 s (fond mimosa).

## Quand les .mp4 Seedance arrivent
1. Vérifier le 9:16, recadrer en 4:5 pour la version post. 2. Ajouter le carton de fin (2 s) avec fondu. 3. Livrer R3 et R4 en story et post à côté de R1 et R2.
"""
    open(path, "w").write(txt)

FAMILIES = [
    ("post-teasing", "Post teasing", "Feed Instagram, portrait 1080×1350, date et heure. La couleur se choisit selon la place du post dans la rangée de trois.", ""),
    ("story-teasing", "Story teasing", "1080×1920, heure en accroche. Zones sûres Instagram respectées, place pour le sticker Whatnot.", ""),
    ("story-live", "Story « on est en live »", "Jour J, au moment de lancer.", ""),
    ("cover-whatnot", "Cover Whatnot", "Format officiel 1080×1920. Sans date ni heure : reste valable si le live est reprogrammé.", ""),
    ("banniere-site", "Bannière site", "16:9, 1600×900, pour la carte « Prochain live » sur ohlaliveparis.com. La B s'insère le mieux dans une carte.", "wide"),
]

def build_gallery(live, out):
    slug = live["slug"]
    os.makedirs(f"{out}/apercus", exist_ok=True)
    files = {}
    sections = []
    for fam, title, desc, cls in FAMILIES:
        cards = []
        for p in sorted(glob.glob(f"{out}/{fam}/*.png")):
            name = os.path.basename(p)
            files[f"{fam}/{name}"] = f"{fam}/{name}"
            if "PLANCHE" in name:
                continue
            im = Image.open(p).convert("RGB"); w = 540; h = int(im.height * w / im.width)
            th = f"apercus/{name[:-4]}.jpg"
            im.resize((w, h), Image.LANCZOS).save(f"{out}/{th}", "JPEG", quality=85, optimize=True)
            files[th] = th
            compo = "A typo" if "A-typo" in name else "B emblème"
            col = name.rsplit("_", 1)[1][:-4].capitalize()
            cards.append(f'<figure><img src="{th}" alt=""><figcaption><span class="tag"><b>{compo}</b> · {col}</span><a href="{fam}/{name}" target="_blank" rel="noopener">Ouvrir le PNG</a></figcaption></figure>')
        planche = f"{fam}/{slug}_{fam}_PLANCHE.png"
        sections.append(f'<section><h2>{title}</h2><p class="desc">{desc}</p><figure class="planche"><img src="{planche}" alt="Planche {title}"><figcaption><span class="tag">Planche de comparaison</span><a href="{planche}" target="_blank" rel="noopener">Ouvrir</a></figcaption></figure><div class="grid {cls}">{"".join(cards)}</div></section>')
    vids = []
    for p in sorted(glob.glob(f"{out}/reels/*.mp4")):
        name = os.path.basename(p); files[f"reels/{name}"] = f"reels/{name}"
        lab = ("R1 Montée" if "R1" in name else "R2 Battements") + (" · story 9:16" if "story" in name else " · post 4:5")
        vids.append(f'<figure><video src="reels/{name}" controls muted playsinline loop preload="metadata"></video><figcaption><span class="tag"><b>{lab}</b></span><a href="reels/{name}" target="_blank" rel="noopener">Ouvrir le MP4</a></figcaption></figure>')
    files["reels/SEEDANCE_prompts_R3-R4.md"] = "reels/SEEDANCE_prompts_R3-R4.md"
    sections.append(f'<section><h2>Réels teasing</h2><p class="desc">Sans son : la musique tendance s\'ajoute dans Instagram. R1 monte la carte élément par élément ; R2 tape un mot par battement en alternant les trois fonds.</p><div class="grid wide">{"".join(vids)}</div><div class="note"><p><strong>R3 et R4 (ambiance Seedance)</strong> — prompts dans <a href="reels/SEEDANCE_prompts_R3-R4.md" target="_blank" rel="noopener">SEEDANCE_prompts_R3-R4.md</a>.</p></div></section>')

    css = """:root{--bg:#F2F0EA;--ink:#1A1A1A;--muted:#7D6A6F;--line:#E0D9D5;--framboise:#963A4C;--card:#FFFFFF;--pill:#F7E3E7}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#2B1119;--ink:#F2F0EA;--muted:#C9B2B8;--line:#4A2A33;--framboise:#F4C846;--card:#3A1A24;--pill:#4A2A33}}
:root[data-theme="dark"]{--bg:#2B1119;--ink:#F2F0EA;--muted:#C9B2B8;--line:#4A2A33;--framboise:#F4C846;--card:#3A1A24;--pill:#4A2A33}
body{background:var(--bg);color:var(--ink);font-family:Jost,"Helvetica Neue",Arial,sans-serif;font-size:15px;line-height:1.5;padding:0 20px;padding-block:32px 64px;margin:0}
.wrap{max-width:1180px;margin:0 auto}header{display:flex;flex-wrap:wrap;gap:16px 40px;align-items:flex-end;justify-content:space-between;border-bottom:2px solid var(--framboise);padding-bottom:20px;margin-bottom:36px}
.eyebrow{font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:var(--framboise);font-weight:600;margin:0 0 6px}
h1{font-family:"Playfair Display",Georgia,serif;font-weight:700;font-size:clamp(30px,5vw,44px);line-height:1.05;margin:0;text-wrap:balance}h1 em{font-style:italic;font-weight:500}
.meta{color:var(--muted);font-size:14px}.meta strong{color:var(--ink);font-weight:500}section{margin-bottom:44px}
h2{font-family:"Playfair Display",Georgia,serif;font-weight:700;font-size:24px;margin:0 0 4px}.desc{color:var(--muted);margin:0 0 16px;max-width:65ch}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:16px}.grid.wide{grid-template-columns:repeat(auto-fill,minmax(260px,1fr))}
figure{margin:0;background:var(--card);border:1px solid var(--line);display:flex;flex-direction:column}figure img,figure video{display:block;width:100%;height:auto;max-width:100%}
figcaption{padding:10px 12px 12px;display:flex;flex-direction:column;gap:6px}.tag{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:600}.tag b{color:var(--ink)}
figcaption a{color:var(--framboise);font-weight:500;text-decoration:none;font-size:13px}figcaption a:hover,figcaption a:focus-visible{text-decoration:underline;outline:none}
.planche{margin:0 0 20px}.planche figcaption{flex-direction:row;justify-content:space-between;align-items:center}
.note{background:var(--pill);border-left:3px solid var(--framboise);padding:12px 16px;margin:16px 0 0;font-size:14px}.note p{margin:0}.note a{color:var(--framboise)}
footer{margin-top:40px;border-top:1px solid var(--line);padding-top:16px;color:var(--muted);font-size:13px}"""
    page = f"""<title>Kit live {html.escape(live['date_human'].split('·')[0].strip())}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,500&family=Jost:wght@400;500;600&display=swap">
<style>{css}</style>
<div class="wrap"><header><div><p class="eyebrow">Ohlalive · kit visuel de live</p><h1>{html.escape(live['title'])} <em>{html.escape(live['title_italic'])}</em></h1></div>
<p class="meta"><strong>{html.escape(live['date_human'])}</strong> · en live sur Whatnot · @ohlaliveparis<br>A typo / B emblème × Framboise / Mimosa / Ivoire</p></header>
{"".join(sections)}
<footer>Ohlalive · Maison de sélection parisienne · Playfair Display &amp; Jost · Framboise 150·58·76 · Mimosa 244·200·70 · Ivoire 242·240·234</footer></div>"""
    open(f"{out}/index.html", "w").write(page)
    json.dump([{"path": k} for k in files], open(f"{out}/_files.json", "w"))
    print("galerie :", f"{out}/index.html", "|", len(files), "fichiers à publier (voir _files.json)")

if __name__ == "__main__":
    live = json.load(open(sys.argv[1]))
    build_all(live, with_reels="--sans-reels" not in sys.argv)
