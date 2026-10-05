#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ohlalive — cartes verticales 1080x1920 : story teasing, story « on est en live », cover Whatnot.
6 dérivés : 3 couleurs x 2 compositions (A typo / B emblème).
"""
import os
from PIL import Image, ImageDraw
from ohlalive_kit import *

OUT_W, OUT_H = 1080, 1920
W, H = OUT_W * SCALE, OUT_H * SCALE
S = SCALE

def render(scheme, compo, spec, s=1.0, dry=False):
    sc = SCHEMES[scheme]
    canvas = Image.new("RGB", (W, H), sc["bg"])
    d = ImageDraw.Draw(canvas)
    cx = W // 2

    if compo == "A":
        logo = lockup(scheme, spec.get("logo_w", 900) * S * s)
        head_size, it_size = spec.get("head_size", 150), spec.get("italic_size", 185)
    else:
        emb  = emblem(scheme, spec.get("emblem_w", 300) * S * s)
        logo = lockup(scheme, spec.get("wordmark_w", 720) * S * s, wordmark_only=True)
        head_size, it_size = spec.get("head_size", 150) * 0.94, spec.get("italic_size", 185) * 0.94

    f_eye  = jost("SemiBold", 34 * S * s)
    f_head = playfair("Bold", head_size * S * s)
    f_it   = playfair_italic("Medium Italic", it_size * S * s)
    f_sub  = jost("SemiBold", 34 * S * s)
    f_foot = jost("Medium", 24 * S)
    f_hand = jost("Medium", 22 * S)

    div_w, div_th = int(100 * S), max(int(3 * S), 2)
    g_emb_logo, g_logo_eye, g_eye_head = int(36 * S * s), int(90 * S * s), int(46 * S * s)
    g_head_it, g_it_div, g_div_sub = int(20 * S * s), int(70 * S * s), int(60 * S * s)

    lh_eye, lh_head, lh_it, lh_sub = (line_height(d, f) for f in (f_eye, f_head, f_it, f_sub))

    block = logo.height + g_logo_eye
    if spec.get("eyebrow"): block += lh_eye + g_eye_head
    block += lh_head + g_head_it + lh_it + g_it_div + div_th
    if spec.get("sub"): block += g_div_sub + lh_sub
    if compo == "B": block += emb.height + g_emb_logo

    top_safe, bottom_safe = int(spec.get("top_safe", 250) * S), int(spec.get("bottom_safe", 320) * S)
    avail = H - top_safe - bottom_safe
    if dry:
        return block, avail

    y = top_safe + (avail - block) // 2

    if compo == "B":
        paste_rgba(canvas, emb, cx - emb.width // 2, y); y += emb.height + g_emb_logo
    paste_rgba(canvas, logo, cx - logo.width // 2, y); y += logo.height + g_logo_eye

    if spec.get("eyebrow"):
        draw_tracked(d, y, spec["eyebrow"], f_eye, sc["accent"], tracking=int(6 * S * s), cx=cx)
        y += lh_eye + g_eye_head

    draw_centered(d, y, spec["head"], f_head, sc["text"], cx); y += lh_head + g_head_it
    draw_centered(d, y, spec["italic"], f_it, sc["text"], cx); y += lh_it + g_it_div
    d.rectangle([cx - div_w // 2, y, cx + div_w // 2, y + div_th], fill=sc["accent"]); y += div_th

    if spec.get("sub"):
        y += g_div_sub
        draw_tracked(d, y, spec["sub"], f_sub, sc["text"], tracking=int(4 * S * s), cx=cx)

    # pied, au-dessus de la zone sûre basse
    foot = spec.get("footer", [])
    fy = H - bottom_safe + int(40 * S)
    for i, line in enumerate(foot):
        f = f_foot if i == 0 and len(foot) > 1 else f_hand
        col = sc["text"] if (i == 0 and len(foot) > 1) else sc["accent"]
        draw_tracked(d, fy, line, f, col, tracking=int(4 * S), cx=cx)
        fy += line_height(d, f) + int(14 * S)

    return finish(canvas, OUT_W, OUT_H)

def build(scheme, compo, spec):
    block, avail = render(scheme, compo, spec, dry=True)
    s = min(1.0, avail / block)
    return render(scheme, compo, spec, s=s)

def build_family(slug, family, spec, compos=("A", "B")):
    out_dir = f"{os.environ.get('KIT_OUT','kit')}/{slug}/{family}"
    os.makedirs(out_dir, exist_ok=True)
    paths, labels = [], []
    names = {"A": "A-typo", "B": "B-embleme"}
    for compo in compos:
        for scheme in ("framboise", "mimosa", "ivoire"):
            img = build(scheme, compo, spec)
            p = f"{out_dir}/{slug}_{family}_{names[compo]}_{scheme}.png"
            img.save(p); paths.append(p); labels.append(f"{names[compo].upper()}  ·  {scheme.upper()}")
            print("saved", p)
    sheet = contact_sheet(paths, labels, cols=3, thumb_w=400)
    sp = f"{out_dir}/{slug}_{family}_PLANCHE.png"
    sheet.save(sp); print("saved", sp)
    return paths, sp

SLUG = "2026-09-22"

STORY_TEASING = {
    "eyebrow": "MARDI 22 SEPTEMBRE  ·  12H",
    "head": "Sélection", "italic": "de luxe",
    "footer": ["EN LIVE SUR WHATNOT", "@OHLALIVEPARIS"],
    "top_safe": 250, "bottom_safe": 330,
}

STORY_LIVE = {
    "eyebrow": "C'EST MAINTENANT",
    "head": "On est", "italic": "en live",
    "sub": "SÉLECTION DE LUXE",
    "footer": ["SUR WHATNOT", "@OHLALIVEPARIS"],
    "top_safe": 250, "bottom_safe": 330,
}

COVER_WHATNOT = {
    "head": "Sélection", "italic": "de luxe",
    "footer": ["@OHLALIVEPARIS"],
    "logo_w": 960, "top_safe": 140, "bottom_safe": 160,
}

if __name__ == "__main__":
    build_family(SLUG, "story-teasing", STORY_TEASING)
    build_family(SLUG, "story-live", STORY_LIVE)
    build_family(SLUG, "cover-whatnot", COVER_WHATNOT)
