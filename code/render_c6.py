"""Carrousel Doctorgane n°6 — « 5 phrases à ne pas dire à quelqu'un qui a un cancer »"""
import sys, math
sys.path.insert(0, "/home/claude/doctorgane/c3")
from PIL import Image, ImageDraw, ImageFont
F = "/home/claude/fonts/"
NAVY = (18, 33, 61); CREAM = (246, 241, 233); CORAL = (255, 111, 97)
GREY = (150, 160, 180); TRACK = (48, 68, 108); DARK_SRC = (110, 115, 130); SAND = (232, 224, 212)
OUT = "/home/claude/doctorgane/c6/"
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


def bullets(d, items, y, fill, font, x=90, maxw=900, gap=26, dot=CORAL):
    for it in items:
        d.ellipse([x, y + 18, x + 20, y + 38], fill=dot)
        y = para(d, it, font, x + 45, y, maxw - 45, fill) + gap
    return y
def pop_m(s): return ImageFont.truetype(F + "Poppins-Medium.ttf", s)
def cross(d, x, y, s, col=CORAL, w=10):
    d.line([(x - s, y - s), (x + s, y + s)], fill=col, width=w); d.line([(x + s, y - s), (x - s, y + s)], fill=col, width=w)
def tick(d, x, y, s, col=(92, 214, 140), w=10):
    d.line([(x - s, y), (x - s * 0.3, y + s * 0.7), (x + s, y - s * 0.7)], fill=col, width=w, joint="curve")

def slide_pair(i, n, bad, good, why):
    im, d = slide(NAVY)
    d.text((90, 95), f"{n}/5", font=pop(40, "SemiBold"), fill=CORAL)
    cross(d, 125, 310, 28)
    d.text((190, 215), "NE DIS PAS", font=pop(32, "SemiBold"), fill=GREY)
    para(d, f"« {bad} »", pop_m(74), 190, 258, 800, CREAM, lh=1.2)
    tick(d, 125, 700, 28)
    d.text((190, 605), "DIS PLUTÔT", font=pop(32, "SemiBold"), fill=(92, 214, 140))
    para(d, f"« {good} »", pop_m(74), 190, 648, 800, CREAM, lh=1.2)
    d.rounded_rectangle([90, 985, 990, 1180], radius=30, fill=TRACK)
    para(d, why, pop(36), 125, 1012, 830, CREAM, lh=1.3)
    dots(d, i, 1290)
    im.save(OUT + f"c6_s{i + 1}.png")

im, d = slide(NAVY)
f = pop(30, "SemiBold"); t = "À LIRE AVANT DE PARLER À UN PROCHE MALADE"
d.text(((1080 - d.textlength(t, font=f)) / 2, 150), t, font=f, fill=CORAL)
big(d, [("LES 5 PHRASES", CREAM), ("À NE PAS DIRE", CREAM), ("À QUELQU'UN", CREAM), ("QUI A UN", CREAM), ("CANCER", CORAL)], 0, 250, 150, center=True)
para(d, "(et quoi dire à la place)", pop(44), 0, 1120, 900, GREY, center=True)
dots(d, 0, 1290)
im.save(OUT + "c6_s1.png")

slide_pair(1, 1, "Tu vas t'en sortir, t'es forte.", "Je suis là, quoi qu'il arrive.", "« Forte » devient une obligation. Le jour où elle n'en peut plus, elle se tait pour ne pas décevoir.")
slide_pair(2, 2, "Ma tante a eu la même chose…", "Raconte-moi comment tu le vis, toi.", "Chaque cancer est différent. Elle n'a pas besoin de l'histoire de ta tante, elle a besoin qu'on écoute la sienne.")
slide_pair(3, 3, "Il faut rester positive.", "Tu as le droit d'avoir peur. Je reste.", "La positivité obligatoire isole. On n'a pas besoin d'être joyeuse pour bien se soigner.")
slide_pair(4, 4, "Dis-moi si tu as besoin de quelque chose.", "Je viens te chercher mardi pour ta séance.", "Demander, c'est fatigant. Proposer quelque chose de précis, c'est un vrai cadeau.")
slide_pair(5, 5, "Tu as l'air en forme !", "Comment tu te sens, vraiment, aujourd'hui ?", "Avoir l'air en forme et aller bien, ce n'est pas pareil. Laisse-lui la place de répondre autre chose que « ça va ».")

im, d = slide(CREAM)
big(d, [("CE QUE MES", NAVY), ("PATIENTES", NAVY), ("ME DISENT", CORAL)], 90, 110, 130)
d.rounded_rectangle([90, 560, 990, 1000], radius=36, fill=NAVY)
para(d, "« Je ne veux pas qu'on me parle autrement. Je veux juste qu'on reste. »", pop_m(54), 140, 620, 800, CREAM, lh=1.3)
para(d, "Pas besoin de trouver les mots parfaits. Être là suffit.", pop(40), 90, 1060, 900, DARK_SRC, lh=1.3)
dots(d, 6, 1290, off=(200, 195, 185))
im.save(OUT + "c6_s7.png")

im, d = slide(NAVY)
ribbon(d, 540, 250, 115, CORAL)
big(d, [("ENVOIE-LE", CREAM), ("À QUELQU'UN QUI", CORAL), ("NE SAIT PAS", CORAL), ("QUOI DIRE.", CORAL)], 0, 400, 130, center=True)
f = pop(34, "SemiBold"); t = "Et enregistre-le, tu en auras besoin un jour."
d.text(((1080 - d.textlength(t, font=f)) / 2, 1060), t, font=f, fill=CREAM)
source(d, "Doctorgane · médecin cancérologue · d'après ce que mes patientes me disent", 1200)
dots(d, 7, 1290)
im.save(OUT + "c6_s8.png")

th = [Image.open(OUT + f"c6_s{i}.png").resize((324, 405)) for i in range(1, 9)]
sheet = Image.new("RGB", (324 * 4, 405 * 2), (0, 0, 0))
for i, t in enumerate(th): sheet.paste(t, ((i % 4) * 324, (i // 4) * 405))
sheet.save(OUT + "_contact.png"); print("ok")
