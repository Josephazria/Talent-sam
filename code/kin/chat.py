"""Format « conversation » Doctorgane : messagerie animée, 1080x1920, 30 fps."""
import math, re, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from kinetic import W, H, FPS, clamp, ease_out, overshoot, ease_io, GRAIN, Film as _Film, load_music
F = "/home/claude/fonts/"
BG1, BG2 = (10, 18, 40), (20, 31, 62)
CREAM = (247, 242, 233); CORAL = (255, 111, 97); GREY = (150, 160, 184); DGB = (34, 46, 80)  # bulle Doctorgane
EMO = ImageFont.truetype(F + "NotoColorEmoji.ttf", 109)
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐❤\U0001F000-\U0001F2FF]+")
def fnt(size, w="Medium"): return ImageFont.truetype(F + f"Poppins-{w}.ttf", int(size))

def emoji_img(s, size):
    im = Image.new("RGBA", (int(109 * 1.25 * len(s)), 130), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((0, 0), s, font=EMO, embedded_color=True); bb = im.getbbox(); im = im.crop(bb) if bb else im
    sc = size / 109.0; return im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)

def render_bubble(text, side, size=50, maxw=700, weight="Medium"):
    """Rend une bulle en RGBA. side: 'L' (Doctorgane) ou 'R' (amie)."""
    f = fnt(size, weight); d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    m = EMOJI_RE.search(text); emo = None
    if m and m.end() == len(text): emo = emoji_img(m.group(0), size * 1.15); text = text[:m.start()].rstrip()
    lines, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if d0.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    lh = int(size * 1.32); tw = max([d0.textlength(l, font=f) for l in lines] + [0])
    if emo is not None:
        if lines and d0.textlength(lines[-1], font=f) + emo.width + 14 <= maxw: tw = max(tw, d0.textlength(lines[-1], font=f) + emo.width + 14)
        else: lines.append(""); tw = max(tw, emo.width)
    px, py = 36, 26; bw = int(tw + 2 * px); bh = int(len(lines) * lh + 2 * py - (lh - size) // 2)
    im = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    col = CORAL if side == "R" else DGB; tcol = (20, 20, 30) if side == "R" else CREAM
    d.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=34, fill=col)
    # petit coin « queue » côté expéditeur
    if side == "R": d.rounded_rectangle([bw - 40, bh - 40, bw - 1, bh - 1], radius=8, fill=col)
    else: d.rounded_rectangle([0, bh - 40, 40, bh - 1], radius=8, fill=col)
    y = py
    for i, l in enumerate(lines):
        d.text((px, y), l, font=f, fill=tcol)
        if emo is not None and i == len(lines) - 1:
            ex = px + (d0.textlength(l, font=f) + 14 if l else 0); im.alpha_composite(emo, (int(ex), int(y + (size - emo.height) // 2 + 4)))
        y += lh
    return im

class Chat:
    """items: liste de (side, text, t0) ; typing: liste de (t_start, t_end) pour les points « en train d'écrire » (côté L)."""
    def __init__(s, msgs, header="Doctorgane", sub="médecin cancérologue · en ligne", bottom=1540, top=350, gap=18):
        s.msgs = []; s.header = header; s.sub = sub; s.bottom = bottom; s.top = top; s.gap = gap
        for side, text, t0, *rest in msgs:
            weight = rest[0] if rest else "Medium"
            s.msgs.append(dict(side=side, text=text, t0=t0, im=render_bubble(text, side, weight=weight), snd="msg"))
        s.typing = []
    def add_typing(s, t_start, t_end): s.typing.append((t_start, t_end))
    def draw(s, fr, t):
        d = ImageDraw.Draw(fr)
        # --- messages visibles + hauteur totale
        vis = [m for m in s.msgs if t >= m["t0"]]
        typ = [(a, b) for a, b in s.typing if a <= t < b]
        heights = [m["im"].height + s.gap for m in vis] + ([112 + s.gap] if typ else [])
        total = sum(heights)
        # décalage de défilement lissé : on calcule la cible, et on interpole sur 0.3 s depuis le dernier changement
        target = max(0, total - (s.bottom - s.top))
        prev_total = total - (heights[-1] if heights else 0)
        prev_target = max(0, prev_total - (s.bottom - s.top))
        t_last = max([m["t0"] for m in vis] + [a for a, b in typ] + [0])
        p = ease_out((t - t_last) / 0.3); off = prev_target + (target - prev_target) * p
        y = s.top - off
        for m in vis:
            im = m["im"]; pp = clamp((t - m["t0"]) / 0.24); sc = 0.85 + 0.15 * overshoot(pp); a = ease_out(min(1, pp * 2))
            lay = im if sc == 1 else im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
            if a < 1: lay = lay.copy(); lay.putalpha(lay.split()[3].point(lambda v: int(v * a)))
            x = 150 if m["side"] == "L" else W - 60 - lay.width
            yy = y + im.height - lay.height  # ancrage bas-gauche/droite
            if yy + lay.height > 290 and yy < H: fr.alpha_composite(lay, (int(x), int(yy)))
            if m["side"] == "L" and yy + im.height > 290: s.avatar(fr, 60, int(y + im.height - 84))
            y += im.height + s.gap
        for a, b in typ:
            pp = clamp((t - a) / 0.2); yy = y
            bx = 150; d.rounded_rectangle([bx, yy, bx + 170, yy + 112], radius=34, fill=DGB)
            for k in range(3):
                ph = math.sin((t - a) * 7 - k * 0.9); r = 11
                d.ellipse([bx + 40 + k * 44 - r, yy + 56 - r - 8 * max(0, ph), bx + 40 + k * 44 + r, yy + 56 + r - 8 * max(0, ph)], fill=(170, 180, 205))
            s.avatar(fr, 60, int(yy + 112 - 84))
        # --- bandeau haut (dessiné après pour masquer le défilement)
        hdr = Image.new("RGBA", (W, 345), (0, 0, 0, 0)); hd = ImageDraw.Draw(hdr)
        for i in range(345):
            a = 255 if i < 300 else int(255 * (1 - (i - 300) / 45))
            hd.line([(0, i), (W, i)], fill=BG1 + (a,))
        fr.alpha_composite(hdr, (0, 0))
        d = ImageDraw.Draw(fr)
        d.line([(70, 190), (46, 214), (70, 238)], fill=CREAM, width=7, joint="curve")
        s.avatar(fr, 120, 164, r=48)
        d.text((240, 170), s.header, font=fnt(48, "SemiBold"), fill=CREAM)
        d.ellipse([240, 236, 256, 252], fill=(76, 217, 100)); d.text((268, 226), s.sub, font=fnt(30, "Regular"), fill=GREY)
        d.line([(0, 292), (W, 292)], fill=(40, 52, 84), width=2)
    def avatar(s, fr, x, y, r=42):
        d = ImageDraw.Draw(fr)
        d.ellipse([x - 4, y - 4, x + 2 * r + 4, y + 2 * r + 4], fill=CORAL)
        d.ellipse([x, y, x + 2 * r, y + 2 * r], fill=(18, 28, 56))
        f = ImageFont.truetype(F + "Anton-Regular.ttf", int(r * 1.15)); t = "D"
        tw = d.textlength(t, font=f); d.text((x + r - tw / 2, y + r * 0.28), t, font=f, fill=CREAM)

class EndCard:
    def __init__(s, t0, lines): s.t0 = t0; s.lines = lines; s.snd = "slam"
    def draw(s, fr, t):
        if t < s.t0: return
        p = ease_out((t - s.t0) / 0.5); d = ImageDraw.Draw(fr)
        ov = Image.new("RGBA", (W, H), (10, 18, 40, int(235 * p))); fr.alpha_composite(ov)
        y = 760 + int(60 * (1 - p))
        for text, size, col, w in s.lines:
            f = ImageFont.truetype(F + "Anton-Regular.ttf", size) if w == "anton" else fnt(size, w)
            tw = d.textlength(text, font=f); d.text(((W - tw) / 2, y), text, font=f, fill=col); y += int(size * 1.25)

class Scene:
    def __init__(s, dur, items, flash=False): s.dur = dur; s.items = items; s.bg = BG1; s.flash = flash

class Film(_Film):
    def frame(s, t):
        i = min(max(j for j in range(len(s.scenes)) if t >= s.bounds[j] - 1e-9), len(s.scenes) - 1)
        lt = t - s.bounds[i]; sc = s.scenes[i]
        fr = Image.fromarray(BGGRAD.copy())
        for it in sc.items: it.draw(fr, lt)
        out = np.asarray(fr.convert("RGB"), dtype=np.float32) + GRAIN[int(t * FPS) % 4]
        return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    def make_audio(s, path, music=None, music_gain=0.4):
        SR = 44100; n = int(s.dur * SR); mix = np.zeros(n); tt = lambda m: np.arange(m) / SR; rg = np.random.default_rng(2)
        def add(at, sig, g):
            a = int(at * SR); e = min(n, a + len(sig))
            if 0 <= a < n: mix[a:e] += g * sig[:e - a]
        def msg():  # « tink » de notification à deux notes
            m = int(0.16 * SR); x = tt(m)
            return (np.sin(2 * np.pi * 1245 * x) * np.exp(-x * 30) + 0.6 * np.sin(2 * np.pi * 1660 * x) * np.exp(-(x - 0.05).clip(0) * 32) * (x > 0.05)) * 0.7
        def slam():
            m = int(0.5 * SR); x = tt(m); return np.sin(2 * np.pi * 70 * x) * np.exp(-x * 8) + 0.2 * rg.normal(0, 1, m) * np.exp(-x * 70)
        for i, sc in enumerate(s.scenes):
            t0 = s.bounds[i]
            for it in sc.items:
                if isinstance(it, Chat):
                    for m in it.msgs: add(t0 + m["t0"], msg(), 0.5 if m["side"] == "L" else 0.4)
                elif getattr(it, "snd", None) == "slam": add(t0 + it.t0, slam(), 0.8)
        if music is not None: mus = music[:n]; mix[:len(mus)] += music_gain * mus
        pk = max(1e-6, np.max(np.abs(mix))); mix = mix / pk * 0.85
        import wave
        st = np.stack([mix, np.roll(mix, 9)], axis=1)
        with wave.open(path, "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())

# fond : dégradé navy + halo corail discret
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
g = (yy / H)[..., None]; base = np.array(BG1, np.float32) * (1 - g) + np.array(BG2, np.float32) * g
glow = np.exp(-(((xx - 900) / 520) ** 2 + ((yy - 200) / 520) ** 2))[..., None] * np.array([70, 28, 24], np.float32)
glow2 = np.exp(-(((xx - 120) / 600) ** 2 + ((yy - 1750) / 600) ** 2))[..., None] * np.array([18, 30, 70], np.float32)
BGGRAD = np.clip(base + glow + glow2, 0, 255).astype(np.uint8)
BGGRAD = np.dstack([BGGRAD, np.full((H, W, 1), 255, np.uint8)])
