# nod

discret. anonyme. sans trace.

Nod permet à des personnes présentes dans un même lieu de se signaler
mutuellement ouvertes à une rencontre, sans qu'un rejet explicite soit
possible. Application web mobile-first (PWA), installable sur l'écran
d'accueil.

## Stack

- **Next.js** (App Router, TypeScript) — interface
- **Supabase** — authentification, base de données, temps réel *(à venir)*
- **Stripe** — crédits et paiements *(à venir)*
- **Vercel** — hébergement et déploiement

## Développement

```bash
npm install
npm run dev
```

L'application démarre sur http://localhost:3000.

## Construction

```bash
npm run build
npm run start
```

## Avancement

- [x] Étape 1 — Squelette, design system, accueil, « comment ça marche »
- [ ] Étape 2 — Compte (Google/Apple), vérification 18+, profil
- [ ] Étape 3 — Détection de lieu, signal, expiration, suppression des données
- [ ] Étape 4 — Matching, rôles, notifications push
- [ ] Étape 5 — Codes événement
- [ ] Étape 6 — Carte
- [ ] Étape 7 — Crédits, Stripe, prolongation
