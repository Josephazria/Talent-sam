# Ohlalive — kit express automatique (couche 1 « l'affiche »)

Validé par Joseph le 05/10/2026 : « tu peux publier et publier automatiquement à chaque live ».

## Ce qui part automatiquement pour CHAQUE live Ohlalive trouvé dans Notion (Planning des lives, Entité = Ohlalive, Statut ≠ Annulé)
| Quand (Paris) | Quoi | Où | Média |
|---|---|---|---|
| J, 10:00 | Story teasing (mimosa) | Instagram Ohlàlive `cmuubqglb0b0ss00yjbq9rnst`, `post_type: story` | `<slug>_story-teasing_mimosa.jpg` |
| J, 10:05 | Post teasing (framboise, 4:5) | Instagram Ohlàlive, `post_type: post` | `<slug>_post-teasing_framboise.jpg` |
| J, 12:00 | Reel R1 « montée » | Instagram Ohlàlive (`post_type: post`, vidéo 4:5) + TikTok OHLALIVE `cmuubcktm0asls00yhzowcs59` (vidéo 9:16, DIRECT_POST, musique « Elegant » id `7406303806911842305`, audio 60 / vidéo 0) | `<slug>_reel-R1_post_web.mp4` / `<slug>_reel-R1_story_web.mp4` |
| J, dans le topo du matin | Story « On est en live » (framboise) + cover Whatnot (ivoire) | PAS publiées : jointes à l'e-mail du topo pour Déborah (sticker Whatnot à poser à la main) | `<slug>_story-live_framboise.png`, `<slug>_cover-whatnot_ivoire.png` |

Live à midi ou avant 14h : story+post à J-1 18:00, reel à J 09:00. Jamais de publication « now ». Jamais deux fois le même live : vérifier `postsListTool` (fenêtre J-2 → J+1) et le contenu (titre du live) avant de programmer.

Couche 2 « marchandise » (3 stories pièces J-1 18h, reel 5 pièces J midi, story Adjugé J+1) : UNIQUEMENT si Déborah a envoyé 5 photos + prix de départ (dossier `photos/<slug>/` ou Notion). Sinon on ne fait rien et on le note dans le topo.

## Procédure (session fraîche, ~10 appels)
1. `git clone --depth 1 -b studio-media https://github.com/Josephazria/talent-sam studio-media` (le dépôt doit être attaché à la session : `add_repo Josephazria/Talent-sam access=push`). Les API GitHub d'écriture sont bloquées par le proxy ; **seul `git push` passe**.
2. Lire Notion (collection `457781b7-0551-4672-94aa-8661e6f5bc0c`) : lives Ohlalive de J et J+1. Dates Notion en UTC (Paris = UTC+2 jusqu'au 25/10/2026, puis UTC+1).
3. Écrire `kit/<slug>/live.json` sur le modèle de `tools/kit/exemple_live.json` (slug = `YYYY-MM-DD` + `-<liveuse>` si deux lives le même jour). Titre par défaut « Sélection de luxe » ; si le live a une marque/un thème dans Notion, l'utiliser (`title` + `title_italic`, max ~3 mots chacun).
4. `pip install pillow` si besoin, `ffmpeg` requis pour le reel. `KIT_OUT=$PWD/kit python3 tools/kit/kit_express.py kit/<slug>/live.json`.
5. Convertir : stills → JPEG q92 ; reels → `ffmpeg -c:v libx264 -crf 23 -pix_fmt yuv420p -movflags +faststart -an *_web.mp4` (< 1 Mo).
6. Copier dans `media/ohlalive/<slug>/`, `git add`, commit, `git push origin studio-media`. URL publique : `https://raw.githubusercontent.com/Josephazria/Talent-sam/studio-media/media/ohlalive/<slug>/<fichier>`.
7. Postiz MCP : `uploadFromUrlTool` pour chaque média → `path` ; puis `integrationSchedulePostTool` (dates en **UTC**, `type: schedule`).
8. Pilotage Studio (artefact `XPusgp2SncMg5bLmT3wstS`) : uploader les aperçus en assets, écrire `posts/<id>` statut `programmé` + `postiz_id`.
9. Si une étape réseau échoue (clone/push, upload) : ne rien programmer à moitié, le dire dans le topo du matin avec le kit en pièce jointe.

Légendes : voix Ohlalive — sobre, « Maison de sélection parisienne », « sur Whatnot » toujours écrit, départ à 1 € si c'est le format du live, jamais de superlatifs creux, 5–7 hashtags max. Jamais de visuel IA d'une pièce vendue.
