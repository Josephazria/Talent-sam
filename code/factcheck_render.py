import random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350
NAVY = (14, 24, 48); DARK = (8, 14, 30); CREAM = (247, 242, 233)
CORAL = (255, 111, 97); GREY = (168, 176, 192); SLATE = (52, 66, 104)
F = "/home/claude/fonts/"
def anton(s): return ImageFont.truetype(F + "Anton-Regular.ttf", s)
def pop(s, w="Medium"): return ImageFont.truetype(F + f"Poppins-{w}.ttf", s)
def lora(s, bold=False):
    f = ImageFont.truetype(F + "Lora.ttf", s)
    try: f.set_variation_by_name("Bold" if bold else "SemiBold")
    except Exception: pass
    return f

def background(col):
    im = Image.new("RGB", (W, H), col)
    # coral halo + vignette
    halo = Image.new("L", (W, H), 0); d = ImageDraw.Draw(halo)
    d.ellipse((W - 520, -380, W + 380, 420), fill=70)
    halo = halo.filter(ImageFilter.GaussianBlur(160))
    im = Image.composite(Image.new("RGB", (W, H), CORAL), im, halo.point(lambda v: v // 3))
    vig = Image.new("L", (W, H), 0); d = ImageDraw.Draw(vig)
    d.rectangle((0, 0, W, H), fill=120); d.ellipse((-200, -150, W + 200, H + 150), fill=0)
    vig = vig.filter(ImageFilter.GaussianBlur(180))
    im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, vig)
    rnd = random.Random(7)
    px = im.load()
    for _ in range(90000):
        x, y = rnd.randrange(W), rnd.randrange(H); r, g, b = px[x, y]; n = rnd.randint(-9, 9)
        px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)))
    return im

def rich_lines(text, font, maxw, draw):
    """text with *coral* segments -> list of lines of (word, color)"""
    words, coral = [], False
    for part in text.split("*"):
        for w in part.split():
            words.append((w, coral))
        coral = not coral
    lines, cur = [], []
    for w in words:
        test = " ".join(x[0] for x in cur + [w])
        if cur and draw.textlength(test, font=font) > maxw:
            lines.append(cur); cur = [w]
        else:
            cur.append(w)
    if cur: lines.append(cur)
    return lines

def draw_rich(draw, text, font, x, y, maxw, col=CREAM, lh=1.32, align="l"):
    sp = draw.textlength(" ", font=font)
    for line in rich_lines(text, font, maxw, draw):
        tw = sum(draw.textlength(w, font=font) for w, _ in line) + sp * (len(line) - 1)
        cx = x if align == "l" else x + (maxw - tw) / 2
        for w, c in line:
            draw.text((cx, y), w, font=font, fill=CORAL if c else col)
            cx += draw.textlength(w, font=font) + sp
        y += font.size * lh
    return y

def stamp(im, text, color, cx, cy, size=150, angle=-8):
    f = anton(size)
    tmp = Image.new("RGBA", (10, 10)); d = ImageDraw.Draw(tmp)
    bb = d.textbbox((0, 0), text, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad = 34
    layer = Image.new("RGBA", (tw + 2 * pad + 20, th + 2 * pad + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((10, 10, 10 + tw + 2 * pad, 10 + th + 2 * pad), radius=18, outline=color, width=12)
    d.text((10 + pad - bb[0], 10 + pad - bb[1]), text, font=f, fill=color)
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    im.paste(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)), layer)

def counter(d, n, total=6):
    d.text((80, 70), f"{n}/{total}", font=pop(32, "SemiBold"), fill=GREY)
    d.text((W - 80, 70), "FACT-CHECK", font=pop(30, "SemiBold"), fill=CORAL, anchor="ra")

def source(d, text):
    draw_rich(d, text, pop(28, "Regular"), 80, H - 120, W - 160, col=GREY, lh=1.3)

def claim_slide(n, bg, quote, verbatim, verdict, big, body, src):
    im = background(bg); d = ImageDraw.Draw(im)
    counter(d, n)
    d.text((80, 160), "L'ARTICLE DIT :", font=pop(32, "SemiBold"), fill=GREY)
    # quote box
    qf = lora(52)
    qtxt = f"« {quote} »" if verbatim else quote
    lines = rich_lines(qtxt, qf, W - 230, d)
    bh = len(lines) * 52 * 1.3 + 70
    d.rounded_rectangle((80, 215, W - 80, 215 + bh), radius=22, fill=SLATE)
    d.rectangle((80, 215, 92, 215 + bh), fill=CORAL)
    draw_rich(d, qtxt, qf, 130, 250, W - 230, lh=1.3)
    y = 215 + bh
    color = CORAL if verdict == "FAUX" else CREAM
    stamp(im, verdict, color, W / 2, y + 150, size=160, angle=-7)
    y += 330
    if big:
        bf = anton(104)
        y = draw_rich(d, big, bf, 80, y, W - 160, lh=1.12, align="c") + 25
    draw_rich(d, body, pop(44, "Medium"), 80, y, W - 160, lh=1.36, align="c")
    source(d, src)
    return im

slides = []

# 1 — couverture
im = background(DARK); d = ImageDraw.Draw(im)
d.text((80, 80), "MEDIAPART · 5 OCTOBRE 2026", font=pop(32, "SemiBold"), fill=GREY)
card = Image.new("RGBA", (900, 470), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
cd.rounded_rectangle((0, 0, 900, 470), radius=14, fill=CREAM)
cd.text((50, 45), "Les « chiffres noirs » d'Octobre rose :", font=lora(34), fill=(90, 90, 100))
draw_rich(cd, "La France tait la hausse catastrophique du nombre de cancers du sein", lora(62, True), 50, 105, 800, col=NAVY, lh=1.2)
card = card.rotate(-2.5, expand=True, resample=Image.BICUBIC)
im.paste(card, (int((W - card.width) / 2), 150), card)
stamp(im, "FACT-CHECK", CORAL, W - 300, 640, size=96, angle=-12)
d = ImageDraw.Draw(im)
y = draw_rich(d, "JE SUIS CANCÉROLOGUE,", anton(108), 80, 760, W - 160, lh=1.1, align="c")
y = draw_rich(d, "ET JE RÉPONDS À *MEDIAPART.*", anton(108), 80, y, W - 160, lh=1.1, align="c")
f40 = pop(40, "SemiBold"); t = "6 phrases · chaque chiffre vérifié"; tw = d.textlength(t, font=f40); x0 = (W - tw - 70) / 2
d.text((x0, y + 40), t, font=f40, fill=GREY); ax = x0 + tw + 22; ay = y + 66
d.line((ax, ay, ax + 44, ay), fill=CORAL, width=6); d.polygon([(ax + 48, ay), (ax + 30, ay - 14), (ax + 30, ay + 14)], fill=CORAL)
slides.append(im)

slides.append(claim_slide(1, NAVY, "l'Inca tait l'essentiel", True, "FAUX", None,
    "Ces chiffres sont *publiés* par Santé publique France et l'INCa. L'étude sur les jeunes femmes (2025) est *cosignée* par eux.",
    "Sources : Lapôtre-Ledoux et al., BEH 2023 ; Pujol et al., The Breast 2025"))
slides.append(claim_slide(2, DARK, "Le nombre de cancers du sein a fortement augmenté", False, "VRAI", "29 934 → 61 214",
    "cas en 1990, puis en 2023. Mais *la moitié* de cette hausse vient d'une population plus nombreuse et plus âgée.",
    "Source : Santé publique France, INCa, Francim – BEH 2023"))
slides.append(claim_slide(3, NAVY, "cette accélération du cancer du sein en France", True, "FAUX", "+0,9 % → +0,3 %",
    "par an depuis 1990, puis depuis 2010 : *ça ralentit.* Et la mortalité baisse de *1,5 % par an.*",
    "Sources : BEH 2023 ; INCa, Panorama des cancers 2026 (taux à âge égal)"))
slides.append(claim_slide(4, DARK, "Ça augmente chez les jeunes femmes", False, "VRAI", "+63 % à 30 ans",
    "depuis 1990. Mais ça monte *à tous les âges* (+67 % à 70 ans), et ça reste rare : à 30 ans, *1 femme sur 3 800* par an.",
    "Sources : Pujol et al., The Breast 2025 ; BEH 2023"))
slides.append(claim_slide(5, NAVY, "La France est parmi les pays les plus touchés", False, "VRAI", "88 %",
    "de survie à 5 ans. Le risque est parmi les plus élevés au monde, *on cherche pourquoi.* Mais on le soigne de mieux en mieux.",
    "Sources : INCa, Panorama des cancers 2026 ; GBD 2023, Lancet Oncol 2026"))
slides.append(claim_slide(6, DARK, "De moins en moins de femmes se font dépister", False, "VRAI", "52,7 % → 46,3 %",
    "de participation entre 2011 et 2024. *C'est ça, le vrai problème.*",
    "Source : INCa, Panorama des cancers 2026"))

# 8 — on peut tout faire dire aux chiffres
im = background(NAVY); d = ImageDraw.Draw(im)
y = draw_rich(d, "ON PEUT FAIRE DIRE", anton(112), 80, 110, W - 160, lh=1.08, align="c")
y = draw_rich(d, "*TOUT* AUX CHIFFRES", anton(112), 80, y, W - 160, lh=1.08, align="c") + 40
for a, b, sym in [("« +63 % chez les femmes de 30 ans »", "« 10 cas de plus pour 100 000 femmes »", "="),
             ("« Deux fois plus de cas »", "« Un risque presque stable depuis 2010 »", "ET")]:
    d.rounded_rectangle((80, y, W - 80, y + 290), radius=22, fill=SLATE)
    yy = draw_rich(d, a, pop(42, "SemiBold"), 120, y + 30, W - 240, align="c")
    d.text((W / 2, yy + 8), sym, font=anton(56), fill=CORAL, anchor="ma")
    draw_rich(d, b, pop(42, "SemiBold"), 120, yy + 85, W - 240, align="c")
    y += 330
draw_rich(d, "Tout est vrai. Un chiffre sans contexte, c'est une *émotion.* Avec, c'est une *information.*",
          pop(44, "Medium"), 80, y + 10, W - 160, align="c")
slides.append(im)

# 9 — ce qui compte
im = background(DARK); d = ImageDraw.Draw(im)
y = draw_rich(d, "CE QUI COMPTE *VRAIMENT*", anton(104), 80, 100, W - 160, lh=1.08, align="c") + 40
for t in ["Ton sein change ? *Consulte,* à tout âge.",
          "Dès 25 ans : un examen par un pro *chaque année.*",
          "De 50 à 74 ans : ta mammo *tous les 2 ans.*"]:
    d.ellipse((80, y + 14, 112, y + 46), fill=CORAL)
    y = draw_rich(d, t, pop(46, "SemiBold"), 140, y, W - 220, lh=1.3) + 28
y = draw_rich(d, "La recherche sur les causes doit continuer : Mediapart a raison d'en parler.",
              pop(38, "Regular"), 80, y + 10, W - 160, col=GREY, align="c") + 40
d.rounded_rectangle((80, y, W - 80, y + 190), radius=22, fill=SLATE)
d.text((W / 2, y + 30), "BILAN : 4 VRAIS · 2 FAUX", font=anton(72), fill=CREAM, anchor="ma")
d.text((W / 2, y + 125), "Et les 2 faux sont ceux qui font peur.", font=pop(36, "Medium"), fill=CORAL, anchor="ma")
draw_rich(d, "Une question ? Pose-la en commentaire", pop(40, "SemiBold"), 80, H - 140, W - 160, align="c")
slides.append(im)

import os
os.makedirs("/home/claude/carrousel/out", exist_ok=True)
for i, s in enumerate(slides, 1):
    s.save(f"/home/claude/carrousel/out/factcheck_{i:02d}.png")
# planche
th = [s.resize((360, 450)) for s in slides]
sheet = Image.new("RGB", (3 * 360 + 40, 3 * 450 + 40), (0, 0, 0))
for i, t in enumerate(th):
    sheet.paste(t, (10 + (i % 3) * 370, 10 + (i // 3) * 460))
sheet.save("/home/claude/carrousel/out/planche.png")
print("ok", len(slides))
