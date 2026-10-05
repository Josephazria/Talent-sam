"""Reel Doctorgane n°5 — « Vrai ou faux » (dessin au feutre, sans voix)
Usage: python3 render_reel4.py --preview t1,t2,... | --out reel4.mp4 [--no-audio]
"""
import sys, argparse, os
sys.path.insert(0, "/home/claude/doctorgane/reel3")
from feutre import *

ap = argparse.ArgumentParser(); ap.add_argument("--out"); ap.add_argument("--preview"); ap.add_argument("--no-audio", action="store_true")
args = ap.parse_args()

def tw(text, size):
    f = ImageFont.truetype(CAVEAT, int(size * SS)); return f.getlength(text) / SS + 2 * max(1, int(size * SS * BOLDK)) / SS
def fit(text, size, maxw=900):
    while tw(text, size) > maxw and size > 30: size -= 2
    return size
def row(parts, cx, yb, size, t0, cps=22.0, gap=0.30, maxw=900):
    sp0 = gap
    while True:
        ws = [tw(p, size) for p, _ in parts]; sp = size * sp0; total = sum(ws) + sp * (len(parts) - 1)
        if total <= maxw or size < 40: break
        size -= 2
    x = cx - total / 2; out = []; t = t0
    for (txt, col), w in zip(parts, ws):
        it = Text(txt, x, yb, size, col, t, cps=cps); out.append(it); t += it.dur; x += w + sp
    return out, t
def underline(text, size, cx, y, col, t0, dur, seed, maxw=900):
    s = fit(text, size, maxw); w = tw(text, s)
    return Stroke(wavy(cx - w / 2, cx + w / 2, y, 7, 3), col, 11, t0, dur, seed=seed)
def scribble(cx, cy, r, col, t0, dur, w=9, seed=0, n=7):
    pts = []
    for j in range(n):
        dy = -r * .82 + j * (2 * r * .82 / (n - 1)); dx = math.sqrt(max(r * r - dy * dy, 1)) * .85
        pts += [(cx - dx, cy + dy), (cx + dx, cy + dy)] if j % 2 == 0 else [(cx + dx, cy + dy), (cx - dx, cy + dy)]
    return Stroke(pts, col, w, t0, dur, seed=seed, amp=.8, pen=False)


def stamp_box(cx, cy, w, h, ang, t0, dur, seed):
    a = math.radians(ang); pts = [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2),(-w/2,-h/2+8)]
    pts = [(cx + x*math.cos(a) - y*math.sin(a), cy + x*math.sin(a) + y*math.cos(a)) for x, y in pts]
    return Stroke(pts, CORAL, 12, t0, dur, seed=seed, amp=1.5, pen=False)

def item(n, l1, l2, line1, line2, tag="FAUX"):
    it = []
    it.append(Text(f"{n}/5", 540, 250, 80, GREY, 0.0, dur=0.25, anchor="c", pen=False))
    it.append(Text(l1, 540, 520, 118, NAVY, 0.2, dur=0.55, anchor="c"))
    it.append(Text(l2, 540, 650, 118, NAVY, 0.7, dur=0.65, anchor="c"))
    it.append(Text(tag, 540, 1030, 250, CORAL, 1.45, dur=0.35, anchor="c", rot=-6, pen=False))
    it.append(Mark(1.45, "pop"))
    it.append(stamp_box(540, 940, 640, 290, -6, 1.7, 0.4, 20 + n))
    it.append(Text(line1, 540, 1280, 92, NAVY, 2.2, dur=0.8, anchor="c"))
    if line2: it.append(Text(line2, 540, 1385, 76, GREY, 3.0, dur=0.7, anchor="c", wght=400))
    return Scene(4.3 if line2 else 3.9, it)

h = []
h.append(Text("Cancer du sein :", 540, 640, 130, NAVY, 0.0, dur=0.6, anchor="c"))
h.append(Text("vrai ou faux ?", 540, 800, 150, CORAL, 0.6, dur=0.7, anchor="c"))
h.append(underline("vrai ou faux ?", 150, 540, 840, CORAL, 1.35, 0.35, 5))
h.append(Text("5 idées reçues", 540, 1030, 90, GREY, 1.75, dur=0.7, anchor="c"))
S0 = Scene(3.0, h)

S1 = item(1, "Le déodorant", "donne un cancer du sein", "Aucune preuve d'un lien.", None)
S2 = item(2, "Le soutien-gorge à armatures", "donne un cancer du sein", "Aucun lien trouvé.", None)
S3 = item(3, "Une boule dans le sein", "= forcément un cancer", "Mais on la fait examiner.", None)
S4 = item(4, "Ça n'arrive qu'après", "50 ans", "Près de 80 % après 50 ans…", "mais pas seulement.")
S5 = item(5, "Personne dans ma famille", "= aucun risque", "Seuls 5 à 10 % sont héréditaires.", "On peut donc l'avoir sans antécédent.")

c = [Stroke(ribbon(540, 620, 160), CORAL, 18, 0.0, 1.0, seed=50, amp=1.2), Mark(1.0, "chime"),
     Text("Les 5 étaient faux", 540, 1050, 120, NAVY, 1.05, dur=0.9, anchor="c"),
     Text("Partage-le", 540, 1230, 150, CORAL, 2.0, dur=0.7, anchor="c"),
     Text("Enregistre-le pour ne plus y croire", 540, 1350, 66, GREY, 2.7, dur=0.8, anchor="c", wght=400)]
S6 = Scene(4.0, c, erase=0)

film = Film([S0, S1, S2, S3, S4, S5, S6])
print("durée", round(film.dur, 2), "s", film.nf, "images", [round(b, 2) for b in film.bounds])
if args.preview:
    os.makedirs("prev", exist_ok=True)
    import glob
    for f_ in glob.glob("prev/p_*.png"): os.remove(f_)
    for tt in [float(x) for x in args.preview.split(",")]:
        film.frame(tt).save(f"prev/p_{tt:05.2f}.png")
    sys.exit()
audio = None
if not args.no_audio:
    audio = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sound.wav"); film.make_audio(audio)
film.encode(args.out or "reel5.mp4", audio)
print("ok")
