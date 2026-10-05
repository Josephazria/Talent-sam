from PIL import Image, ImageDraw, ImageFont
import math, os, random

F = "/home/claude/fonts/"
NAVY = (18, 33, 61); CREAM = (246, 241, 233); CORAL = (255, 111, 97)
GREY = (150, 160, 180); TRACK = (48, 68, 108)
OUT = "/home/claude/doctorgane/c3/"

def anton(s): return ImageFont.truetype(F + "Anton-Regular.ttf", s)
def pop(s, w="Regular"): return ImageFont.truetype(F + f"Poppins-{w}.ttf", s)

def wrap(d, text, font, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split(" "):
            test = (cur + " " + w).strip()
            if d.textlength(test, font=font) <= maxw: cur = test
            else: lines.append(cur); cur = w
        lines.append(cur)
    return lines

def para(d, text, font, x, y, maxw, fill, lh=1.35, center=False, W=1080):
    for ln in wrap(d, text, font, maxw):
        tx = (W - d.textlength(ln, font=font)) / 2 if center else x
        d.text((tx, y), ln, font=font, fill=fill)
        y += int(font.size * lh)
    return y

def big(d, lines, x, y, size, W=1080, center=False, lh=1.08):
    f = anton(size)
    for t, c in lines:
        tx = (W - d.textlength(t, font=f)) / 2 if center else x
        d.text((tx, y), t, font=f, fill=c)
        y += int(size * lh)
    return y

def ribbon(d, cx, cy, s, col):
    w = int(s * 0.22)
    d.arc([cx - s*0.42, cy - s*0.95, cx + s*0.42, cy + s*0.1], 180, 360, fill=col, width=w)
    d.line([(cx - s*0.42, cy - s*0.42), (cx + s*0.35, cy + s*0.85)], fill=col, width=w)
    d.line([(cx + s*0.42, cy - s*0.42), (cx - s*0.35, cy + s*0.85)], fill=col, width=w)

def dots(d, n, i, y, W=1080, on=CORAL, off=(60, 75, 105)):
    x0 = W/2 - (n-1)*14
    for k in range(n):
        c = on if k == i else off
        d.ellipse([x0 + k*28 - 6, y - 6, x0 + k*28 + 6, y + 6], fill=c)

def source(d, text, y, col=GREY, W=1080):
    f = pop(24)
    d.text(((W - d.textlength(text, font=f)) / 2, y), text, font=f, fill=col)

N = 7
def slide(bg=NAVY):
    im = Image.new("RGB", (1080, 1350), bg); return im, ImageDraw.Draw(im)

def bullets(d, items, y, fill, font, x=90, maxw=900, gap=26, dot=CORAL):
    for it in items:
        d.ellipse([x, y + 18, x + 20, y + 38], fill=dot)
        y = para(d, it, font, x + 45, y, maxw - 45, fill) + gap
    return y

DARK_SRC = (110, 115, 130)

# ---- S1 hook
im, d = slide()
ribbon(d, 540, 250, 110, CORAL)
f = pop(30, "SemiBold"); t = "OCTOBRE ROSE  ·  CANCER DU SEIN"
d.text(((1080 - d.textlength(t, font=f)) / 2, 400), t, font=f, fill=CORAL)
big(d, [("CE N'EST PAS", CREAM), ("QU'UNE", CREAM), ("BOULE", CORAL)], 0, 480, 170, center=True)
para(d, "(les changements du sein à connaître)", pop(38), 0, 1090, 900, CREAM, center=True)
f = pop(30, "SemiBold"); t = "Glisse"
tx = 1080 - 150 - d.textlength(t, font=f)
d.text((tx, 1225), t, font=f, fill=CORAL)
d.line([(1080-135, 1246), (1080-85, 1246)], fill=CORAL, width=5)
d.polygon([(1080-80, 1246), (1080-100, 1233), (1080-100, 1259)], fill=CORAL)
dots(d, N, 0, 1290)
im.save(OUT + "c3_s1.png")

# ---- S2 la boule + réassurance
im, d = slide(CREAM)
big(d, [("D'ABORD,", NAVY), ("LA BOULE", CORAL)], 90, 120, 150)
y = para(d, "Le signe le plus connu : une masse palpable, souvent indolore, aux contours irréguliers.", pop(42), 90, 480, 900, NAVY)
# encart réassurance
d.rounded_rectangle([90, y + 50, 990, y + 470], radius=36, fill=NAVY)
d.text((140, y + 90), "À SAVOIR", font=pop(30, "SemiBold"), fill=CORAL)
para(d, "La grande majorité des boules dans le sein ne sont pas des cancers.", pop(46, "SemiBold"), 140, y + 150, 800, CREAM)
para(d, "Mais on la fait examiner.", pop(40, "SemiBold"), 140, y + 380, 800, CORAL)
source(d, "Sources : InfoCancer (Arcagy), Radiothérapie Hartmann", 1200, DARK_SRC)
dots(d, N, 1, 1290, off=(200, 195, 185))
im.save(OUT + "c3_s2.png")

# ---- S3 la peau
im, d = slide()
big(d, [("1. LA PEAU", CORAL)], 90, 110, 130)
# visuel : peau d'orange (points) + fossette
cx, cy, R = 540, 560, 215
d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=TRACK)
random.seed(4)
step = 26
for gy in range(-R, R + 1, step):
    for gx in range(-R, R + 1, step):
        px = cx + gx + (step / 2 if (gy // step) % 2 else 0) + random.uniform(-3, 3)
        py = cy + gy + random.uniform(-3, 3)
        if (px - cx) ** 2 + (py - cy) ** 2 < (R - 22) ** 2:
            d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(110, 130, 170))
# fossette (retrait)
fx, fy = cx + 70, cy - 40
for k, r in enumerate((62, 44, 26)):
    d.ellipse([fx - r, fy - r, fx + r, fy + r], outline=CORAL, width=5)
d.ellipse([fx - 7, fy - 7, fx + 7, fy + 7], fill=CORAL)
para(d, "Schéma illustratif", pop(24), 0, cy + R + 24, 900, GREY, center=True)
bullets(d, ["Aspect « peau d'orange »", "Fossette ou capiton", "Rougeur qui persiste"], 880, CREAM, pop(44, "SemiBold"))
source(d, "Source : Radiothérapie Hartmann", 1200)
dots(d, N, 2, 1290)
im.save(OUT + "c3_s3.png")

# ---- S4 le mamelon
im, d = slide(CREAM)
big(d, [("2. LE MAMELON", CORAL)], 90, 110, 130)
cx, cy, R = 540, 560, 210
d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(232, 224, 212), outline=NAVY, width=6)
d.ellipse([cx - 52, cy - 52, cx + 52, cy + 52], fill=CORAL)
d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(210, 80, 70))
for ang in range(0, 360, 60):
    a = math.radians(ang)
    sx, sy = cx + math.cos(a) * 165, cy + math.sin(a) * 165
    ex, ey = cx + math.cos(a) * 92, cy + math.sin(a) * 92
    d.line([(sx, sy), (ex, ey)], fill=NAVY, width=7)
    for da in (150, -150):
        b = a + math.radians(da)
        d.line([(ex, ey), (ex + math.cos(b) * 22, ey + math.sin(b) * 22)], fill=NAVY, width=7)
para(d, "Schéma illustratif", pop(24), 0, cy + R + 24, 900, DARK_SRC, center=True)
bullets(d, ["Qui rentre (rétraction)", "Écoulement sans allaitement", "Croûtes, plaques rouges, démangeaisons"], 880, NAVY, pop(42, "SemiBold"), gap=18)
source(d, "Source : Radiothérapie Hartmann", 1200, DARK_SRC)
dots(d, N, 3, 1290, off=(200, 195, 185))
im.save(OUT + "c3_s4.png")

# ---- S5 forme + aisselle
im, d = slide()
big(d, [("3. LA FORME", CORAL), ("ET L'AISSELLE", CREAM)], 90, 110, 130)
bullets(d, ["Un sein dont la taille ou la forme change",
            "Un ganglion dur sous le bras ou au-dessus de la clavicule",
            "Une douleur persistante dans un sein"], 520, CREAM, pop(46, "SemiBold"), gap=34)
d.rounded_rectangle([90, 1020, 990, 1150], radius=30, fill=TRACK)
para(d, "Un seul de ces signes ne veut pas dire cancer. Seul un examen permet de le dire.", pop(32, "SemiBold"), 125, 1038, 830, CREAM, lh=1.3)
source(d, "Sources : InfoCancer (Arcagy), Radiothérapie Hartmann", 1200)
dots(d, N, 4, 1290)
im.save(OUT + "c3_s5.png")

# ---- S6 que faire
im, d = slide(CREAM)
y = big(d, [("UN CHANGEMENT", NAVY), ("QUI PERSISTE ?", CORAL)], 90, 110, 130)
y = para(d, "Fais-le examiner par ton médecin, ta sage-femme ou ton gynécologue, dans les meilleurs délais.", pop(42, "SemiBold"), 90, y + 50, 900, NAVY)
d.rounded_rectangle([90, y + 40, 990, y + 380], radius=36, fill=NAVY)
d.text((140, y + 80), "ET LE DÉPISTAGE ?", font=pop(30, "SemiBold"), fill=CORAL)
para(d, "Il reste indispensable : une mammographie tous les 2 ans entre 50 et 74 ans, prise en charge à 100 %.", pop(38), 140, y + 135, 800, CREAM)
source(d, "Sources : InfoCancer (Arcagy), Assurance Maladie", 1200, DARK_SRC)
dots(d, N, 5, 1290, off=(200, 195, 185))
im.save(OUT + "c3_s6.png")

# ---- S7 CTA
im, d = slide()
ribbon(d, 540, 260, 120, CORAL)
big(d, [("ENVOIE-LE", CREAM), ("À QUELQU'UN", CORAL)], 0, 420, 150, center=True)
y = para(d, "Qui a une mammo à faire, ou qui n'a jamais regardé ces signes.", pop(42), 0, 800, 880, CREAM, center=True)
f = pop(34, "SemiBold"); t = "Enregistre ce post pour plus tard"
d.text(((1080 - d.textlength(t, font=f)) / 2, 1060), t, font=f, fill=CORAL)
source(d, "Sources : InfoCancer (Arcagy), Radiothérapie Hartmann, Assurance Maladie", 1200)
dots(d, N, 6, 1290)
im.save(OUT + "c3_s7.png")

# planche
th = [Image.open(OUT + f"c3_s{i}.png").resize((324, 405)) for i in range(1, 8)]
sheet = Image.new("RGB", (324 * 4, 405 * 2), (0, 0, 0))
for i, t in enumerate(th): sheet.paste(t, ((i % 4) * 324, (i // 4) * 405))
sheet.save(OUT + "_contact.png")
print("ok")
