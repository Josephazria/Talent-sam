# THE LIVE CORNER — médias et boîte à outils (branche `tlc-media`)

Branche technique : hébergement public des visuels pour Postiz (`raw.githubusercontent.com`)
et boîte à outils du kit par vente. Rien ici n'est destiné à être lu par une cliente.

## Arborescence
- `tlc/<marque>-<AAAA-MM-JJ>/` — les fichiers d'une vente :
  `post_annonce.jpg` (4:5), `story_annonce.jpg` (9:16), `story_veille.jpg` (9:16, J-1, « Enregistre le live pour être prévenue »),
  `story_ce_soir.jpg` (9:16, J-0), `hero_site_1080.jpg` + `hero_site_1920.jpg` (site), `reel_defile_9x16.mp4`, `sources/` (photos utilisées).
- `tlc/kit/` — scripts + polices + logos : `kit_vente_tlc.py` (kit 5 par défaut), `tlc_reels.py` (`--which r1`),
  `galerie_court.py`. Pré-requis : `pip install pillow numpy cairosvg rembg onnxruntime`, `ffmpeg`.

## Produire un kit (depuis n'importe quelle session)
```
git clone --depth 1 --branch tlc-media https://github.com/Josephazria/talent-sam
cd talent-sam/tlc/kit
python3 kit_vente_tlc.py --marque "Kouka" --date "Mardi 13 octobre" --heure 17h --remise 70 \
    --couleur "#B9A58B" --portees ../../portees_kouka --hero <clé> --out ../kouka-2026-10-13
python3 tlc_reels.py --marque "Kouka" --date "Mardi 13 octobre" --heure 17h --couleur "#B9A58B" \
    --portees ../../portees_kouka/*.jpg --which r1 --out ../kouka-2026-10-13
git add tlc/<dossier> && git commit -m "kit Kouka 13/10" && git push origin tlc-media
```
URL publique d'un fichier : `https://raw.githubusercontent.com/Josephazria/talent-sam/tlc-media/tlc/<dossier>/<fichier>`
→ `uploadFromUrlTool` (Postiz) puis `integrationSchedulePostTool`.

## Règles de publication (accord Joseph, 05/10/2026)
- Canaux Postiz : Instagram « The Live Corner - Ventes privées en live » `cmuubsrzc0b1gs00yztkfzb8s` ;
  TikTok « The Live Corner » `cmuubxar30b5es00yp3k6xgwz`.
- J-3 12h Paris : post annonce (Instagram). J-1 12h Paris : reel (Instagram + TikTok) ET story veille (Instagram, post_type story,
  image `story_veille.jpg`). Type `schedule`, jamais `now`. Si J-3 est déjà passé : le lendemain 12h (ou dans 2 h si c'est J-1).
- Stories avec sticker (annonce J-0 10h, « C'est ce soir » 1 h avant) : jamais programmées — Déborah les poste avec le sticker lien Whatnot.
- Texte centré sur couverture/coin (bloc remise · date · Whatnot · logo, bas à 86 % de la hauteur) — Joseph, 05/10/2026.
- Légende : « Vente exclusive <Marque>. En live sur Whatnot, <jour date> à <heure>. Jusqu'à −<XX> %. Lien dans la bio. »
  Toujours « vente exclusive » (plus « vente privée »), toujours « en live sur Whatnot ».
- Garde-fou : programmation directe, visible dans le Topo du matin ; Joseph annule dans Postiz si besoin.
