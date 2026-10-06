#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Réels The Live Corner — v4 du 05/10/2026 (vente Lancaster 3), paramétré par marque.
  R1 « Le défilé »   : hook typo (« VENTE EXCLUSIVE » / nom), les photos portées plein cadre (coupes franches 1,6 s, zoom lent),
                       label « MARQUE · VENTE EXCLUSIVE · EN LIVE SUR WHATNOT », carton final.
  R2 « Battements »  : les pièces détourées tombent une par une (0,62 s) sur papier / couleur en alternance, mots entre deux
                       (« Marque. » / « Une vente exclusive. » / « En live sur Whatnot. » / la date), carton final.
  Carton final       : lockup A sans point → « VENTE EXCLUSIVE » → nom → filet → « <date> · <heure> · En live sur Whatnot »
                       → slogan « Le live qui vous va bien. » (kit court) → point rouge en dernier.
Depuis le 05/10/2026 : « sur Whatnot » écrit partout (Joseph) ; kit court = R1 + R2 (un seul montage), carton slogan seul.
`--complet` rend aussi le carton « signature » et le montage R2 B.
Story 9:16 et post 4:5, 30 fps, H.264, sans son. Rendu par segments puis concat sans ré-encodage.

  python3 tlc_reels.py --marque Lancaster --date "Mercredi 7 octobre" --heure 18h --couleur "#F5A11A" \
      --portees portees/bordeaux_mur.jpg portees/bordeaux_chaise.jpg ... --packs packshots/noir.png packshots/camel.png --out reels_lancaster
"""
import os, io, sys, subprocess, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = (243, 238, 227); INK = (31, 27, 23); RED = (216, 38, 28)
FPS = 30
FONT_F = os.path.join(HERE, "fonts", "Fraunces.ttf"); FONT_A = os.path.join(HERE, "fonts", "Archivo.ttf")
LOGO = os.path.join(HERE, "assets", "A_vertical_transparent.svg")
LIVE = "En live sur Whatnot"
SLOGANS = {"slogan": ["Le live qui vous va bien."], "signature": ["Les plus belles marques", "aux plus beaux prix."]}

def OPSZ_FIX(s):
    # 06/10/2026 : taille optique réelle sous 144 px (le « − » et les déliés disparaissaient en opsz 144)
    return max(9, min(144, s))
def fraunces(s, w=500):
    f = ImageFont.truetype(FONT_F, s); f.set_variation_by_axes([OPSZ_FIX(s), 0, w, 1]); return f
def archivo(s, w=500):
    f = ImageFont.truetype(FONT_A, s); f.set_variation_by_axes([w, 100]); return f
def lockup(w, col=INK, dot=True):
    svg = open(LOGO, encoding="utf-8").read().replace('fill="#1F1B17"', 'fill="#%02X%02X%02X"' % col)
    if not dot: svg = svg.replace('fill="#D8261C"', 'fill="#D8261C" fill-opacity="0"')
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=w))).convert("RGBA")
def ease(t):
    t = min(max(t, 0.0), 1.0); return 1 - (1 - t) ** 3
def ffmpeg(out, w, h):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-",
                             "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
def blend(base, layer, alpha=1.0, dy=0, dx=0):
    H, W = base.shape[:2]; lay = layer
    if dy or dx:
        s = np.zeros_like(lay)
        ys, ye = max(0, dy), min(H, H + dy); xs, xe = max(0, dx), min(W, W + dx)
        s[ys:ye, xs:xe] = lay[ys - dy:ye - dy, xs - dx:xe - dx]; lay = s
    a = lay[..., 3:4].astype(np.float32) / 255.0 * alpha
    return base * (1 - a) + lay[..., :3].astype(np.float32) * a
def grain(frame, amp=1.2):
    n = np.random.uniform(-amp, amp, size=frame.shape[:2] + (1,))
    return np.clip(frame + n, 0, 255).round().astype(np.uint8)
def text_layer(W, H, draws):
    S = 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for kind, text, size, color, cx, x, yb, tr in draws:
        f = fraunces(size * S) if kind == "f" else archivo(size * S, 600 if kind == "a6" else 500)
        if tr:
            total = sum(d.textlength(c, font=f) for c in text) + tr * S * (len(text) - 1)
            xx = (cx * S - total / 2) if cx is not None else x * S
            for c in text:
                d.text((xx, yb * S), c, font=f, fill=color + (255,), anchor="ls"); xx += d.textlength(c, font=f) + tr * S
        else:
            if cx is not None: d.text((cx * S, yb * S), text, font=f, fill=color + (255,), anchor="ms")
            else: d.text((x * S, yb * S), text, font=f, fill=color + (255,), anchor="ls")
    return np.array(im.resize((W, H), Image.LANCZOS))
def text_width(text, size, kind="f", tr=0, w=500):
    f = fraunces(size) if kind == "f" else archivo(size, w)
    d = ImageDraw.Draw(Image.new("L", (4, 4)))
    return sum(d.textlength(c, font=f) for c in text) + tr * (len(text) - 1) if tr else d.textlength(text, font=f)
def fit_label(text, size, maxw, tr):
    while size > 14 and text_width(text, size, "a", tr, 600) > maxw: size -= 1
    return size
def img_layer(im_rgba, W, H, x, y):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lay.alpha_composite(im_rgba, (int(x), int(y))); return np.array(lay)
def cover(im, W, H, anchor=0.0):
    r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    x0 = (im.width - W) // 2; y0 = int(anchor * max(0, im.height - H)); return im.crop((x0, y0, x0 + W, y0 + H))
def kenburns_frames(photo, W, H, n, zoom=1.07, anchor=0.05):
    big = cover(photo, int(W * zoom) + 2, int(H * zoom) + 2, anchor)
    for i in range(n):
        z = 1 + (zoom - 1) * ease(i / max(1, n - 1)) * 0.9
        cw, ch = int(big.width / z), int(big.height / z)
        x0 = (big.width - cw) // 2; y0 = int((big.height - ch) * 0.25)
        yield np.array(big.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.LANCZOS)).astype(np.float32)
def cutout(path):
    im0 = Image.open(path)
    if im0.mode in ("RGBA", "LA") and np.array(im0.split()[-1]).min() < 10:
        out = im0.convert("RGBA"); bb = out.getbbox(); return out.crop(bb) if bb else out
    im = im0.convert("RGB"); a = np.array(im).astype(int); h, w, _ = a.shape; k = max(8, min(h, w) // 25)
    corners = np.concatenate([a[:k, :k].reshape(-1, 3), a[:k, -k:].reshape(-1, 3), a[-k:, :k].reshape(-1, 3), a[-k:, -k:].reshape(-1, 3)])
    bg = np.median(corners, axis=0); dist = np.abs(a - bg).max(axis=2)
    alpha = np.clip((dist - 10) * 10, 0, 255).astype(np.uint8)
    out = Image.fromarray(np.dstack([a, alpha]).astype(np.uint8), "RGBA"); bb = out.getbbox()
    return out.crop(bb) if bb else out
def fit(im, mw, mh):
    r = min(mw / im.width, mh / im.height); return im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
def shadow_layer(W, H, bag, bx, by):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); s = Image.new("RGBA", (bag.width + 160, 140), (0, 0, 0, 0))
    ImageDraw.Draw(s).ellipse((60, 40, bag.width + 100, 100), fill=(0, 0, 0, 60)); s = s.filter(ImageFilter.GaussianBlur(24))
    sh.alpha_composite(s, (int(bx - 80), int(by + bag.height - 80))); return np.array(sh)

# ------------------------------------------------------------------ carton final
def final_card_frames(W, H, seconds, quand, slogan, marque):
    s = W / 1080
    lk_w = int(300 * s) if H > 1500 else int(240 * s)
    lk0 = lockup(lk_w, INK, dot=False); lk1 = lockup(lk_w, INK, dot=True)
    top = int(H * 0.16) if H > 1500 else int(H * 0.11); cx = W // 2
    L_lk0 = img_layer(lk0, W, H, cx - lk0.width // 2, top); L_lk1 = img_layer(lk1, W, H, cx - lk1.width // 2, top)
    y = top + lk0.height + int(70 * s)
    L_vp = text_layer(W, H, [("a6", "VENTE EXCLUSIVE", int(26 * s), INK, cx, None, y, 7 * s)])
    y += int(150 * s)
    L_name = text_layer(W, H, [("f", marque, int(190 * s), INK, cx, None, y, 0)])
    y += int(40 * s); y2 = y + int(24 * s)
    wsize = int(40 * s)
    while wsize > int(26 * s) and text_width(quand, wsize, "a") > W * 0.88: wsize -= 2
    L_when = text_layer(W, H, [("a", quand, wsize, INK, cx, None, y2 + int(66 * s), 0)])
    lines = SLOGANS[slogan]; ys = H - int(H * 0.16) - int(50 * s)
    if len(lines) == 2:
        L_sig = [text_layer(W, H, [("f", lines[0], int(52 * s), INK, cx, None, ys, 0)]), text_layer(W, H, [("f", lines[1], int(52 * s), INK, cx, None, ys + int(66 * s), 0)])]
        tl_sig = [("sig0", 2.4, 3.3), ("sig1", 3.1, 4.0)]
    else:
        size = int(72 * s)
        while size > int(40 * s) and text_width(lines[0], size) > W * 0.84: size -= 2
        L_sig = [text_layer(W, H, [("f", lines[0], size, INK, cx, None, ys + int(40 * s), 0)])]
        tl_sig = [("sig0", 2.4, 3.5)]
    filet = np.zeros((H, W, 4), np.uint8); filet[y:y + 2, cx - int(40 * s):cx + int(40 * s)] = INK + (255,)
    tl = [("lk", 0.0, 0.7), ("vp", 0.5, 1.0), ("name", 0.8, 1.5), ("filet", 1.5, 1.8), ("when", 1.7, 2.3)] + tl_sig + [("dot", 4.2, 4.6)]
    layers = {"lk": L_lk0, "vp": L_vp, "name": L_name, "filet": filet, "when": L_when}
    for i, L in enumerate(L_sig): layers[f"sig{i}"] = L
    bg = np.zeros((H, W, 3), np.float32); bg[:] = PAPER
    for f in range(int(seconds * FPS)):
        t = f / FPS; fr = bg.copy()
        for name, t0, t1 in tl:
            if t < t0: continue
            p = ease((t - t0) / (t1 - t0))
            if name == "dot": fr = blend(fr, L_lk1, alpha=p)
            else: fr = blend(fr, layers[name], alpha=p, dy=int(round(12 * (1 - p))) if name.startswith("sig") or name in ("name", "when") else 0)
        yield fr

def seg_card(last_png, W, H, out_path, quand, slogan, marque, card=5.0):
    last = np.array(Image.open(last_png).convert("RGB")).astype(np.float32)
    proc = ffmpeg(out_path, W, H)
    for k, fr in enumerate(final_card_frames(W, H, card, quand, slogan, marque)):
        if k < 9: fr = last * (1 - k / 9) + fr * (k / 9)
        proc.stdin.write(grain(fr).tobytes())
    proc.stdin.close(); proc.wait()

# ------------------------------------------------------------------ R1
def seg_r1_body(photos, W, H, out_path, last_png, marque, per=1.6, hook=2.2):
    s = W / 1080; cx = W // 2
    proc = ffmpeg(out_path, W, H)
    bg = np.zeros((H, W, 3), np.float32); bg[:] = PAPER
    yc = H // 2
    L_vp = text_layer(W, H, [("a6", "VENTE EXCLUSIVE", int(30 * s), INK, cx, None, yc - int(90 * s), 8 * s)])
    nsize = int(230 * s)
    while nsize > 100 and text_width(marque, nsize) > W * 0.9: nsize -= 4
    L_nm = text_layer(W, H, [("f", marque, nsize, INK, cx, None, yc + int(90 * s), 0)])
    for f in range(int(hook * FPS)):
        t = f / FPS; fr = bg.copy()
        fr = blend(fr, L_vp, ease(t / 0.35))
        if t > 0.25: fr = blend(fr, L_nm, ease((t - 0.25) / 0.45), dy=int(round(16 * (1 - ease((t - 0.25) / 0.45)))))
        proc.stdin.write(grain(fr).tobytes())
    lk = lockup(int(110 * s), INK); L_lk = img_layer(lk, W, H, W - int(56 * s) - lk.width, int(48 * s) if H < 1500 else int(120 * s))
    label_y = H - (int(56 * s) if H < 1500 else int(150 * s))
    label = f"{marque.upper()}  ·  VENTE EXCLUSIVE  ·  EN LIVE SUR WHATNOT"
    lsize = fit_label(label, int(22 * s), W * 0.9, 4 * s)
    L_lab = text_layer(W, H, [("a6", label, lsize, INK, cx, None, label_y, 4 * s)])
    n = int(per * FPS)
    for i, p in enumerate(photos):
        photo = Image.open(p).convert("RGB")
        for j, fr in enumerate(kenburns_frames(photo, W, H, n, anchor=0.0)):
            fr = blend(fr, L_lk); fr = blend(fr, L_lab)
            if i == 0 and j < 6: fr = fr * (j / 6) + bg * (1 - j / 6)
            proc.stdin.write(grain(fr, 0.8).tobytes())
        print("  R1 photo", i + 1, flush=True)
    Image.fromarray(np.clip(fr, 0, 255).astype(np.uint8)).save(last_png)
    proc.stdin.close(); proc.wait()

# ------------------------------------------------------------------ R2
def seg_r2_card(kind, item, col, W, H, out_path, marque, last_png=None, beat=0.62):
    s = W / 1080; cx = W // 2
    ink = INK if col == PAPER else PAPER
    lk = lockup(int(120 * s), ink)
    bg = np.zeros((H, W, 3), np.float32); bg[:] = col
    L_lk = img_layer(lk, W, H, cx - lk.width // 2, int(70 * s) if H < 1500 else int(150 * s))
    if kind == "robe":
        b = fit(cutout(item), int(W * 0.70), int(H * (0.58 if H < 1500 else 0.62)))
        bx = cx - b.width // 2; by = H - int(H * 0.07) - b.height
        L_sh = shadow_layer(W, H, b, bx, by); L_b = img_layer(b, W, H, bx, by)
        lab = f"VENTE EXCLUSIVE  ·  {marque.upper()}  ·  SUR WHATNOT"
        L_t = text_layer(W, H, [("a6", lab, fit_label(lab, int(22 * s), W * 0.9, 5 * s), ink, cx, None, (int(70 * s) if H < 1500 else int(150 * s)) + lk.height + int(60 * s), 5 * s)])
    else:
        size = int(150 * s)
        while size > int(80 * s) and text_width(item, size) > W * 0.88: size -= 4
        L_t = text_layer(W, H, [("f", item, size, ink, cx, None, H // 2 + int(55 * s), 0)])
    proc = ffmpeg(out_path, W, H)
    for f in range(int(beat * FPS)):
        t = f / FPS; p = ease(t / 0.18)
        fr = bg.copy(); fr = blend(fr, L_lk)
        if kind == "robe":
            fr = blend(fr, L_sh, p); fr = blend(fr, L_b, p, dy=int(round(60 * (1 - p)))); fr = blend(fr, L_t)
        else:
            fr = blend(fr, L_t, p, dy=int(round(14 * (1 - p))))
        proc.stdin.write(grain(fr).tobytes())
    if last_png: Image.fromarray(np.clip(fr, 0, 255).astype(np.uint8)).save(last_png)
    proc.stdin.close(); proc.wait()

def concat(segments, out_path):
    lst = out_path + ".txt"
    with open(lst, "w") as fh:
        for sgm in segments: fh.write(f"file '{os.path.abspath(sgm)}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", out_path], check=True)
    os.remove(lst)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--marque", required=True); ap.add_argument("--date", required=True); ap.add_argument("--heure", default="")
    ap.add_argument("--couleur", default="#F5A11A"); ap.add_argument("--portees", nargs="+", required=True); ap.add_argument("--packs", nargs="*", default=[])
    ap.add_argument("--which", default="all"); ap.add_argument("--out", required=True); ap.add_argument("--complet", action="store_true")
    a = ap.parse_args()
    marque = a.marque; COLOR = tuple(int(a.couleur.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    when = f"{a.date} · {a.heure}" if a.heure else a.date
    quand = f"{when} · {LIVE}"; mot_date = (f"{a.date}, {a.heure}." if a.heure else f"{a.date}.")
    slogans = list(SLOGANS) if a.complet else ["slogan"]
    out = a.out; seg = os.path.join(out, "_segments"); os.makedirs(seg, exist_ok=True)
    formats = [("story", 1080, 1920)] + ([("post", 1080, 1350)] if a.complet else [])
    slug = marque.lower().replace(" ", "-")
    packs = a.packs; n = len(packs)
    # montage R2 A : les pièces en boucle, un mot toutes les deux ou trois pièces ; papier aux positions paires, couleur aux impaires
    mots = [f"{marque}.", "Une vente exclusive.", f"{LIVE}.", mot_date]
    A = []; k = 0
    if n == 0: mots = []   # pas de packshots → pas de R2 (kit 5 : --which r1)
    for mi, mot in enumerate(mots):
        for _ in range(2 if n >= 2 else 1): A.append(("robe", k % n)); k += 1
        if mi < len(mots) - 1 and n >= 3: A.append(("robe", k % n)); k += 1
        A.append(("mot", mot))
    if n and len(A) % 2 == 0: A.append(("robe", k % n))     # la dernière pièce ferme sur la couleur
    R2 = {"A": A}
    if a.complet: R2["B"] = A[:]; R2["B"].insert(0, ("robe", (k + 1) % n))
    for fmt, W, H in formats:
        if a.which in ("all", "r1"):
            body = os.path.join(seg, f"r1_body_{fmt}.mp4"); last = os.path.join(seg, f"r1_last_{fmt}.png")
            if not os.path.exists(last): seg_r1_body(a.portees, W, H, body, last, marque); print("R1 corps", fmt, flush=True)
            for slo in slogans:
                card = os.path.join(seg, f"r1_card_{slo}_{fmt}.mp4"); seg_card(last, W, H, card, quand, slo, marque)
                concat([body, card], os.path.join(out, f"{slug}_reel-R1-defile_{fmt}_{slo}.mp4")); print("R1", fmt, slo, flush=True)
        if a.which in ("all", "r2") and n:
            done = {}
            for variant, cards in R2.items():
                segs = []
                for idx, (kind, item) in enumerate(cards):
                    col = PAPER if idx % 2 == 0 else COLOR
                    sl = "".join(ch for ch in str(item).lower().replace(" ", "-") if ch.isalnum() or ch == "-")
                    key = f"robe{item}_{'p' if col == PAPER else 'c'}" if kind == "robe" else f"mot_{sl}_{'p' if col == PAPER else 'c'}"
                    path = os.path.join(seg, f"r2_{key}_{fmt}.mp4"); last = path[:-4] + "_last.png"
                    if key not in done:
                        seg_r2_card(kind, packs[item] if kind == "robe" else item, col, W, H, path, marque, last); done[key] = last
                    segs.append(path)
                for slo in slogans:
                    card = os.path.join(seg, f"r2{variant}_card_{slo}_{fmt}.mp4"); seg_card(done[key], W, H, card, quand, slo, marque)
                    concat(segs + [card], os.path.join(out, f"{slug}_reel-R2{variant}-battements_{fmt}_{slo}.mp4")); print("R2" + variant, fmt, slo, flush=True)
    print("OK", out)
