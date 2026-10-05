"""Carrousel Doctorgane n°4 — « 5 bonnes nouvelles sur le cancer du sein » (chiffres sourcés INCa / SpF / PubMed)"""
import sys, math
sys.path.insert(0, "/home/claude/doctorgane/c3")
from PIL import Image, ImageDraw, ImageFont
F = "/home/claude/fonts/"
NAVY = (18, 33, 61); CREAM = (246, 241, 233); CORAL = (255, 111, 97)
GREY = (150, 160, 180); TRACK = (48, 68, 108); DARK_SRC = (110, 115, 130); SAND = (232, 224, 212)
OUT = "/home/claude/doctorgane/c4/"
N = 8

def anton(s): return ImageFont.truetype(F + "Anton-Regular.ttf", s)
def pop(s, w="Regular"): return ImageFont.truetype(F + f"Poppins-{w}.ttf", s)

def wrap(d, text, font, maxw):
    lines = []
    for para_ in text.split("\n"):
        cur = ""
        for w in para_.split(" "):
            test = (cur + " " + w).strip()
            if d.textlength(test, font=font) <= maxw: cur = test
            else: lines.append(cur); cur = w
        lines.append(cur)
    return lines

def para(d, text, font, x, y, maxw, fill, lh=1.35, center=False, W=1080):
    for ln in wrap(d, text, font, maxw):
        tx = (W - d.textlength(ln, font=font)) / 2 if center else x
        d.text((tx, y), ln, font=font, fill=fill); y += int(font.size * lh)
    return y

def big(d, lines, x, y, size, W=1080, center=False, lh=1.08):
    f = anton(size)
    for t, c in lines:
        tx = (W - d.textlength(t, font=f)) / 2 if center else x
        d.text((tx, y), t, font=f, fill=c); y += int(size * lh)
    return y

def ribbon(d, cx, cy, s, col):
    w = int(s * 0.22)
    d.arc([cx - s*0.42, cy - s*0.95, cx + s*0.42, cy + s*0.1], 180, 360, fill=col, width=w)
    d.line([(cx - s*0.42, cy - s*0.42), (cx + s*0.35, cy + s*0.85)], fill=col, width=w)
    d.line([(cx + s*0.42, cy - s*0.42), (cx - s*0.35, cy + s*0.85)], fill=col, width=w)

def dots(d, i, y, W=1080, on=CORAL, off=(60, 75, 105)):
    x0 = W/2 - (N-1)*14
    for k in range(N):
        d.ellipse([x0 + k*28 - 6, y - 6, x0 + k*28 + 6, y + 6], fill=on if k == i else off)

def source(d, text, y, col=GREY, W=1080, size=24):
    f = pop(size)
    while d.textlength(text, font=f) > 960 and size > 16:
        size -= 1; f = pop(size)
    d.text(((W - d.textlength(text, font=f)) / 2, y), text, font=f, fill=col)

def slide(bg=NAVY):
    im = Image.new("RGB", (1080, 1350), bg); return im, ImageDraw.Draw(im)

def bar(d, x, y, w, h, frac, fill, track, label, lab_col):
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=track)
    d.rounded_rectangle([x, y, x + max(h, int(w * frac)), y + h], radius=h // 2, fill=fill)
    f = anton(int(h * 0.62)); d.text((x + int(w * frac) - d.textlength(label, font=f) - 28, y + h * 0.17), label, font=f, fill=lab_col)

# ---- S1 accroche
im, d = slide()
ribbon(d, 540, 200, 95, CORAL)
f = pop(30, "SemiBold"); t = "OCTOBRE ROSE"
d.text(((1080 - d.textlength(t, font=f)) / 2, 330), t, font=f, fill=CORAL)
y = big(d, [("5 BONNES", CREAM), ("NOUVELLES", CREAM)], 0, 390, 150, center=True)
f = pop(44, "SemiBold"); t = "SUR LE"
d.text(((1080 - d.textlength(t, font=f)) / 2, y + 28), t, font=f, fill=GREY)
sz = 190
while anton(sz).getlength("CANCER DU SEIN") > 940: sz -= 4
big(d, [("CANCER DU SEIN", CORAL)], 0, y + 85, sz, center=True)
para(d, "avec les vrais chiffres, et leurs sources", pop(36), 0, y + 85 + int(sz * 1.3), 900, CREAM, center=True)
f = pop(30, "SemiBold"); t = "Glisse"; tx = 1080 - 150 - d.textlength(t, font=f)
d.text((tx, 1225), t, font=f, fill=CORAL); d.line([(1080-135, 1246), (1080-85, 1246)], fill=CORAL, width=5)
d.polygon([(1080-80, 1246), (1080-100, 1233), (1080-100, 1259)], fill=CORAL)
dots(d, 0, 1290); im.save(OUT + "c4_s1.png")

# ---- S2 survie
im, d = slide(CREAM)
big(d, [("1. ON SURVIT", NAVY), ("DE PLUS EN PLUS", CORAL)], 90, 110, 120)
f = pop(34, "SemiBold")
d.text((90, 470), "Diagnostiqué en 1989-1993", font=f, fill=DARK_SRC)
bar(d, 90, 520, 900, 110, .80, SAND if False else (190, 185, 175), SAND, "80 %", NAVY)
d.text((90, 690), "Diagnostiqué en 2010-2015", font=f, fill=NAVY)
bar(d, 90, 740, 900, 110, .88, CORAL, SAND, "88 %", CREAM)
para(d, "Survie nette à 5 ans après un cancer du sein, en France.", pop(40, "SemiBold"), 90, 930, 900, NAVY)
para(d, "8 points de plus en une génération.", pop(36), 90, 1060, 900, DARK_SRC)
source(d, "Source : Institut national du cancer (INCa)", 1200, DARK_SRC)
dots(d, 1, 1290, off=(200, 195, 185)); im.save(OUT + "c4_s2.png")

# ---- S3 mortalité
im, d = slide()
big(d, [("2. MOINS", CREAM), ("DE DÉCÈS", CORAL)], 90, 110, 130, lh=1.2)
f = pop(34, "SemiBold")
d.text((90, 520), "1990", font=f, fill=GREY)
bar(d, 90, 570, 900, 110, 1.0, (120, 135, 170), TRACK, "20,2", CREAM)
d.text((90, 740), "2018", font=f, fill=CREAM)
bar(d, 90, 790, 900, 110, 14.0 / 20.2, CORAL, TRACK, "14,0", CREAM)
para(d, "décès par an pour 100 000 femmes (taux standardisé sur l'âge)", pop(32), 90, 930, 900, CREAM)
para(d, "Environ 30 % de décès en moins.", pop(46, "SemiBold"), 90, 1040, 900, CREAM)
para(d, "La baisse continue : 1,5 % de moins par an (2019-2023).", pop(30), 90, 1112, 900, GREY)
source(d, "Sources : Santé publique France, INCa", 1200)
dots(d, 2, 1290); im.save(OUT + "c4_s3.png")

# ---- S4 précoce
im, d = slide(CREAM)
big(d, [("3. ON LE TROUVE", NAVY), ("PLUS TÔT", CORAL)], 90, 110, 130)
cols = [CORAL] * 6 + [NAVY] * 3 + [(190, 185, 175)]
R, gx, gy = 58, 185, 160
x0 = 540 - 2 * gx
for k, c in enumerate(cols):
    r_, c_ = divmod(k, 5)
    cx, cy = x0 + c_ * gx, 560 + r_ * gy
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=c)
y = 790
for c, t in ((CORAL, "6 sur 10 : stade précoce"), (NAVY, "3 sur 10 : stade intermédiaire"), ((190, 185, 175), "1 sur 10 : stade avancé")):
    d.ellipse([110, y + 6, 142, y + 38], fill=c); d.text((165, y), t, font=pop(36, "SemiBold"), fill=NAVY); y += 66
para(d, "Plus c'est précoce, plus les traitements peuvent être allégés.", pop(32), 90, y + 20, 900, DARK_SRC)
source(d, "Sources : Santé publique France, INCa", 1200, DARK_SRC)
dots(d, 3, 1290, off=(200, 195, 185)); im.save(OUT + "c4_s4.png")

# ---- S5 traitements plus légers
im, d = slide()
big(d, [("4. DES TRAITEMENTS", CREAM), ("PLUS LÉGERS", CORAL)], 90, 100, 110)
rows = [("RADIOTHÉRAPIE", "25 séances ➜ 5 séances", "Selon les patientes · essais START et FAST-Forward"),
        ("AISSELLE", "Parfois, plus besoin d'opérer les ganglions", "Certaines petites tumeurs · essai INSEMA, 5 502 patientes"),
        ("CHIMIOTHÉRAPIE", "Parfois, un test permet de s'en passer", "Certains cancers hormonodépendants · essai TAILORx")]
y = 400
for lab, main, sub in rows:
    d.rounded_rectangle([90, y, 990, y + 235], radius=32, fill=TRACK)
    d.text((130, y + 28), lab, font=pop(26, "SemiBold"), fill=CORAL)
    if "➜" in main:
        a, b = main.split(" ➜ "); fa = anton(78); xx = 130
        d.text((xx, y + 70), a, font=fa, fill=CREAM); xx += d.textlength(a, font=fa) + 28
        d.line([(xx, y + 118), (xx + 70, y + 118)], fill=CORAL, width=10); d.polygon([(xx + 92, y + 118), (xx + 66, y + 98), (xx + 66, y + 138)], fill=CORAL)
        xx += 120; d.text((xx, y + 70), b, font=fa, fill=CORAL)
    else:
        para(d, main, pop(40, "SemiBold"), 130, y + 70, 820, CREAM, lh=1.15)
    d.text((130, y + 183), sub, font=pop(22), fill=GREY)
    y += 265
source(d, "Sources : PubMed (Lancet 2008-2020, NEJM 2018 et 2025)", 1200)
dots(d, 4, 1290); im.save(OUT + "c4_s5.png")

# ---- S6 vivre après
im, d = slide(CREAM)
big(d, [("5. ON VIT", NAVY), ("APRÈS", CORAL)], 90, 110, 140)
big(d, [("913 089", CORAL)], 0, 540, 230, center=True)
para(d, "personnes vivent en France avec un antécédent de cancer du sein.", pop(44, "SemiBold"), 0, 840, 860, NAVY, center=True)
para(d, "Estimation 2017", pop(30), 0, 1020, 860, DARK_SRC, center=True)
source(d, "Source : Institut national du cancer (INCa)", 1200, DARK_SRC)
dots(d, 5, 1290, off=(200, 195, 185)); im.save(OUT + "c4_s6.png")

# ---- S7 la vérité complète
im, d = slide()
big(d, [("ET LA VÉRITÉ", CREAM), ("COMPLÈTE ?", CORAL)], 90, 110, 130)
y = para(d, "Ce n'est pas fini : environ 61 000 nouveaux cas par an en France (2023).", pop(42, "SemiBold"), 90, 480, 900, CREAM)
y = para(d, "Mais plus on le trouve tôt, mieux on le soigne.", pop(42, "SemiBold"), 90, y + 20, 900, CORAL)
d.rounded_rectangle([90, y + 60, 990, y + 400], radius=36, fill=TRACK)
d.text((140, y + 100), "LE DÉPISTAGE", font=pop(30, "SemiBold"), fill=CORAL)
para(d, "Une mammographie tous les 2 ans entre 50 et 74 ans, prise en charge à 100 %.", pop(40), 140, y + 155, 800, CREAM)
source(d, "Sources : INCa, Assurance Maladie", 1200)
dots(d, 6, 1290); im.save(OUT + "c4_s7.png")

# ---- S8 appel
im, d = slide(CREAM)
ribbon(d, 540, 260, 120, CORAL)
big(d, [("PARTAGE-LES,", NAVY), ("ENREGISTRE-LES", CORAL)], 0, 420, 120, center=True)
para(d, "Ces chiffres méritent d'être connus.", pop(42), 0, 780, 880, NAVY, center=True)
f = pop(34, "SemiBold"); t = "Abonne-toi pour la suite d'Octobre Rose"
d.text(((1080 - d.textlength(t, font=f)) / 2, 960), t, font=f, fill=CORAL)
source(d, "Sources : INCa, Santé publique France, PubMed", 1200, DARK_SRC)
dots(d, 7, 1290, off=(200, 195, 185)); im.save(OUT + "c4_s8.png")

th = [Image.open(OUT + f"c4_s{i}.png").resize((324, 405)) for i in range(1, 9)]
sheet = Image.new("RGB", (324 * 4, 405 * 2), (0, 0, 0))
for i, t in enumerate(th): sheet.paste(t, ((i % 4) * 324, (i // 4) * 405))
sheet.save(OUT + "_contact.png"); print("ok")
