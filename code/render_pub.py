from PIL import Image, ImageDraw, ImageFont
import math
F = "/home/claude/fonts/"
NAVY = (18, 33, 61); CREAM = (246, 241, 233); CORAL = (255, 111, 97); GREY = (150, 160, 180); SAND = (232, 224, 212); DARK = (110, 115, 130)
W, H = 1080, 1920
def anton(s): return ImageFont.truetype(F + "Anton-Regular.ttf", s)
def pop(s, w="Regular"): return ImageFont.truetype(F + f"Poppins-{w}.ttf", s)
def ctext(d, t, y, f, col, cx=540): d.text((cx - d.textlength(t, font=f) / 2, y), t, font=f, fill=col)
def star(d, cx, cy, r1, r2, n, col, rot=0):
    pts = []
    for k in range(2 * n):
        r = r1 if k % 2 == 0 else r2; a = math.radians(rot + k * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=col)
def rot_text(im, t, f, col, cx, cy, ang):
    tw = int(f.getlength(t)) + 40; th = f.size + 40
    lay = Image.new("RGBA", (tw, th), (0, 0, 0, 0)); ImageDraw.Draw(lay).text((20, 10), t, font=f, fill=col)
    lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC)
    im.paste(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)), lay)
def stamp(im, t, cx, cy, ang, col=CORAL, size=54):
    f = pop(size, "Bold"); tw = int(f.getlength(t)) + 70; th = size + 50
    lay = Image.new("RGBA", (tw, th), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
    dd.rounded_rectangle([4, 4, tw - 4, th - 4], radius=18, outline=col, width=8)
    dd.text((35, 20), t, font=f, fill=col)
    lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC)
    im.paste(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)), lay)

# ---------- Story 1 : la pub
im = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(im)
# bandeau haut
d.rectangle([0, 0, W, 300], fill=NAVY)
ctext(d, "OFFRE SPÉCIALE OCTOBRE", 215, pop(34, "SemiBold"), CORAL)
# starburst NOUVEAU
star(d, 540, 520, 230, 190, 14, CORAL)
ctext(d, "NOUVEAU", 455, anton(120), CREAM)
# la boîte produit
bx, by, bw, bh = 300, 760, 480, 400
d.rounded_rectangle([bx + 18, by + 22, bx + bw + 18, by + bh + 22], radius=30, fill=SAND)
d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=30, fill=NAVY)
d.rounded_rectangle([bx + 30, by + 30, bx + bw - 30, by + 130], radius=16, fill=CORAL)
ctext(d, "?", by + 150, anton(230), CREAM)
# accroche
ctext(d, "RÉDUIT LES DÉCÈS", 1215, anton(92), NAVY)
ctext(d, "PAR CANCER DU SEIN", 1310, anton(92), NAVY)
ctext(d, "DE 23 %*", 1405, anton(120), CORAL)
# arguments
f = pop(40, "SemiBold"); y = 1565
for t in ["Prix : 0 €", "Sans ordonnance", "Livré dans ta boîte aux lettres"]:
    tw_ = d.textlength(t, font=f); x0 = 540 - (tw_ + 60) / 2
    d.line([(x0, y + 30), (x0 + 16, y + 46), (x0 + 44, y + 12)], fill=CORAL, width=9, joint="curve")
    d.text((x0 + 60, y), t, font=f, fill=NAVY); y += 60
ctext(d, "*Agence internationale de recherche sur le cancer, 2015, femmes de 50 à 69 ans invitées", 1770, pop(21), DARK)
stamp(im, "0 €", 880, 860, -18, CORAL, 70)
ctext(d, "@doctorgane", 1835, pop(28, "SemiBold"), GREY)
im.save("story_pub_1.png")

# ---------- Story 2 : la révélation
im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
ctext(d, "LE PRODUIT MIRACLE,", 330, anton(96), CREAM)
ctext(d, "C'EST…", 430, anton(96), CREAM)
ctext(d, "LA MAMMO", 580, anton(150), CORAL)
ctext(d, "DU DÉPISTAGE", 735, anton(150), CORAL)
# enveloppe
ex, ey, ew, eh = 290, 980, 500, 320
d.rounded_rectangle([ex, ey, ex + ew, ey + eh], radius=22, fill=CREAM)
d.polygon([(ex, ey), (ex + ew / 2, ey + eh * 0.58), (ex + ew, ey)], fill=SAND, outline=NAVY, width=0)
d.line([(ex, ey), (ex + ew / 2, ey + eh * 0.58), (ex + ew, ey)], fill=NAVY, width=10)
d.rounded_rectangle([ex + ew - 150, ey + 30, ex + ew - 40, ey + 130], radius=10, fill=CORAL)
ctext(d, "🎀", ey + 40, pop(60), CREAM, ex + ew - 95) if False else None
f = pop(42, "SemiBold"); y = 1370
for t in ["De 50 à 74 ans, tous les 2 ans", "Pris en charge à 100 %", "L'invitation arrive par courrier", "Et ça dure 15 minutes"]:
    ctext(d, t, y, f, CREAM); y += 64
ctext(d, "Envoie ça à celle qui a laissé la lettre sur le frigo.", 1680, pop(34), CORAL)
ctext(d, "@doctorgane", 1835, pop(28, "SemiBold"), GREY)
im.save("story_pub_2.png")

a = Image.open("story_pub_1.png").resize((405, 720)); b = Image.open("story_pub_2.png").resize((405, 720))
s = Image.new("RGB", (830, 720), (0, 0, 0)); s.paste(a, (0, 0)); s.paste(b, (425, 0)); s.save("_pub.png"); print("ok")
