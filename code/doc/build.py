"""Montage du documentaire « Le cancer ne disparaîtra jamais » (Doctorgane)."""
import sys, json, os, subprocess, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from doc import *

HERE = os.path.dirname(os.path.abspath(__file__)); M = os.environ.get("DOC_MEDIA", HERE + "/media/"); PH = "/home/claude/ts/doctorgane/photos/"
K = 1.08          # accélération de la voix
OFF = 0.5         # couverture statique avant la voix
def T(t): return OFF + t / K

# ---------------- sous-titres
raw = json.load(open(M + "words.json"))["words"]
words = []
for w in raw:
    tx = w["text"]
    if tx.startswith("[") or tx.endswith("]") or w.get("type") != "word": continue
    if tx in (":", "?", "!") and words: words[-1]["text"] += (" " + tx if tx != "," else tx); continue
    words.append({"text": tx, "start": T(w["start"]), "end": T(w["end"])})

L = []; MUTE = []; FLASH = []
def mute(a, b): MUTE.append((T(a), T(b)))
def img(name, a, b, **k):
    p = M + name + ".jpg" if os.path.exists(M + name + ".jpg") else PH + name + ".jpg"
    L.append(Img(p, T(a), T(b), **k)); L.append(Shade(T(a), T(b)))
def txt(s, cx, cy, size, a, b=None, **k): L.append(Txt(s, cx, cy, size, T(a), T(b) if b else 1e9, **k)); return L[-1]
def solid(a, b, **k): L.append(Solid(T(a), T(b), **k))
def end(layer, b): layer.t1 = T(b)

# ---------------- COUVERTURE + HOOK (peau)
img("skin", -OFF * K, 9.5, z=(1.0, 1.28), c0=(0.5, 0.5), c1=(0.42, 0.42), trans=None)
L[-2].snd = None
cov = [txt("LE CANCER", W / 2, 640, 170, -OFF * K - 0.5, 1.6, anim="fade", dur=0.01, snd=None),
       txt("NE DISPARAÎTRA", W / 2, 810, 150, -OFF * K - 0.5, 1.6, anim="fade", dur=0.01, snd=None),
       txt("JAMAIS.", W / 2, 985, 190, -OFF * K - 0.5, 1.6, col=CORAL, anim="fade", dur=0.01, snd=None),
       txt("(mais on peut arrêter d'en mourir)", W / 2, 1140, 54, -OFF * K - 0.5, 1.6, fname="semi", anim="fade", dur=0.01, snd=None)]
mute(-1, 1.6)
txt("1 CELLULE SUR 4", W / 2, 700, 150, 5.17, 9.5, col=CORAL, anim="slam", snd="hit")
txt("PORTE DÉJÀ UNE MUTATION", W / 2, 850, 58, 7.2, 9.5, fname="xbold", anim="up", snd=None)

# ---------------- « Et tout va bien »
L.append(ImgCard(PH + "cells2.jpg", T(9.5), T(12.8), cy=820, w=960, h=960, z=(1.0, 1.2)))
txt("ET TOUT", W / 2, 1420, 130, 10.1, 12.8, anim="up", snd=None)
txt("VA BIEN.", W / 2, 1560, 150, 11.8, 12.8, col=CORAL, anim="pop")
mute(9.5, 12.8)

# ---------------- La question
solid(12.8, 21.9)
txt("QUESTION :", W / 2, 420, 60, 13.4, 21.2, fname="xbold", col=GREY, anim="up", snd=None)
txt("UN JOUR,", W / 2, 560, 70, 14.7, 21.2, fname="xbold", anim="up", snd=None)
txt("LE CANCER VA-T-IL", W / 2, 700, 110, 15.8, 21.2, anim="up", snd=None)
txt("DISPARAÎTRE ?", W / 2, 840, 150, 17.0, 21.2, col=CORAL, anim="pop")
txt("RÉPONSE HONNÊTE DE CANCÉROLOGUE :", W / 2, 1060, 44, 19.0, 21.2, fname="semi", col=GREY, anim="fade", snd=None)
txt("NON.", W / 2, 900, 460, 21.3, 21.9, col=CORAL, anim="slam", snd="hit")
mute(12.8, 21.9)
solid(21.9, 26.9, top=(20, 30, 58))
txt("MAIS ON PEUT", W / 2, 700, 100, 22.6, 26.9, anim="up", snd=None)
txt("ARRÊTER", W / 2, 850, 190, 23.0, 26.9, anim="pop")
txt("D'EN MOURIR.", W / 2, 1040, 140, 23.5, 26.9, col=NAVY, box=CORAL, anim="pop")
txt("Je vais te montrer comment.", W / 2, 1230, 50, 24.7, 26.9, fname="semi", col=GREY, anim="fade", snd=None)
mute(21.9, 26.9)

# ---------------- Pourquoi il restera
img("dna", 26.9, 35.4, z=(1.05, 1.3), c0=(0.5, 0.55), c1=(0.5, 0.45))
txt("DES MILLIARDS", W / 2, 520, 120, 29.0, 35.4, anim="pop")
txt("DE COPIES PAR JOUR", W / 2, 640, 60, 29.3, 35.4, fname="xbold", anim="up", snd=None)
txt("DES FAUTES DE FRAPPE", W / 2, 800, 64, 31.4, 35.4, fname="xbold", col=NAVY, box=CORAL, anim="pop")
txt("RÉPARÉES EN PERMANENCE", W / 2, 920, 64, 33.4, 35.4, fname="xbold", col=NAVY, box=CREAM, anim="pop")
img("rogue", 35.4, 41.2, z=(1.0, 1.45), c0=(0.5, 0.5), c1=(0.5, 0.45))
txt("UNE CELLULE QUI", W / 2, 470, 80, 36.6, 41.2, anim="up", snd=None)
txt("N'ÉCOUTE PLUS PERSONNE", W / 2, 590, 100, 39.6, 41.2, col=CORAL, anim="pop")
L.append(ImgCard(PH + "museum.jpg", T(41.2), T(45.6), cy=820, w=960, h=1200, z=(1.0, 1.12)))
txt("VIEUX COMME LA VIE", W / 2, 1560, 100, 41.8, 45.6, anim="up", snd=None)
L.append(ImgCard(PH + "cnhm.jpg", T(45.6), T(48.1), cy=760, w=1000, h=760, z=(1.0, 1.15), credit="Crâne de Centrosaurus — ostéosarcome (Lancet Oncology, 2020)"))
L.append(Counter(0, 76, lambda v: f"{int(round(v))} MILLIONS", W / 2, 1300, 140, T(45.7), dur=1.2, t1=T(48.1)))
txt("D'ANNÉES", W / 2, 1450, 90, 46.6, 48.1, anim="up", snd=None)
mute(45.6, 48.1)
solid(48.1, 51.9, halo=True)
txt("ON NE L'EFFACERA PAS.", W / 2, 560, 80, 48.7, 51.9, fname="xbold", col=GREY, anim="fade", snd=None)
txt("MAIS ON A", W / 2, 760, 110, 50.2, 51.9, anim="up", snd=None)
txt("5", W / 2, 1060, 480, 50.8, 51.9, col=CORAL, anim="slam", snd="hit")
txt("ARMES", W / 2, 1360, 170, 51.1, 51.9, anim="pop", snd=None)
mute(48.1, 51.9)

# ---------------- ARME 1
L.append(Card(1, "L'EMPÊCHER", T(51.9), T(54.4))); L.append(Solid(T(51.9), T(54.4))); L[-1], L[-2] = L[-2], L[-1]; mute(51.9, 54.4)
solid(54.4, 59.0)
L.append(People(10, 4, 5, W / 2, 950, 170, T(54.6), T(55.7), t1=T(59.0)))
txt("4 CANCERS SUR 10", W / 2, 560, 120, 55.7, 59.0, col=CORAL, anim="pop")
txt("LIÉS À CE QU'ON PEUT CHANGER", W / 2, 1300, 50, 57.4, 59.0, fname="xbold", anim="up", snd=None)
for name, a, b, lab in [("cig", 59.0, 60.2, "TABAC"), ("wine", 60.2, 61.4, "ALCOOL"), ("sun", 61.4, 62.4, "SOLEIL"), ("vaccine", 62.4, 64.2, "VIRUS")]:
    img(name, a, b, z=(1.12, 1.0))
    txt(lab, W / 2, 900, 200, a + 0.05, b, col=CREAM, anim="slam", snd="hit")
mute(59.0, 64.2)
img("sydney", 64.2, 75.3, z=(1.3, 1.05), c0=(0.55, 0.45), c1=(0.5, 0.5))
txt("AUSTRALIE", W / 2, 420, 150, 64.6, 75.3, anim="pop")
txt("VACCIN HPV + DÉPISTAGE", W / 2, 560, 56, 65.8, 75.3, fname="xbold", col=NAVY, box=CREAM, anim="pop", snd=None)
txt("LE CANCER DU COL", W / 2, 760, 80, 68.4, 75.3, anim="up", snd=None)
txt("DEVIENT RARE", W / 2, 880, 120, 70.8, 75.3, col=NAVY, box=CORAL, anim="pop")

# ---------------- ARME 2
L.append(Solid(T(75.3), T(78.8))); L.append(Card(2, "L'ATTRAPER TÔT", T(75.3), T(78.8))); mute(75.3, 78.8)
solid(78.8, 85.3)
txt("SEIN", W / 2, 360, 110, 78.9, 85.3, anim="pop")
txt("CÔLON", W / 2, 470, 110, 79.5, 85.3, anim="pop")
txt("COL", W / 2, 580, 110, 80.5, 85.3, anim="pop")
txt("ON DÉPISTE.", W / 2, 1420, 80, 81.3, 85.3, fname="xbold", col=CORAL, anim="up", snd=None)
L.append(Shrink(W / 2, 1030, T(82.1), T(85.3)))
txt("PLUS C'EST PETIT, PLUS ÇA SE GUÉRIT", W / 2, 1420, 48, 83.2, 85.3, fname="xbold", anim="fade", snd=None)
L[-3].t1 = T(83.1)
mute(78.8, 85.3)
img("blood", 85.3, 93.2, z=(1.0, 1.22), c0=(0.45, 0.6), c1=(0.4, 0.62))
txt("ET DEMAIN ?", W / 2, 440, 120, 85.5, 93.2, anim="pop")
txt("UNE PRISE DE SANG", W / 2, 580, 80, 87.4, 93.2, anim="up", snd=None)
txt("QUI CHERCHE PLUSIEURS CANCERS", W / 2, 680, 50, 88.6, 93.2, fname="xbold", anim="up", snd=None)
txt("EN TEST", W / 2, 840, 90, 90.4, 93.2, col=NAVY, box=CORAL, anim="slam", snd="hit")
txt("PAS ENCORE PROUVÉ", W / 2, 960, 56, 91.5, 93.2, fname="xbold", anim="pop", snd=None)

# ---------------- ARME 3
L.append(Solid(T(93.2), T(95.8))); L.append(Card(3, "GUÉRIR", T(93.2), T(95.8))); mute(93.2, 95.8)
solid(95.8, 101.4)
txt("CANCER DU TESTICULE", W / 2, 560, 64, 95.9, 101.4, fname="xbold", anim="up", snd=None)
L.append(Counter(0, 96, lambda v: f"{int(round(v))} %", W / 2, 900, 380, T(98.2), dur=1.0, t1=T(101.4)))
txt("EN VIE 5 ANS APRÈS", W / 2, 1160, 64, 100.1, 101.4, fname="xbold", anim="up", snd=None)
solid(101.4, 105.0, top=(20, 30, 58))
txt("CANCER DU SEIN", W / 2, 560, 64, 101.6, 105.0, fname="xbold", anim="up", snd=None)
L.append(Counter(0, 88, lambda v: f"{int(round(v))} %", W / 2, 900, 380, T(103.4), dur=0.9, t1=T(105.0)))
txt("SURVIE À 5 ANS · FRANCE", W / 2, 1160, 44, 103.8, 105.0, fname="semi", col=GREY, anim="fade", snd=None)
mute(98.0, 105.0)
img("hospital", 105.0, 109.2, z=(1.0, 1.18), c0=(0.5, 0.55), c1=(0.5, 0.5))
txt("PAS UN MIRACLE.", W / 2, 560, 110, 105.6, 109.2, anim="up")
txt("UN MARDI MATIN.", W / 2, 720, 120, 106.7, 109.2, col=NAVY, box=CORAL, anim="pop")
mute(105.0, 109.2)

# ---------------- ARME 4
L.append(Solid(T(109.2), T(112.4))); L.append(Card(4, "VIVRE AVEC", T(109.2), T(112.4))); mute(109.2, 112.4)
img("pill", 112.4, 119.2, z=(1.0, 1.35), c0=(0.5, 0.6), c1=(0.47, 0.66))
txt("CERTAINES LEUCÉMIES", W / 2, 420, 70, 112.5, 119.2, fname="xbold", anim="up", snd=None)
txt("1 COMPRIMÉ / JOUR", W / 2, 560, 130, 114.8, 119.2, col=CORAL, anim="pop")
txt("ESPÉRANCE DE VIE PRESQUE NORMALE", W / 2, 720, 48, 116.9, 119.2, fname="xbold", col=NAVY, box=CREAM, anim="pop", snd=None)
solid(119.2, 122.3)
txt("UNE MALADIE", W / 2, 760, 120, 119.3, 122.3, anim="up", snd=None)
txt("CHRONIQUE", W / 2, 940, 200, 120.6, 122.3, col=CORAL, anim="slam", snd="hit")
mute(119.2, 122.3)

# ---------------- ARME 5
L.append(Solid(T(122.3), T(125.3))); L.append(Card(5, "NE RIEN FAIRE", T(122.3), T(125.3))); mute(122.3, 125.3)
img("oldman", 125.3, 133.3, z=(1.0, 1.2), c0=(0.5, 0.6), c1=(0.5, 0.55))
txt("APRÈS 80 ANS", W / 2, 400, 80, 125.4, 133.3, anim="up", snd=None)
txt("1 HOMME SUR 2", W / 2, 540, 150, 127.3, 133.3, col=CORAL, anim="pop")
txt("A DES CELLULES DE CANCER DE LA PROSTATE", W / 2, 670, 40, 128.6, 133.3, fname="xbold", anim="up", snd=None)
txt("LA PLUPART NE LE SAURONT JAMAIS", W / 2, 760, 46, 130.8, 133.3, fname="xbold", col=NAVY, box=CREAM, anim="pop", snd=None)
mute(125.3, 133.3)
solid(133.3, 139.0)
txt("ON NE MEURT PAS", W / 2, 520, 100, 133.4, 139.0, anim="up", snd=None)
txt("DE TOUS LES CANCERS.", W / 2, 640, 90, 134.3, 139.0, anim="up", snd=None)
txt("PARFOIS, ON MEURT", W / 2, 860, 90, 135.6, 139.0, col=GREY, anim="up", snd=None)
txt("AVEC.", W / 2, 1110, 330, 137.9, 139.0, col=CORAL, anim="slam", snd="hit")
mute(133.3, 139.0)

# ---------------- PARADOXE
solid(139.0, 140.9, top=(30, 20, 40))
txt("LE PARADOXE", W / 2, 900, 160, 139.4, 140.9, col=CORAL, anim="pop", snd="hit")
mute(139.0, 140.9)
img("crowd", 140.9, 145.2, z=(1.0, 1.15), c0=(0.5, 0.5), c1=(0.5, 0.45))
txt("+ DE CANCERS", W / 2, 520, 140, 142.6, 145.2, col=NAVY, box=CORAL, anim="pop")
txt("PARCE QU'ON VIT PLUS VIEUX", W / 2, 680, 54, 143.9, 145.2, fname="xbold", anim="up", snd=None)
mute(140.9, 145.2)
solid(145.2, 155.4)
L.append(Chart(T(145.2), T(155.4), T(145.7)))
m34 = txt("−34 %", W / 2, 1460, 230, 149.6, 153.2, col=CORAL, anim="slam", snd="hit")
txt("MORTALITÉ PAR CANCER · ÉTATS-UNIS · 1991 – 2022", W / 2, 1600, 34, 150.4, 155.4, fname="semi", col=GREY, anim="fade", snd=None)
txt("4,5 MILLIONS DE VIES", W / 2, 1460, 120, 153.3, 155.4, col=CORAL, anim="pop")
mute(145.2, 155.4)

# ---------------- FIN
FINAL = T(165.6) + 1.6
img("sunrise", 155.4, (FINAL - OFF) * K, z=(1.0, 1.15), c0=(0.5, 0.6), c1=(0.5, 0.55))
txt("LE CANCER NE DISPARAÎTRA PAS.", W / 2, 520, 64, 156.2, fname="xbold", anim="up", snd=None)
txt("LA PEUR, SI.", W / 2, 700, 190, 158.3, col=CORAL, anim="pop", snd="hit")
txt("LAQUELLE DES 5 ARMES", W / 2, 1230, 76, 161.3, anim="up", snd=None)
txt("TU NE CONNAISSAIS PAS ?", W / 2, 1330, 76, 161.6, col=NAVY, box=CORAL, anim="pop")
txt("Dis-le-moi en commentaire", W / 2, 1460, 46, 163.6, fname="semi", anim="fade", snd=None)
mute(155.4, 170)

# ---------------- surcouches globales
L.append(Pips(T(51.9), T(139.0), [T(51.9), T(75.3), T(93.2), T(109.2), T(122.3)]))
L.append(Captions(words, MUTE))
for l in L:
    if isinstance(l, (Img, ImgCard, Solid, Card)) and l.t0 > 0.6: FLASH.append(l.t0)
FILM = Film(L, FINAL, flashes=sorted(set(FLASH)))

if __name__ == "__main__":
    if sys.argv[1] == "--preview":
        os.makedirs(HERE + "/prev", exist_ok=True)
        for tt in sys.argv[2].split(","):
            FILM.frame(T(float(tt))).save(f"{HERE}/prev/f_{tt}.jpg", quality=88)
    elif sys.argv[1] == "--chunk":   # rendu d'un segment d'images : --chunk i n out.mp4
        i, n, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        a = FILM.nf * i // n; b = FILM.nf * (i + 1) // n
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
               "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for k in range(a, b): p.stdin.write(FILM.frame(k / FPS).tobytes())
        p.stdin.close(); p.wait()
    elif sys.argv[1] == "--events":
        ev = []
        for l in L:
            s = getattr(l, "snd", None)
            if s == "ticks": ev += [("tick", x) for x in l.ticks]
            elif s: ev.append((s, l.t0))
        json.dump({"dur": FINAL, "events": ev, "riser": [T(47.4), T(144.8)]}, open(HERE + "/events.json", "w"))
        print(len(ev), FINAL)
