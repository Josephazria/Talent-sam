import Link from "next/link";
import { BackIcon } from "@/components/Icons";

// Écran d'attente réutilisable pour les fonctionnalités des prochaines étapes.
export default function AParaitre({ titre }: { titre: string }) {
  return (
    <>
      <Link href="/" className="corner corner--left" aria-label="Retour">
        <BackIcon />
      </Link>
      <main className="screen screen--center">
        <p className="eyebrow">{titre}</p>
        <hr className="rule" />
        <p className="subtitle" style={{ maxWidth: 280 }}>
          Cette partie arrive bientôt.
        </p>
      </main>
    </>
  );
}
