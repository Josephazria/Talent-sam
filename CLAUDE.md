# VitaminD Studio — contexte pour Claude Code

Ce dépôt (branche `studio-media`, orpheline) contient les outils et les médias du Studio de Joseph : Ohlalive (priorité), The Live Corner (TLC), VitaminD, Doctorgane. Joseph pilote, Déborah Moussaï est la liveuse/associée. Joseph est direct, déteste les longs processus et les longues questions : on livre, on montre, il corrige.

## Où est quoi
- `tools/README.md` : procédure complète du kit express automatique (lire en premier).
- `tools/kit/` : moteur visuel Python/PIL (`ohlalive_kit.py`, `kit_express.py`, `reels.py`, `sud.py`, `story_sud.py`…). Rendu 4×, LANCZOS, grain léger. Polices dans `tools/fonts/` (variable `KIT_FONTS`), sortie via `KIT_OUT`. Dépendances : `pillow`, `numpy`, `ffmpeg`.
- `tools/newsletter/` : newsletter éditoriale HTML (envoyée via Brevo).
- `media/ohlalive/<slug>/` : médias publiés ; `media/ohlalive/sud/<ville>/` = campagne « Ohlalive arrive dans le Sud » (11 posts + 11 reels) ; `media/ohlalive/brand/` = en-tête.
- URL publique d'un média : `https://raw.githubusercontent.com/Josephazria/Talent-sam/studio-media/<chemin>` (Postiz ne lit que des URL publiques ; le dépôt est donc public, jamais de secret dedans).
- Assets de marque (lockups, vignettes) : fichiers du projet claude.ai « Ohlàlive » ; docs du projet sous `claude/kit-live/` (copie des scripts).

## Outils / connecteurs (compte claude.ai de Joseph)
- **Postiz** (MCP) : programmer posts/stories/reels IG + TikTok. `uploadFromUrlTool` (URL publique) puis `integrationSchedulePostTool` (dates en UTC). Ids des comptes dans `tools/README.md`. Jamais de publication « now ». Ne peut pas supprimer.
- **Notion** : Planning des lives `collection://457781b7-0551-4672-94aa-8661e6f5bc0c` ; Contacts & clientes `collection://09b7e99c-83a4-4048-887e-097d4e3c65dc` (Marque, Origine, Consentement…).
- **Lovable** : site Ohlalive (projet `ba0d455e-c9bf-4fed-afff-0cf5b8ca88be`) et TLC (`d73a02d7-45d7-4e96-89d8-3195cf97818f`). Brevo (e-mailing) n'est joignable que par la fonction SQL `studio.brevo(...)` du projet TLC ; la clé est dans le coffre Supabase, jamais en clair.
- Navigateur intégré de l'app Claude (sessions déjà connectées, dont Meta Ads Manager). Les sandboxes cloud n'atteignent que GitHub et les registres de paquets : `git push` passe, l'API GitHub d'écriture et l'API Postiz directe non.
- Tâches planifiées (cloud, fuseau Europe/Paris) : topo du matin 07:48, sync sites↔Notion 07:22, kit Ohlalive auto 07:27, kit TLC auto 07:31, newsletter hebdo dim. 17:53, veille Doctorgane.
- Skills de compte à utiliser : `ohlalive-communication`, `kitohlalive`, `tlc-kit-vente`, `the-live-corner-contenu`, `vitamindcommunication`, `doctorgane`.

## Marque Ohlalive (figée)
- « Ohlalive » à l'écrit ; mot-marque « Oh là live ! » (Playfair Display, « là » en italique, point du « ! » coloré). Polices Playfair Display + Jost.
- MIMOSA (244,200,70) · FRAMBOISE (150,58,76) · ivoire (242,240,234) · encre (26,26,26). Un accent par support, aplats, pas de dégradé, logo jamais déformé. Baseline « Maison de sélection parisienne ». Handle `@ohlaliveparis`.
- Produit : premium/luxe/niche uniquement, jamais fast fashion. « Sur Whatnot » toujours écrit. Jamais d'image IA d'une pièce réellement vendue ; IA non trompeuse (cf. skill).
- Rien n'est arrêté sur : rémunération des associées, parcours client, statut juridique, INPI (classes 25/35). Ne jamais présenter comme décidé. INPI et handles à vérifier avant toute pub sponsorisée.

## Règles de travail
- Texte validé avant série de visuels ; si Joseph dicte un texte, l'appliquer tel quel.
- Livrer des planches de contrôle ; vérifier marges et zones sûres story (260 px haut/bas).
- Actions engageantes (publier, envoyer un e-mail, dépenser en pub) : accord explicite de Joseph. Jamais de saisie de moyens de paiement ni de mot de passe.
- Pub Meta : le compte personnel de Joseph est restreint (« Invalid request (#1) » + moyen de paiement manquant, constaté le 07/10/2026) ; c'est Déborah/l'admin du Business Manager qui crée et paie. Budget max 50 €/mois/marque. Codes postaux, jamais un département.

## À savoir (au 14/10/2026)
- Campagne Sud : les 11 posts/reels portent encore le 07 56 98 14 26 et l'ancien texte ; la story Sud (`media/ohlalive/sud/STORY_sud_*.png`) porte le **06 59 64 32 57** et le texte explicite (« Vous avez un dressing à vider ? / Contactez-nous. On s'occupe de tout. »). Refonte des posts/reels en attente du go de Joseph ; numéro à confirmer partout.
- Clé SMTP Brevo exposée en conversation le 05/10 : à supprimer côté Brevo.
