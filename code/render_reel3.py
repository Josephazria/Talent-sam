"""Reel Doctorgane n°3 — « Radiothérapie du sein : de 25 séances à 5 » (dessin au feutre, sans voix)
Usage: python3 render_reel3.py --preview 1.5,3.8,... | --out reel3.mp4 [--no-audio]
"""
import sys, argparse, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feutre import *

ap = argparse.ArgumentParser(); ap.add_argument("--out"); ap.add_argument("--preview"); ap.add_argument("--no-audio", action="store_true")
args = ap.parse_args()

def tw(text, size):
    f = ImageFont.truetype(CAVEAT, int(size * SS)); return f.getlength(text) / SS + 2 * max(1, int(size * SS * BOLDK)) / SS
def fit(text, size, maxw=900):
    while tw(text, size) > maxw and size > 30: size -= 2
    return size

def row(parts, cx, yb, size, t0, cps=22.0, gap=0.30, maxw=900):
    """Ligne multicolore centrée, taille ajustée à la largeur. Retourne (items, t_fin)."""
    sp0 = gap
    while True:
        ws = [tw(p, size) for p, _ in parts]; sp = size * sp0; total = sum(ws) + sp * (len(parts) - 1)
        if total <= maxw or size < 40: break
        size -= 2
    x = cx - total / 2; out = []; t = t0
    for (txt, col), w in zip(parts, ws):
        it = Text(txt, x, yb, size, col, t, cps=cps); out.append(it); t += it.dur; x += w + sp
    return out, t

def grid(rows, cols, x0, y0, cell, gap, t0, step, col_box=NAVY, col_chk=CORAL, seed=1):
    items = []; k = 0
    for r in range(rows):
        for c in range(cols):
            x = x0 + c * (cell + gap); y = y0 + r * (cell + gap); ts = t0 + k * step
            items.append(Stroke(rrect(x, y, cell, cell, 18), col_box, 7, ts, step * .85, seed=seed + k, amp=1.3, pen=False))
            items.append(Stroke(check(x + cell / 2, y + cell / 2 + 4, cell * .62), col_chk, 11, ts + step * .45, step * .55, snd="tick", seed=seed + 100 + k, amp=1.0, pen=False))
            k += 1
    return items

DAYS = ["L", "M", "M", "J", "V"]
def day_labels(x0, yb, cell, gap, t0, size=56):
    return [Text(d, x0 + i * (cell + gap) + cell / 2, yb, size, GREY, t0 + i * .06, dur=.2, anchor="c", pen=False) for i, d in enumerate(DAYS)]

def underline(text, size, cx, y, col, t0, dur, seed, maxw=900):
    s = fit(text, size, maxw); w = tw(text, s)
    return Stroke(wavy(cx - w / 2, cx + w / 2, y, 7, 3), col, 11, t0, dur, seed=seed)

# ============ SCÈNE 1 : accroche = compteur 25 -> 5 ============
it1 = []
t_, _ = row([("Radiothérapie du sein", NAVY)], 540, 330, 130, 0.0, cps=60); it1 += t_
NS, YBN = 820, 1050
vals = list(range(25, 4, -1)); T0, D, EXP = 0.45, 1.65, 1.7
times = [0.0] + [T0 + D * ((k / (len(vals) - 1)) ** EXP) for k in range(1, len(vals))]
TL = times[-1]
it1.append(Counter(540, YBN, NS, vals, times, [NAVY] * (len(vals) - 1) + [CORAL]))
it1.append(Mark(TL, "pop"))
wR = tw("5", NS)
it1.append(Stroke(ellipse(540, YBN - 282, 300, 335, 1.07, -120), CORAL, 13, TL + 0.12, 0.5, seed=3, pen=False))
it1.append(Text("séances", 540, 1285, 170, NAVY, TL + 0.2, dur=0.6, anchor="c"))
it1.append(underline("séances", 170, 540, 1323, CORAL, TL + 0.85, 0.35, 6))
it1.append(Text("pour certains cancers", 540, 1410, 72, GREY, TL + 1.0, dur=0.75, anchor="c"))
S1 = Scene(TL + 2.2, it1)

# ============ SCÈNE 1bis : c'est quoi ? (grand public) ============
itb = []
t_, _ = row([("La radiothérapie,", NAVY), ("c'est quoi ?", CORAL)], 540, 320, 120, 0.0, cps=26); itb += t_
itb.append(Stroke([(402, 585), (394, 800), (402, 1070)], NAVY, 11, 0.95, 0.35, seed=61, amp=1.2, pen=False))
breast = catmull([(402, 712), (470, 735), (555, 772), (632, 812), (684, 836), (708, 852), (690, 872), (652, 908), (600, 962), (528, 1002), (452, 1018), (402, 1014)], 12)
itb.append(Stroke(breast, NAVY, 11, 1.3, 0.7, seed=62, amp=1.4))
itb.append(Text("le sein", 560, 660, 62, NAVY, 1.95, dur=0.4, anchor="c", pen=False))
itb.append(Text("rayons", 870, 660, 62, CORAL, 2.0, dur=0.4, anchor="c", pen=False))
for k, (ys, ye) in enumerate(((735, 818), (885, 868), (1035, 925))):
    sh_, hd_ = arrow(985, ys, 610, ye, head=40, bend=-10 if k != 1 else 0)
    itb += [Stroke(sh_, CORAL, 14, 2.15 + k * 0.22, 0.3, seed=63 + k, amp=1.0, pen=False),
            Stroke(hd_, CORAL, 14, 2.42 + k * 0.22, 0.14, snd="tick", seed=70 + k, amp=.6, pen=False)]
itb.append(Text("Des rayons, visés avec précision", 540, 1190, 84, NAVY, 3.0, dur=0.8, anchor="c"))
itb.append(Text("sur le sein, après l'opération.", 540, 1285, 84, NAVY, 3.8, dur=0.75, anchor="c"))
itb.append(Text("Pour éviter que le cancer revienne.", 540, 1390, 84, CORAL, 4.6, dur=0.85, anchor="c"))
itb.append(Text("Chaque séance dure quelques minutes.", 540, 1480, 62, GREY, 5.55, dur=0.8, anchor="c", wght=400))
SB = Scene(7.0, itb)

# ============ SCÈNE 2 : avant = 5 semaines ============
it2 = []
t_, _ = row([("Avant :", NAVY), ("5 semaines", CORAL)], 540, 320, 140, 0.0, cps=24); it2 += t_
CELL, GAP = 116, 12; GW = 5 * CELL + 4 * GAP; X0 = 540 - GW / 2
it2 += day_labels(X0, 530, CELL, GAP, 0.8, size=64)
it2 += grid(5, 5, X0, 558, CELL, GAP, 1.0, 0.07, seed=10)
it2.append(Text("25 séances", 540, 1395, 205, CORAL, 2.85, dur=0.65, anchor="c"))
it2.append(Text("du lundi au vendredi", 540, 1485, 92, NAVY, 3.6, dur=0.75, anchor="c"))
S2 = Scene(5.4, it2)

# ============ SCÈNE 3 : puis 15 séances ============
it3 = []
t_, _ = row([("Puis :", NAVY), ("3 semaines", CORAL)], 540, 320, 140, 0.0, cps=24); it3 += t_
it3 += day_labels(X0, 520, CELL, GAP, 0.8, size=64)
it3 += grid(3, 5, X0, 548, CELL, GAP, 1.0, 0.08, seed=40)
it3.append(Text("15 séances", 540, 1125, 200, CORAL, 2.3, dur=0.6, anchor="c"))
it3.append(Text("Des rayons un peu plus forts,", 540, 1225, 88, NAVY, 3.0, dur=0.85, anchor="c"))
it3.append(Text("donc moins de séances", 540, 1312, 88, NAVY, 3.95, dur=0.7, anchor="c"))
it3.append(Text("même efficacité", 540, 1435, 135, NAVY, 4.75, dur=0.75, anchor="c"))
it3.append(underline("même efficacité", 135, 540, 1467, CORAL, 5.55, 0.4, 8))
it3.append(Text("Étude sur 2 215 femmes", 540, 1515, 56, GREY, 5.6, dur=0.8, anchor="c"))
S3 = Scene(6.85, it3)

# ============ SCÈNE 4 : aujourd'hui = 5 séances ============
it4 = []
t_, _ = row([("Aujourd'hui,", NAVY), ("parfois :", CORAL)], 540, 320, 140, 0.0, cps=22); it4 += t_
C4, G4 = 140, 22; GW4 = 5 * C4 + 4 * G4; X4 = 540 - GW4 / 2
it4 += day_labels(X4, 585, C4, G4, 0.8, size=68)
for i in range(5):
    x = X4 + i * (C4 + G4); ts = 0.9 + i * 0.38
    it4.append(Stroke(rrect(x, 610, C4, C4, 20), NAVY, 8, ts, 0.2, seed=70 + i, amp=1.3))
    it4.append(Stroke(check(x + C4 / 2, 610 + C4 / 2 + 4, C4 * .62), CORAL, 14, ts + 0.18, 0.2, snd="tick", seed=80 + i, amp=1.0))
it4.append(Text("5 séances", 540, 990, 240, CORAL, 2.9, dur=0.7, anchor="c"))
it4.append(Text("= 1 semaine", 540, 1140, 165, NAVY, 3.7, dur=0.75, anchor="c"))
wA = tw("aussi efficace", 135)
it4.append(Text("aussi efficace", 540, 1292, 135, NAVY, 4.5, dur=0.7, anchor="c"))
it4.append(Stroke(ellipse(540, 1264, wA / 2 + 55, 96, 1.07, -150), CORAL, 11, 5.25, 0.5, seed=9))
it4.append(Text("pour éviter que ça revienne", 540, 1405, 90, NAVY, 5.5, dur=0.85, anchor="c"))
it4.append(Text("Étude sur 4 096 femmes (2020)", 540, 1490, 56, GREY, 6.3, dur=0.75, anchor="c"))
S4 = Scene(7.45, it4)

# ============ SCÈNE 5 : nuance ============
it5 = []
it5.append(Text("Petite nuance :", 540, 470, 150, CORAL, 0.0, dur=0.75, anchor="c"))
it5.append(Text("Certains cancers : 5 séances.", 540, 650, 92, NAVY, 0.85, dur=1.0, anchor="c"))
it5.append(Text("D'autres : plus de séances.", 540, 775, 92, NAVY, 2.0, dur=0.95, anchor="c"))
it5.append(Text("C'est ton médecin qui choisit.", 540, 925, 92, CORAL, 3.15, dur=1.05, anchor="c"))
it5.append(underline("C'est ton médecin qui choisit.", 92, 540, 960, CORAL, 4.25, 0.35, 12))
S5 = Scene(6.2, it5)
cx, cy = 540, 1250
it5 += [Stroke(rrect(cx - 130, cy - 110, 260, 320, 24), NAVY, 9, 4.7, 0.4, seed=21, pen=False),
        Stroke(rrect(cx - 48, cy - 138, 96, 48, 12), NAVY, 9, 5.0, 0.2, seed=22, pen=False)]
for r_ in range(3):
    yy_ = cy - 20 + r_ * 85; ts = 5.15 + r_ * 0.17
    it5.append(Stroke(check(cx - 78, yy_ + 2, 44), CORAL, 10, ts, 0.16, snd="tick", seed=40 + r_, amp=.8, pen=False))
    it5.append(Stroke([(cx - 30, yy_), (cx + 88, yy_)], GREY, 8, ts + 0.05, 0.14, seed=36 + r_, pen=False))

# ============ SCÈNE 6 : appel ============
it6 = [Stroke(ribbon(540, 660, 175), CORAL, 18, 0.0, 1.2, seed=50, amp=1.2),
       Mark(1.2, "chime"),
       Text("Enregistre-le", 540, 1110, 175, NAVY, 1.25, dur=0.85, anchor="c"),
       Text("Prochain dessin :", 540, 1280, 100, GREY, 2.2, dur=0.8, anchor="c"),
       Text("la chimio", 540, 1420, 150, CORAL, 3.0, dur=0.6, anchor="c")]
S6 = Scene(4.0, it6, erase=0)

film = Film([S1, SB, S2, S3, S4, S5, S6])
print("durée", round(film.dur, 2), "s", film.nf, "images")
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
film.encode(args.out or "reel3.mp4", audio)
print("ok")
