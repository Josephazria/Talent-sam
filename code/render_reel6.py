"""Reel Doctorgane n°6 — « Pourquoi les éléphants n'ont presque jamais de cancer » (feutre, sans voix)"""
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
def underline(text, size, cx, y, col, t0, dur, seed, maxw=900):
    s = fit(text, size, maxw); w = tw(text, s)
    return Stroke(wavy(cx - w / 2, cx + w / 2, y, 7, 3), col, 11, t0, dur, seed=seed)
def scribble(cx, cy, r, col, t0, dur, w=9, seed=0, n=7):
    pts = []
    for j in range(n):
        dy = -r * .82 + j * (2 * r * .82 / (n - 1)); dx = math.sqrt(max(r * r - dy * dy, 1)) * .85
        pts += [(cx - dx, cy + dy), (cx + dx, cy + dy)] if j % 2 == 0 else [(cx + dx, cy + dy), (cx - dx, cy + dy)]
    return Stroke(pts, col, w, t0, dur, seed=seed, amp=.8, pen=False)
def grid(rows, cols, x0, y0, cell, gap, t0, step, col_box=NAVY, col_chk=CORAL, seed=1):
    items = []; k = 0
    for r in range(rows):
        for c in range(cols):
            x = x0 + c * (cell + gap); y = y0 + r * (cell + gap); ts = t0 + k * step
            items.append(Stroke(rrect(x, y, cell, cell, 18), col_box, 7, ts, step * .85, seed=seed + k, amp=1.3, pen=False))
            items.append(Stroke(check(x + cell / 2, y + cell / 2 + 4, cell * .62), col_chk, 11, ts + step * .45, step * .55, snd="tick", seed=seed + 100 + k, amp=1.0, pen=False))
            k += 1
    return items

# ---- éléphant (profil, tourné vers la gauche)
def elephant(ox=0, oy=0, k=1.0):
    def P(x, y): return (ox + x * k, oy + y * k)
    body = catmull([P(238,1150), P(222,1070), P(228,990), P(248,910), P(272,850), P(300,795), P(338,740), P(385,695), P(445,662),
                    P(530,642), P(640,640), P(760,665), P(848,722), P(898,815), P(905,905), P(892,975), P(884,1060), P(880,1150),
                    P(802,1150), P(802,1072), P(760,1052), P(640,1060), P(520,1060), P(470,1072), P(470,1150), P(392,1150), P(392,1070),
                    P(382,1000), P(352,955), P(318,975), P(298,1030), P(280,1098), P(262,1150)], 10)
    ear = catmull([P(562,690), P(520,735), P(512,805), P(538,862), P(598,882), P(648,845), P(646,760), P(606,700)], 12)
    tusk = catmull([P(336,872), P(312,900), P(286,926), P(270,934)], 8)
    return body, ear, tusk, P(432,758)

# ============ S1 : accroche ============
it1 = []
it1.append(Text("Un éléphant a", 540, 300, 118, NAVY, 0.0, dur=0.6, anchor="c"))
it1.append(Text("100 fois plus de cellules", 540, 425, 118, CORAL, 0.6, dur=0.9, anchor="c"))
it1.append(Text("que toi.", 540, 550, 118, NAVY, 1.5, dur=0.4, anchor="c"))
body, ear, tusk, eye = elephant(0, 0, 1.0)
it1.append(Stroke(body, NAVY, 11, 1.9, 2.0, seed=71, amp=1.4))
it1.append(Stroke(ear, NAVY, 10, 3.95, 0.5, seed=72, amp=1.2))
it1.append(Stroke(tusk, NAVY, 9, 4.45, 0.2, seed=73, amp=.8, pen=False))
it1.append(Stroke(ellipse(eye[0], eye[1], 7, 7, 1.1, 0), NAVY, 9, 4.65, 0.12, snd="tick", seed=74, amp=.5, pen=False))
# petit humain
it1.append(Stroke(ellipse(985, 1060, 16, 16, 1.08, -90), CORAL, 8, 4.8, 0.2, seed=75, amp=.6, pen=False))
it1.append(Stroke([(985, 1078), (985, 1122), (968, 1150)], CORAL, 8, 5.0, 0.18, seed=76, amp=.6, pen=False))
it1.append(Stroke([(985, 1122), (1002, 1150)], CORAL, 8, 5.15, 0.1, seed=77, amp=.6, pen=False))
it1.append(Stroke([(966, 1095), (1004, 1095)], CORAL, 8, 5.22, 0.1, seed=78, amp=.6, pen=False))
it1.append(Text("toi", 985, 1210, 56, CORAL, 5.3, dur=0.25, anchor="c", pen=False))
it1.append(Text("Il devrait avoir", 540, 1360, 100, NAVY, 5.6, dur=0.7, anchor="c"))
it1.append(Text("100 fois plus de cancers.", 540, 1475, 100, CORAL, 6.3, dur=0.9, anchor="c"))
S1 = Scene(8.2, it1)

# ============ S2 : il en a moins ============
it2 = []
it2.append(Text("Il en a moins.", 540, 360, 160, CORAL, 0.0, dur=0.7, anchor="c"))
it2.append(underline("Il en a moins.", 160, 540, 400, CORAL, 0.75, 0.35, 12))
it2.append(Text("Meurent d'un cancer :", 540, 560, 76, GREY, 1.2, dur=0.7, anchor="c", wght=400))
BX, BW, BH = 120, 840, 70
it2.append(Text("Éléphants", BX, 700, 80, NAVY, 2.0, dur=0.5))
it2.append(Stroke(rrect(BX, 730, BW, BH, 22), NAVY, 8, 2.5, 0.5, seed=21, pen=False))
it2.append(Stroke([(BX + 12, 765), (BX + 12 + BW * 0.05 + 20, 765)], CORAL, 42, 3.0, 0.25, seed=22, amp=.5, pen=False))
it2.append(Text("moins de 5 %", BX + BW * 0.05 + 60, 790, 76, CORAL, 3.3, dur=0.5))
it2.append(Text("Humains", BX, 960, 80, NAVY, 4.0, dur=0.5))
it2.append(Stroke(rrect(BX, 990, BW, BH, 22), NAVY, 8, 4.5, 0.5, seed=23, pen=False))
it2.append(Stroke([(BX + 12, 1025), (BX + 12 + BW * 0.25 - 12, 1025)], NAVY, 42, 5.0, 0.5, seed=24, amp=.5, pen=False))
it2.append(Text("11 à 25 %", BX + BW * 0.25 + 40, 1050, 76, NAVY, 5.55, dur=0.5))
it2.append(Text("644 éléphants autopsiés", 540, 1300, 62, GREY, 6.2, dur=0.7, anchor="c", wght=400))
it2.append(Text("Étude publiée en 2015", 540, 1380, 62, GREY, 6.9, dur=0.6, anchor="c", wght=400))
S2 = Scene(8.0, it2)

# ============ S3 : le gène gardien ============
it3 = []
it3.append(Text("Dans chacune de tes cellules,", 540, 290, 84, NAVY, 0.0, dur=0.9, anchor="c"))
it3.append(Text("un gène surveille les erreurs.", 540, 390, 84, NAVY, 0.9, dur=0.9, anchor="c"))
it3.append(Text("Toi :", 540, 560, 96, GREY, 2.0, dur=0.3, anchor="c"))
it3 += grid(1, 1, 540 - 55, 590, 110, 0, 2.3, 0.4, seed=30)
it3.append(Text("1 copie", 540, 800, 96, NAVY, 2.75, dur=0.4, anchor="c"))
it3.append(Text("L'éléphant :", 540, 930, 96, GREY, 3.3, dur=0.45, anchor="c"))
C3, G3 = 92, 14; GW3 = 5 * C3 + 4 * G3; X3 = 540 - GW3 / 2
it3 += grid(4, 5, X3, 965, C3, G3, 3.8, 0.11, seed=40)
it3.append(Text("20 copies", 540, 1500, 130, CORAL, 6.1, dur=0.5, anchor="c"))
S3 = Scene(7.6, it3)

# ============ S4 : la vraie leçon ============
it4 = []
it4.append(Text("L'éléphant ne répare pas mieux.", 540, 310, 86, NAVY, 0.0, dur=1.0, anchor="c"))
it4.append(Text("Il élimine plus vite.", 540, 450, 120, CORAL, 1.1, dur=0.8, anchor="c"))
it4.append(underline("Il élimine plus vite.", 120, 540, 486, CORAL, 1.9, 0.3, 13))
cx, cy = 540, 820
it4.append(Stroke(ellipse(cx, cy, 170, 160, 1.06, -100), NAVY, 11, 2.3, 0.7, seed=51, amp=1.6))
it4.append(Stroke(ellipse(cx + 20, cy - 10, 52, 48, 1.08, -60), NAVY, 9, 3.0, 0.3, seed=52, amp=1.0))
it4.append(Stroke([(cx - 95, cy + 70), (cx - 60, cy + 95)], GREY, 7, 3.3, 0.1, seed=53, pen=False))
it4.append(Stroke([(cx + 60, cy + 80), (cx + 100, cy + 60)], GREY, 7, 3.4, 0.1, seed=54, pen=False))
it4.append(Text("cellule abîmée", 540, 1050, 62, GREY, 3.5, dur=0.4, anchor="c", pen=False))
it4.append(Stroke([(cx - 150, cy - 140), (cx + 150, cy + 140)], CORAL, 16, 3.95, 0.22, seed=55, amp=1.2, pen=False))
it4.append(Stroke([(cx + 150, cy - 140), (cx - 150, cy + 140)], CORAL, 16, 4.17, 0.22, snd="tick", seed=56, amp=1.2, pen=False))
it4.append(Mark(4.2, "pop"))
it4.append(Text("Une cellule abîmée reçoit", 540, 1230, 80, NAVY, 4.5, dur=0.8, anchor="c"))
it4.append(Text("l'ordre de mourir,", 540, 1325, 80, NAVY, 5.3, dur=0.6, anchor="c"))
it4.append(Text("2 fois plus souvent que chez nous.", 540, 1430, 80, CORAL, 5.9, dur=1.0, anchor="c"))
S4 = Scene(7.9, it4)

# ============ S5 : le vertige ============
it5 = []
it5.append(Text("Chez l'humain,", 540, 420, 100, NAVY, 0.0, dur=0.5, anchor="c"))
it5.append(Text("quand ce gène est en panne", 540, 540, 90, NAVY, 0.55, dur=0.9, anchor="c"))
it5.append(Text("de naissance,", 540, 650, 90, NAVY, 1.45, dur=0.5, anchor="c"))
it5.append(Text("le cancer arrive", 540, 830, 110, CORAL, 2.1, dur=0.6, anchor="c"))
it5.append(Text("presque à coup sûr.", 540, 955, 110, CORAL, 2.7, dur=0.75, anchor="c"))
it5.append(Text("C'est dire ce qu'il vaut.", 540, 1180, 92, NAVY, 3.7, dur=0.9, anchor="c"))
it5.append(underline("C'est dire ce qu'il vaut.", 92, 540, 1215, CORAL, 4.6, 0.3, 14))
it5.append(Text("(maladie génétique rare : syndrome de Li-Fraumeni)", 540, 1330, 48, GREY, 4.9, dur=0.8, anchor="c", wght=400))
S5 = Scene(6.4, it5)

# ============ S6 : la chute ============
it6 = []
it6.append(Text("Aujourd'hui, des chercheurs", 540, 330, 84, NAVY, 0.0, dur=0.8, anchor="c"))
it6.append(Text("testent la version éléphant", 540, 430, 84, NAVY, 0.8, dur=0.8, anchor="c"))
it6.append(Text("de ce gène contre", 540, 530, 84, NAVY, 1.6, dur=0.6, anchor="c"))
it6.append(Text("des cancers humains.", 540, 630, 84, CORAL, 2.2, dur=0.7, anchor="c"))
body, ear, tusk, eye = elephant(230, 335, 0.55)
it6.append(Stroke(body, NAVY, 9, 3.0, 1.2, seed=81, amp=1.2))
it6.append(Stroke(ear, NAVY, 8, 4.2, 0.35, seed=82, amp=1.0))
it6.append(Stroke(ellipse(eye[0], eye[1], 5, 5, 1.1, 0), NAVY, 8, 4.55, 0.1, snd="tick", seed=84, amp=.4, pen=False))
it6.append(Text("La réponse était peut-être", 540, 1050, 84, NAVY, 4.7, dur=0.8, anchor="c"))
it6.append(Text("dans la savane.", 540, 1150, 84, CORAL, 5.5, dur=0.6, anchor="c"))
it6.append(Stroke(ribbon(540, 1330, 95), CORAL, 13, 6.2, 0.8, seed=50, amp=1.1))
it6.append(Mark(7.0, "chime"))
it6.append(Text("Partage-le à quelqu'un qui aime les éléphants", 540, 1500, 62, GREY, 7.05, dur=1.0, anchor="c", wght=400))
S6 = Scene(9.0, it6, erase=0)

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
film.encode(args.out or "reel6.mp4", audio)
print("ok")
