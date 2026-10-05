"""Carrousel Doctorgane n°5 — « À Paris, moins d.1 femme sur 3 » (SpF 2026, ARS IDF)"""
import sys, math
sys.path.insert(0, "/home/claude/doctorgane/c3")
from PIL import Image, ImageDraw, ImageFont
F = "/home/claude/fonts/"
NAVY = (18, 33, 61); CREAM = (246, 241, 233); CORAL = (255, 111, 97)
GREY = (150, 160, 180); TRACK = (48, 68, 108); DARK_SRC = (110, 115, 130); SAND = (232, 224, 212)
OUT = "/home/claude/doctorgane/c5/"
N = 7

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


def bullets(d, items, y, fill, font, x=90, maxw=900, gap=26, dot=CORAL):
    for it in items:
        d.ellipse([x, y + 18, x + 20, y + 38], fill=dot)
        y = para(d, it, font, x + 45, y, maxw - 45, fill) + gap
    return y

def hbar(d, x, y, w, h, frac, fill, track, label, lab_col, name, name_col, name_font):
    d.text((x, y - name_font.size - 14), name, font=name_font, fill=name_col)
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=track)
    d.rounded_rectangle([x, y, x + max(h, int(w * frac)), y + h], radius=h // 2, fill=fill)
    f = anton(int(h * 0.6)); tw_ = d.textlength(label, font=f)
    bx = x + int(w * frac)
    if bx - tw_ - 28 > x + 10: d.text((bx - tw_ - 28, y + h * 0.17), label, font=f, fill=lab_col)
    else: d.text((bx + 22, y + h * 0.17), label, font=f, fill=fill)

def women(d, n, hi, x0, y, s, col_on, col_off, gap):
    """n silhouettes simples (tête + corps) ; les hi premières en couleur."""
    for k in range(n):
        c = col_on if k < hi else col_off
        x = x0 + k * (s + gap)
        d.ellipse([x + s*0.28, y, x + s*0.72, y + s*0.44], fill=c)
        d.rounded_rectangle([x + s*0.12, y + s*0.52, x + s*0.88, y + s*1.45], radius=int(s*0.3), fill=c)

# ---- S1 accroche
im, d = slide()
f = pop(30, "SemiBold"); t = "OCTOBRE ROSE  ·  FEMMES DE 50 À 74 ANS"
d.text(((1080 - d.textlength(t, font=f)) / 2, 110), t, font=f, fill=CORAL)
y = big(d, [("À PARIS,", CREAM), ("MOINS D'1", CORAL), ("FEMME SUR 3", CORAL)], 0, 175, 175, center=True)
women(d, 3, 1, 540 - (3*130 + 2*36)/2, y + 30, 130, CORAL, TRACK, 36)
para(d, "fait son dépistage organisé\ndu cancer du sein", pop(48, "SemiBold"), 0, y + 255, 980, CREAM, center=True, lh=1.2)
source(d, "Santé publique France, 2025", 1180, GREY, size=28)
dots(d, 0, 1290)
im.save(OUT + "c5_s1.png")

# ---- S2 les chiffres
im, d = slide(CREAM)
big(d, [("LE DÉPISTAGE", NAVY), ("ORGANISÉ EN 2025", CORAL)], 90, 100, 115)
nf = pop(40, "SemiBold"); X, Wb, Hb = 90, 900, 86
rows = [("Paris", 30.2, "30,2 %", CORAL), ("Île-de-France", 37.8, "37,8 %", NAVY), ("France", 47.5, "47,5 %", NAVY)]
y = 440
for name, v, lab, c in rows:
    hbar(d, X, y, Wb, Hb, v / 100, c, SAND, lab, CREAM, name, NAVY, nf); y += 185
# objectif
d.text((X, y - 54), "Objectif européen", font=nf, fill=DARK_SRC)
d.rounded_rectangle([X, y, X + Wb, y + Hb], radius=Hb // 2, outline=NAVY, width=5)
fo = anton(52); d.text((X + int(Wb*0.70) - d.textlength("70 %", font=fo) - 28, y + 15), "70 %", font=fo, fill=NAVY)
d.line([(X + int(Wb*0.70), y - 10), (X + int(Wb*0.70), y + Hb + 10)], fill=CORAL, width=6)
source(d, "Santé publique France (bulletin national, juillet 2026) · Taux sur les femmes de 50 à 74 ans", 1200, DARK_SRC)
dots(d, 1, 1290, off=(200, 195, 185))
im.save(OUT + "c5_s2.png")

# ---- S3 ça veut dire quoi
im, d = slide()
big(d, [("CE QUE ÇA", CREAM), ("VEUT DIRE", CORAL)], 90, 100, 130)
y = bullets(d, ["Ce chiffre compte seulement le programme organisé, celui de l'invitation par courrier.",
                "Certaines femmes se font dépister à côté, via leur gynéco ou leur radiologue. Ça n'est pas compté ici.",
                "Mais même avec ça, on reste loin des 70 % recommandés en Europe."], 420, CREAM, pop(40, "SemiBold"), gap=30)
source(d, "Santé publique France : part du dépistage hors programme estimée à 18 % en 2021-2022 (France)", 1200)
dots(d, 2, 1290)
im.save(OUT + "c5_s3.png")

# ---- S4 bonne nouvelle
im, d = slide(CREAM)
big(d, [("LA BONNE", NAVY), ("NOUVELLE", CORAL)], 90, 100, 130)
para(d, "Paris remonte.", pop(48, "SemiBold"), 90, 400, 900, NAVY)
fa = anton(118)
d.text((100, 500), "24,3 %", font=fa, fill=DARK_SRC)
d.text((120 + d.textlength("24,3 %", font=fa) + 40, 500), "➔", font=pop(120, "Bold"), fill=CORAL) if False else None
# flèche dessinée
ax = 100 + d.textlength("24,3 %", font=fa) + 40; ay = 575
d.line([(ax, ay), (ax + 90, ay)], fill=CORAL, width=12); d.polygon([(ax + 115, ay), (ax + 80, ay - 26), (ax + 80, ay + 26)], fill=CORAL)
d.text((ax + 140, 500), "30,2 %", font=fa, fill=CORAL)
d.text((100, 650), "2024", font=pop(36, "SemiBold"), fill=DARK_SRC)
d.text((ax + 140, 650), "2025", font=pop(36, "SemiBold"), fill=CORAL)
d.rounded_rectangle([90, 800, 990, 1090], radius=36, fill=NAVY)
para(d, "À côté, la Seine-et-Marne est à 46 %. Donc c'est possible, même en Île-de-France.", pop(40, "SemiBold"), 140, 850, 800, CREAM, lh=1.3)
source(d, "Santé publique France, bulletin national juillet 2026 (taux standardisés)", 1200, DARK_SRC)
dots(d, 3, 1290, off=(200, 195, 185))
im.save(OUT + "c5_s4.png")

# ---- S5 c'est quoi
im, d = slide()
big(d, [("LE DÉPISTAGE", CREAM), ("ORGANISÉ, C'EST :", CORAL)], 90, 100, 115)
y = bullets(d, ["De 50 à 74 ans, tous les 2 ans",
                "Une mammographie + un examen des seins",
                "Pris en charge à 100 %, sans avance de frais",
                "Chaque mammo normale est relue par un 2e radiologue",
                "L'invitation arrive par courrier ou sur ton compte ameli"], 400, CREAM, pop(40, "SemiBold"), gap=26)
source(d, "Institut national du cancer · Assurance Maladie", 1200)
dots(d, 4, 1290)
im.save(OUT + "c5_s5.png")

# ---- S6 pourquoi
im, d = slide(CREAM)
big(d, [("POURQUOI", NAVY), ("ÇA COMPTE", CORAL)], 90, 100, 130)
fa = anton(230); t = "- 23 %"
d.text(((1080 - d.textlength(t, font=fa)) / 2, 400), t, font=fa, fill=CORAL)
para(d, "de décès par cancer du sein chez les femmes invitées au dépistage, par rapport à celles qui ne le sont pas.", pop(42, "SemiBold"), 0, 680, 880, NAVY, center=True, lh=1.3)
para(d, "Et environ - 40 % chez celles qui y vont vraiment.", pop(40), 0, 930, 880, DARK_SRC, center=True, lh=1.3)
source(d, "Agence internationale de recherche sur le cancer, 2015 (femmes de 50 à 69 ans)", 1200, DARK_SRC)
dots(d, 5, 1290, off=(200, 195, 185))
im.save(OUT + "c5_s6.png")

# ---- S7 CTA
im, d = slide()
ribbon(d, 540, 250, 115, CORAL)
big(d, [("ENVOIE-LE", CREAM), ("À UNE PARISIENNE", CORAL), ("DE 50 À 74 ANS", CORAL)], 0, 400, 130, center=True)
para(d, "Sa prochaine invitation est peut-être déjà dans sa boîte aux lettres.", pop(40), 0, 860, 880, CREAM, center=True, lh=1.3)
f = pop(34, "SemiBold"); t = "Enregistre ce post pour en reparler"
d.text(((1080 - d.textlength(t, font=f)) / 2, 1060), t, font=f, fill=CORAL)
source(d, "Sources : Santé publique France, INCa, Assurance Maladie, IARC", 1200)
dots(d, 6, 1290)
im.save(OUT + "c5_s7.png")

th = [Image.open(OUT + f"c5_s{i}.png").resize((324, 405)) for i in range(1, 8)]
sheet = Image.new("RGB", (324 * 4, 405 * 2), (0, 0, 0))
for i, t in enumerate(th): sheet.paste(t, ((i % 4) * 324, (i // 4) * 405))
sheet.save(OUT + "_contact.png"); print("ok")