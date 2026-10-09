"""Moteur « documentaire » Doctorgane : plans plein cadre (Ken Burns), typo cinétique,
compteurs, graphiques animés, sous-titres mot à mot, transitions punch/whip. 1080x1920, 30 fps."""
import math, json, functools, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

W, H, FPS = 1080, 1920, 30
FD = "/home/claude/fonts/"
NAVY = (14, 24, 48); DARK = (8, 14, 30); CREAM = (247, 242, 233); CORAL = (255, 111, 97)
GREY = (168, 176, 192); SLATE = (52, 66, 104); WHITE = (255, 255, 255)

@functools.lru_cache(None)
def font(name, size):
    f = {"anton": "Anton-Regular.ttf", "bold": "Poppins-Bold.ttf", "xbold": "Poppins-ExtraBold.ttf",
         "black": "Poppins-Black.ttf", "semi": "Poppins-SemiBold.ttf", "med": "Poppins-Medium.ttf",
         "reg": "Poppins-Regular.ttf"}[name]
    return ImageFont.truetype(FD + f, int(size))

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3            # ease out cubic
def eio(x): x = clamp(x); return 0.5 - 0.5 * math.cos(math.pi * x)
def back(x, k=1.6): x = clamp(x); return 1 + (k + 1) * (x - 1) ** 3 + k * (x - 1) ** 2
def lerp(a, b, p): return a + (b - a) * p

# ---------------------------------------------------------------- rendu de texte
@functools.lru_cache(maxsize=512)
def text_layer(text, fname, size, col, box=None, shadow=True, stroke=0, maxw=980, pad=40, track=0):
    f = font(fname, size)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    while d0.textlength(text, font=f) > maxw and size > 20:
        size -= 2; f = font(fname, size)
    l, t, r, b = d0.textbbox((0, 0), text, font=f, stroke_width=stroke)
    w, h = int(r - l) + 2 * pad, int(b - t) + 2 * pad
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if box:
        ImageDraw.Draw(lay).rounded_rectangle([pad - 26, pad - 14, pad + (r - l) + 26, pad + (b - t) + 18], radius=16, fill=box)
    if shadow and not box:
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad - l, pad - t + 6), text, font=f, fill=(0, 0, 0, 200), stroke_width=stroke + 2, stroke_fill=(0, 0, 0, 200))
        lay = Image.alpha_composite(lay, sh.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(lay).text((pad - l, pad - t), text, font=f, fill=col, stroke_width=stroke, stroke_fill=(0, 0, 0))
    return lay

def paste(fr, lay, cx, cy, sc=1.0, a=1.0, align="c"):
    if a <= 0.01 or sc <= 0.01: return
    if abs(sc - 1) > 1e-3:
        lay = lay.resize((max(1, int(lay.width * sc)), max(1, int(lay.height * sc))), Image.BILINEAR)
    if a < 0.999:
        lay = lay.copy(); lay.putalpha(lay.split()[3].point(lambda v: int(v * a)))
    x = cx - lay.width / 2 if align == "c" else (cx - 40 if align == "l" else cx - lay.width + 40)
    fr.alpha_composite(lay, (int(x), int(cy - lay.height / 2)))

# ---------------------------------------------------------------- calques
class Layer:
    t0 = 0.0; t1 = 1e9; snd = None
    def on(s, t): return s.t0 <= t < s.t1

class Img(Layer):
    """Image plein cadre avec Ken Burns : zoom z0->z1, centre (x,y) normalisés c0->c1."""
    SMAX = 1.32
    def __init__(s, path, t0, t1, z=(1.0, 1.12), c0=(0.5, 0.5), c1=(0.5, 0.5), dim=0.0, grade=True, snd="whoosh", trans="punch"):
        s.path, s.t0, s.t1, s.z, s.c0, s.c1, s.dim, s.snd, s.trans = path, t0, t1, z, c0, c1, dim, snd, trans
        im = Image.open(path).convert("RGB")
        im = ImageOps.fit(im, (int(W * s.SMAX), int(H * s.SMAX)), Image.LANCZOS, centering=(0.5, 0.5))
        if grade:  # léger étalonnage doc : contraste + saturation un peu tenue
            im = ImageEnhance.Contrast(im).enhance(1.06); im = ImageEnhance.Color(im).enhance(0.95)
        if dim: im = ImageEnhance.Brightness(im).enhance(1 - dim)
        s.im = im
    def draw(s, fr, t):
        p = eio((t - s.t0) / max(0.01, s.t1 - s.t0))
        z = lerp(s.z[0], s.z[1], p)
        lt = t - s.t0
        if s.trans == "punch" and lt < 0.35: z *= 1 + 0.10 * (1 - eo(lt / 0.35))
        z = max(z, 1.0); cw, ch = s.im.width / z - 1, s.im.height / z - 1
        cx = lerp(s.c0[0], s.c1[0], p) * s.im.width; cy = lerp(s.c0[1], s.c1[1], p) * s.im.height
        x0 = clamp(cx - cw / 2, 0, s.im.width - cw); y0 = clamp(cy - ch / 2, 0, s.im.height - ch)
        crop = s.im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
        if s.trans == "whip" and lt < 0.3:  # glissé rapide avec flou de bougé
            q = eo(lt / 0.3); off = int((1 - q) * W * 0.6)
            crop = crop.filter(ImageFilter.BoxBlur(int(30 * (1 - q)))) if q < 0.95 else crop
            base = Image.new("RGB", (W, H), DARK); base.paste(crop, (off, 0)); crop = base
        fr.paste(crop, (0, 0))

class ImgCard(Layer):
    """Photo paysage : fond flou plein cadre + carte nette arrondie avec Ken Burns."""
    def __init__(s, path, t0, t1, cy=860, w=1000, h=760, z=(1.0, 1.15), snd="whoosh", credit=None):
        s.t0, s.t1, s.cy, s.w, s.h, s.z, s.snd, s.credit = t0, t1, cy, w, h, z, snd, credit
        im = Image.open(path).convert("RGB")
        s.src = ImageOps.fit(im, (int(w * 1.2), int(h * 1.2)), Image.LANCZOS)
        bg = ImageOps.fit(im, (W // 6, H // 6), Image.LANCZOS).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)
        s.bg = ImageEnhance.Brightness(bg).enhance(0.42)
        s.mask = Image.new("L", (w, h), 0); ImageDraw.Draw(s.mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=40, fill=255)
    def draw(s, fr, t):
        p = eio((t - s.t0) / max(0.01, s.t1 - s.t0)); z = lerp(s.z[0], s.z[1], p); lt = t - s.t0
        fr.paste(s.bg, (0, 0))
        cw, ch = s.src.width / 1.2 / z * 1.2 / 1.2, s.src.height / 1.2 / z
        cw = s.w / z * 1.0; ch = s.h / z
        x0 = (s.src.width - cw) / 2; y0 = (s.src.height - ch) / 2
        card = s.src.resize((s.w, s.h), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
        sc = 0.9 + 0.1 * eo(lt / 0.4); a = eo(lt / 0.25)
        card = card.convert("RGBA"); m = s.mask.point(lambda v: int(v * a)); card.putalpha(m)
        if sc < 0.999: card = card.resize((int(s.w * sc), int(s.h * sc)), Image.BILINEAR)
        fr.alpha_composite(card, (int((W - card.width) / 2), int(s.cy - card.height / 2)))
        if s.credit:
            paste(fr, text_layer(s.credit, "reg", 26, GREY, None, False, 0, 1000), W / 2, s.cy + s.h / 2 + 40, 1, a)

class Solid(Layer):
    """Fond uni dégradé navy avec halo corail."""
    def __init__(s, t0, t1, top=NAVY, bot=DARK, halo=True, snd="whoosh"):
        s.t0, s.t1, s.snd = t0, t1, snd
        g = np.linspace(0, 1, H)[:, None, None]
        arr = np.array(top)[None, None, :] * (1 - g) + np.array(bot)[None, None, :] * g
        arr = np.repeat(arr, W, axis=1)
        if halo:
            yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W * 0.5) / 700) ** 2 + ((yy - H * 0.42) / 800) ** 2)
            arr = arr + np.clip(1 - r, 0, 1)[..., None] ** 2 * np.array([60, 18, 10])[None, None, :]
        s.bg = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    def draw(s, fr, t): fr.paste(s.bg, (0, 0))

class Shade(Layer):
    """Dégradé sombre bas (et haut) pour la lisibilité des textes sur photo."""
    _cache = {}
    def __init__(s, t0, t1, strength=0.75, top=0.35):
        s.t0, s.t1 = t0, t1; key = (strength, top)
        if key not in Shade._cache:
            y = np.linspace(0, 1, H)
            a = np.clip((y - 0.45) / 0.5, 0, 1) ** 1.4 * strength + np.clip((0.18 - y) / 0.18, 0, 1) * top
            m = np.zeros((H, W, 4), np.uint8); m[..., :3] = DARK; m[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)[:, None]
            Shade._cache[key] = Image.fromarray(m, "RGBA")
        s.lay = Shade._cache[key]
    def draw(s, fr, t): fr.alpha_composite(s.lay)

class Txt(Layer):
    def __init__(s, text, cx, cy, size, t0, t1=1e9, col=CREAM, fname="anton", anim="pop", box=None, dur=0.32, snd="pop", maxw=980, stroke=0, align="c", out=0.18):
        s.text, s.cx, s.cy, s.size, s.t0, s.t1, s.col, s.fname, s.anim, s.box, s.dur, s.snd, s.maxw, s.stroke, s.align, s.out = \
            text, cx, cy, size, t0, t1, col, fname, anim, box, dur, snd, maxw, stroke, align, out
    def draw(s, fr, t):
        lay = text_layer(s.text, s.fname, s.size, s.col, s.box, True, s.stroke, s.maxw)
        p = (t - s.t0) / s.dur; a = 1.0; sc = 1.0; dy = 0
        if s.anim == "pop": sc = 0.55 + 0.45 * back(p); a = eo(p * 2)
        elif s.anim == "slam": sc = 1 + 0.9 * (1 - eo(p)); a = eo(p * 3)
        elif s.anim == "up": dy = 70 * (1 - eo(p)); a = eo(p)
        elif s.anim == "fade": a = eo(p)
        elif s.anim == "wipe":  # révélation gauche->droite
            q = eo(p); lay = lay.crop((0, 0, max(1, int(lay.width * q)), lay.height)); a = 1
            fr.alpha_composite(lay, (int(s.cx - text_layer(s.text, s.fname, s.size, s.col, s.box, True, s.stroke, s.maxw).width / 2), int(s.cy - lay.height / 2))); return
        if s.t1 < 1e8 and t > s.t1 - s.out: a *= clamp((s.t1 - t) / s.out)
        paste(fr, lay, s.cx, s.cy + dy, sc, a, s.align)

class Counter(Layer):
    """Compteur qui défile v0 -> v1 (avec ticks sonores)."""
    def __init__(s, v0, v1, fmt, cx, cy, size, t0, dur=1.2, t1=1e9, col=CORAL, fname="anton"):
        s.v0, s.v1, s.fmt, s.cx, s.cy, s.size, s.t0, s.dur, s.t1, s.col, s.fname = v0, v1, fmt, cx, cy, size, t0, dur, t1, col, fname
        s.snd = "ticks"; s.ticks = [t0 + k * dur / 14 for k in range(14)]
    def draw(s, fr, t):
        p = eo((t - s.t0) / s.dur); v = lerp(s.v0, s.v1, p)
        lay = text_layer(s.fmt(v), s.fname, s.size, s.col, None, True, 0, 1000)
        sc = 1 + 0.06 * math.sin(math.pi * clamp((t - s.t0 - s.dur) / 0.25)) if t > s.t0 + s.dur else 1
        paste(fr, lay, s.cx, s.cy, sc, eo((t - s.t0) * 5))

class People(Layer):
    """n silhouettes, dont k colorées (apparition en rafale puis coloration)."""
    def __init__(s, n, k, cols, cx, cy, cell, t0, tcol, t1=1e9, col=GREY, hi=CORAL):
        s.n, s.k, s.cols, s.cx, s.cy, s.cell, s.t0, s.tcol, s.t1, s.col, s.hi = n, k, cols, cx, cy, cell, t0, tcol, t1, col, hi
        s.snd = "ticks"; s.ticks = [t0 + i * 0.05 for i in range(n)] + [tcol + i * 0.09 for i in range(k)]
    def draw(s, fr, t):
        d = ImageDraw.Draw(fr); rows = math.ceil(s.n / s.cols); g = s.cell
        x0 = s.cx - s.cols * g / 2 + g / 2; y0 = s.cy - rows * g * 1.25 / 2 + g * 0.6
        for i in range(s.n):
            ti = s.t0 + i * 0.05
            if t < ti: break
            p = back((t - ti) / 0.25); x = x0 + (i % s.cols) * g; y = y0 + (i // s.cols) * g * 1.25
            hot = i < s.k and t >= s.tcol + i * 0.09
            c = s.hi if hot else s.col; r = g * 0.17 * p
            d.ellipse([x - r, y - g * 0.32 - r, x + r, y - g * 0.32 + r], fill=c)
            bw, bh = g * 0.27 * p, g * 0.30 * p
            d.rounded_rectangle([x - bw, y - g * 0.08, x + bw, y - g * 0.08 + 2 * bh], radius=int(bw * 0.9), fill=c)

class Chart(Layer):
    """Graphique du paradoxe : cas (monte) vs mortalité (descend), tracé progressif."""
    def __init__(s, t0, t1, tdeath):
        s.t0, s.t1, s.tdeath = t0, t1, tdeath; s.snd = "riser"
    def draw(s, fr, t):
        d = ImageDraw.Draw(fr); X0, X1, Y0, Y1 = 130, 950, 560, 1180
        d.line([X0, Y1, X1, Y1], fill=(90, 104, 140), width=4); d.line([X0, Y0 - 40, X0, Y1], fill=(90, 104, 140), width=4)
        paste(fr, text_layer("1991", "semi", 38, GREY, None, False), X0 + 30, Y1 + 50)
        paste(fr, text_layer("2022", "semi", 38, GREY, None, False), X1 - 30, Y1 + 50)
        def curve(f, p, col, wdt=12):
            n = 80; pts = [(X0 + (X1 - X0) * i / n, f(i / n)) for i in range(int(n * p) + 1)]
            if len(pts) > 1: d.line(pts, fill=col, width=wdt, joint="curve")
            if pts:
                x, y = pts[-1]; d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=col)
        p1 = eio((t - s.t0) / 2.2)
        curve(lambda u: Y1 - 120 - 380 * (u ** 1.15) + 18 * math.sin(u * 19), p1, GREY, 10)
        if p1 > 0.15:
            q = eo((p1 - 0.15) * 3); d.ellipse([170, 1292, 194, 1316], fill=GREY)
            paste(fr, text_layer("NOMBRE DE CAS", "bold", 38, GREY, None, False), 215, 1304, 1, q, "l")
        p2 = eio((t - s.tdeath) / 2.4)
        if t >= s.tdeath:
            curve(lambda u: Y0 + 30 + 300 * (u ** 0.9) + 14 * math.sin(u * 23), p2, CORAL, 14)
            if p2 > 0.1:
                q = eo((p2 - 0.1) * 3); d.ellipse([560, 1292, 584, 1316], fill=CORAL)
                paste(fr, text_layer("RISQUE D'EN MOURIR", "bold", 38, CORAL, None, False), 605, 1304, 1, q, "l")

class Shrink(Layer):
    """Tumeur qui rétrécit : plus c'est petit, plus ça se guérit."""
    def __init__(s, cx, cy, t0, t1):
        s.cx, s.cy, s.t0, s.t1 = cx, cy, t0, t1; s.snd = "pop"
    def draw(s, fr, t):
        lt = t - s.t0; d = ImageDraw.Draw(fr)
        r = lerp(200, 60, eio((lt - 1.2) / 1.6)) * back(lt / 0.5)
        for k in range(3, 0, -1):
            rr = r * (1 + 0.14 * k) * (1 + 0.03 * math.sin(lt * 4 + k))
            d.ellipse([s.cx - rr, s.cy - rr, s.cx + rr, s.cy + rr], outline=CORAL + (90,), width=3)
        d.ellipse([s.cx - r, s.cy - r, s.cx + r, s.cy + r], fill=CORAL)
        g = eo((lt - 2.8) / 0.4)
        if g > 0:
            paste(fr, text_layer("✓", "bold", 120, NAVY, None, False), s.cx, s.cy - 6, g)

class Card(Layer):
    """Carton de chapitre « ARME n/5 »."""
    def __init__(s, n, title, t0, t1):
        s.n, s.title, s.t0, s.t1 = n, title, t0, t1; s.snd = "hit"
    def draw(s, fr, t):
        lt = t - s.t0
        paste(fr, text_layer("ARME", "xbold", 54, CORAL, None, False, 0, 980), W / 2, 520, 1, eo(lt * 4))
        big = text_layer(str(s.n), "anton", 520, CREAM, None, True)
        paste(fr, big, W / 2, 860, 1 + 0.35 * (1 - eo(lt / 0.35)), eo(lt * 5))
        paste(fr, text_layer(s.title, "anton", 120, CREAM, CORAL, False, 0, 960), W / 2, 1270, 0.6 + 0.4 * back((lt - 0.25) / 0.35), eo((lt - 0.25) * 5))
        d = ImageDraw.Draw(fr); bw, gap = 150, 20; x0 = W / 2 - (5 * bw + 4 * gap) / 2
        for i in range(5):
            x = x0 + i * (bw + gap); c = CORAL if i < s.n else SLATE
            fill = 1 if i < s.n - 1 else eo((lt - 0.4) / 0.4) if i == s.n - 1 else 1
            d.rounded_rectangle([x, 1470, x + bw, 1486], radius=8, fill=SLATE)
            if i < s.n: d.rounded_rectangle([x, 1470, x + bw * fill, 1486], radius=8, fill=c)

class Pips(Layer):
    """Indicateur discret en haut : progression dans les 5 armes."""
    def __init__(s, t0, t1, marks): s.t0, s.t1, s.marks = t0, t1, marks
    def draw(s, fr, t):
        n = sum(1 for m in s.marks if t >= m); d = ImageDraw.Draw(fr); bw, gap = 64, 12; x0 = W / 2 - (5 * bw + 4 * gap) / 2
        for i in range(5):
            x = x0 + i * (bw + gap)
            d.rounded_rectangle([x, 150, x + bw, 160], radius=5, fill=CORAL if i < n else (255, 255, 255, 90))

class Captions(Layer):
    """Sous-titres mot à mot : groupes de 2-4 mots, mot actif en corail."""
    def __init__(s, words, mute, y=1430, size=66):
        s.t0, s.t1, s.mute, s.y, s.size = 0, 1e9, mute, y, size
        s.groups = []; cur = []
        for w in words:
            cur.append(w)
            txt = " ".join(x["text"] for x in cur)
            if w["text"][-1] in ".?!…:," and len(cur) >= 2 or len(txt) > 20 or len(cur) >= 4:
                s.groups.append(cur); cur = []
        if cur: s.groups.append(cur)
        for i, g in enumerate(s.groups):
            g0 = g[0]["start"]; nxt = s.groups[i + 1][0]["start"] if i + 1 < len(s.groups) else g[-1]["end"] + 0.6
            s.groups[i] = (g0, min(nxt, g[-1]["end"] + 0.5), g)
    def draw(s, fr, t):
        if any(a <= t < b for a, b in s.mute): return
        for g0, g1, g in s.groups:
            if g0 <= t < g1: break
        else: return
        f = font("xbold", s.size); d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
        texts = [w["text"].upper() for w in g]; widths = [d0.textlength(x, font=f) for x in texts]; sp = d0.textlength(" ", font=f)
        total = sum(widths) + sp * (len(texts) - 1); x = W / 2 - total / 2
        lay = Image.new("RGBA", (W, 240), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        for w, tx, wd in zip(g, texts, widths):
            if t < w["start"] - 0.02: x += wd + sp; continue
            act = w["start"] <= t < w["end"] + 0.05
            dl.text((x, 80), tx, font=f, fill=CORAL if act else WHITE, stroke_width=7, stroke_fill=(0, 0, 0))
            x += wd + sp
        sh = lay.split()[3].filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.6))
        shadow = Image.new("RGBA", lay.size, (0, 0, 0, 0)); shadow.putalpha(sh)
        fr.alpha_composite(shadow, (0, int(s.y - 120 + 8))); fr.alpha_composite(lay, (0, int(s.y - 120)))

# ---------------------------------------------------------------- film
VIG = None
def vignette():
    global VIG
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        VIG = (1 - 0.38 * np.clip(r - 0.5, 0, 1) ** 1.4)[..., None].astype(np.float32)
    return VIG
GRAIN = [np.random.default_rng(k).normal(0, 3.0, (H, W, 1)).astype(np.float32) for k in range(6)]

class Film:
    def __init__(s, layers, dur, flashes=()):
        s.layers, s.dur, s.flashes = layers, dur, flashes; s.nf = int(dur * FPS)
    def frame(s, t):
        fr = Image.new("RGBA", (W, H), DARK + (255,))
        for L in s.layers:
            if L.on(t): L.draw(fr, t)
        arr = np.asarray(fr.convert("RGB"), dtype=np.float32) * vignette()
        for tf in s.flashes:
            if 0 <= t - tf < 0.14: arr = arr + (1 - (t - tf) / 0.14) * 90
        arr = arr + GRAIN[int(t * FPS) % 6]
        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
