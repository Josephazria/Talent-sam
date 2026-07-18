import Link from "next/link";
import { MapIcon, GearIcon } from "@/components/Icons";

// Écran 1 — Accueil
export default function Accueil() {
  return (
    <>
      <Link
        href="/carte"
        className="corner corner--left"
        aria-label="Voir la carte"
      >
        <MapIcon />
      </Link>
      <Link
        href="/parametres"
        className="corner corner--right"
        aria-label="Paramètres"
      >
        <GearIcon />
      </Link>

      <main className="screen screen--center">
        <h1 className="wordmark">nod</h1>
        <p className="tagline">discret. anonyme. sans trace.</p>

        <div className="mt-4" style={{ width: "100%", maxWidth: 320 }}>
          <Link href="/activer" className="btn btn--primary btn--block">
            activer mon signal
          </Link>
        </div>

        <div className="mt-3">
          <Link href="/comment-ca-marche" className="btn btn--ghost">
            comment ça marche
          </Link>
        </div>
      </main>
    </>
  );
}
