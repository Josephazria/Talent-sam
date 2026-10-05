#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ohlalive arrive dans le Sud : 1 post (1080x1350) + 1 reel (1080x1920) par ville. python3 sud.py [slug ...]"""
import os, sys
from multiprocessing import Pool
import pub_locale as pl
import reels as rl
from ohlalive_kit import *
OUT = os.environ.get("SUD_OUT", "/home/claude/carrousel/sud")
# slug, titre, eyebrow, italique, couleur, entrée du titre (reel)
CITIES = [
 ("marseille",     "Marseille",     "OHLALIVE ARRIVE  ·  DANS LE SUD",     "vide son dressing.", "framboise", "rise"),
 ("nice",          "Nice",          "OHLALIVE ARRIVE  ·  CÔTE D'AZUR",     "vide son dressing.", "mimosa",    "wipe"),
 ("saint-tropez",  "Saint-Tropez",  "OHLALIVE ARRIVE  ·  DANS LE SUD",     "passe en live.",     "ivoire",    "zoom"),
 ("cannes",        "Cannes",        "OHLALIVE ARRIVE  ·  CÔTE D'AZUR",     "passe en live.",     "framboise", "wipe"),
 ("saint-raphael", "Saint-Raphaël", "OHLALIVE ARRIVE  ·  DANS LE VAR",     "vend en live.",      "mimosa",    "zoom"),
 ("frejus",        "Fréjus",        "OHLALIVE ARRIVE  ·  DANS LE VAR",     "vide son dressing.", "ivoire",    "rise"),
 ("antibes",       "Antibes",       "OHLALIVE ARRIVE  ·  CÔTE D'AZUR",     "vend en live.",      "framboise", "zoom"),
 ("monaco",        "Monaco",        "OHLALIVE ARRIVE  ·  DANS LE SUD",     "vide son dressing.", "mimosa",    "rise"),
 ("toulon",        "Toulon",        "OHLALIVE ARRIVE  ·  DANS LE VAR",     "passe en live.",     "ivoire",    "wipe"),
 ("aix",           "Aix",           "OHLALIVE ARRIVE  ·  EN PROVENCE",     "vide son dressing.", "framboise", "rise"),
 ("montpellier",   "Montpellier",   "OHLALIVE ARRIVE  ·  EN OCCITANIE",    "vend en live.",      "mimosa",    "wipe"),
]
END = {"framboise": "mimosa", "ivoire": "mimosa", "mimosa": "framboise"}

def make_post(c):
    slug, title, eyebrow, ital, col, _ = c
    pl.EYEBROW, pl.ITALIC = eyebrow, ital
    img = pl.post(col, title)
    p = f"{OUT}/{slug}/ohlalive-sud_{slug}_post_{col}.png"
    os.makedirs(os.path.dirname(p), exist_ok=True); img.save(p); return p

def make_reel(c):
    slug, title, eyebrow, ital, col, entry = c
    sc, ec = SCHEMES[col], SCHEMES[END[col]]
    size = (1080, 1920); W, H = size; S = SCALE; cx = W / 2
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    hs = 270
    while True:   # ajuste le titre à 900 px
        f = playfair("Bold", hs * S)
        if d.textbbox((0, 0), title, font=f)[2] / S <= 900 or hs < 120: break
        hs -= 6
    logo = rl.down(lockup(col, 560 * S))
    eye  = rl.text_layer(eyebrow, jost("SemiBold", 30 * S), sc["accent"], tracking=int(5 * S))
    head = rl.text_layer(title, playfair("Bold", hs * S), sc["text"])
    it   = rl.text_layer(ital, playfair_italic("Medium Italic", 140 * S), sc["text"])
    div  = rl.rect_layer(100, 4, sc["accent"])
    # carte finale
    e1 = rl.text_layer("On vide", playfair("Bold", 200 * S), ec["text"])
    e2 = rl.text_layer("votre dressing.", playfair_italic("Medium Italic", 150 * S), ec["text"])
    ed = rl.rect_layer(100, 4, ec["accent"])
    ec1 = rl.text_layer("CONTACTEZ-NOUS", jost("SemiBold", 40 * S), ec["text"], tracking=int(7 * S))
    ec2 = rl.text_layer("ohlaliveparis.com", playfair("Medium", 78 * S), ec["accent"])
    ec3 = rl.text_layer("ou en DM  ·  @ohlaliveparis", playfair_italic("Medium Italic", 42 * S), ec["text"])
    sud = rl.text_layer("MAISON DE SÉLECTION PARISIENNE", jost("Medium", 24 * S), ec["text"], tracking=int(5 * S))

    hh = [logo.height, eye.height, head.height, it.height, div.height]
    gp = [0, 100, 56, 22, 70]
    block = sum(hh) + sum(gp); y = 260 + (H - 520 - block) // 2
    ys = []
    for h, g in zip(hh, gp):
        y += g; ys.append(y + h / 2); y += h
    # carte finale
    eh = [e1.height, e2.height, ed.height, ec1.height, ec2.height, ec3.height]
    eg = [0, 16, 70, 70, 26, 22]
    blk = sum(eh) + sum(eg); y = 250 + (H - 520 - blk) // 2
    eys = []
    for h, g in zip(eh, eg):
        y += g; eys.append(y + h / 2); y += h
    T_END, DUR = 4.7, 7.4

    def frames():
        for i in range(int(DUR * rl.FPS)):
            t = i / rl.FPS; items = []
            if t < T_END:
                bg = sc["bg"]
                for L, cy, ts in ((logo, ys[0], .15), (eye, ys[1], .9)):
                    p = rl.ease_out((t - ts) / .7); items.append((L, cx, cy + (1 - p) * 36, p, 1.0))
                p = rl.ease_out((t - 1.5) / .8)
                if entry == "rise":  items.append((head, cx, ys[2] + (1 - p) * 60, p, 1.0))
                elif entry == "zoom": items.append((head, cx, ys[2], p, 1.22 - .22 * p))
                else:
                    wcut = max(1, int(head.width * p)); items.append((head.crop((0, 0, wcut, head.height)), cx - head.width / 2 + wcut / 2, ys[2], 1.0 if p > 0 else 0, 1.0))
                p = rl.ease_out((t - 2.4) / .8); items.append((it, cx, ys[3] + (1 - p) * 40, p, 1.0))
                p = rl.ease_out((t - 3.2) / .5); items.append((div, cx, ys[4], 1.0 if p > 0 else 0, max(p, .01)))
                if t > T_END - .35:   # sortie douce avant la carte
                    k = (t - (T_END - .35)) / .35
                    items = [(L, x, y_, o * (1 - k), s) for (L, x, y_, o, s) in items]
            else:
                bg = ec["bg"]; u = t - T_END
                for L, cy, ts in ((e1, eys[0], .05), (e2, eys[1], .3)):
                    p = rl.ease_out((u - ts) / .6); items.append((L, cx, cy + (1 - p) * 40, p, 1.0))
                p = rl.ease_out((u - .8) / .5); items.append((ed, cx, eys[2], 1.0 if p > 0 else 0, max(p, .01)))
                for L, cy, ts in ((ec1, eys[3], 1.0), (ec2, eys[4], 1.25), (ec3, eys[5], 1.5)):
                    p = rl.ease_out((u - ts) / .6); items.append((L, cx, cy, p, 1.0))
                p = rl.ease_out((u - 1.9) / .6); items.append((sud, cx, H - 330, p, 1.0))
            yield rl.grain_frame(rl.composite(bg, size, items))
    p = f"{OUT}/{slug}/ohlalive-sud_{slug}_reel_{col}.mp4"
    rl.encode(frames(), size, p)
    w = p.replace(".mp4", "_web.mp4")
    os.system(f'ffmpeg -y -loglevel error -i "{p}" -c:v libx264 -crf 23 -pix_fmt yuv420p -movflags +faststart -an "{w}"')
    return p

def job(a):
    kind, c = a
    return (make_post if kind == "post" else make_reel)(c)

if __name__ == "__main__":
    sel = set(sys.argv[1:])
    cs = [c for c in CITIES if not sel or c[0] in sel]
    with Pool(3) as pool:
        for r in pool.imap_unordered(job, [("post", c) for c in cs] + [("reel", c) for c in cs]): print(r, flush=True)
