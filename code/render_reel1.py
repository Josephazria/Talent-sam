"""Reel Doctorgane n°1 — « Une mammographie, ça irradie ? »
1080x1920, 30 fps, charte navy / crème / corail, Anton + Poppins.
Usage: python3 render_reel.py [--audio voix.mp3] [--timings timings.json] [--out reel.mp4]
Aucun en-tête ni filigrane (Joseph ajoute sa signature lui-même).
"""
import sys, json, math, subprocess, os, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("--audio"); ap.add_argument("--timings"); ap.add_argument("--out", default="reel1.mp4")
ap.add_argument("--frames", help="dossier: exporte quelques images clés au lieu de la vidéo")
args = ap.parse_args()

W, H, FPS = 1080, 1920, 30
NAVY = (18, 33, 61); CREAM = (246, 241, 233); CORAL = (255, 111, 97)
GREY = (150, 160, 180); TRACK = (48, 68, 108)
FD = "/home/claude/fonts/"
ANTON = FD + "Anton-Regular.ttf"; POP = FD + "Poppins-SemiBold.ttf"; POPR = FD + "Poppins-Regular.ttf"

# ---------- phrases / minutage ----------
SENT = [
    "Une mammographie, ça irradie ?",
    "Oui. Un tout petit peu.",
    "Je suis radiothérapeute, les rayons, c'est mon métier.",
    "La dose d'une mammographie, c'est l'équivalent de quelques semaines d'exposition naturelle.",
    "Rien qu'en vivant en France.",
    "Et le bénéfice du dépistage dépasse très largement ce risque.",
    "Alors ne repousse pas ta mammo.",
    "Et partage cette vidéo à quelqu'un qui hésite encore.",
]
if args.timings:
    T = json.load(open(args.timings)); STARTS = T["starts"]; END = T["end"]
else:  # estimation (brouillon) : 20,8 s de voix
    t = 0.12; STARTS = []
    for s in SENT:
        STARTS.append(round(t, 2)); t += 0.052 * len(s) + 0.30
    END = 21.4
    sc = (END - 0.6) / t; STARTS = [round(x * sc, 2) for x in STARTS]
DUR = END + 0.6
NF = int(DUR * FPS)

# ---------- fond ----------
yy, xx = np.mgrid[0:H, 0:W]
d = np.sqrt(((xx - W / 2) / (W * 0.8)) ** 2 + ((yy - H * 0.45) / (H * 0.7)) ** 2)
k = np.clip(1 - d, 0, 1)[..., None]
BG = (np.array((12, 24, 48)) * (1 - k) + np.array((24, 44, 82)) * k).astype(np.uint8)
BGIMG = Image.fromarray(BG)

# ---------- outils texte / animation ----------
_cache = {}
def layer(text, path, size, fill, maxw=None):
    key = (text, path, size, fill, maxw)
    if key in _cache: return _cache[key]
    f = ImageFont.truetype(path, size)
    if maxw:
        while f.getlength(text) > maxw and size > 20:
            size -= 4; f = ImageFont.truetype(path, size)
    l, t, r, b = f.getbbox(text)
    pad = 8
    im = Image.new("RGBA", (int(r - l) + 2 * pad, int(b - t) + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - l, pad - t), text, font=f, fill=fill + (255,))
    _cache[key] = im; return im

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def out_cubic(x): return 1 - (1 - x) ** 3
def out_back(x, s=1.6): x = x - 1; return 1 + (s + 1) * x ** 3 + s * x ** 2

def put(base, im, cx, cy, scale=1.0, alpha=1.0):
    if alpha <= 0.01 or scale <= 0.01: return
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if alpha < 1.0:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def pop(base, im, cx, cy, lt, delay=0.0, dur=0.30, drift=0):
    x = (lt - delay) / dur
    if x <= 0: return
    x = clamp(x)
    put(base, im, cx, cy + (1 - out_cubic(x)) * drift, 0.72 + 0.28 * out_back(x), clamp(x * 3))

def ribbon(base, cx, cy, s, col, alpha=1.0):
    S = 3; ov = Image.new("RGBA", (int(s * 3 * S), int(s * 3 * S)), (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)
    c = ov.width / 2; w = int(s * 0.24 * S); u = s * S
    dr.arc([c - .42 * u, c - 1.0 * u, c + .42 * u, c + .05 * u], 180, 360, fill=col + (255,), width=w)
    dr.line([(c - .40 * u, c - .48 * u), (c + .36 * u, c + .85 * u)], fill=col + (255,), width=w)
    dr.line([(c + .40 * u, c - .48 * u), (c - .36 * u, c + .85 * u)], fill=col + (255,), width=w)
    ov = ov.resize((ov.width // S, ov.height // S), Image.LANCZOS)
    put(base, ov, cx, cy, 1.0, alpha)

# ---------- scènes (lt = temps local depuis le début de la phrase) ----------
def scene1(im, lt):
    pop(im, layer("UNE MAMMO,", ANTON, 240, CREAM, 900), 540, 760, lt, 0.0)
    pop(im, layer("ÇA IRRADIE ?", ANTON, 300, CORAL, 900), 540, 1010, lt, 0.28)

def scene2(im, lt):
    pop(im, layer("OUI.", ANTON, 520, CREAM, 900), 540, 760, lt, 0.0)
    pop(im, layer("UN TOUT PETIT PEU.", ANTON, 200, CORAL, 900), 540, 1130, lt, 0.55)

def scene3(im, lt):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)
    for i in range(4):
        ph = (lt * 0.7 + i / 4) % 1.0; r = 90 + ph * 560
        dr.ellipse([540 - r, 900 - r, 540 + r, 900 + r], outline=CORAL + (int(95 * (1 - ph)),), width=7)
    im.alpha_composite(ov)
    chip = layer("RADIOTHÉRAPEUTE", POP, 54, NAVY)
    bw, bh = chip.width + 70, chip.height + 44
    ch = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    ImageDraw.Draw(ch).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=bh // 2, fill=CORAL + (255,))
    ch.alpha_composite(chip, ((bw - chip.width) // 2, (bh - chip.height) // 2))
    pop(im, ch, 540, 640, lt, 0.0)
    pop(im, layer("LES RAYONS,", ANTON, 250, CREAM, 900), 540, 900, lt, 0.35)
    pop(im, layer("C'EST MON MÉTIER", ANTON, 250, CREAM, 900), 540, 1110, lt, 0.60)

def scene4(im, lt, lt5):
    # lt : depuis début S4 ; lt5 : depuis début S5 (None avant)
    pop(im, layer("UNE MAMMOGRAPHIE =", POP, 56, CREAM, 900), 540, 520, lt, 0.0)
    pop(im, layer("≈ 1 À 2 MOIS", ANTON, 300, CORAL, 900), 540, 700, lt, 0.35)
    pop(im, layer("D'EXPOSITION NATURELLE", POP, 54, CREAM, 900), 540, 880, lt, 0.80)
    # barre « 1 an »
    x0, x1, y0, y1 = 90, 990, 1010, 1100
    a = clamp((lt - 1.2) / 0.5)
    bar = Image.new("RGBA", (W, 260), (0, 0, 0, 0)); dr = ImageDraw.Draw(bar)
    dr.rounded_rectangle([x0, 20, x1, 110], radius=18, fill=TRACK + (int(255 * a),))
    seg = (x1 - x0) * 7 / 52 * out_cubic(clamp((lt - 1.9) / 0.9))
    if seg > 2:
        dr.rounded_rectangle([x0, 20, x0 + seg, 110], radius=18, fill=CORAL + (255,))
    for i in range(1, 52):
        xt = x0 + i * (x1 - x0) / 52
        dr.line([(xt, 34), (xt, 96)], fill=(18, 33, 61, int(150 * a)), width=2)
    im.alpha_composite(bar, (0, y0 - 20))
    pop(im, layer("1 AN", POP, 38, GREY), x1 - 40, 1160, lt, 1.4)
    pop(im, layer("UNE MAMMO", POP, 40, CORAL), x0 + 105, 1165, lt, 2.6)
    pop(im, layer("Ordres de grandeur · source : IRSN", POPR, 30, GREY), 540, 1330, lt, 1.6)
    if lt5 is not None:
        pop(im, layer("RIEN QU'EN VIVANT EN FRANCE", POP, 50, CREAM, 900), 540, 1250, lt5, 0.0, drift=30)

def scene6(im, lt):
    th = math.radians(14 * out_back(clamp((lt - 0.4) / 0.9), 1.2))
    S = 2; ov = Image.new("RGBA", (W * S, 760 * S), (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)
    px, py = 540 * S, 140 * S
    L = 330 * S
    er = (px + L * math.cos(th), py + L * math.sin(th)); el = (px - L * math.cos(th), py - L * math.sin(th))
    dr.line([(px, py), (px, 560 * S)], fill=CREAM + (255,), width=14 * S)
    dr.rounded_rectangle([400 * S, 560 * S, 680 * S, 586 * S], radius=12 * S, fill=CREAM + (255,))
    dr.line([el, er], fill=CREAM + (255,), width=16 * S)
    dr.ellipse([px - 22 * S, py - 22 * S, px + 22 * S, py + 22 * S], fill=CORAL + (255,))
    for (ex, ey), col, rr in ((el, CORAL, 24), (er, CREAM, 74)):
        pyc = ey + 190 * S
        dr.line([(ex, ey), (ex - 100 * S, pyc)], fill=GREY + (255,), width=4 * S)
        dr.line([(ex, ey), (ex + 100 * S, pyc)], fill=GREY + (255,), width=4 * S)
        dr.pieslice([ex - 110 * S, pyc - 110 * S, ex + 110 * S, pyc + 110 * S], 0, 180, fill=TRACK + (255,))
        dr.ellipse([ex - rr * S, pyc - rr * 2 * S, ex + rr * S, pyc - 0 * S] if False else
                   [ex - rr * S, pyc - 2 * rr * S, ex + rr * S, pyc], fill=col + (255,))
    ov = ov.resize((W, 760), Image.LANCZOS)
    a = clamp(lt / 0.3)
    ov.putalpha(ov.getchannel("A").point(lambda v: int(v * a)))
    im.alpha_composite(ov, (0, 480))
    pop(im, layer("RISQUE", POP, 40, CORAL), el[0] / S, 480 + el[1] / S + 190 + 165, lt, 0.9)
    pop(im, layer("BÉNÉFICE", POP, 40, CREAM), er[0] / S, 480 + er[1] / S + 190 + 165, lt, 0.9)
    pop(im, layer("LE BÉNÉFICE", ANTON, 210, CREAM, 900), 540, 1350, lt, 0.2)
    pop(im, layer("DÉPASSE LE RISQUE", ANTON, 190, CORAL, 900), 540, 1580, lt, 0.5)

def scene7(im, lt):
    pop(im, layer("NE REPOUSSE", ANTON, 330, CREAM, 900), 540, 640, lt, 0.0)
    pop(im, layer("PAS TA", ANTON, 330, CREAM, 900), 540, 930, lt, 0.28)
    pop(im, layer("MAMMO.", ANTON, 420, CORAL, 900), 540, 1250, lt, 0.56)

def scene8(im, lt):
    ribbon(im, 540, 640, 150, CORAL, clamp(lt / 0.3))
    pop(im, layer("PARTAGE-LE", ANTON, 330, CREAM, 900), 540, 1000, lt, 0.2)
    pop(im, layer("À QUELQU'UN", ANTON, 230, CORAL, 900), 540, 1240, lt, 0.7)
    pop(im, layer("QUI HÉSITE ENCORE", ANTON, 170, CREAM, 900), 540, 1420, lt, 1.2)

def frame(t):
    im = BGIMG.convert("RGBA")
    i = max(j for j in range(8) if t >= STARTS[j]) if t >= STARTS[0] else 0
    lt = t - STARTS[i]
    if i == 0: scene1(im, lt)
    elif i == 1: scene2(im, lt)
    elif i == 2: scene3(im, lt)
    elif i in (3, 4):
        scene4(im, t - STARTS[3], (t - STARTS[4]) if i == 4 else None)
    elif i == 5: scene6(im, lt)
    elif i == 6: scene7(im, lt)
    else: scene8(im, lt)
    return im.convert("RGB")

# ---------- sortie ----------
if args.frames:
    os.makedirs(args.frames, exist_ok=True)
    marks = [STARTS[0] + 0.9, STARTS[1] + 1.0, STARTS[2] + 1.2, STARTS[3] + 0.6, STARTS[3] + 4.2,
             STARTS[4] + 0.8, STARTS[5] + 1.6, STARTS[6] + 1.4, STARTS[7] + 2.0]
    for n, m in enumerate(marks):
        frame(m).save(f"{args.frames}/f{n + 1}.png")
    json.dump({"starts": STARTS, "end": END}, open(f"{args.frames}/t.json", "w"))
    sys.exit()

cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
if args.audio:
    cmd += ["-i", args.audio, "-c:a", "aac", "-b:a", "192k", "-shortest"]
cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-t", f"{DUR:.2f}", args.out]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for n in range(NF):
    p.stdin.write(frame(n / FPS).tobytes())
p.stdin.close(); p.wait()
print("ok", args.out, f"{DUR:.1f}s", STARTS)
