#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ohlalive — KIT EXPRESS (couche 1 « l'affiche », validé dans son principe le 05/10/2026).
Une couleur par pièce, composition A typo :
  post-teasing (framboise) · story-teasing (mimosa) · story-live (framboise) · cover-whatnot (ivoire) · reel R1 story + post (framboise)
Usage : python3 kit_express.py kit/<slug>/live.json [--sans-reel]
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ohlalive_kit import contact_sheet
import post_teasing, vertical_kit, reels

ROOT = os.environ.get("KIT_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "kit"))
COLORS = {"post-teasing": "framboise", "story-teasing": "mimosa", "story-live": "framboise", "cover-whatnot": "ivoire"}

def build(live, with_reel=True):
    slug = live["slug"]; out = f"{ROOT}/{slug}"; os.makedirs(out, exist_ok=True)
    paths, labels = [], []
    p = f"{out}/{slug}_post-teasing_{COLORS['post-teasing']}.png"
    post_teasing.build(COLORS["post-teasing"], "A", live).save(p); paths.append(p); labels.append("POST TEASING 4:5")
    specs = {
        "story-teasing": {"eyebrow": live["date_label"], "head": live["title"], "italic": live["title_italic"],
                          "footer": ["EN LIVE SUR WHATNOT", "@OHLALIVEPARIS"], "top_safe": 250, "bottom_safe": 330},
        "story-live": {"eyebrow": "C'EST MAINTENANT", "head": "On est", "italic": "en live", "sub": live["sub_upper"],
                       "footer": ["SUR WHATNOT", "@OHLALIVEPARIS"], "top_safe": 250, "bottom_safe": 330},
        "cover-whatnot": {"head": live["title"], "italic": live["title_italic"], "sub": live.get("brands_line"),
                          "footer": ["@OHLALIVEPARIS"], "logo_w": 960, "top_safe": 140, "bottom_safe": 160},
    }
    for fam, spec in specs.items():
        p = f"{out}/{slug}_{fam}_{COLORS[fam]}.png"
        vertical_kit.build(COLORS[fam], "A", spec).save(p); paths.append(p); labels.append(fam.upper().replace("-", " "))
        print("saved", p)
    contact_sheet(paths, labels, cols=4, thumb_w=360).save(f"{out}/{slug}_EXPRESS_PLANCHE.png")
    if with_reel:
        for fmt, size in {"story": (1080, 1920), "post": (1080, 1350)}.items():
            p = f"{out}/{slug}_reel-R1-montee_framboise_{fmt}.mp4"
            reels.encode(reels.reel_montee("framboise", size, live, p), size, p); print("saved", p)
    return out

if __name__ == "__main__":
    live = json.load(open(sys.argv[1]))
    build(live, with_reel="--sans-reel" not in sys.argv)
