"""Reel Doctorgane n°4 — « Cancer du sein : et les hommes ? » (dessin au feutre, sans voix)
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

# ============ SCÈNE 1 : accroche = 100 ronds, 1 seul est un homme ============
it1 = []
it1.append(Text("Cancer du sein :", 540, 285, 120, NAVY, 0.0, dur=0.5, anchor="c"))
it1.append(Text("et les hommes ?", 540, 410, 125, CORAL, 0.45, dur=0.65, anchor="c"))
R_, SP = 26, 78; GX0 = 540 - 4.5 * SP; GY0 = 520
SPEC = (3, 6); k = 0
for r in range(10):
    for c in range(10):
        if (r, c) == SPEC: continue
        it1.append(Stroke(ellipse(GX0 + c * SP, GY0 + r * SP, R_, R_, 1.06, -90 + (k * 53) % 360), NAVY, 5, 0.8 + k * 0.010, 0.09, snd=None, seed=200 + k, amp=.9, pen=False)); k += 1
mk = Mark(0.8, "none"); mk.ticks = [0.9 + j * 0.07 for j in range(15)]; it1.append(mk)
sx, sy = GX0 + SPEC[1] * SP, GY0 + SPEC[0] * SP
it1.append(Stroke(ellipse(sx, sy, R_, R_, 1.05, -60), CORAL, 8, 1.95, 0.25, snd="scratch", seed=7, pen=False))
it1.append(scribble(sx, sy, R_, CORAL, 2.2, 0.28, w=9, seed=3))
it1.append(Mark(2.2, "pop"))
it1.append(Stroke(ellipse(sx, sy, 58, 58, 1.07, -140), CORAL, 9, 2.5, 0.42, seed=8))
it1.append(Text("Environ 1 cas sur 100", 540, 1360, 122, CORAL, 2.95, dur=0.9, anchor="c"))
it1.append(Text("concerne un homme", 540, 1462, 98, NAVY, 3.9, dur=0.75, anchor="c"))
it1.append(Text("D'après l'Institut national du cancer", 540, 1512, 42, GREY, 4.7, dur=0.7, anchor="c", wght=400))
S1 = Scene(5.7, it1)

# ============ SCÈNE 2 : les signes ============
it2 = []
t_, _ = row([("Les signes", NAVY), ("à connaître", CORAL)], 540, 300, 118, 0.0, cps=24); it2 += t_
K_ = 1.35
def P(u, v): return (330 + u * K_, 690 + v * K_)
it2.append(Stroke([P(0, -230), P(-8, -40), P(0, 160)], NAVY, 11, 0.9, 0.3, seed=61, amp=1.2, pen=False))
cont = catmull([P(0, -90), P(40, -80), P(80, -62), P(108, -42), P(121, -29), P(131, -28), P(141, -20), P(141, -6), P(131, 2), P(118, 5), P(95, 22), P(55, 40), P(0, 50)], 12)
it2.append(Stroke(cont, NAVY, 11, 1.2, 0.6, seed=62, amp=1.3))
bx, by = P(56, -12); br = 24 * K_
it2.append(Stroke(ellipse(bx, by, br, br, 1.05, -50), CORAL, 9, 1.85, 0.28, seed=63, pen=False))
it2.append(scribble(bx, by, br, CORAL, 2.15, 0.28, w=9, seed=4))
it2.append(Mark(2.15, "pop"))
it2.append(Text("une boule", 830, 565, 90, CORAL, 2.45, dur=0.45, anchor="c", pen=False))
sh_, hd_ = arrow(690, 575, bx + br + 8, by - 18, head=36, bend=-8)
it2 += [Stroke(sh_, CORAL, 10, 2.75, 0.28, seed=64, amp=1.0, pen=False), Stroke(hd_, CORAL, 10, 3.01, 0.14, snd="tick", seed=65, amp=.6, pen=False)]
it2.append(Text("mamelon", 835, 805, 90, NAVY, 3.25, dur=0.45, anchor="c", pen=False))
nx_, ny_ = P(143, -12)
sh_, hd_ = arrow(668, 782, nx_ + 14, ny_ + 18, head=34, bend=10)
it2 += [Stroke(sh_, NAVY, 9, 3.55, 0.28, seed=66, amp=1.0, pen=False), Stroke(hd_, NAVY, 9, 3.81, 0.14, snd="tick", seed=67, amp=.6, pen=False)]
XT = 225
it2.append(Stroke(check(140, 1085, 72), CORAL, 14, 4.05, 0.2, snd="tick", seed=70, amp=1.0, pen=False))
it2.append(Text("Une boule, souvent", XT, 1070, 84, NAVY, 4.1, dur=0.5, maxw=780))
it2.append(Text("juste derrière le mamelon", XT, 1160, 84, NAVY, 4.6, dur=0.65, maxw=780))
it2.append(Stroke(check(140, 1350, 72), CORAL, 14, 5.4, 0.2, snd="tick", seed=71, amp=1.0, pen=False))
it2.append(Text("Un mamelon qui rentre", XT, 1335, 84, NAVY, 5.45, dur=0.55, maxw=780))
it2.append(Text("ou qui a une plaie", XT, 1425, 84, NAVY, 6.0, dur=0.5, maxw=780))
it2.append(Text("Comme chez la femme.", 540, 1505, 58, GREY, 6.6, dur=0.6, anchor="c", wght=400))
S2 = Scene(7.5, it2)

# ============ SCÈNE 3 : le piège ============
it3 = []
it3.append(Text("Le piège :", 540, 340, 140, CORAL, 0.0, dur=0.5, anchor="c"))
it3.append(Text("chez l'homme,", 540, 500, 108, NAVY, 0.55, dur=0.6, anchor="c"))
it3.append(Text("on n'y pense presque pas.", 540, 625, 100, NAVY, 1.15, dur=0.9, anchor="c"))
it3.append(Text("Résultat :", 540, 830, 88, GREY, 2.15, dur=0.4, anchor="c"))
it3.append(Text("souvent découvert plus tard.", 540, 950, 104, CORAL, 2.55, dur=0.95, anchor="c"))
it3.append(underline("souvent découvert plus tard.", 104, 540, 985, CORAL, 3.5, 0.3, 11))
cx3, cy3 = 540, 1270
it3.append(Stroke(ellipse(cx3, cy3, 140, 140, 1.04, -100), NAVY, 11, 3.7, 0.45, seed=31))
it3.append(Stroke([(cx3, cy3), (cx3, cy3 - 92)], NAVY, 11, 4.15, 0.16, seed=32, pen=False))
it3.append(Stroke([(cx3, cy3), (cx3 + 68, cy3 + 38)], CORAL, 12, 4.3, 0.18, snd="tick", seed=33, pen=False))
S3 = Scene(5.2, it3)

# ============ SCÈNE 4 : un doute -> avis médical ; traitements proches ============
it4 = []
it4.append(Text("Un doute ?", 540, 330, 140, CORAL, 0.0, dur=0.5, anchor="c"))
it4.append(Text("Un avis médical", 540, 480, 108, NAVY, 0.55, dur=0.7, anchor="c"))
it4.append(Text("et on est fixé.", 540, 595, 108, NAVY, 1.3, dur=0.7, anchor="c"))
it4.append(Text("Et si c'est un cancer :", 540, 810, 86, GREY, 2.2, dur=0.7, anchor="c"))
it4.append(Text("traitements proches", 540, 940, 112, NAVY, 2.95, dur=0.8, anchor="c"))
it4.append(Text("de ceux des femmes.", 540, 1060, 112, CORAL, 3.8, dur=0.8, anchor="c"))
it4.append(underline("de ceux des femmes.", 112, 540, 1094, CORAL, 4.65, 0.3, 12))
it4.append(Text("Chirurgie, radiothérapie,", 540, 1260, 68, GREY, 4.95, dur=0.7, anchor="c", wght=400))
it4.append(Text("chimio, hormonothérapie…", 540, 1345, 68, GREY, 5.65, dur=0.7, anchor="c", wght=400))
it4.append(Text("selon chaque situation", 540, 1430, 68, GREY, 6.35, dur=0.7, anchor="c", wght=400))
S4 = Scene(7.4, it4)

# ============ SCÈNE 5 : la famille ============
it5 = []
it5.append(Text("Dans la famille ?", 540, 340, 128, CORAL, 0.0, dur=0.7, anchor="c"))
it5.append(Text("Un cancer du sein", 540, 500, 100, NAVY, 0.75, dur=0.65, anchor="c"))
it5.append(Text("chez un homme proche ?", 540, 615, 100, NAVY, 1.45, dur=0.8, anchor="c"))
it5.append(Text("Dis-le à ton médecin.", 540, 800, 112, CORAL, 2.4, dur=0.85, anchor="c"))
it5.append(underline("Dis-le à ton médecin.", 112, 540, 834, CORAL, 3.3, 0.3, 13))
it5.append(Text("C'est une info utile.", 540, 930, 70, GREY, 3.55, dur=0.6, anchor="c", wght=400))
tx_, ty_ = 540, 1120
kids = [(400, 1330, NAVY), (680, 1330, CORAL)]
it5.append(Stroke(ellipse(tx_, ty_, 40, 40, 1.05, -80), GREY, 9, 3.9, 0.28, seed=41, pen=False))
for i, (kx, ky, kc) in enumerate(kids):
    it5.append(Stroke([(tx_ - 12 + 24 * i, ty_ + 40), (kx + (30 if i == 0 else -30), ky - 38)], GREY, 8, 4.2 + i * 0.18, 0.18, seed=42 + i, pen=False))
    it5.append(Stroke(ellipse(kx, ky, 40, 40, 1.05, -80 + 30 * i), kc, 9, 4.4 + i * 0.22, 0.28, snd="scratch", seed=45 + i, pen=False))
S5 = Scene(5.5, it5)

# ============ SCÈNE 6 : appel ============
it6 = [Stroke(ribbon(540, 640, 170), CORAL, 18, 0.0, 1.1, seed=50, amp=1.2),
       Mark(1.1, "chime"),
       Text("Partage-le", 540, 1090, 175, NAVY, 1.15, dur=0.8, anchor="c"),
       Text("ça peut servir à un proche", 540, 1210, 78, GREY, 2.0, dur=0.8, anchor="c"),
       Text("Prochain dessin :", 540, 1350, 90, GREY, 2.9, dur=0.6, anchor="c"),
       Text("la chimio", 540, 1480, 140, CORAL, 3.55, dur=0.55, anchor="c")]
S6 = Scene(4.6, it6, erase=0)

film = Film([S1, S2, S3, S4, S5, S6])
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
film.encode(args.out or "reel4.mp4", audio)
print("ok")
